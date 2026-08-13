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