import random

from app.simulation.agents import spawn_agents
from app.simulation.graph import (
    load_venue,
    build_adjacency,
    shortest_path,
)


class Engine:

    def __init__(self, n_agents=400):
        # For the demo, initially send everyone toward Exit A.
        self.policy = {
            "exit_a": 1.0
        }

        self.agents = spawn_agents(
            n_agents,
            policy=self.policy
        )

    def step(self):
        """
        Move every active agent one node along its route.
        """

        for agent in self.agents:

            # Ignore agents that have already arrived.
            if agent.state == "arrived":
                continue

            # If the agent has reached its destination,
            # mark it as arrived.
            if agent.current_node == agent.destination:
                agent.state = "arrived"
                continue

            # Safety check.
            if not agent.route:
                agent.state = "arrived"
                continue

            # Find current position in the route.
            try:
                current_index = agent.route.index(
                    agent.current_node
                )
            except ValueError:
                # Current node is not in route.
                agent.state = "arrived"
                continue

            # Move one node forward.
            if current_index + 1 < len(agent.route):

                agent.current_node = (
                    agent.route[current_index + 1]
                )

            # Check whether destination was reached.
            if agent.current_node == agent.destination:
                agent.state = "arrived"

    def get_state(self):
        """
        Return the number of agents currently
        occupying each node.
        """

        occupancy = {}

        for agent in self.agents:

            node = agent.current_node

            occupancy[node] = (
                occupancy.get(node, 0) + 1
            )

        return occupancy

    def reroute(
        self,
        from_node,
        to_node,
        redirect_percentage,
    ):
        """
        Redirect a percentage of agents whose
        current destination is from_node.

        Example:

            exit_a -> exit_b
            30%

        If 400 agents are going to Exit A,
        approximately 120 agents will be
        redirected to Exit B.
        """

        venue = load_venue()

        adjacency = build_adjacency(
            venue
        )

        # -----------------------------------------
        # Validate percentage
        # -----------------------------------------

        try:
            redirect_percentage = float(
                redirect_percentage
            )
        except (TypeError, ValueError):
            return 0

        redirect_percentage = max(
            0.0,
            min(
                redirect_percentage,
                100.0
            )
        )

        # -----------------------------------------
        # Find agents assigned to the
        # congested destination.
        # -----------------------------------------

        candidates = [
            agent
            for agent in self.agents
            if agent.destination == from_node
        ]

        if not candidates:
            return 0

        # -----------------------------------------
        # Calculate number to redirect.
        # -----------------------------------------

        n_to_redirect = int(
            len(candidates)
            * (
                redirect_percentage
                / 100.0
            )
        )

        if n_to_redirect <= 0:
            return 0

        # -----------------------------------------
        # Randomly select agents.
        # -----------------------------------------

        chosen = random.sample(
            candidates,
            min(
                n_to_redirect,
                len(candidates)
            )
        )

        rerouted = 0

        # -----------------------------------------
        # Change their destination and route.
        # -----------------------------------------

        for agent in chosen:

            new_route = shortest_path(
                adjacency,
                agent.current_node,
                to_node,
            )

            if not new_route:
                continue

            agent.destination = to_node

            agent.route = new_route

            # If the agent had already arrived
            # at the old exit, activate it again.
            agent.state = "moving"

            rerouted += 1

        return rerouted


if __name__ == "__main__":

    engine = Engine(400)

    for i in range(20):

        engine.step()

        positions = [
            agent.current_node
            for agent in engine.agents[:5]
        ]

        print(
            f"tick {i}: {positions}"
        )

        print(
            engine.get_state()
        )