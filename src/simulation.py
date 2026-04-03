"""
simulation.py
-------------
Simulation runner and performance metrics for controller comparison.

Provides:
  - simulate_controller() : run any controller for N steps and collect history
  - compute_metrics()     : summarise a simulation history into KPIs
  - compare_controllers() : run all controllers and print a comparison table
"""

import numpy as np
from plant import MultiUnitPlant


# ------------------------------------------------------------------ #
#  Initial Conditions
# ------------------------------------------------------------------ #

DEFAULT_INITIAL_STATE = (0.8, 420, 5, 2000, 0.5, 0.8)
#                         CA   T   F    Q    R  purity


# ------------------------------------------------------------------ #
#  Simulation Runner
# ------------------------------------------------------------------ #

def simulate_controller(plant, controller, steps=50, mode="pid",
                         initial_state=None, verbose=False):
    """
    Simulate a controller for a fixed number of time steps.

    Args:
        plant:         MultiUnitPlant instance
        controller:    PIDController | MinimaxController | MCTSController
        steps:         number of simulation steps
        mode:          "pid" | "minimax" | "mcts"
        initial_state: starting state tuple (defaults to DEFAULT_INITIAL_STATE)
        verbose:       if True, print state at each step

    Returns:
        history dict with keys:
          T, Conversion, Purity, Energy, Score, Safe
    """
    state = initial_state if initial_state is not None else DEFAULT_INITIAL_STATE

    history = {
        "T"          : [],
        "Conversion" : [],
        "Purity"     : [],
        "Energy"     : [],
        "Score"      : [],
        "Safe"       : [],
    }

    for step in range(steps):

        # Select action and advance state
        if mode == "pid":
            state = controller.control(state)

        elif mode == "minimax":
            action, _ = controller.best_action(state)
            state = plant.plant_step(state, action)

        elif mode == "mcts":
            state = controller.run(state)

        else:
            raise ValueError(f"Unknown mode: {mode!r}. Use 'pid', 'minimax', or 'mcts'.")

        CA, T, F, Q, R, purity = state
        conversion = 1 - CA / plant.CA0

        history["T"].append(T)
        history["Conversion"].append(conversion)
        history["Purity"].append(purity)
        history["Energy"].append(Q)
        history["Score"].append(plant.evaluate(state))
        history["Safe"].append(plant.safe(state))

        if verbose:
            print(f"Step {step+1:3d} | T={T:.1f}K  Conv={conversion:.3f}"
                  f"  Purity={purity:.3f}  Q={Q:.0f}  Safe={plant.safe(state)}")

    return history


# ------------------------------------------------------------------ #
#  Metrics Computation
# ------------------------------------------------------------------ #

def compute_metrics(history):
    """
    Compute summary KPIs from a simulation history.

    Args:
        history: dict returned by simulate_controller()

    Returns:
        metrics dict
    """
    T    = np.array(history["T"])
    conv = np.array(history["Conversion"])
    pur  = np.array(history["Purity"])
    eng  = np.array(history["Energy"])
    sc   = np.array(history["Score"])

    return {
        "Avg Temperature (K)"   : round(float(np.mean(T)),   2),
        "Std Temperature (K)"   : round(float(np.std(T)),    2),
        "Max Temperature (K)"   : round(float(np.max(T)),    2),
        "Avg Conversion"        : round(float(np.mean(conv)), 4),
        "Min Conversion"        : round(float(np.min(conv)),  4),
        "Avg Purity"            : round(float(np.mean(pur)),  4),
        "Avg Energy (W)"        : round(float(np.mean(eng)),  1),
        "Final Score"           : round(float(sc[-1]),        4),
        "Safety Violations"     : int(np.sum(~np.array(history["Safe"]))),
    }


# ------------------------------------------------------------------ #
#  Comparison Table Printer
# ------------------------------------------------------------------ #

def compare_controllers(pid_metrics, minimax_metrics, mcts_metrics):
    """
    Print a formatted side-by-side comparison of controller metrics.
    """
    keys = list(pid_metrics.keys())
    col_w = 22

    header = f"{'Metric':<28} {'PID':>{col_w}} {'Minimax':>{col_w}} {'MCTS':>{col_w}}"
    sep    = "-" * len(header)

    print("\n" + sep)
    print(header)
    print(sep)

    for k in keys:
        pid_v     = pid_metrics[k]
        minimax_v = minimax_metrics[k]
        mcts_v    = mcts_metrics[k]
        print(f"{k:<28} {str(pid_v):>{col_w}} {str(minimax_v):>{col_w}} {str(mcts_v):>{col_w}}")

    print(sep + "\n")
