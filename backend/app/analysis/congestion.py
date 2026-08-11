from typing import Any


# Congestion thresholds
LOW_THRESHOLD = 0.60
MODERATE_THRESHOLD = 0.80
HIGH_THRESHOLD = 0.90


def calculate_utilization(occupancy: int, capacity: int) -> float:
    """
    Calculate how much of a node's capacity is currently being used.

    utilization = occupancy / capacity
    """

    if capacity <= 0:
        return 0.0

    utilization = occupancy / capacity

    # Keep the value between 0 and 1
    return min(max(utilization, 0.0), 1.0)


def classify_congestion(utilization: float) -> str:
    """
    Classify congestion based on utilization.

    < 0.60  -> low
    < 0.80  -> moderate
    < 0.90  -> high
    >= 0.90 -> critical
    """

    if utilization < LOW_THRESHOLD:
        return "low"

    if utilization < MODERATE_THRESHOLD:
        return "moderate"

    if utilization < HIGH_THRESHOLD:
        return "high"

    return "critical"


def analyze_node(node: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze one venue node.

    Expected input:
    {
        "id": "exit_a",
        "occupancy": 460,
        "capacity": 500
    }

    Returns:
    {
        "id": "exit_a",
        "occupancy": 460,
        "capacity": 500,
        "utilization": 0.92,
        "status": "critical"
    }
    """

    node_id = node.get("id", "unknown")
    occupancy = int(node.get("occupancy", 0))
    capacity = int(node.get("capacity", 0))

    utilization = calculate_utilization(
        occupancy,
        capacity
    )

    status = classify_congestion(utilization)

    return {
        "id": node_id,
        "occupancy": occupancy,
        "capacity": capacity,
        "utilization": round(utilization, 4),
        "status": status
    }


def analyze_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Analyze all venue nodes.
    """

    return [analyze_node(node) for node in nodes]


def find_bottleneck(
    analyzed_nodes: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """
    Find the most congested node.

    Returns None if there are no nodes.
    """

    if not analyzed_nodes:
        return None

    bottleneck = max(
        analyzed_nodes,
        key=lambda node: node["utilization"]
    )

    return {
        "node_id": bottleneck["id"],
        "severity": bottleneck["utilization"],
        "status": bottleneck["status"]
    }


def calculate_congestion_score(
    analyzed_nodes: list[dict[str, Any]]
) -> int:
    """
    Calculate an overall congestion score from 0-100.

    The score is based on the highest node utilization.
    """

    if not analyzed_nodes:
        return 0

    highest_utilization = max(
        node["utilization"]
        for node in analyzed_nodes
    )

    return round(highest_utilization * 100)

def find_alternatives(
    analyzed_nodes: list[dict[str, Any]],
    bottleneck_id: str | None,
) -> list[dict[str, Any]]:
    """
    Find less-congested nodes that can potentially be used
    as alternatives to the current bottleneck.

    A node is considered an alternative when:
    - It is not the bottleneck.
    - Its utilization is below 80%.
    """

    alternatives = []

    for node in analyzed_nodes:

        if node["id"] == bottleneck_id:
            continue

        utilization = float(node["utilization"])

        if utilization < MODERATE_THRESHOLD:

            available_capacity = max(
                node["capacity"] - node["occupancy"],
                0,
            )

            alternatives.append(
                {
                    "node_id": node["id"],
                    "utilization": utilization,
                    "available_capacity": available_capacity,
                }
            )

    # Most available capacity first
    alternatives.sort(
        key=lambda node: node["available_capacity"],
        reverse=True,
    )

    return alternatives