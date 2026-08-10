def get_candidate_actions(analytics: dict) -> list[dict]:
    """
    Given analytics data (bottlenecks + alternatives), return a list of
    valid, real candidate actions the AI is allowed to choose from.
    Never let the AI invent an action outside this list.
    """
    bottlenecks = analytics.get("bottlenecks", [])
    alternatives = analytics.get("alternatives", [])

    if not bottlenecks:
        return []  # nothing congested, no action needed

    worst = max(bottlenecks, key=lambda b: b["utilization"])

    candidates = []
    for alt in alternatives:
        if alt["utilization"] < 0.6:  # only suggest genuinely open alternatives
            candidates.append({
                "action": f"Open {alt['node'].replace('_', ' ').title()}",
                "from_node": worst["node"],
                "to_node": alt["node"],
                "alt_utilization": alt["utilization"],
            })

    # sort so the least-congested alternative is first (best option)
    candidates.sort(key=lambda c: c["alt_utilization"])
    return candidates


if __name__ == "__main__":
    mock_analytics = {
        "bottlenecks": [{"node": "exit_a", "utilization": 0.92}],
        "alternatives": [
            {"node": "exit_b", "utilization": 0.34},
            {"node": "exit_c", "utilization": 0.21},
        ],
    }
    print(get_candidate_actions(mock_analytics))