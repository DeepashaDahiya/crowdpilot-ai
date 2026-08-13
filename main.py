from app.api import simulation
from app.api import analysis
from app.api import recommendations

app.include_router(simulation.router)
app.include_router(analysis.router)
app.include_router(recommendations.router)
