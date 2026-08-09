import random
from graph import load_venue, build_adjacency, shortest_path

class Agent:
    def __init__(self, agent_id, current_node, destination, route):
        self.id = agent_id
        self.current_node = current_node
        self.destination = destination
        self.route = route
        self.state = "moving"

def spawn_agents(n, gate="gate_a"):
    venue = load_venue()
    adj = build_adjacency(venue)
    exits = [node for node in venue["nodes"] if node.startswith("exit_")]
    agents = []
    for i in range(n):
        destination = random.choice(exits)
        route = shortest_path(adj, gate, destination)
        agents.append(Agent(agent_id=i, current_node=gate, destination=destination, route=route))
    return agents

if __name__ == "__main__":
    agents = spawn_agents(400)
    print(len(agents))
    print(vars(agents[0]))
    