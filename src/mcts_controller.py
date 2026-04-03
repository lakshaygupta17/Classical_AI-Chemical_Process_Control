"""
mcts_controller.py
------------------
Monte Carlo Tree Search (MCTS) controller for stochastic process optimisation.

MCTS builds a partial search tree by iterating four phases:
  1. Selection    -- traverse tree using UCT to balance explore vs. exploit
  2. Expansion    -- add a new child node via a random action
  3. Simulation   -- random rollout from expanded node to estimate value
  4. Backprop     -- propagate rollout reward back up through ancestors

No explicit disturbance model is required; stochasticity is handled
naturally through random rollouts.
"""

import math
import random
from copy import deepcopy

from plant import MultiUnitPlant


class MCTSNode:
    """A node in the MCTS search tree."""

    __slots__ = ("state", "parent", "children", "visits", "value")

    def __init__(self, state, parent=None):
        self.state    = state
        self.parent   = parent
        self.children = []
        self.visits   = 0
        self.value    = 0.0


class MCTSController:
    """
    Monte Carlo Tree Search controller.

    Args:
        plant:        MultiUnitPlant instance
        simulations:  number of MCTS iterations per decision
        rollout_depth: length of random simulation rollout
        exploration_c: UCT exploration constant (√2 by default)
    """

    def __init__(
        self,
        plant: MultiUnitPlant,
        simulations:   int   = 200,
        rollout_depth: int   = 10,
        exploration_c: float = math.sqrt(2),
    ):
        self.plant         = plant
        self.simulations   = simulations
        self.rollout_depth = rollout_depth
        self.C             = exploration_c
        self.actions       = plant.ACTIONS

    # ------------------------------------------------------------------ #
    #  UCT Selection Criterion
    # ------------------------------------------------------------------ #

    def uct(self, node: MCTSNode) -> float:
        """
        Upper Confidence Bound for Trees (UCT).

        Unvisited nodes return +∞ to guarantee they are expanded first.
        """
        if node.visits == 0:
            return float("inf")
        exploitation = node.value / node.visits
        exploration  = self.C * math.sqrt(
            math.log(node.parent.visits) / node.visits
        )
        return exploitation + exploration

    # ------------------------------------------------------------------ #
    #  MCTS Phases
    # ------------------------------------------------------------------ #

    def _select(self, root: MCTSNode):
        """Descend tree greedily by UCT until a leaf or unexpanded node."""
        node  = root
        state = deepcopy(root.state)
        while node.children:
            node  = max(node.children, key=self.uct)
            state = node.state
        return node, state

    def _expand(self, node: MCTSNode, state):
        """Add one new child via a random action."""
        action    = random.choice(self.actions)
        new_state = self.plant.plant_step(state, action)
        child     = MCTSNode(new_state, parent=node)
        node.children.append(child)
        return child, new_state

    def _simulate(self, state) -> float:
        """Random rollout from `state` for `rollout_depth` steps."""
        rollout = deepcopy(state)
        for _ in range(self.rollout_depth):
            action  = random.choice(self.actions)
            rollout = self.plant.plant_step(rollout, action)
        return self.plant.evaluate(rollout)

    def _backpropagate(self, node: MCTSNode, reward: float):
        """Propagate reward from `node` up to (and including) root."""
        current = node
        while current is not None:
            current.visits += 1
            current.value  += reward
            current = current.parent

    # ------------------------------------------------------------------ #
    #  Public Interface
    # ------------------------------------------------------------------ #

    def run(self, root_state):
        """
        Run MCTS from `root_state` and return the most-visited child state.

        Args:
            root_state: current plant state (CA, T, F, Q, R, purity)

        Returns:
            best_state: state of the most-visited child node
        """
        root = MCTSNode(root_state)

        for _ in range(self.simulations):
            # 1. Selection
            node, state = self._select(root)

            # 2. Expansion
            child, new_state = self._expand(node, state)

            # 3. Simulation
            reward = self._simulate(new_state)

            # 4. Backpropagation
            self._backpropagate(child, reward)

        if not root.children:
            return root_state  # no children expanded (edge case)

        best_child = max(root.children, key=lambda n: n.visits)
        return best_child.state
