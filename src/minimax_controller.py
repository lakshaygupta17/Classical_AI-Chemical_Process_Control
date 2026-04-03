"""
minimax_controller.py
---------------------
Minimax controller with Alpha-Beta pruning for robust process control.

The plant-controller interaction is framed as a two-player zero-sum game:
  - MAX player (controller): selects an action to maximise plant performance
  - MIN player (disturbance): applies worst-case perturbations to minimise it

Alpha-Beta pruning eliminates branches that cannot affect the minimax value,
substantially reducing the search tree without sacrificing optimality.
"""

from plant import MultiUnitPlant


class MinimaxController:
    """
    Adversarial controller using Minimax with Alpha-Beta pruning.

    Models the environment as a rational adversary applying worst-case
    disturbances at each alternate ply of the search tree.

    Args:
        plant:  MultiUnitPlant instance
        depth:  minimax search depth (higher = more robust, slower)
    """

    def __init__(self, plant: MultiUnitPlant, depth: int = 3):
        self.plant   = plant
        self.depth   = depth
        self.actions = plant.ACTIONS

    # ------------------------------------------------------------------ #
    #  Disturbance Model (MIN player)
    # ------------------------------------------------------------------ #

    def apply_disturbance(self, state):
        """
        Worst-case disturbance scenario:
          - Feed concentration spike (+5% CA)
          - Temperature perturbation (+10 K)

        Represents sensor noise, upstream upsets, or utility failures.
        """
        CA, T, F, Q, R, purity = state
        CA = CA * 1.05   # concentration spike
        T  = T  + 10.0   # temperature upset
        return (CA, T, F, Q, R, purity)

    # ------------------------------------------------------------------ #
    #  Minimax with Alpha-Beta Pruning
    # ------------------------------------------------------------------ #

    def minimax(self, state, depth, alpha, beta, maximizing):
        """
        Recursive minimax search with alpha-beta pruning.

        Args:
            state:      current plant state
            depth:      remaining search depth
            alpha:      best value MAX can guarantee so far
            beta:       best value MIN can guarantee so far
            maximizing: True if it is the controller's (MAX) turn

        Returns:
            Heuristic value of the state.
        """
        if depth == 0:
            return self.plant.evaluate(state)

        if maximizing:
            max_eval = float("-inf")
            for action in self.actions:
                child_state = self.plant.plant_step(state, action)
                val = self.minimax(child_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, val)
                alpha    = max(alpha, val)
                if beta <= alpha:
                    break  # β-cutoff
            return max_eval

        else:
            # MIN turn: apply worst-case disturbance
            disturbed = self.apply_disturbance(state)
            return self.minimax(disturbed, depth - 1, alpha, beta, True)

    # ------------------------------------------------------------------ #
    #  Public Interface
    # ------------------------------------------------------------------ #

    def best_action(self, state):
        """
        Select the action that maximises the guaranteed minimax value.

        Args:
            state: current plant state (CA, T, F, Q, R, purity)

        Returns:
            action string (one of plant.ACTIONS)
            best_val float (minimax value of selected action)
        """
        best_val    = float("-inf")
        best_action = None

        for action in self.actions:
            child_state = self.plant.plant_step(state, action)
            val = self.minimax(
                child_state,
                self.depth,
                float("-inf"),
                float("inf"),
                False,  # next ply is MIN (disturbance)
            )
            if val > best_val:
                best_val    = val
                best_action = action

        return best_action, best_val
