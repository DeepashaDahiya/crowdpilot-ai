import asyncio
from collections import Counter

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.simulation.engine import Engine
from app.simulation.graph import load_venue


router = APIRouter(
    tags=["Simulation"]
)

sim = {
    "engine": None,
    "status": "idle",
}


# =========================================================
# SIMULATION TICK LOOP
# =========================================================

async def tick_loop():
    while True:

        if (
            sim["status"] == "running"
            and sim["engine"] is not None
        ):
            sim["engine"].step()

        # P1 simulation updates every 500 ms
        await asyncio.sleep(0.5)


# =========================================================
# STARTUP
# =========================================================

@router.on_event("startup")
async def startup_event():
    asyncio.create_task(tick_loop())


# =========================================================
# START SIMULATION
# =========================================================

@router.post("/simulation/start")
def start():

    sim["engine"] = Engine(400)
    sim["status"] = "running"

    return {
        "status": "running"
    }


# =========================================================
# PAUSE SIMULATION
# =========================================================

@router.post("/simulation/pause")
def pause():

    if sim["engine"] is None:
        return {
            "status": "idle"
        }

    sim["status"] = "paused"

    return {
        "status": "paused"
    }


# =========================================================
# RESET SIMULATION
# =========================================================

@router.post("/simulation/reset")
def reset():

    sim["engine"] = None
    sim["status"] = "idle"

    return {
        "status": "idle"
    }


# =========================================================
# DEBUG ENDPOINT
# =========================================================

@router.get("/simulation/debug")
def debug():

    if sim["engine"] is None:
        return {
            "error": "simulation not running"
        }

    counts = Counter(
        (
            agent.destination,
            agent.state
        )
        for agent in sim["engine"].agents
    )

    return {
        f"{destination}-{state}": count
        for (
            destination,
            state
        ), count in counts.items()
    }


# =========================================================
# SIMULATION STATE
# =========================================================

@router.get("/simulation/state")
def get_state():

    # -----------------------------------------------------
    # Simulation has not started
    # -----------------------------------------------------

    if sim["engine"] is None:

        return {
            "venue": "stadium_01",

            "crowd": {
                "total": 0,
                "moving": 0,
            },

            "nodes": [],
        }


    # -----------------------------------------------------
    # Load venue configuration
    # -----------------------------------------------------

    venue = load_venue()

    venue_nodes = venue.get(
        "nodes",
        []
    )

    venue_capacities = venue.get(
        "capacities",
        {}
    )


    # -----------------------------------------------------
    # Get current occupancy from P1 engine
    # -----------------------------------------------------

    occupancy = sim["engine"].get_state()


    # -----------------------------------------------------
    # Crowd statistics
    # -----------------------------------------------------

    total = len(
        sim["engine"].agents
    )

    moving = sum(
        1
        for agent in sim["engine"].agents
        if agent.state == "moving"
    )


    # -----------------------------------------------------
    # Build state for EVERY venue node
    #
    # This is important for P2's heatmap.
    #
    # Even if a node has zero agents, it must still
    # appear in the response.
    # -----------------------------------------------------

    nodes = []

    for node_id in venue_nodes:

        node_occupancy = occupancy.get(
            node_id,
            0
        )

        # Exit capacities come from stadium.json.
        # Non-exit nodes currently use 1000 as the
        # fallback capacity because stadium.json only
        # defines explicit capacities for exits.

        capacity = venue_capacities.get(
            node_id,
            1000
        )

        if capacity <= 0:
            utilization = 0.0
        else:
            utilization = round(
                node_occupancy / capacity,
                2
            )

        nodes.append(
            {
                "id": node_id,

                "occupancy": node_occupancy,

                "capacity": capacity,

                "utilization": utilization,
            }
        )


    # -----------------------------------------------------
    # Final P1 simulation contract
    # -----------------------------------------------------

    return {
        "venue": "stadium_01",

        "crowd": {
            "total": total,
            "moving": moving,
        },

        "nodes": nodes,
    }


# =========================================================
# REROUTE REQUEST
# =========================================================

class RerouteRequest(BaseModel):

    from_node: str

    to_node: str

    redirect_percentage: float


# =========================================================
# REROUTE
# =========================================================

@router.post("/simulation/reroute")
def reroute(
    req: RerouteRequest
):

    # -----------------------------------------------------
    # Simulation must be running
    # -----------------------------------------------------

    if sim["engine"] is None:

        raise HTTPException(
            status_code=400,
            detail="simulation not running",
        )


    # -----------------------------------------------------
    # Validate venue nodes
    # -----------------------------------------------------

    venue = load_venue()

    valid_nodes = set(
        venue.get(
            "nodes",
            []
        )
    )

    if (
        req.from_node not in valid_nodes
        or req.to_node not in valid_nodes
    ):

        raise HTTPException(
            status_code=400,
            detail="invalid node name",
        )


    # -----------------------------------------------------
    # Validate redirect percentage
    # -----------------------------------------------------

    if not (
        0 <= req.redirect_percentage <= 100
    ):

        raise HTTPException(
            status_code=400,
            detail="redirect_percentage must be between 0 and 100",
        )


    # -----------------------------------------------------
    # Do not reroute a node to itself
    # -----------------------------------------------------

    if req.from_node == req.to_node:

        raise HTTPException(
            status_code=400,
            detail="from_node and to_node must be different",
        )


    # -----------------------------------------------------
    # Perform reroute through P1 engine
    # -----------------------------------------------------

    rerouted_count = sim["engine"].reroute(
        req.from_node,
        req.to_node,
        req.redirect_percentage,
    )


    return {
        "status": "ok",
        "from_node": req.from_node,
        "to_node": req.to_node,
        "redirect_percentage": req.redirect_percentage,
        "rerouted_count": rerouted_count,
    }