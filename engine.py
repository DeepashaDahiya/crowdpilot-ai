from agents import spawn_agents

class Engine:
    def __init__(self, n_agents=400):
        self.agents = spawn_agents(n_agents)

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

if __name__ == "__main__":
    
    engine = Engine(400)
    for i in range(20):
        engine.step()
        positions = [a.current_node for a in engine.agents[:5]]
        print(f"tick {i}: {positions}")
        print(engine.get_state())
