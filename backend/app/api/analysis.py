# TODO: implement routes
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


# Keeps utilization history while the server is running.
metrics_tracker = MetricsTracker()


# ---------------------------------------------------------
# TEMPORARY MOCK SIMULATION
# ---------------------------------------------------------
# This is only for testing P2 until Person 1 implements
# the real simulation.
# ---------------------------------------------------------

simulation_tick = 0


def get_simulation_state() -> dict:
    """
    Temporary dynamic simulation for testing P2.

    Every request represents one simulation tick.

    Exit A:
        60% → 70% → 82% → 90% → 94% → 60%
    """

    global simulation_tick

    simulation_tick += 1

    occupancy_sequence = [
        300,
        350,
        410,
        450,
        470,
        300,
    ]

    index = (simulation_tick - 1) % len(occupancy_sequence)

    exit_a_occupancy = occupancy_sequence[index]

    # Other nodes change slightly with the simulation.
    exit_b_occupancy = [
        250,
        250,
        240,
        220,
        200,
        250,
    ][index]

    exit_c_occupancy = [
        100,
        110,
        120,
        140,
        160,
        100,
    ][index]

    main_hall_occupancy = [
        400,
        430,
        470,
        520,
        550,
        400,
    ][index]

    food_court_occupancy = [
        160,
        180,
        200,
        220,
        240,
        160,
    ][index]

    gate_a_occupancy = [
        120,
        140,
        160,
        180,
        190,
        120,
    ][index]

    return {
        "venue": "stadium_01",

        "crowd": {
            "total": 500,
            "moving": 420,
        },

        "nodes": [
            {
                "id": "gate_a",
                "occupancy": gate_a_occupancy,
                "capacity": 300,
            },

            {
                "id": "main_hall",
                "occupancy": main_hall_occupancy,
                "capacity": 800,
            },

            {
                "id": "food_court",
                "occupancy": food_court_occupancy,
                "capacity": 400,
            },

            {
                "id": "exit_a",
                "occupancy": exit_a_occupancy,
                "capacity": 500,
            },

            {
                "id": "exit_b",
                "occupancy": exit_b_occupancy,
                "capacity": 500,
            },

            {
                "id": "exit_c",
                "occupancy": exit_c_occupancy,
                "capacity": 500,
            },
        ],
    }

# ---------------------------------------------------------
# ANALYSIS ENDPOINT
# ---------------------------------------------------------

@router.get("")
def get_analysis():
    """
    Analyze the current crowd simulation state.

    Flow:

        Simulation state
              ↓
        Analyze nodes
              ↓
        Find bottleneck
              ↓
        Find alternatives
              ↓
        Calculate metrics
              ↓
        Return analytics
    """

    try:

        # -------------------------------------------------
        # 1. Get current simulation state
        # -------------------------------------------------

        state = get_simulation_state()

        nodes = state.get("nodes", [])


        # -------------------------------------------------
        # 2. Handle empty simulation
        # -------------------------------------------------

        if not nodes:

            return {
                "venue": state.get(
                    "venue",
                    "unknown",
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


        # -------------------------------------------------
        # 3. Analyze every node
        # -------------------------------------------------

        analyzed_nodes = analyze_nodes(nodes)


        # -------------------------------------------------
        # 4. Find the most congested node
        # -------------------------------------------------

        bottleneck = find_bottleneck(
            analyzed_nodes
        )

        bottlenecks = []

        if bottleneck:
            bottlenecks.append(bottleneck)


        # -------------------------------------------------
        # 5. Find alternative nodes
        # -------------------------------------------------

        bottleneck_id = None

        if bottleneck:
            bottleneck_id = bottleneck["node_id"]

        alternatives = find_alternatives(
            analyzed_nodes,
            bottleneck_id,
        )


        # -------------------------------------------------
        # 6. Calculate metrics and predictions
        # -------------------------------------------------

        metrics = build_metrics(
            analyzed_nodes,
            metrics_tracker,
        )


        # -------------------------------------------------
        # 7. Return P2 analytics
        # -------------------------------------------------

        return {

            "venue": state.get(
                "venue",
                "unknown",
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


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Analytics calculation failed: {str(exc)}",
        )