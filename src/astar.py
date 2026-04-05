"""
astar.py — A* Optimal Startup Sequencing

Finds the minimum-cost order to activate plant units, respecting
prerequisite dependencies. Heuristic h(n) = sum of remaining unit
costs (admissible → guarantees optimal solution).
"""

import heapq


class StartupPlanner:
    """
    A* search for optimal plant startup sequencing.

    Prerequisite constraints are encoded as a dependency graph.
    Heuristic h(n) = sum of costs of all remaining units — admissible,
    so A* is guaranteed to return the optimal sequence.
    """

    UNITS = ["cooling", "feed", "reactor", "separator", "recycle"]

    PREREQS = {
        "reactor":   {"cooling", "feed"},
        "separator": {"reactor"},
        "recycle":   {"separator"},
        "cooling":   set(),
        "feed":      set(),
    }

    UNIT_COST = {
        "cooling":   1,
        "feed":      1,
        "reactor":   3,
        "separator": 2,
        "recycle":   2,
    }

    def neighbors(self, state):
        active = set(state)
        return [
            state + (u,)
            for u in self.UNITS
            if u not in active and self.PREREQS[u].issubset(active)
        ]

    def g_cost(self, state):
        return sum(self.UNIT_COST[u] for u in state)

    def heuristic(self, state):
        """Admissible: sum of costs of all units not yet activated."""
        active = set(state)
        return sum(self.UNIT_COST[u] for u in self.UNITS if u not in active)

    def search(self):
        """
        Run A* search.

        Returns
        -------
        tuple  : (sequence, total_cost)
                 sequence — tuple of unit names in activation order
                 total_cost — integer cost of that sequence
        """
        start   = tuple()
        pq      = [(self.heuristic(start), 0, start)]
        visited = set()
        g_score = {start: 0}

        while pq:
            f, g, state = heapq.heappop(pq)
            if len(state) == len(self.UNITS):
                return state, g
            if state in visited:
                continue
            visited.add(state)
            for nb in self.neighbors(state):
                new_g = g + self.UNIT_COST[nb[-1]]
                if nb not in g_score or new_g < g_score[nb]:
                    g_score[nb] = new_g
                    heapq.heappush(pq, (new_g + self.heuristic(nb), new_g, nb))

        return None, float("inf")


if __name__ == "__main__":
    planner = StartupPlanner()
    plan, cost = planner.search()
    print("Optimal Startup Sequence:", " → ".join(plan))
    print(f"Total Startup Cost      : {cost} time units")
