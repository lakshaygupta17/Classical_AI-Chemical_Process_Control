# ==============================================================
# ------------------------ MAIN --------------------------------
# ==============================================================

if __name__ == "__main__":

    plant = MultiUnitPlant()

    initial_state = (0.8, 420, 5, 2000, 0.5, 0.8)

    print("\n===== STARTUP PLANNER (A*) =====")
    planner = StartupPlanner()
    plan = planner.search()
    print("Startup Order:", plan)

    print("\n===== CSP SAFE OPERATING POINT =====")
    csp = CSP()
    solution = csp.backtrack()
    print("One Feasible Solution:", solution)

    print("\n===== MINIMAX ROBUST CONTROL =====")
    minimax = MinimaxController(plant)
    action = minimax.best_action(initial_state)
    print("Best Action (Adversarial):", action)

    print("\n===== MCTS STOCHASTIC OPTIMIZATION =====")
    mcts = MCTSController(plant)
    best_state = mcts.run(initial_state)
    print("Best State (MCTS):", best_state)


class PIDController:
    def __init__(self, plant, Kp=5, Ki=0.1, Kd=1):
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

        adjustment = (self.Kp*error + \
                      self.Ki*self.integral + \
                      self.Kd*derivative)

        self.prev_error = error

        Q += adjustment
        Q = max(0, min(Q, 5000))

        new_state = self.plant.plant_step(
            (CA, T, F, Q, R, purity),
            "inc_flow" if random.random() > 0.5 else "dec_flow"
        )

        return new_state

