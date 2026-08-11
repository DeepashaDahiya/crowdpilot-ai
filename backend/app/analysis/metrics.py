from collections import defaultdict, deque
from typing import Any


# Number of recent utilization readings to remember
HISTORY_SIZE = 10

# Prediction threshold from the project specification
PREDICTION_UTILIZATION_THRESHOLD = 0.80


class MetricsTracker:
    """
    Tracks recent utilization values for each venue node.

    Example history:

    exit_a:
        0.70
        0.75
        0.81
        0.87
        0.92
    """

    def __init__(self, history_size: int = HISTORY_SIZE):
        self.history_size = history_size

        self.history: dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=self.history_size)
        )

    def update(self, analyzed_nodes: list[dict[str, Any]]) -> None:
        """
        Add the latest utilization value for every node.
        """

        for node in analyzed_nodes:
            node_id = node["id"]
            utilization = float(node["utilization"])

            self.history[node_id].append(utilization)

    def get_history(self, node_id: str) -> list[float]:
        """
        Return recent utilization values for a node.
        """

        return list(self.history.get(node_id, []))

    def calculate_trend(self, node_id: str) -> float:
        """
        Calculate the change in utilization.

        Positive value  -> utilization increasing
        Negative value  -> utilization decreasing
        Zero             -> no change

        Example:

        Previous = 0.80
        Current  = 0.90

        Trend = 0.10
        """

        values = self.get_history(node_id)

        if len(values) < 2:
            return 0.0

        previous = values[-2]
        current = values[-1]

        return round(current - previous, 4)

    def is_trending_up(self, node_id: str) -> bool:
        """
        Check whether utilization is increasing.
        """

        return self.calculate_trend(node_id) > 0

    def generate_prediction(
        self,
        node: dict[str, Any]
    ) -> str | None:
        """
        Generate a congestion prediction.

        Prediction is generated when:
        1. utilization > 0.80
        2. utilization is increasing
        """

        node_id = node["id"]
        utilization = float(node["utilization"])

        if utilization > PREDICTION_UTILIZATION_THRESHOLD:
            if self.is_trending_up(node_id):
                return (
                    f"High congestion predicted at "
                    f"{node_id} within ~60 seconds."
                )

        return None

    def get_node_metrics(
        self,
        node: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Return trend and prediction information for one node.
        """

        node_id = node["id"]

        trend = self.calculate_trend(node_id)
        prediction = self.generate_prediction(node)

        return {
            "node_id": node_id,
            "utilization": node["utilization"],
            "trend": trend,
            "prediction": prediction
        }

    def clear(self) -> None:
        """
        Clear all stored utilization history.
        """

        self.history.clear()


def calculate_average_utilization(
    analyzed_nodes: list[dict[str, Any]]
) -> float:
    """
    Calculate average utilization across all nodes.
    """

    if not analyzed_nodes:
        return 0.0

    total = sum(
        float(node["utilization"])
        for node in analyzed_nodes
    )

    return round(total / len(analyzed_nodes), 4)


def calculate_average_wait(
    analyzed_nodes: list[dict[str, Any]]
) -> float:
    """
    Calculate average wait if wait information exists.

    The current contract.json does not provide wait time per node,
    so this returns 0 until the simulation supplies that information.
    """

    wait_values = []

    for node in analyzed_nodes:
        if "wait_time" in node:
            wait_values.append(float(node["wait_time"]))

    if not wait_values:
        return 0.0

    return round(
        sum(wait_values) / len(wait_values),
        2
    )


def build_metrics(
    analyzed_nodes: list[dict[str, Any]],
    tracker: MetricsTracker
) -> dict[str, Any]:
    """
    Build the metrics section returned by the analytics API.
    """

    tracker.update(analyzed_nodes)

    congestion_score = 0

    if analyzed_nodes:
        congestion_score = round(
            max(
                node["utilization"]
                for node in analyzed_nodes
            ) * 100
        )

    predictions = []

    for node in analyzed_nodes:
        prediction = tracker.generate_prediction(node)

        if prediction:
            predictions.append(prediction)

    return {
        "congestion_score": congestion_score,
        "average_wait": calculate_average_wait(analyzed_nodes),
        "predictions": predictions
    }