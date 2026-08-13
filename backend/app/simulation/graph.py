import json
from collections import deque

import os
def load_venue(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "venues", "stadium.json")
    with open(path) as f:
        return json.load(f)

def build_adjacency(venue):
    adj = {node: [] for node in venue["nodes"]}
    for a, b in venue["edges"]:
        adj[a].append(b)
        adj[b].append(a)
    return adj

def shortest_path(adj, start, end):
    queue = deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end:
            return path
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None

if __name__ == "__main__":
    venue = load_venue()
    adj = build_adjacency(venue)
    print(adj)
    print(shortest_path(adj, "gate_a", "exit_c"))
    