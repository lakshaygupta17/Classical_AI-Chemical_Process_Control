"""
visualisation.py
----------------
Plotting utilities for controller performance analysis.

Provides:
  - plot_single()       : single metric for one controller
  - plot_comparison()   : same metric across all three controllers on one axis
  - plot_all_metrics()  : full 15-plot diagnostic suite (5 metrics × 3 controllers)
  - plot_dashboard()    : 3×5 subplot dashboard — all metrics, all controllers
"""

import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# Output directory for saved figures
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

METRIC_LABELS = {
    "T"          : ("Temperature", "Temperature (K)"),
    "Conversion" : ("Conversion",  "Conversion Ratio"),
    "Purity"     : ("Purity",      "Product Purity"),
    "Energy"     : ("Energy Usage","Cooling Duty Q (W)"),
    "Score"      : ("Score",       "Composite Score"),
}

CONTROLLER_COLORS = {
    "PID"     : "#2196F3",   # blue
    "Minimax" : "#F44336",   # red
    "MCTS"    : "#4CAF50",   # green
}


def _ensure_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)


# ------------------------------------------------------------------ #
#  Single-Controller Plot
# ------------------------------------------------------------------ #

def plot_single(history, controller_name, metric, save=True):
    """
    Plot one metric for one controller.

    Args:
        history:         dict from simulate_controller()
        controller_name: label string e.g. "PID"
        metric:          key in history e.g. "T"
        save:            if True, save to results/ directory
    """
    title, ylabel = METRIC_LABELS[metric]
    color = CONTROLLER_COLORS.get(controller_name, "#607D8B")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(history[metric], color=color, linewidth=2)
    ax.set_title(f"{controller_name} — {title}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Time Step")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        _ensure_results_dir()
        fname = os.path.join(RESULTS_DIR, f"{controller_name.lower()}_{metric.lower()}.png")
        plt.savefig(fname, dpi=150)
        print(f"Saved: {fname}")

    plt.show()


# ------------------------------------------------------------------ #
#  Multi-Controller Comparison Plot
# ------------------------------------------------------------------ #

def plot_comparison(histories, metric, save=True):
    """
    Overlay the same metric for PID, Minimax, and MCTS on one axis.

    Args:
        histories: dict mapping controller name -> history dict
        metric:    key in history e.g. "T"
        save:      if True, save to results/
    """
    title, ylabel = METRIC_LABELS[metric]

    fig, ax = plt.subplots(figsize=(9, 4))
    for name, history in histories.items():
        ax.plot(
            history[metric],
            label=name,
            color=CONTROLLER_COLORS.get(name, "#607D8B"),
            linewidth=2,
        )
    ax.set_title(f"Controller Comparison — {title}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Time Step")
    ax.set_ylabel(ylabel)
    ax.legend(frameon=True)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        _ensure_results_dir()
        fname = os.path.join(RESULTS_DIR, f"comparison_{metric.lower()}.png")
        plt.savefig(fname, dpi=150)
        print(f"Saved: {fname}")

    plt.show()


# ------------------------------------------------------------------ #
#  Full 15-Plot Diagnostic Suite
# ------------------------------------------------------------------ #

def plot_all_metrics(pid_hist, minimax_hist, mcts_hist, save=True):
    """
    Generate all 15 individual plots (5 metrics × 3 controllers).
    """
    histories = {
        "PID"     : pid_hist,
        "Minimax" : minimax_hist,
        "MCTS"    : mcts_hist,
    }
    for name, history in histories.items():
        for metric in METRIC_LABELS:
            plot_single(history, name, metric, save=save)


# ------------------------------------------------------------------ #
#  Dashboard — All Metrics × All Controllers
# ------------------------------------------------------------------ #

def plot_dashboard(pid_hist, minimax_hist, mcts_hist, save=True):
    """
    Single 3×5 subplot dashboard: rows = controllers, cols = metrics.

    Provides a compact at-a-glance comparison for the report.
    """
    controllers = [("PID", pid_hist), ("Minimax", minimax_hist), ("MCTS", mcts_hist)]
    metrics     = list(METRIC_LABELS.keys())

    fig = plt.figure(figsize=(20, 10))
    fig.suptitle("Controller Performance Dashboard", fontsize=16, fontweight="bold", y=1.01)
    gs  = gridspec.GridSpec(3, 5, figure=fig, hspace=0.45, wspace=0.35)

    for row, (ctrl_name, history) in enumerate(controllers):
        color = CONTROLLER_COLORS[ctrl_name]
        for col, metric in enumerate(metrics):
            ax = fig.add_subplot(gs[row, col])
            ax.plot(history[metric], color=color, linewidth=1.5)
            _, ylabel = METRIC_LABELS[metric]
            if col == 0:
                ax.set_ylabel(ctrl_name, fontsize=11, fontweight="bold")
            if row == 0:
                ax.set_title(ylabel.replace(" (", "\n("), fontsize=9)
            ax.tick_params(labelsize=7)
            ax.grid(True, alpha=0.25)

    plt.tight_layout()

    if save:
        _ensure_results_dir()
        fname = os.path.join(RESULTS_DIR, "dashboard.png")
        plt.savefig(fname, dpi=150, bbox_inches="tight")
        print(f"Saved: {fname}")

    plt.show()
