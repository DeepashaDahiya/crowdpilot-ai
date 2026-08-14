"""
CrowdPilot AI - Congestion Analysis

P2 responsibilities:
- Calculate node utilization
- Classify congestion severity
- Identify the most congested node
- Find alternative nodes with available capacity
"""

from typing import Any


# =========================================================
# CONGESTION THRESHOLDS
# =========================================================

LOW_THRESHOLD = 0.60
MODERATE_THRESHOLD = 0.80
HIGH_THRESHOLD = 0.90


# =========================================================
# UTILIZATION
# =========================================================

def calculate_utilization(
    occupancy: float,
    capacity: float,
) -> float:
    """
    Calculate utilization from occupancy and capacity.

    Example:
        occupancy = 410
        capacity = 500

        utilization = 410 / 500 = 0.82
    """

    if capacity <= 0:
        return 0.0

    utilization = occupancy / capacity

    # Keep the value within 0-1.
    utilization = max(
        0.0,
        min(utilization, 1.0),
    )

    return round(utilization, 2)


# =========================================================
# CONGESTION STATUS
# =========================================================

def get_congestion_status(
    utilization: float,
) -> str:
    """
    Classify utilization.

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


# =========================================================
# ANALYZE NODES
# =========================================================

def analyze_nodes(
    nodes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Analyze every venue node.

    Input from P1:

    {
        "id": "exit_a",
        "occupancy": 410,
        "capacity": 500
    }

    Output:

    {
        "id": "exit_a",
        "occupancy": 410,
        "capacity": 500,
        "utilization": 0.82,
        "status": "high"
    }
    """

    analyzed_nodes = []

    for node in nodes:

        node_id = node.get(
            "id",
            "unknown",
        )

        occupancy = node.get(
            "occupancy",
            0,
        )

        capacity = node.get(
            "capacity",
            0,
        )

        # -------------------------------------------------
        # Convert values safely
        # -------------------------------------------------

        try:
            occupancy = float(occupancy)
        except (TypeError, ValueError):
            occupancy = 0.0

        try:
            capacity = float(capacity)
        except (TypeError, ValueError):
            capacity = 0.0

        # -------------------------------------------------
        # Use P1 utilization if supplied.
        # Otherwise calculate it ourselves.
        # -------------------------------------------------

        supplied_utilization = node.get(
            "utilization"
        )

        if supplied_utilization is not None:

            try:
                utilization = float(
                    supplied_utilization
                )

                utilization = max(
                    0.0,
                    min(utilization, 1.0),
                )

                utilization = round(
                    utilization,
                    2,
                )

            except (TypeError, ValueError):

                utilization = calculate_utilization(
                    occupancy,
                    capacity,
                )

        else:

            utilization = calculate_utilization(
                occupancy,
                capacity,
            )

        # -------------------------------------------------
        # Determine congestion status
        # -------------------------------------------------

        status = get_congestion_status(
            utilization
        )

        # -------------------------------------------------
        # Preserve the node information
        # -------------------------------------------------

        analyzed_node = dict(node)

        analyzed_node["occupancy"] = (
            int(occupancy)
            if occupancy.is_integer()
            else occupancy
        )

        analyzed_node["capacity"] = (
            int(capacity)
            if capacity.is_integer()
            else capacity
        )

        analyzed_node["utilization"] = utilization

        analyzed_node["status"] = status

        analyzed_nodes.append(
            analyzed_node
        )

    return analyzed_nodes


# =========================================================
# FIND BOTTLENECK
# =========================================================

def find_bottleneck(
    analyzed_nodes: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Find the single most-congested node.

    Returns:

    {
        "node_id": "exit_a",
        "severity": 0.92,
        "status": "critical"
    }

    Returns None when there are no nodes.
    """

    if not analyzed_nodes:
        return None

    bottleneck = max(
        analyzed_nodes,
        key=lambda node: node.get(
            "utilization",
            0,
        ),
    )

    utilization = float(
        bottleneck.get(
            "utilization",
            0,
        )
    )

    return {
        "node_id": bottleneck.get(
            "id",
            "unknown",
        ),
        "severity": round(
            utilization,
            2,
        ),
        "status": bottleneck.get(
            "status",
            get_congestion_status(
                utilization
            ),
        ),
    }


# =========================================================
# FIND ALTERNATIVES
# =========================================================

def find_alternatives(
    analyzed_nodes: list[dict[str, Any]],
    bottleneck_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Find less-congested nodes that can act as alternatives.

    The bottleneck itself is excluded.

    Alternatives are sorted by utilization:
        lowest utilization first.

    Example:

        exit_a = 0.82  <- bottleneck
        exit_b = 0.50
        exit_c = 0.20

    Result:

        exit_c
        exit_b
    """

    alternatives = []

    for node in analyzed_nodes:

        node_id = node.get(
            "id",
            "unknown",
        )

        # -------------------------------------------------
        # Never recommend the current bottleneck
        # -------------------------------------------------

        if node_id == bottleneck_id:
            continue

        utilization = float(
            node.get(
                "utilization",
                0,
            )
        )

        capacity = float(
            node.get(
                "capacity",
                0,
            )
        )

        occupancy = float(
            node.get(
                "occupancy",
                0,
            )
        )

        available_capacity = max(
            0,
            capacity - occupancy,
        )

        # -------------------------------------------------
        # Only consider nodes with available capacity
        # -------------------------------------------------

        if available_capacity <= 0:
            continue

        alternatives.append(
            {
                "node_id": node_id,
                "utilization": round(
                    utilization,
                    2,
                ),
                "available_capacity": int(
                    available_capacity
                ),
            }
        )

    # -----------------------------------------------------
    # Prefer the least congested alternatives
    # -----------------------------------------------------

    alternatives.sort(
        key=lambda node: node["utilization"]
    )

    return alternatives