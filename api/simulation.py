import asyncio
from fastapi import FastAPI
from engine import Engine

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
sim = {"engine": None, "status": "idle"}

async def tick_loop():
    while True:
        if sim["status"] == "running" and sim["engine"] is not None:
            sim["engine"].step()
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tick_loop())

@app.post("/simulation/start")
def start():
    sim["engine"] = Engine(400)
    sim["status"] = "running"
    return {"status": "running"}

@app.post("/simulation/pause")
def pause():
    sim["status"] = "paused"
    return {"status": "paused"}

@app.post("/simulation/reset")
def reset():
    sim["engine"] = None
    sim["status"] = "idle"
    return {"status": "idle"}

@app.get("/simulation/state")
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
        nodes.append({
            "id": node_id,
            "occupancy": count,
            "capacity": cap,
            "utilization": round(count / cap, 2)
        })
        
    return {"crowd": {"total": total, "moving": moving}, "nodes": nodes}
from pydantic import BaseModel

class RerouteRequest(BaseModel):
    from_node: str
    to_node: str
    redirect_percentage: float

@app.post("/simulation/reroute")
def reroute(req: RerouteRequest):
    if sim["engine"] is None:
        return {"error": "simulation not running"}
    n_rerouted = sim["engine"].reroute(req.from_node, req.to_node, req.redirect_percentage)
    return {"rerouted_count": n_rerouted}