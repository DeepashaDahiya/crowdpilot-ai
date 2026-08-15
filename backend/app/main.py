from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#from app.api import simulation
from app.api import analysis


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="CrowdPilot AI Backend"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.api import simulation
app.include_router(simulation.router)


# =========================================================
# API ROUTERS
# =========================================================

# Person 1 — Simulation
# app.include_router(simulation.router)


# Person 2 — Analytics
app.include_router(
    analysis.router
)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }