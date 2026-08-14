from fastapi import APIRouter, HTTPException

from app.analysis.congestion import (
    analyze_nodes,
    find_bottleneck,
    find_alternatives,
)

from app.analysis.metrics import (
    MetricsTracker,
    build_metrics,
)


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


# =========================================================
# METRICS HISTORY
# =========================================================

# Keeps utilization history while the server is running.
metrics_tracker = MetricsTracker()


# =========================================================
# SIMULATION STATE ADAPTER
# =========================================================

def get_simulation_state() -> dict:
    """
    Get the current simulation state from P1.

    P1 owns:
        - agents
        - movement
        - routes
        - simulation engine

    P2 owns:
        - utilization
        - congestion status
        - bottlenecks
        - alternatives
        - metrics
        - predictions

    Expected P1 state:

    {
        "venue": "stadium_01",

        "crowd": {
            "total": 400,
            "moving": 350
        },

        "nodes": [
            {
                "id": "exit_a",
                "occupancy": 410,
                "capacity": 500,
                "utilization": 0.82
            }
        ]
    }
    """

    try:

        # -------------------------------------------------
        # Import P1 simulation module
        # -------------------------------------------------

        from app.api import simulation


        # -------------------------------------------------
        # Get state from P1
        # -------------------------------------------------

        state = simulation.get_state()


        # -------------------------------------------------
        # Protect against None
        # -------------------------------------------------

        if state is None:

            return {
                "venue": "stadium_01",

                "crowd": {
                    "total": 0,
                    "moving": 0,
                },

                "nodes": [],
            }


        # -------------------------------------------------
        # Ensure required keys exist
        # -------------------------------------------------

        state.setdefault(
            "venue",
            "stadium_01",
        )

        state.setdefault(
            "crowd",
            {
                "total": 0,
                "moving": 0,
            },
        )

        state.setdefault(
            "nodes",
            [],
        )


        return state


    # -----------------------------------------------------
    # P1 simulation is not available yet
    # -----------------------------------------------------

    except (ImportError, AttributeError):

        return {
            "venue": "stadium_01",

            "crowd": {
                "total": 0,
                "moving": 0,
            },

            "nodes": [],
        }


# =========================================================
# ANALYSIS ENDPOINT
# =========================================================

@router.get("")
def get_analysis():
    """
    Analyze the current crowd simulation state.

    Flow:

        P1 Simulation
              ↓
        Simulation State
              ↓
        Analyze Nodes
              ↓
        Find Bottleneck
              ↓
        Find Alternatives
              ↓
        Calculate Metrics
              ↓
        Return P2 Analytics
    """

    try:

        # =================================================
        # 1. GET CURRENT SIMULATION STATE
        # =================================================

        state = get_simulation_state()

        nodes = state.get(
            "nodes",
            [],
        )


        # =================================================
        # 2. HANDLE EMPTY SIMULATION
        # =================================================

        if not nodes:

            return {
                "venue": state.get(
                    "venue",
                    "stadium_01",
                ),

                "crowd": state.get(
                    "crowd",
                    {
                        "total": 0,
                        "moving": 0,
                    },
                ),

                "nodes": [],

                "bottlenecks": [],

                "alternatives": [],

                "metrics": {
                    "congestion_score": 0,
                    "average_wait": 0.0,
                    "predictions": [],
                },
            }


        # =================================================
        # 3. ANALYZE EVERY NODE
        # =================================================

        analyzed_nodes = analyze_nodes(
            nodes
        )


        # =================================================
        # 4. FIND BOTTLENECK
        # =================================================

        bottleneck = find_bottleneck(
            analyzed_nodes
        )


        bottlenecks = []

        if bottleneck:

            bottlenecks.append(
                bottleneck
            )


        # =================================================
        # 5. FIND ALTERNATIVE NODES
        # =================================================

        bottleneck_id = None

        if bottleneck:

            bottleneck_id = bottleneck.get(
                "node_id"
            )


        alternatives = find_alternatives(
            analyzed_nodes,
            bottleneck_id,
        )


        # =================================================
        # 6. BUILD METRICS + PREDICTIONS
        # =================================================

        metrics = build_metrics(
            analyzed_nodes,
            metrics_tracker,
        )


        # =================================================
        # 7. RETURN P2 ANALYTICS CONTRACT
        # =================================================

        return {

            "venue": state.get(
                "venue",
                "stadium_01",
            ),

            "crowd": state.get(
                "crowd",
                {
                    "total": 0,
                    "moving": 0,
                },
            ),

            "nodes": analyzed_nodes,

            "bottlenecks": bottlenecks,

            "alternatives": alternatives,

            "metrics": metrics,
        }


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Analytics calculation failed: "
                f"{str(exc)}"
            ),
        )