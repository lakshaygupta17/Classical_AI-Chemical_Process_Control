"""
main.py
-------
Entry point for the Classical AI — Chemical Process Control project.

Runs all four AI techniques and the PID baseline in sequence,
then produces a full performance comparison.

Usage:
    python src/main.py
"""

from plant               import MultiUnitPlant
from startup_planner     import StartupPlanner
from csp_solver          import OperatingPointCSP
from minimax_controller  import MinimaxController
from mcts_controller     import MCTSController
from pid_controller      import PIDController
from simulation          import (
    simulate_controller,
    compute_metrics,
    compare_controllers,
    DEFAULT_INITIAL_STATE,
)
from visualisation import (
    plot_comparison,
    plot_dashboard,
    plot_all_metrics,
)


def main():

    print("=" * 60)
    print("  Classical AI for Chemical Process Control")
    print("=" * 60)

    # ---------------------------------------------------------------- #
    # 1. Plant Initialisation
    # ---------------------------------------------------------------- #
    plant         = MultiUnitPlant()
    initial_state = DEFAULT_INITIAL_STATE
    print(f"\nInitial state: {initial_state}")
    print(f"Initial score: {plant.evaluate(initial_state):.4f}")
    print(f"Initial safe:  {plant.safe(initial_state)}")

    # ---------------------------------------------------------------- #
    # 2. A* Startup Planner
    # ---------------------------------------------------------------- #
    print("\n" + "=" * 60)
    print("  [1/4] A* STARTUP SEQUENCING")
    print("=" * 60)
    planner      = StartupPlanner()
    startup_seq  = planner.search()
    print(f"Optimal startup order: {startup_seq}")

    # ---------------------------------------------------------------- #
    # 3. CSP Operating Point Selection
    # ---------------------------------------------------------------- #
    print("\n" + "=" * 60)
    print("  [2/4] CSP — SAFE OPERATING POINT")
    print("=" * 60)
    csp      = OperatingPointCSP()
    solution = csp.backtrack()
    print(f"One feasible operating point: {solution}")

    all_solutions = csp.find_all_solutions(limit=5)
    print(f"First 5 feasible solutions:")
    for i, s in enumerate(all_solutions, 1):
        print(f"  {i}. {s}")

    # ---------------------------------------------------------------- #
    # 4. Minimax — Best Action from Initial State
    # ---------------------------------------------------------------- #
    print("\n" + "=" * 60)
    print("  [3/4] MINIMAX — ROBUST CONTROL ACTION")
    print("=" * 60)
    minimax          = MinimaxController(plant, depth=3)
    action, mm_value = minimax.best_action(initial_state)
    print(f"Best action (adversarial): {action}  (minimax value: {mm_value:.4f})")

    # ---------------------------------------------------------------- #
    # 5. MCTS — Best Next State
    # ---------------------------------------------------------------- #
    print("\n" + "=" * 60)
    print("  [4/4] MCTS — STOCHASTIC OPTIMISATION")
    print("=" * 60)
    mcts       = MCTSController(plant, simulations=200)
    best_state = mcts.run(initial_state)
    print(f"Best state found by MCTS: {best_state}")
    print(f"Score: {plant.evaluate(best_state):.4f}  Safe: {plant.safe(best_state)}")

    # ---------------------------------------------------------------- #
    # 6. Controller Comparison — Full Simulation
    # ---------------------------------------------------------------- #
    print("\n" + "=" * 60)
    print("  CONTROLLER COMPARISON (50 steps each)")
    print("=" * 60)

    pid = PIDController(plant)

    print("Simulating PID...")
    pid_hist = simulate_controller(plant, pid, steps=50, mode="pid")

    print("Simulating Minimax...")
    minimax_hist = simulate_controller(plant, minimax, steps=50, mode="minimax")

    print("Simulating MCTS...")
    mcts_hist = simulate_controller(plant, mcts, steps=50, mode="mcts")

    # Metrics
    pid_metrics     = compute_metrics(pid_hist)
    minimax_metrics = compute_metrics(minimax_hist)
    mcts_metrics    = compute_metrics(mcts_hist)

    compare_controllers(pid_metrics, minimax_metrics, mcts_metrics)

    # ---------------------------------------------------------------- #
    # 7. Plots
    # ---------------------------------------------------------------- #
    print("Generating plots...")
    histories = {"PID": pid_hist, "Minimax": minimax_hist, "MCTS": mcts_hist}

    # Comparison overlays (one per metric)
    for metric in ["T", "Conversion", "Purity", "Energy", "Score"]:
        plot_comparison(histories, metric, save=True)

    # Full dashboard
    plot_dashboard(pid_hist, minimax_hist, mcts_hist, save=True)

    # Individual plots (15 total)
    plot_all_metrics(pid_hist, minimax_hist, mcts_hist, save=True)

    print("\nAll plots saved to results/")
    print("Done.")


if __name__ == "__main__":
    main()
