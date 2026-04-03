"""
startup_planner.py
------------------
A* search for optimal plant startup sequencing.

The plant units must be activated in a safe, dependency-respecting order.
A* finds the minimum-cost path through the startup state space.

State:  tuple of activated units so far, e.g. ('cooling', 'feed')
Goal:   all five units activated
Cost:   number of activation steps taken (uniform)
h(n):   number of units still to be activated (admissible — never overestimates)
"""

import heapq


UNITS = ("cooling", "feed", "reactor", "separator", "recycle")


class StartupPlanner:
    """
    Plans the optimal startup sequence for a multi-unit plant using A*.

    The heuristic h(n) = number of remaining inactive units is admissible
    because each remaining unit requires at least one more activation step.
    """

    def __init__(self, units=None):
        self.units = units if units is not None else list(UNITS)
        self.goal_len = len(self.units)

    # ------------------------------------------------------------------ #
    #  Search Components
    # ------------------------------------------------------------------ #

    def neighbors(self, state):
        """Generate successor states by activating one additional unit."""
        successors = []
        for unit in self.units:
            if unit not in state:
                successors.append(state + (unit,))
        return successors

    def cost(self, state):
        """g(n): number of activation steps taken so far."""
        return len(state)

    def heuristic(self, state):
        """h(n): admissible estimate — units remaining to activate."""
        return self.goal_len - len(state)

    # ------------------------------------------------------------------ #
    #  A* Search
    # ------------------------------------------------------------------ #

    def search(self):
        """
        Run A* to find the optimal startup sequence.

        Returns:
            Tuple of unit names in activation order, or None if no solution.
        """
        start = tuple()

        # Priority queue entries: (f_value, tie_breaker, state)
        counter = 0
        pq = []
        heapq.heappush(pq, (0, counter, start))
        visited = set()
        nodes_expanded = 0

        while pq:
            _, _, state = heapq.heappop(pq)

            if state in visited:
                continue
            visited.add(state)
            nodes_expanded += 1

            # Goal check
            if len(state) == self.goal_len:
                print(f"[A*] Solution found after expanding {nodes_expanded} nodes.")
                return state

            for neighbor in self.neighbors(state):
                if neighbor not in visited:
                    g = self.cost(neighbor)
                    h = self.heuristic(neighbor)
                    f = g + h
                    counter += 1
                    heapq.heappush(pq, (f, counter, neighbor))

        print("[A*] No solution found.")
        return None
