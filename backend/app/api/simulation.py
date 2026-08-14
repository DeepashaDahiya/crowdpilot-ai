import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from collections import Counter
from app.simulation.engine import Engine
from app.simulation.graph import load_venue

router = APIRouter()
sim = {"engine": None, "status": "idle"}

async def tick_loop():
    while True:
        if sim["status"] == "running" and sim["engine"] is not None:
            sim["engine"].step()
        await asyncio.sleep(0.5)

@router.post("/simulation/start")
def start():
    sim["engine"] = Engine(400)
    sim["status"] = "running"
    return {"status": "running"}

@router.post("/simulation/pause")
def pause():
    sim["status"] = "paused"
    return {"status": "paused"}

@router.post("/simulation/reset")
def reset():
    sim["engine"] = None
    sim["status"] = "idle"
    return {"status": "idle"}

@router.get("/simulation/debug")
def debug():
    if sim["engine"] is None:
        return {"error": "not running"}
    counts = Counter((a.destination, a.state) for a in sim["engine"].agents)
    return {f"{dest}-{state}": n for (dest, state), n in counts.items()}

@router.get("/simulation/state")
def get_state():
    if sim["engine"] is None:
        return {"crowd": {"total": 0, "moving": 0}, "nodes": []}
    occupancy = sim["engine"].get_state()
    total = len(sim["engine"].agents)
    moving = sum(1 for a in sim["engine"].agents if a.state == "moving")
    capacities = {"exit_a": 500, "exit_b": 500, "exit_c": 500}
    nodes = []
    for node_id, count in occupancy.items():
        cap = capacities.get(node_id, 1000)
        nodes.append({"id": node_id, "occupancy": count, "capacity": cap, "utilization": round(count / cap, 2)})
    return {"crowd": {"total": total, "moving": moving}, "nodes": nodes}

class RerouteRequest(BaseModel):
    from_node: str
    to_node: str
    redirect_percentage: float

@router.post("/simulation/reroute")
def reroute(req: RerouteRequest):
    if sim["engine"] is None:
        raise HTTPException(status_code=400, detail="simulation not running")
    valid_nodes = load_venue()["nodes"]
    if req.from_node not in valid_nodes or req.to_node not in valid_nodes:
        raise HTTPException(status_code=400, detail="invalid node name")
    n_rerouted = sim["engine"].reroute(req.from_node, req.to_node, req.redirect_percentage)
    return {"rerouted_count": n_rerouted}