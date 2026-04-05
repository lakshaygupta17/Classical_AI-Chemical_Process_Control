"""
main.py — Classical AI for Chemical Process Control

Entry point. Runs all five algorithms in sequence:
  1. A*       — optimal startup sequencing
  2. CSP+AC-3 — safe operating point selection
  3. Minimax  — adversarial robust control
  4. MCTS     — stochastic optimisation
  5. PID      — classical baseline

Then simulates PID / Minimax / MCTS for 60 steps, prints a
performance table and renders all comparison plots.

Usage
-----
  python main.py
"""

import random
import numpy as np

random.seed(42)
np.random.seed(42)

from plant      import MultiUnitPlant
from astar      import StartupPlanner
from csp        import CSP
from minimax    import MinimaxController
from mcts       import MCTSController
from pid        import PIDController
from simulation import simulate_controller, compute_metrics, print_metrics_table
from visualise  import (
    plot_startup_sequence,
    plot_csp_feasible_region,
    plot_controller_comparison,
    plot_temperature_detail,
    plot_score_distributions,
    plot_metrics_table,
)


def main():
    plant = MultiUnitPlant()
    print("=" * 60)
    print("  Classical AI for Chemical Process Control")
    print("=" * 60)

    # ── 1. A* Startup Sequencing ────────────────────────────────
    print("\n[1/5] A* Optimal Startup Sequencing")
    planner = StartupPlanner()
    plan, cost = planner.search()
    print("  Sequence :", " → ".join(plan))
    print(f"  Total cost: {cost} time units")
    plot_startup_sequence(plan, cost, StartupPlanner.UNIT_COST)

    # ── 2. CSP + AC-3 ───────────────────────────────────────────
    print("\n[2/5] CSP with AC-3 Arc Consistency")
    csp = CSP()
    solution, msg = csp.solve()
    print("  Status  :", msg)
    print("  Solution:", solution)
    csp2 = CSP()
    all_solutions = csp2.get_all_solutions(30)
    print(f"  Feasible solutions found: {len(all_solutions)}")
    plot_csp_feasible_region(all_solutions)

    # ── 3–5. Simulate controllers ────────────────────────────────
    pid_ctrl     = PIDController(plant)
    minimax_ctrl = MinimaxController(plant, depth=3)
    mcts_ctrl    = MCTSController(plant, simulations=300)

    print("\n[3/5] Running PID...")
    pid_hist     = simulate_controller(plant, pid_ctrl,     steps=60, mode="pid")

    print("[4/5] Running Minimax (may take ~20 s)...")
    minimax_hist = simulate_controller(plant, minimax_ctrl, steps=60, mode="minimax")

    print("[5/5] Running MCTS   (may take ~20 s)...")
    mcts_hist    = simulate_controller(plant, mcts_ctrl,    steps=60, mode="mcts")

    print("\nAll simulations complete.")

    # ── Metrics ─────────────────────────────────────────────────
    pid_m     = compute_metrics(pid_hist,     "PID")
    minimax_m = compute_metrics(minimax_hist, "Minimax")
    mcts_m    = compute_metrics(mcts_hist,    "MCTS")
    print()
    print_metrics_table([pid_m, minimax_m, mcts_m])

    # ── Plots ────────────────────────────────────────────────────
    plot_controller_comparison(pid_hist, minimax_hist, mcts_hist)
    plot_temperature_detail(pid_hist, minimax_hist, mcts_hist)
    plot_score_distributions(pid_hist, minimax_hist, mcts_hist)
    plot_metrics_table(pid_m, minimax_m, mcts_m)

    print("\nDone.")


if __name__ == "__main__":
    main()
