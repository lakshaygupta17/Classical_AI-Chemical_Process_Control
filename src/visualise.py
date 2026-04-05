"""
visualise.py — All plots for the project

Functions
---------
plot_startup_sequence(plan, cost)
    Gantt-style bar chart for A* startup sequence.

plot_csp_feasible_region(solutions)
    Scatter plots of feasible CSP operating points.

plot_controller_comparison(pid_hist, minimax_hist, mcts_hist)
    6-panel grid: temperature, conversion, purity, energy, score, bar chart.

plot_temperature_detail(pid_hist, minimax_hist, mcts_hist)
    Close-up temperature setpoint tracking.

plot_score_distributions(pid_hist, minimax_hist, mcts_hist)
    Boxplot + violin plot of score distributions.

plot_metrics_table(pid_m, minimax_m, mcts_m)
    Rendered matplotlib table of all metrics.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

COLORS = {"PID": "#2196F3", "Minimax": "#E91E63", "MCTS": "#4CAF50"}

UNIT_COLORS = {
    "cooling":   "#29B6F6",
    "feed":      "#66BB6A",
    "reactor":   "#EF5350",
    "separator": "#AB47BC",
    "recycle":   "#FF7043",
}


# ── A* ─────────────────────────────────────────────────────────────────────

def plot_startup_sequence(plan, cost, unit_cost):
    """Gantt-style bar chart for A* startup sequence."""
    fig, ax = plt.subplots(figsize=(12, 3))
    x = 0
    for unit in plan:
        w = unit_cost[unit]
        ax.barh(0, w, left=x, height=0.5,
                color=UNIT_COLORS[unit], edgecolor="k", lw=1.2)
        ax.text(x + w / 2, 0, f"{unit}\n({w}u)",
                ha="center", va="center",
                fontsize=11, fontweight="bold", color="white")
        x += w
    ax.set_xlim(0, x + 0.2)
    ax.set_yticks([])
    ax.set_xlabel("Cumulative Startup Cost (time units)", fontsize=11)
    ax.set_title(
        f"A* Optimal Plant Startup Sequence  |  Total Cost = {cost} time units",
        fontsize=13, fontweight="bold",
    )
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.show()


# ── CSP ────────────────────────────────────────────────────────────────────

def plot_csp_feasible_region(solutions):
    """Scatter plots of feasible CSP operating points."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    Ts = [s["T"] for s in solutions]
    Fs = [s["F"] for s in solutions]
    Qs = [s["Q"] for s in solutions]
    Rs = [s["R"] for s in solutions]

    sc1 = axes[0].scatter(Fs, Ts, c=Qs, cmap="coolwarm", s=90,
                          edgecolors="k", lw=0.5)
    plt.colorbar(sc1, ax=axes[0], label="Cooling Q (J/min)")
    axes[0].axhline(500, color="r", ls="--", lw=1.2, label="T_max = 500K")
    axes[0].set_xlabel("Flow F (L/min)")
    axes[0].set_ylabel("Temperature T (K)")
    axes[0].set_title("CSP Feasible Region: T vs F  (colour = Q)")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    sc2 = axes[1].scatter(Fs, Rs, c=Qs, cmap="viridis", s=90,
                          edgecolors="k", lw=0.5)
    plt.colorbar(sc2, ax=axes[1], label="Cooling Q (J/min)")
    axes[1].set_xlabel("Flow F (L/min)")
    axes[1].set_ylabel("Recycle Ratio R")
    axes[1].set_title("CSP Feasible Region: R vs F  (colour = Q)")
    axes[1].grid(alpha=0.3)

    plt.suptitle(
        "CSP Feasible Operating Points (AC-3 + Backtracking + MRV)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout()
    plt.show()


# ── Controller comparison ──────────────────────────────────────────────────

def plot_controller_comparison(pid_hist, minimax_hist, mcts_hist):
    """6-panel performance comparison grid."""
    metrics_keys = ["T", "Conversion", "Purity", "Energy", "Score"]
    ylabels      = [
        "Temperature (K)", "Conversion", "Purity",
        "Cooling Q (J/min)", "Score",
    ]
    titles = [
        "Reactor Temperature", "Conversion", "Separator Purity",
        "Cooling Energy", "Objective Score",
    ]

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    axes = axes.flatten()

    for i, (mk, yl, ti) in enumerate(zip(metrics_keys, ylabels, titles)):
        ax = axes[i]
        ax.plot(pid_hist[mk],     color=COLORS["PID"],     lw=2, label="PID")
        ax.plot(minimax_hist[mk], color=COLORS["Minimax"], lw=2, label="Minimax")
        ax.plot(mcts_hist[mk],    color=COLORS["MCTS"],    lw=2, label="MCTS")
        if mk == "T":
            ax.axhline(450, color="k", ls="--", lw=1.2, label="Setpoint 450K")
            ax.axhline(500, color="r", ls=":",  lw=1.2, label="T_max 500K")
        ax.set_title(ti, fontsize=12, fontweight="bold")
        ax.set_xlabel("Time Step")
        ax.set_ylabel(yl)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    # 6th panel: final-score bar chart
    ax = axes[5]
    names   = ["PID", "Minimax", "MCTS"]
    fscores = [
        pid_hist["Score"][-1],
        minimax_hist["Score"][-1],
        mcts_hist["Score"][-1],
    ]
    bars = ax.bar(names, fscores,
                  color=[COLORS[n] for n in names], alpha=0.85, edgecolor="k")
    for bar, val in zip(bars, fscores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{val:.2f}", ha="center", va="bottom", fontweight="bold")
    ax.set_title("Final Score Comparison", fontweight="bold")
    ax.set_ylabel("Score")
    ax.grid(axis="y", alpha=0.3)

    plt.suptitle(
        "Classical AI Controllers — Multi-metric Performance Comparison",
        fontsize=14, fontweight="bold", y=1.01,
    )
    plt.tight_layout()
    plt.show()


def plot_temperature_detail(pid_hist, minimax_hist, mcts_hist):
    """Close-up temperature setpoint tracking."""
    steps = range(len(pid_hist["T"]))
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(steps, pid_hist["T"],     color=COLORS["PID"],     lw=2, label="PID")
    ax.plot(steps, minimax_hist["T"], color=COLORS["Minimax"], lw=2, label="Minimax")
    ax.plot(steps, mcts_hist["T"],    color=COLORS["MCTS"],    lw=2, label="MCTS")
    ax.axhline(450, color="k", ls="--", lw=1.5, label="Setpoint 450K")
    ax.axhline(500, color="r", ls=":",  lw=1.5, label="Safety Limit 500K")
    ax.fill_between(steps, 440, 460, alpha=0.08, color="green", label="±10K band")
    ax.set_title("Reactor Temperature — Setpoint Tracking Detail",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Temperature (K)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_score_distributions(pid_hist, minimax_hist, mcts_hist):
    """Boxplot + violin plot of controller score distributions."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    data = [pid_hist["Score"], minimax_hist["Score"], mcts_hist["Score"]]

    bp = axes[0].boxplot(data, labels=["PID", "Minimax", "MCTS"],
                         patch_artist=True, notch=True)
    for patch, c in zip(bp["boxes"], COLORS.values()):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    axes[0].set_title("Score Distribution — Boxplot", fontweight="bold")
    axes[0].set_ylabel("Score")
    axes[0].grid(alpha=0.3)

    vp = axes[1].violinplot(data, positions=[1, 2, 3], showmeans=True)
    for body, c in zip(vp["bodies"], COLORS.values()):
        body.set_facecolor(c)
        body.set_alpha(0.6)
    axes[1].set_xticks([1, 2, 3])
    axes[1].set_xticklabels(["PID", "Minimax", "MCTS"])
    axes[1].set_title("Score Distribution — Violin Plot", fontweight="bold")
    axes[1].set_ylabel("Score")
    axes[1].grid(alpha=0.3)

    plt.suptitle("Controller Score Distributions", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_metrics_table(pid_m, minimax_m, mcts_m):
    """Rendered matplotlib table of all metrics."""
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.axis("off")

    keys = [k for k in pid_m if k != "Controller"]
    cols = ["Metric", "PID", "Minimax", "MCTS"]
    rows = [[k, str(pid_m[k]), str(minimax_m[k]), str(mcts_m[k])] for k in keys]

    tbl = ax.table(cellText=rows, colLabels=cols, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.6)

    for j in range(4):
        tbl[0, j].set_facecolor("#263238")
        tbl[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, len(rows) + 1):
        for j in range(4):
            tbl[i, j].set_facecolor("#ECEFF1" if i % 2 == 0 else "white")

    ax.set_title("Performance Metrics Summary", fontsize=13,
                 fontweight="bold", pad=20)
    plt.tight_layout()
    plt.show()
