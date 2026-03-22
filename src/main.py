import numpy as np
import matplotlib.pyplot as plt

# Import the modules we just created
from plant_model import MultiUnitPlant
from planners import StartupPlanner, CSP
from controllers import PIDController, MinimaxController, MCTSController

def simulate_controller(plant, controller, steps=50, mode="pid"):
    state = (0.8, 420, 5, 2000, 0.5, 0.8)
    history = {
        "T": [], "Conversion": [], "Purity": [], "Energy": [], "Score": []
    }
    
    for _ in range(steps):
        if mode == "pid":
            state = controller.control(state)
        elif mode == "minimax":
            action = controller.best_action(state)
            if action:
                state = plant.plant_step(state, action)
        elif mode == "mcts":
            state = controller.run(state)
            
        CA, T, F, Q, R, purity = state
        conversion = 1 - (CA / plant.CA0)
        
        history["T"].append(T)
        history["Conversion"].append(conversion)
        history["Purity"].append(purity)
        history["Energy"].append(Q)
        history["Score"].append(plant.evaluate(state))
        
    return history

def compute_metrics(history):
    return {
        "Avg Temperature": np.mean(history["T"]),
        "Avg Conversion": np.mean(history["Conversion"]),
        "Avg Purity": np.mean(history["Purity"]),
        "Avg Energy": np.mean(history["Energy"]),
        "Final Score": history["Score"][-1],
        "Max Temperature": max(history["T"]),
        "Min Conversion": min(history["Conversion"]),
        "Std Temperature": np.std(history["T"])
    }

def plot_metric(data, title, ylabel):
    plt.figure()
    plt.plot(data)
    plt.title(title)
    plt.xlabel("Time Step")
    plt.ylabel(ylabel)
    plt.show()

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
    
    print("\n===== RUNNING CONTROLLER COMPARISON =====")
    pid = PIDController(plant)
    
    pid_hist = simulate_controller(plant, pid, mode="pid")
    minimax_hist = simulate_controller(plant, minimax, mode="minimax")
    mcts_hist = simulate_controller(plant, mcts, mode="mcts")
    
    pid_metrics = compute_metrics(pid_hist)
    minimax_metrics = compute_metrics(minimax_hist)
    mcts_metrics = compute_metrics(mcts_hist)
    
    print("\nPID Metrics:", pid_metrics)
    print("\nMinimax Metrics:", minimax_metrics)
    print("\nMCTS Metrics:", mcts_metrics)
    
    # Plotting an example (PID Temperature)
    plot_metric(pid_hist["T"], "PID Temperature", "Temperature (K)")
