# Classical AI for Chemical Process Control

> **Course Project** — Applying Classical Artificial Intelligence techniques to autonomous control, startup planning, and constraint-based optimisation of a multi-unit chemical process plant.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Team Members](#team-members)
- [System Description](#system-description)
- [AI Techniques Implemented](#ai-techniques-implemented)
- [Repository Structure](#repository-structure)
- [Installation & Usage](#installation--usage)
- [Results & Performance Analysis](#results--performance-analysis)
- [Concepts & Background](#concepts--background)
- [Dependencies](#dependencies)
- [License](#license)

---

## Project Overview

This project applies **five Classical Artificial Intelligence techniques** to solve real-world operational challenges in a **multi-unit chemical process plant**. Rather than treating the plant as a black box, the system is modelled with real chemical engineering equations (mass balances, energy balances, vapour-liquid equilibrium) and then controlled, planned, and optimised using principled AI decision-making.

**The core research question:**
*Can classical AI planning, search, and constraint-satisfaction methods match or outperform a conventional PID controller for chemical process control?*

The project covers:

- Automated plant **startup sequencing** using A\* search — finds the minimum-cost, dependency-respecting activation order, expanding only **15 nodes** to reach the optimal solution
- Identification of **safe operating regions** using CSP with AC-3 arc consistency and MRV backtracking — enumerates up to **30 feasible operating points**
- **Robust disturbance rejection** using Minimax with Alpha-Beta pruning — guarantees best action under worst-case disturbances at depth 3
- **Stochastic optimisation** under uncertainty using Monte Carlo Tree Search (300 simulations, depth 15) — achieves the **highest composite score** of all controllers
- **Baseline comparison** against an industry-standard PID controller

**Key result:** Both AI controllers (Minimax and MCTS) outperform PID by a factor of **~7.7×** on the composite performance score (12.74 and 12.77 vs. 1.66), while maintaining **zero safety violations** across all 60 simulation steps.

---

## Team Members

**Team Name: The A\*lchemists**

| Name | Roll Number | Department |
|------|-------------|------------|
| Lakshay Gupta | 23CH10037 | Chemical Engineering |
| Ayush Goel | 23CH10092 | Chemical Engineering |
| Muhammad Hamza | 23CH30019 | Chemical Engineering |
| Krishna Rai | 23CH3FP03 | Chemical Engineering |

**GitHub:** https://github.com/lakshaygupta17/Classical_AI-Chemical_Process_Control

---

## System Description

The simulated plant consists of four interconnected process units:

### Continuous Stirred Tank Reactor (CSTR)
A non-isothermal reactor where the first-order exothermic reaction `A → B` occurs. The state is governed by coupled differential equations:

- **Mass balance:** `dCA/dt = (F/V)(CA0 - CA) - k·CA`
- **Energy balance:** `dT/dt = (F/V)(T0 - T) + (-ΔH/ρCp)·k·CA - Q/(ρCp·V)`

Key parameters: reactor volume `V = 100 L`, rate constant `k = 0.15 min⁻¹`, heat of reaction `ΔH = -5000 J/mol`.

### Heat Exchanger
Controls reactor temperature by removing heat via a coolant stream:

- `Q = UA · (T_reactor - T_coolant)` where `UA = 4000 J/(min·K)`, `T_coolant = 300 K`

### Flash Separator
Separates product from unreacted feed using vapour-liquid equilibrium (relative volatility `α = 2.5`):

- `y = αx / (1 + (α - 1)x)`

### Recycle Loop
Returns unreacted material to the reactor inlet, improving overall conversion at the cost of increased system complexity and potential instability.

### System Architecture

```
         ┌──────────────────────────────────────────┐
         │              RECYCLE LOOP                │
         └────────────────────┬─────────────────────┘
                              │
  Feed ──► [CSTR Reactor] ──► [Heat Exchanger] ──► [Flash Separator] ──► Product
              │                      │
           State: CA, T          Cooling: Q
```

### State Space

The full plant state is represented as a 6-tuple: `state = (CA, T, F, Q, R, purity)`

| Variable | Description | Units | Bounds |
|----------|-------------|-------|--------|
| `CA` | Reactant concentration | mol/L | `[0, CA0]` |
| `T` | Reactor temperature | K | `[350, 500]` |
| `F` | Feed flow rate | L/min | `[1, 10]` |
| `Q` | Cooling duty | J/min | `[0, 5000]` |
| `R` | Recycle ratio | — | `[0, 2]` |
| `purity` | Separator product purity | — | `[0, 1]` |

---

## AI Techniques Implemented

### 1. A\* Search — Startup Sequencing

**Problem:** The plant must be started up in a safe, dependency-respecting order. Starting the reactor before cooling is online is a safety violation.

**Formulation:**
- **State:** Ordered tuple of activated units, e.g. `("cooling", "feed", "reactor")`
- **Cost function:** `g(n)` = cumulative activation cost of units started so far
- **Heuristic:** `h(n)` = sum of activation costs of all remaining units (admissible — never overestimates)

**Result:** Optimal sequence `cooling → feed → reactor → separator → recycle`, total cost = **9 time units**, found after expanding only **15 nodes**.

---

### 2. CSP with AC-3 + MRV Backtracking — Operating Point Selection

**Problem:** Find combinations of `(T, F, Q, R)` satisfying all safety and performance constraints simultaneously.

**Variables and Domains:**

| Variable | Domain | Step |
|----------|--------|------|
| `T` | 380 – 500 K | 10 K |
| `F` | 2 – 10 L/min | 1 |
| `Q` | 1000 – 5000 J/min | 250 |
| `R` | 0.0 – 2.0 | 0.25 |

**Constraints:** `T ≤ 500 K` · steady-state conversion ≥ 70% · `Q ≥ 80%` of reaction heat · `F(1+R) ≤ 20 L/min`

**Result:** AC-3 prunes domains before backtracking. Up to **30 feasible operating points** enumerated. Example solution: `T = 430 K, F = 4 L/min, Q = 2250 J/min, R = 0.25`.

---

### 3. Minimax with Alpha-Beta Pruning — Robust Control

**Problem:** Design a control policy robust to worst-case process disturbances, modelling the environment as a rational adversary.

**Game formulation:**
- **MAX player (controller):** Maximises composite performance score across 7 discrete actions
- **MIN player (disturbance):** Applies worst-case perturbations from 5 scenarios: feed spike, feed drop, temperature surge, cooling failure, nominal

**Configuration:** Search depth 3 · Alpha-Beta pruning eliminates branches where `β ≤ α`

**Evaluation function:** `score = 10·conversion + 5·purity - 0.01·|T - 450| - Q/1000`

**Computational cost:** ~0.8 ms/step · full 60-step simulation in **0.05 s** (~50× PID)

---

### 4. Monte Carlo Tree Search — Stochastic Optimisation

**Problem:** Select actions under stochastic uncertainty without an explicit disturbance model.

**MCTS Phases:**
1. **Selection** — traverse tree using UCB1: `Q(n)/N(n) + √2 · √(ln N(parent)/N(n))`
2. **Expansion** — add one new child via a random untried action
3. **Simulation** — 15-step random rollout to estimate cumulative value
4. **Backpropagation** — propagate reward back to root, updating all ancestors

**Configuration:** 300 simulations per step · rollout depth 15 · exploration constant `C = √2`

**Computational cost:** ~22.5 ms/step · full 60-step simulation in **1.35 s** (~1338× PID)

**Reproducibility:** Results verified stable across 5 independent random seeds — final score variance < 0.3%

---

### 5. PID Controller — Baseline

A standard PID controller targeting `T = 450 K` with anti-windup integral clamping and a conversion-based heuristic for flow adjustment.

**Parameters:** `Kp = 6.0`, `Ki = 0.05`, `Kd = 1.5` · Anti-windup clamp: ±5000

**Computational cost:** < 1 ms/step (instantaneous)

---

## Repository Structure

```
Classical_AI-Chemical_Process_Control/
│
├── notebook/
│   └── AIFA_Final.ipynb        # Main Jupyter notebook — all code and results
│
├── src/
│   ├── main.py                 # Entry point — runs full pipeline
│   ├── plant.py                # MultiUnitPlant model (CSTR, HX, separator)
│   ├── startup_planner.py      # A* search for startup sequencing
│   ├── csp_solver.py           # CSP with AC-3 + MRV backtracking
│   ├── minimax_controller.py   # Minimax with Alpha-Beta pruning
│   ├── mcts_controller.py      # MCTS with UCB1
│   ├── pid_controller.py       # PID baseline with anti-windup
│   ├── simulation.py           # Simulation runner + metrics + comparison table
│   └── visualisation.py        # All plots — individual, comparison, dashboard
│
├── results/
│   ├── results1.png            # Multi-metric performance comparison dashboard
│   ├── results2.png            # Reactor temperature setpoint tracking detail
│   ├── results3.png            # Score distribution — boxplot and violin plot
│   └── result_table.png        # Performance metrics summary table
│
├── documentation/
│   └── report.pdf              # Full course project report (LaTeX compiled)
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation & Usage

### Prerequisites

- Python 3.8 or higher
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/lakshaygupta17/Classical_AI-Chemical_Process_Control.git
cd Classical_AI-Chemical_Process_Control
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Notebook

```bash
jupyter notebook notebook/AIFA_Final.ipynb
```

Or run as a standalone script:

```bash
python src/main.py
```

### 4. Expected Output

```
============================================================
  Classical AI for Chemical Process Control
============================================================

[A*] Solution found after expanding 15 nodes.
Startup Order: ('cooling', 'feed', 'reactor', 'separator', 'recycle')  |  Total cost: 9

CSP — Feasible operating point: {'T': 430, 'F': 4, 'Q': 2250, 'R': 0.25}
CSP — 30 feasible operating points enumerated.

Minimax best action (adversarial): inc_cooling   (minimax value: 12.74)

MCTS best state found — Score: 12.77   Safe: True

Controller            Avg/step    Total (60 steps)   Relative Cost
--------------------------------------------------------------------
PID                    <1 ms          0.00 s              1x
Minimax (depth=3)      0.8 ms         0.05 s             ~50x
MCTS (300 sims)       22.5 ms         1.35 s           ~1338x
```

All plots are saved to `results/`.

---

## Results & Performance Analysis

All controllers start from identical initial conditions:
`state₀ = (CA=0.8 mol/L, T=420 K, F=5 L/min, Q=2000 J/min, R=0.5, purity=0.8)`
Simulation duration: **60 time steps**.

### Quantitative Comparison

| Metric | PID | Minimax | MCTS |
|--------|-----|---------|------|
| Avg Temperature (K) | 362.80 | 382.57 | 396.81 |
| Std Temperature (K) | 15.33 | 9.17 | **7.17** ✓ |
| Max Temperature (K) | 415.38 | 415.91 | 416.44 |
| Avg Conversion | 0.4954 | 0.8270 | **0.8589** ✓ |
| Final Conversion | 0.500 | 0.9374 | **0.937** ✓ |
| Avg Purity | 0.7097 | 0.9121 | **0.9299** ✓ |
| Avg Energy Q (J/min) | 4759.6 | **193.3** ✓ | 516.7 |
| Final Score | 1.6582 | 12.7386 | **12.7679** ✓ |
| Avg Score | 1.9994 | 11.2888 | **11.6583** ✓ |
| Safety Violations | 0 | 0 | 0 |
| A* Path Length | — | — | 5 steps, cost 9 |
| A* Nodes Expanded | — | — | 15 nodes |
| Avg Time / Step | < 1 ms | 0.8 ms | 22.5 ms |

### Result Plots

| Figure | Description |
|--------|-------------|
| `results1.png` | Multi-metric dashboard: temperature, conversion, purity, energy, score evolution + final score bar chart |
| `results2.png` | Temperature setpoint tracking with ±10 K band and 500 K safety limit annotated |
| `results3.png` | Score distributions as boxplot and violin plot across all 60 steps per controller |
| `result_table.png` | Full performance metrics summary table |

### Key Findings

**AI controllers outperform PID by ~7.7×** — MCTS achieves a final score of 12.77 and Minimax 12.74, compared to PID's 1.66. PID converges to a low-temperature steady state (avg 362.8 K) while consuming maximum cooling energy (avg Q = 4759.6 J/min), yielding only 49.5% average conversion.

**MCTS achieves the highest scores overall** — avg conversion 85.9%, avg purity 92.99%, final score 12.77 — by discovering action sequences through 300 stochastic rollouts per step.

**Minimax achieves the lowest temperature variance** (Std = 9.17 K) and the lowest energy consumption (avg Q = 193.3 J/min) due to its conservative adversarial planning strategy.

**Zero safety violations across all controllers** — T < 500 K maintained across all 60 steps in all three controllers, validating the correctness of the plant model and control logic.

**Computational cost is feasible for chemical process control** — MCTS at 22.5 ms/step completes the 60-step simulation in 1.35 s. Since a "time step" represents minutes of real plant operation, all three controllers are well within real-time feasibility.

---

## Concepts & Background

### Why Classical AI for Process Control?

Modern chemical plants rely on PID for single-loop control and human operators for high-level decisions. Classical AI provides a principled framework to automate these higher-level decisions:

| Decision Level | Challenge | AI Technique |
|----------------|-----------|--------------|
| Startup sequencing | Dependency ordering, safety | A\* Search |
| Operating point selection | Multi-variable constraints | CSP + AC-3 + MRV |
| Real-time control (adversarial) | Worst-case disturbances | Minimax + Alpha-Beta |
| Real-time control (stochastic) | Unknown disturbance model | MCTS (UCB1) |
| Baseline benchmark | Industry standard | PID |

### Evaluation Metric

```
score = 10·conversion + 5·purity - 0.01·|T - 450| - Q/1000
```

Rewards high conversion and purity; penalises deviation from the 450 K temperature setpoint and high cooling energy use.

### Key References

- Russell, S. & Norvig, P. — *Artificial Intelligence: A Modern Approach*, 4th ed. (Chapters 3, 4, 5, 6)
- Seborg, D. E. et al. — *Process Dynamics and Control*, 4th ed.
- Kocsis, L. & Szepesvári, C. — *Bandit Based Monte-Carlo Planning* (UCB1 / MCTS theory)

---

## Dependencies

```
numpy
matplotlib
```

No external AI or ML libraries are used. All five algorithms are implemented from scratch in pure Python. Full list in `requirements.txt`.

---

## License

This project was developed as a final coursework submission at IIT Kharagpur. All code is original work by the project team. Not licensed for commercial use.

---

*Classical AI · Chemical Process Control · IIT Kharagpur · The A\*lchemists*
