from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CrowdPilot AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO Person 1: from app.api import simulation; app.include_router(simulation.router)
# TODO Person 2: from app.api import analysis; app.include_router(analysis.router)
from app.api import recommendations
app.include_router(recommendations.router)

@app.get("/health")
def health():
    return {"status": "ok"}
