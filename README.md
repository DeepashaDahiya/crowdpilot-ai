## Simulation Engine (Person 1)

### Run it
1. `python -m venv venv && source venv/bin/activate`
2. `pip install fastapi uvicorn requests`
3. `uvicorn api.simulation:app --reload`

### Endpoints
- `POST /simulation/start` — spawns 400 agents at gate_a, begins ticking every 0.5s
- `POST /simulation/pause` — stops ticking
- `POST /simulation/reset` — clears simulation back to idle
- `GET /simulation/state` — returns `{crowd: {total, moving}, nodes: [{id, occupancy, capacity, utilization}]}`
- `GET /simulation/debug` — internal: returns per-destination/state agent counts (not for frontend use)
- `POST /simulation/reroute` — body: `{from_node, to_node, redirect_percentage}` — redirects that % of in-transit agents from one exit toward another. Returns `{rerouted_count}`.

### Venue format
`data/venues/stadium.json` — `nodes` (list), `edges` (list of pairs), `capacities` (per-exit).
Current demo path: gate_a → corridor_1 → corridor_2 → corridor_3 → main_hall → exit_a/exit_b/exit_c (5–6 hops, ~2s to fully arrive at 0.5s/tick).

### Known behavior
Agents move in lockstep — all agents on the same policy/path arrive on the same tick (no per-agent speed variance). Crowd policy defaults to 70/15/15 split favoring exit_a for a reliable demo bottleneck.

### Error handling
- State requested before start → returns empty state, not an error
- Reroute with unknown node name → 400 `"invalid node name"`
- Reroute before start → 400 `"simulation not running"`
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
