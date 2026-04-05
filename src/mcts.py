"""
mcts.py — Monte Carlo Tree Search (MCTS) Controller

Four phases per iteration:
  1. Selection   — traverse tree using UCB1
  2. Expansion   — add one untried child node
  3. Simulation  — random rollout for 15 steps
  4. Backpropagation — update visits/value up to root

UCB1 formula:
  Q(n)/N(n) + C * sqrt(ln(N(parent)) / N(n))   where C = sqrt(2)

Default: 300 simulations per decision step, rollout depth = 15.
"""

import math
import random


class MCTSNode:
    __slots__ = (
        "state", "parent", "action",
        "children", "visits", "value", "untried_actions",
    )

    ACTIONS = [
        "inc_flow", "dec_flow",
        "inc_recycle", "dec_recycle",
        "inc_cooling", "dec_cooling",
        "hold",
    ]

    def __init__(self, state, parent=None, action=None):
        self.state   = state
        self.parent  = parent
        self.action  = action
        self.children = []
        self.visits   = 0
        self.value    = 0.0
        self.untried_actions = list(self.ACTIONS)


class MCTSController:
    """
    MCTS with UCB1 tree policy and random rollout simulation.
    C = sqrt(2) (UCB1 theoretical optimum).
    """

    C = math.sqrt(2)

    ACTIONS = [
        "inc_flow", "dec_flow",
        "inc_recycle", "dec_recycle",
        "inc_cooling", "dec_cooling",
        "hold",
    ]

    def __init__(self, plant, simulations=300):
        self.plant       = plant
        self.simulations = simulations

    def ucb1(self, node):
        if node.visits == 0:
            return float("inf")
        return (
            node.value / node.visits
            + self.C * math.sqrt(math.log(node.parent.visits) / node.visits)
        )

    def select(self, node):
        while node.untried_actions == [] and node.children:
            node = max(node.children, key=self.ucb1)
        return node

    def expand(self, node):
        action = node.untried_actions.pop(
            random.randrange(len(node.untried_actions))
        )
        child = MCTSNode(
            self.plant.plant_step(node.state, action), node, action
        )
        node.children.append(child)
        return child

    def rollout(self, state, depth=15):
        for _ in range(depth):
            state = self.plant.plant_step(state, random.choice(self.ACTIONS))
        return self.plant.evaluate(state)

    def backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.value  += reward
            node = node.parent

    def best_action(self, root_state):
        """Run MCTS from root_state and return the most visited child's action."""
        root = MCTSNode(root_state)
        root.visits = 1          # prevent log(0) in UCB1

        for _ in range(self.simulations):
            node = self.select(root)
            if node.untried_actions:
                node = self.expand(node)
            self.backpropagate(node, self.rollout(node.state))

        if not root.children:
            return "hold"
        return max(root.children, key=lambda n: n.visits).action


if __name__ == "__main__":
    from plant import MultiUnitPlant
    plant = MultiUnitPlant()
    ctrl  = MCTSController(plant, simulations=300)
    state = (0.8, 420.0, 5.0, 2000.0, 0.5, 0.8)
    print("Best action:", ctrl.best_action(state))
