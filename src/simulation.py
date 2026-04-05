"""
simulation.py — Simulation engine and performance metrics

Runs each controller for a fixed number of steps from a common
initial state and computes comparative performance metrics.

Initial state: (CA=0.8, T=420K, F=5, Q=2000, R=0.5, purity=0.8)
"""

import numpy as np


INITIAL_STATE = (0.8, 420.0, 5.0, 2000.0, 0.5, 0.8)


def simulate_controller(plant, controller, steps=60, mode="pid"):
    """
    Simulate a controller for `steps` time steps.

    Parameters
    ----------
    plant      : MultiUnitPlant
    controller : PIDController | MinimaxController | MCTSController
    steps      : int
    mode       : "pid" | "minimax" | "mcts"

    Returns
    -------
    dict with keys: T, CA, Conversion, Purity, Energy, Score, Safe
    """
    state = INITIAL_STATE
    history = {
        "T": [], "CA": [], "Conversion": [],
        "Purity": [], "Energy": [], "Score": [], "Safe": [],
    }

    for _ in range(steps):
        if   mode == "pid":
            state = controller.control(state)
        elif mode in ("minimax", "mcts"):
            state = plant.plant_step(state, controller.best_action(state))

        CA, T, F, Q, R, purity = state
        history["T"].append(T)
        history["CA"].append(CA)
        history["Conversion"].append(plant.conversion(state))
        history["Purity"].append(purity)
        history["Energy"].append(Q)
        history["Score"].append(plant.evaluate(state))
        history["Safe"].append(plant.safe(state))

    return history


def compute_metrics(history, name=""):
    """Summarise a simulation history into a flat metrics dict."""
    T, conv, pur, eng, sco = (
        history[k] for k in ["T", "Conversion", "Purity", "Energy", "Score"]
    )
    return {
        "Controller":        name,
        "Avg Temp (K)":      round(np.mean(T),    2),
        "Std Temp (K)":      round(np.std(T),      2),
        "Max Temp (K)":      round(max(T),          2),
        "Avg Conversion":    round(np.mean(conv),   4),
        "Final Conversion":  round(conv[-1],         4),
        "Avg Purity":        round(np.mean(pur),    4),
        "Avg Energy (Q)":    round(np.mean(eng),    1),
        "Final Score":       round(sco[-1],          4),
        "Avg Score":         round(np.mean(sco),    4),
        "Safety Violations": sum(1 for s in history["Safe"] if not s),
    }


def print_metrics_table(metrics_list):
    """Pretty-print a comparison table of metrics dicts."""
    names = [m["Controller"] for m in metrics_list]
    keys  = [k for k in metrics_list[0] if k != "Controller"]

    header = f"{'Metric':<28}" + "".join(f"{n:>12}" for n in names)
    print("=" * len(header))
    print(header)
    print("=" * len(header))
    for key in keys:
        row = f"{key:<28}" + "".join(f"{str(m[key]):>12}" for m in metrics_list)
        print(row)
    print("=" * len(header))


if __name__ == "__main__":
    import random
    random.seed(42)
    np.random.seed(42)

    from plant   import MultiUnitPlant
    from pid     import PIDController
    from minimax import MinimaxController
    from mcts    import MCTSController

    plant = MultiUnitPlant()

    pid_ctrl     = PIDController(plant)
    minimax_ctrl = MinimaxController(plant, depth=3)
    mcts_ctrl    = MCTSController(plant, simulations=300)

    print("Running PID...")
    pid_hist     = simulate_controller(plant, pid_ctrl,     steps=60, mode="pid")
    print("Running Minimax (may take ~20s)...")
    minimax_hist = simulate_controller(plant, minimax_ctrl, steps=60, mode="minimax")
    print("Running MCTS   (may take ~20s)...")
    mcts_hist    = simulate_controller(plant, mcts_ctrl,    steps=60, mode="mcts")
    print("All simulations complete.\n")

    metrics = [
        compute_metrics(pid_hist,     "PID"),
        compute_metrics(minimax_hist, "Minimax"),
        compute_metrics(mcts_hist,    "MCTS"),
    ]
    print_metrics_table(metrics)
