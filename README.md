# CrowdPilot AI

AI-powered predictive crowd control for safer, smoother events.

## Structure

```
frontend/   React/Next.js dashboard (Person 2 primary, Person 3 for AI panel)
backend/    FastAPI backend
  app/api/          route handlers (simulation.py, analysis.py, recommendations.py)
  app/simulation/   graph.py, agents.py, engine.py   (Person 1)
  app/analysis/     congestion.py, metrics.py        (Person 2)
  app/ai/           hf_client.py, recommender.py, prompts.py  (Person 3)
data/venues/  venue definitions (stadium.json)
docs/         architecture notes, API contract, demo script
```

## API Contract

See `docs/contract.json` — frozen on Day 1, do not change field names after that.

## Setup

Backend:
```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```
cd frontend
npm install
npm run dev
```

## Branches

- `main` — protected, PR only
- `feature/simulation` — Person 1
- `feature/analytics` — Person 2
- `feature/ai` — Person 3
