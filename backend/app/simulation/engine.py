import random
from backend.app.simulation.agents import spawn_agents

class Engine:
    

    def __init__(self, n_agents=400):
        self.policy = {"exit_a": 1.0}
        self.agents = spawn_agents(n_agents, policy=self.policy)


    def step(self):
        for agent in self.agents:
            if agent.state == "arrived":
                continue
            if agent.current_node == agent.destination:
                agent.state = "arrived"
                continue
            current_index = agent.route.index(agent.current_node)
            if current_index + 1 < len(agent.route):
                agent.current_node = agent.route[current_index + 1]
            if agent.current_node == agent.destination:
                agent.state = "arrived"

    def get_state(self):
        occupancy = {}
        for agent in self.agents:
            occupancy[agent.current_node] = occupancy.get(agent.current_node, 0) + 1
        return occupancy           
    def reroute(self, from_node, to_node, redirect_percentage):
        from backend.app.simulation.graph import load_venue, build_adjacency, shortest_path
        venue = load_venue()
        adj = build_adjacency(venue)

        candidates = [a for a in self.agents if a.destination == from_node and a.state == "moving"]
        n_to_redirect = int(len(candidates) * (redirect_percentage / 100))
        chosen = random.sample(candidates, min(n_to_redirect, len(candidates)))

        for agent in chosen:
            new_route = shortest_path(adj, agent.current_node, to_node)
            if new_route:
                agent.destination = to_node
                agent.route = new_route

        return len(chosen)

if __name__ == "__main__":
    
    engine = Engine(400)
    for i in range(20):
        engine.step()
        positions = [a.current_node for a in engine.agents[:5]]
        print(f"tick {i}: {positions}")
        print(engine.get_state())
