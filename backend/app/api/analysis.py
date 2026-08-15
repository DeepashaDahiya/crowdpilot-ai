from fastapi import APIRouter, HTTPException

from app.api import simulation

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

# Keeps utilization history while the backend is running.

metrics_tracker = MetricsTracker()


# =========================================================
# SIMULATION STATE ADAPTER
# =========================================================

def get_simulation_state() -> dict:
    """
    P2 consumes the live simulation state owned by P1.

    P1:
        /simulation/state
        ↓
        crowd
        nodes
        occupancy
        capacity
        utilization

    P2:
        congestion analysis
        bottleneck detection
        alternatives
        metrics
        predictions
    """

    try:

        state = simulation.get_state()

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to read P1 simulation state: "
                f"{str(exc)}"
            ),
        )


    # -----------------------------------------------------
    # Protect against None
    # -----------------------------------------------------

    if state is None:

        return {
            "venue": "stadium_01",

            "crowd": {
                "total": 0,
                "moving": 0,
            },

            "nodes": [],
        }


    # -----------------------------------------------------
    # Ensure required fields exist
    # -----------------------------------------------------

    if not isinstance(
        state,
        dict
    ):

        raise HTTPException(
            status_code=503,
            detail="Invalid simulation state returned by P1",
        )


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


# =========================================================
# EMPTY ANALYSIS RESPONSE
# =========================================================

def empty_analysis(
    state: dict,
) -> dict:

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


# =========================================================
# ANALYSIS ENDPOINT
# =========================================================

@router.get("")
def get_analysis():
    """
    Analyze the current live P1 simulation state.

    Flow:

        P1 Simulation
              ↓
        simulation.get_state()
              ↓
        analyze_nodes()
              ↓
        find_bottleneck()
              ↓
        find_alternatives()
              ↓
        build_metrics()
              ↓
        P2 Analytics Response
    """

    try:

        # =================================================
        # 1. GET LIVE P1 STATE
        # =================================================

        state = get_simulation_state()

        nodes = state.get(
            "nodes",
            [],
        )


        # =================================================
        # 2. HANDLE IDLE SIMULATION
        # =================================================

        if not nodes:

            return empty_analysis(
                state
            )


        # =================================================
        # 3. ANALYZE ALL NODES
        # =================================================

        analyzed_nodes = analyze_nodes(
            nodes
        )


        # =================================================
        # 4. FIND SINGLE HIGHEST-RISK NODE
        # =================================================

        bottleneck = find_bottleneck(
            analyzed_nodes
        )

        bottlenecks = []

        if bottleneck is not None:

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
        # 7. RETURN P2 CONTRACT
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
    # ANALYTICS ERROR
    # =====================================================

    except HTTPException:
        raise


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Analytics calculation failed: "
                f"{str(exc)}"
            ),
        )