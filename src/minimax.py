"""
minimax.py — Minimax Controller with Alpha-Beta Pruning

Adversarial control formulated as a two-player zero-sum game:
  MAX = controller  — maximises objective score
  MIN = environment — applies worst-case disturbance

Disturbance repertoire (5 scenarios):
  feed spike, feed drop, temperature surge, cooling failure, nominal.

Alpha-beta pruning eliminates branches where beta <= alpha, giving
the same result as full Minimax with far fewer node evaluations.
Default search depth = 3 (controller plans 3 steps ahead).
"""


class MinimaxController:
    """
    Adversarial controller: Minimax + Alpha-Beta pruning.
    MAX = controller, MIN = environment (disturbances).
    """

    ACTIONS = [
        "inc_flow", "dec_flow",
        "inc_recycle", "dec_recycle",
        "inc_cooling", "dec_cooling",
        "hold",
    ]

    DISTURBANCES = [
        {"name": "feed_spike",   "dCA": +0.10, "dT":  +5},
        {"name": "feed_drop",    "dCA": -0.10, "dT":  -5},
        {"name": "temp_surge",   "dCA":  0.00, "dT": +15},
        {"name": "cool_failure", "dCA":  0.00, "dT": +20},
        {"name": "nominal",      "dCA":  0.00, "dT":   0},
    ]

    def __init__(self, plant, depth=3):
        self.plant = plant
        self.depth = depth

    def apply_disturbance(self, state, d):
        CA, T, F, Q, R, purity = state
        CA = max(0.0, min(CA + d["dCA"], self.plant.CA0))
        T  = min(T + d["dT"], self.plant.T_max + 50)
        return (CA, T, F, Q, R, purity)

    def minimax(self, state, depth, alpha, beta, maximizing):
        if depth == 0 or not self.plant.safe(state):
            return self.plant.evaluate(state)

        if maximizing:
            best = -float("inf")
            for action in self.ACTIONS:
                val  = self.minimax(
                    self.plant.plant_step(state, action),
                    depth - 1, alpha, beta, False,
                )
                best  = max(best, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break          # β-cutoff
            return best
        else:
            best = +float("inf")
            for d in self.DISTURBANCES:
                val  = self.minimax(
                    self.apply_disturbance(state, d),
                    depth - 1, alpha, beta, True,
                )
                best = min(best, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break          # α-cutoff
            return best

    def best_action(self, state):
        """Return the action with the highest guaranteed minimax value."""
        best_val, best_act = -float("inf"), "hold"
        for action in self.ACTIONS:
            val = self.minimax(
                self.plant.plant_step(state, action),
                self.depth, -float("inf"), float("inf"), False,
            )
            if val > best_val:
                best_val, best_act = val, action
        return best_act


if __name__ == "__main__":
    from plant import MultiUnitPlant
    plant = MultiUnitPlant()
    ctrl  = MinimaxController(plant, depth=3)
    state = (0.8, 420.0, 5.0, 2000.0, 0.5, 0.8)
    print("Best action:", ctrl.best_action(state))
