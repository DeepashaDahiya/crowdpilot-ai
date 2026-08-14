"""
CrowdPilot AI - Metrics and Prediction

P2 responsibilities:
- Congestion score
- Average wait estimate
- Recent utilization history
- Congestion trend
- Short-term congestion prediction
"""

from collections import defaultdict, deque


# =========================================================
# CONFIGURATION
# =========================================================

HISTORY_SIZE = 5

PREDICTION_THRESHOLD = 0.80

TREND_EPSILON = 0.01


# =========================================================
# METRICS TRACKER
# =========================================================

class MetricsTracker:
    """
    Stores recent utilization values for each node.

    Example:

        exit_a:
            [0.60, 0.70, 0.82, 0.90]

    This allows P2 to determine whether congestion
    is increasing.
    """

    def __init__(
        self,
        history_size: int = HISTORY_SIZE,
    ):
        self.history_size = history_size

        self.history = defaultdict(
            lambda: deque(
                maxlen=self.history_size
            )
        )

    def update(
        self,
        nodes: list[dict],
    ):
        """
        Add the current utilization of every node
        to its history.
        """

        for node in nodes:

            node_id = node.get(
                "id",
                "unknown",
            )

            utilization = float(
                node.get(
                    "utilization",
                    0,
                )
            )

            self.history[node_id].append(
                utilization
            )

    def get_history(
        self,
        node_id: str,
    ) -> list[float]:

        return list(
            self.history.get(
                node_id,
                [],
            )
        )

    def get_trend(
        self,
        node_id: str,
    ) -> float:
        """
        Calculate the change between the newest
        and oldest available utilization value.

        Positive = increasing
        Negative = decreasing
        Zero = stable
        """

        history = self.get_history(
            node_id
        )

        if len(history) < 2:
            return 0.0

        return round(
            history[-1] - history[0],
            3,
        )

    def is_increasing(
        self,
        node_id: str,
    ) -> bool:

        return (
            self.get_trend(node_id)
            > TREND_EPSILON
        )


# =========================================================
# CONGESTION SCORE
# =========================================================

def calculate_congestion_score(
    nodes: list[dict],
) -> int:
    """
    Calculate overall venue congestion score.

    Uses the highest node utilization.

    Example:

        exit_a = 0.82
        exit_b = 0.50
        exit_c = 0.20

        score = 82
    """

    if not nodes:
        return 0

    maximum_utilization = max(
        float(
            node.get(
                "utilization",
                0,
            )
        )
        for node in nodes
    )

    return round(
        maximum_utilization * 100
    )


# =========================================================
# AVERAGE WAIT
# =========================================================

def calculate_average_wait(
    nodes: list[dict],
) -> float:
    """
    Estimate average wait from congestion.

    This is a simple heuristic for the prototype.

    It intentionally avoids pretending to be a
    real queueing model.

    Higher utilization -> higher estimated wait.
    """

    if not nodes:
        return 0.0

    total_wait = 0.0
    counted_nodes = 0

    for node in nodes:

        utilization = float(
            node.get(
                "utilization",
                0,
            )
        )

        # Only congestion above 60% contributes
        # to the estimated waiting time.
        excess = max(
            0.0,
            utilization - 0.60,
        )

        wait = excess * 20

        total_wait += wait
        counted_nodes += 1

    if counted_nodes == 0:
        return 0.0

    return round(
        total_wait / counted_nodes,
        1,
    )


# =========================================================
# PREDICTIONS
# =========================================================

def generate_predictions(
    nodes: list[dict],
    tracker: MetricsTracker,
) -> list[str]:
    """
    Generate short-term congestion predictions.

    Rule:

        utilization > 0.80
        AND
        utilization is trending upward

        → prediction
    """

    predictions = []

    for node in nodes:

        node_id = node.get(
            "id",
            "unknown",
        )

        utilization = float(
            node.get(
                "utilization",
                0,
            )
        )

        # -------------------------------------------------
        # Only predict when already above 80%
        # -------------------------------------------------

        if utilization <= PREDICTION_THRESHOLD:
            continue

        # -------------------------------------------------
        # Need an increasing trend
        # -------------------------------------------------

        if not tracker.is_increasing(
            node_id
        ):
            continue

        trend = tracker.get_trend(
            node_id
        )

        # -------------------------------------------------
        # Human-readable node name
        # -------------------------------------------------

        display_name = node_id.replace(
            "_",
            " ",
        ).title()

        predictions.append(
            (
                f"High congestion predicted at "
                f"{display_name} within ~60 seconds."
            )
        )

    return predictions


# =========================================================
# BUILD METRICS
# =========================================================

def build_metrics(
    nodes: list[dict],
    tracker: MetricsTracker,
) -> dict:
    """
    Update history and build the complete metrics object.
    """

    # -----------------------------------------------------
    # Update utilization history FIRST
    # -----------------------------------------------------

    tracker.update(
        nodes
    )

    # -----------------------------------------------------
    # Calculate metrics
    # -----------------------------------------------------

    congestion_score = (
        calculate_congestion_score(
            nodes
        )
    )

    average_wait = (
        calculate_average_wait(
            nodes
        )
    )

    predictions = (
        generate_predictions(
            nodes,
            tracker,
        )
    )

    return {
        "congestion_score": congestion_score,
        "average_wait": average_wait,
        "predictions": predictions,
    }