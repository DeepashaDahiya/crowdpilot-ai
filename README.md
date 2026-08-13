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

## AI / Recommendation Engine (Person 3)

### What it does
Given live congestion data, the system generates a structured, validated operational recommendation using a Hugging Face-hosted LLM — never freeform text, always a constrained JSON action the simulation can execute.

### Architecture

Analytics data
→ get_candidate_actions() (deterministic — only real, valid exits ever offered)
→ build_recommendation_prompt() (forces JSON-only output, numeric/confident tone)
→ call_model() (Hugging Face Inference Providers, meta-llama/Llama-3.1-8B-Instruct)
→ validate_recommendation() (rejects invalid actions, falls back to best candidate)
→ /recommendation endpoint

### Key design decisions
- **The AI never invents actions.** `recommender.py` computes valid candidate exits from real utilization data first; the model can only pick from that list.
- **Validation + fallback layer.** If the model returns invalid JSON, an unlisted action, or a bad redirect_percentage, `validate_recommendation()` silently substitutes a safe, deterministic answer — the demo never breaks from a bad model response.
- **In-memory caching.** Successful responses are cached per-bottleneck; if a live HF call fails mid-demo, the last known-good recommendation for that scenario is served instead.

### Endpoints
| Method | Path | Description |
|---|---|---|
| POST | `/recommendation` | Fetches live analytics (via `ANALYSIS_URL`), returns a validated AI recommendation |
| POST | `/apply-recommendation` | Sends a reroute instruction to the simulation engine (via `SIMULATION_BASE_URL`) |

### Environment variables (see `.env.example`)

HF_API_TOKEN=your_huggingface_token_here
HF_MODEL_ID=meta-llama/Llama-3.1-8B-Instruct
ANALYSIS_URL=http://localhost:8002/analysis
SIMULATION_BASE_URL=http://localhost:8000

### Testing without teammates' live servers
`mock_analysis_server.py` and `mock_simulation_server.py` simulate Person 2's and Person 1's real endpoints respectively — run either on its own port and point the corresponding `.env` variable at it to test independently. Delete both once real integration is fully confirmed at demo time.

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
