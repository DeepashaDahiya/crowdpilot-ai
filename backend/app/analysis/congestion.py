"""
CrowdPilot AI - Congestion Analysis

P2 responsibilities:
- Calculate node utilization
- Classify congestion severity
- Analyze all venue nodes
- Identify the most congested node
- Find alternative exits with available capacity
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
        occupancy = 400
        capacity = 500

        utilization = 0.80
    """

    if capacity <= 0:
        return 0.0

    utilization = occupancy / capacity

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
    Classify congestion level.

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
    Analyze every node received from P1.

    P1 provides:

    {
        "id": "exit_a",
        "occupancy": 400,
        "capacity": 500,
        "utilization": 0.8
    }

    P2 adds:

    {
        "status": "high"
    }
    """

    analyzed_nodes: list[dict[str, Any]] = []

    for node in nodes:

        node_id = node.get(
            "id",
            "unknown",
        )

        # -------------------------------------------------
        # Read occupancy
        # -------------------------------------------------

        try:
            occupancy = float(
                node.get(
                    "occupancy",
                    0,
                )
            )
        except (TypeError, ValueError):
            occupancy = 0.0

        # -------------------------------------------------
        # Read capacity
        # -------------------------------------------------

        try:
            capacity = float(
                node.get(
                    "capacity",
                    0,
                )
            )
        except (TypeError, ValueError):
            capacity = 0.0

        # -------------------------------------------------
        # Calculate utilization ourselves
        #
        # This keeps P2 authoritative for analytics.
        # -------------------------------------------------

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
        # Preserve original node information
        # -------------------------------------------------

        analyzed_node = dict(node)

        if occupancy.is_integer():
            analyzed_node["occupancy"] = int(
                occupancy
            )
        else:
            analyzed_node["occupancy"] = occupancy

        if capacity.is_integer():
            analyzed_node["capacity"] = int(
                capacity
            )
        else:
            analyzed_node["capacity"] = capacity

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
    Find the single most congested node.

    Example:

        exit_a = 0.80
        exit_b = 0.20
        exit_c = 0.10

    Result:

        {
            "node_id": "exit_a",
            "severity": 0.80,
            "status": "high"
        }
    """

    if not analyzed_nodes:
        return None

    bottleneck = max(
        analyzed_nodes,
        key=lambda node: float(
            node.get(
                "utilization",
                0,
            )
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
# FIND ALTERNATIVE EXITS
# =========================================================

def find_alternatives(
    analyzed_nodes: list[dict[str, Any]],
    bottleneck_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Find suitable alternative exits.

    Rules:
    1. Only exit_* nodes are valid.
    2. Current bottleneck is excluded.
    3. Full exits are excluded.
    4. Least congested exits are preferred.
    """

    alternatives: list[dict[str, Any]] = []

    for node in analyzed_nodes:

        node_id = str(
            node.get(
                "id",
                "unknown",
            )
        )

        # -------------------------------------------------
        # Exclude current bottleneck
        # -------------------------------------------------

        if node_id == bottleneck_id:
            continue

        # -------------------------------------------------
        # Only exits can be rerouting destinations
        # -------------------------------------------------

        if not node_id.startswith("exit_"):
            continue

        # -------------------------------------------------
        # Read utilization
        # -------------------------------------------------

        try:
            utilization = float(
                node.get(
                    "utilization",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            utilization = 0.0

        # -------------------------------------------------
        # Read capacity
        # -------------------------------------------------

        try:
            capacity = float(
                node.get(
                    "capacity",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            capacity = 0.0

        # -------------------------------------------------
        # Read occupancy
        # -------------------------------------------------

        try:
            occupancy = float(
                node.get(
                    "occupancy",
                    0.0,
                )
            )
        except (TypeError, ValueError):
            occupancy = 0.0

        # -------------------------------------------------
        # Calculate available capacity
        # -------------------------------------------------

        available_capacity = max(
            0.0,
            capacity - occupancy,
        )

        # Ignore full exits.
        if available_capacity <= 0:
            continue

        alternatives.append(
            {
                "node_id": node_id,
                "utilization": round(
                    max(
                        0.0,
                        min(
                            utilization,
                            1.0,
                        ),
                    ),
                    2,
                ),
                "available_capacity": int(
                    available_capacity
                ),
            }
        )

    # -----------------------------------------------------
    # Best alternative first
    #
    # 1. Lowest utilization
    # 2. If equal, highest available capacity
    # -----------------------------------------------------

    alternatives.sort(
        key=lambda item: (
            item["utilization"],
            -item["available_capacity"],
        )
    )

    return alternatives