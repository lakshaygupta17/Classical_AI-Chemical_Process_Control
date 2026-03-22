
import heapq
import numpy as np

class StartupPlanner:
    def __init__(self):
        self.units = ["cooling", "feed", "reactor", "separator", "recycle"]

    def neighbors(self, state):
        states = []
        for unit in self.units:
            if unit not in state:
                new_state = state + (unit,)
                states.append(new_state)
        return states

    def cost(self, state):
        return len(state)

    def heuristic(self, state):
        return 5 - len(state)

    def search(self):
        start = tuple()
        goal_len = 5
        pq = []
        heapq.heappush(pq, (0, start))
        visited = set()

        while pq:
            f, state = heapq.heappop(pq)
            if len(state) == goal_len:
                return state
            
            visited.add(state)
            
            for neighbor in self.neighbors(state):
                if neighbor not in visited:
                    f_new = self.cost(neighbor) + self.heuristic(neighbor)
                    heapq.heappush(pq, (f_new, neighbor))
        return None

class CSP:
    def __init__(self):
        self.variables = ["T", "F", "Q", "R"]
        self.domains = {
            "T": list(range(350, 501, 25)),
            "F": list(range(1, 11)),
            "Q": list(range(0, 5001, 500)),
            "R": [round(x, 1) for x in np.arange(0, 2.1, 0.5)]
        }
        self.constraints = [
            lambda T, F, Q, R: T <= 500,
            lambda T, F, Q, R: F > 0,
            lambda T, F, Q, R: Q >= 0,
            lambda T, F, Q, R: R >= 0
        ]

    def consistent(self, assignment):
        if len(assignment) < 4:
            return True
        T, F, Q, R = assignment["T"], assignment["F"], assignment["Q"], assignment["R"]
        return all(c(T, F, Q, R) for c in self.constraints)

    def backtrack(self, assignment=None):
        if assignment is None:
            assignment = {}
            
        if len(assignment) == len(self.variables):
            return assignment
            
        var = [v for v in self.variables if v not in assignment][0]
        for value in self.domains[var]:
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
            del assignment[var]
        return None
