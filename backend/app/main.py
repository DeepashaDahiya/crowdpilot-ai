import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import simulation
from app.api import analysis
from app.api import recommendations

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

# =========================================================
# API ROUTERS
# =========================================================
app.include_router(simulation.router)
app.include_router(analysis.router)
app.include_router(recommendations.router)

# =========================================================
# BACKGROUND TICK LOOP
# =========================================================
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation.tick_loop())

# =========================================================
# HEALTH CHECK
# =========================================================
@app.get("/health")
def health():
    return {"status": "ok"}