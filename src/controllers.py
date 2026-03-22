import math
import random
from copy import deepcopy

class MinimaxController:
    def __init__(self, plant, depth=3):
        self.plant = plant
        self.depth = depth
        self.actions = ["inc_flow", "dec_flow", "inc_recycle", "dec_recycle", "inc_cooling", "dec_cooling"]

    def disturbance(self, state):
        CA, T, F, Q, R, purity = state
        CA *= 1.05
        T += 10
        return (CA, T, F, Q, R, purity)

    def minimax(self, state, depth, alpha, beta, maximizing):
        if depth == 0:
            return self.plant.evaluate(state)
            
        if maximizing:
            max_eval = -float("inf")
            for action in self.actions:
                new_state = self.plant.plant_step(state, action)
                eval_score = self.minimax(new_state, depth-1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            disturbed = self.disturbance(state)
            return self.minimax(disturbed, depth-1, alpha, beta, True)

    def best_action(self, state):
        best_val = -float("inf")
        best_action = None
        for action in self.actions:
            new_state = self.plant.plant_step(state, action)
            val = self.minimax(new_state, self.depth, -float("inf"), float("inf"), False)
            if val > best_val:
                best_val = val
                best_action = action
        return best_action

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0

class MCTSController:
    def __init__(self, plant, simulations=200):
        self.plant = plant
        self.simulations = simulations
        self.actions = ["inc_flow", "dec_flow", "inc_recycle", "dec_recycle", "inc_cooling", "dec_cooling"]

    def uct(self, node):
        if node.visits == 0:
            return float("inf")
        return (node.value / node.visits) + math.sqrt(2 * math.log(node.parent.visits) / node.visits)

    def run(self, root_state):
        root = MCTSNode(root_state)
        
        for _ in range(self.simulations):
            node = root
            state = deepcopy(root_state)
            
            # Selection
            while node.children:
                node = max(node.children, key=self.uct)
                
            # Expansion
            action = random.choice(self.actions)
            new_state = self.plant.plant_step(node.state, action)
            child = MCTSNode(new_state, node)
            node.children.append(child)
            
            # Simulation
            rollout = deepcopy(new_state)
            for _ in range(10):
                a = random.choice(self.actions)
                rollout = self.plant.plant_step(rollout, a)
            reward = self.plant.evaluate(rollout)
            
            # Backpropagation
            curr = child
            while curr:
                curr.visits += 1
                curr.value += reward
                curr = curr.parent
                
        best_child = max(root.children, key=lambda n: n.visits)
        return best_child.state

class PIDController:
    def __init__(self, plant, Kp=5.0, Ki=0.1, Kd=1.0):
        self.plant = plant
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0
        self.prev_error = 0

    def control(self, state, target_temp=450):
        CA, T, F, Q, R, purity = state
        error = target_temp - T
        self.integral += error
        derivative = error - self.prev_error
        
        adjustment = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        self.prev_error = error
        
        Q += adjustment
        Q = max(0, min(Q, 5000))
        
        # Simulate small random flow adjustments
        action = "inc_flow" if random.random() > 0.5 else "dec_flow"
        new_state = self.plant.plant_step((CA, T, F, Q, R, purity), action)
        return new_state
