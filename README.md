## Simulation Engine (Person 1)

### Run it
1. `python -m venv venv && source venv/bin/activate`
2. `pip install fastapi uvicorn requests`
3. `uvicorn api.simulation:app --reload`

### Endpoints
- `POST /simulation/start` — spawns 400 agents, begins ticking
- `POST /simulation/pause` — stops ticking
- `POST /simulation/reset` — clears simulation back to idle
- `GET /simulation/state` — returns current crowd/node occupancy
- `POST /simulation/reroute` — body: `{from_node, to_node, redirect_percentage}`, redirects that % of in-transit agents

### Venue format
See `data/venues/stadium.json` — nodes list, edges list, per-exit capacities.
