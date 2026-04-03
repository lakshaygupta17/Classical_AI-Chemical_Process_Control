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

- Automated plant **startup sequencing** using A* search
- Identification of **safe operating regions** using CSP with backtracking
- **Robust disturbance rejection** using Minimax with Alpha-Beta pruning
- **Stochastic optimisation** under uncertainty using Monte Carlo Tree Search
- **Baseline comparison** against an industry-standard PID controller

---

## Team Members

| Name | Roll Number | Department |
|------|-------------|------------|
| Student Name 1 | Roll No. 1 | Department |
| Student Name 2 | Roll No. 2 | Department |
| Student Name 3 | Roll No. 3 | Department |
| Student Name 4 | Roll No. 4 | Department |

> *(Update with actual names and roll numbers before submission)*

---

## System Description

The simulated plant consists of four interconnected process units:

### Continuous Stirred Tank Reactor (CSTR)
A non-isothermal reactor where the first-order exothermic reaction `A → B` occurs. The state is governed by coupled differential equations:

- **Mass balance:** `dCA/dt = (F/V)(CA0 - CA) - k·CA`
- **Energy balance:** `dT/dt = (F/V)(T0 - T) + (-ΔH/ρCp)·k·CA - Q/(ρCp·V)`

Key parameters: reactor volume `V = 100 L`, rate constant `k = 0.15 s⁻¹`, heat of reaction `ΔH = -5000 J/mol`.

### Heat Exchanger
Controls reactor temperature by removing heat via a coolant stream. The cooling duty is computed as:

- `Q = UA · (T_reactor - T_coolant)`  where `UA = 4000 W/K`, `T_coolant = 300 K`

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

The full plant state is represented as a 6-tuple:

```python
state = (CA, T, F, Q, R, purity)
```

| Variable | Description | Units | Bounds |
|----------|-------------|-------|--------|
| `CA` | Reactant concentration | mol/L | `[0, CA0]` |
| `T` | Reactor temperature | K | `[350, 500]` |
| `F` | Feed flow rate | L/s | `[1, 10]` |
| `Q` | Cooling duty | W | `[0, 5000]` |
| `R` | Recycle ratio | — | `[0, 2]` |
| `purity` | Separator product purity | — | `[0, 1]` |

---

## AI Techniques Implemented

### 1. A* Search — Startup Sequencing (`StartupPlanner`)

**Problem:** The plant must be started up in a safe, dependency-respecting order. Starting the reactor before cooling is online, for example, is a safety violation.

**Formulation:**
- **State:** Ordered tuple of activated units, e.g. `("cooling", "feed", "reactor")`
- **Actions:** Activate any not-yet-activated unit
- **Cost function:** `g(n) = len(state)` — number of steps taken
- **Heuristic:** `h(n) = 5 - len(state)` — number of units remaining to activate

**Output:** `('cooling', 'feed', 'reactor', 'separator', 'recycle')` — the optimal startup order.

---

### 2. CSP with Backtracking — Operating Point Selection (`CSP`)

**Problem:** Find a combination of operating variables that satisfies all plant safety and performance constraints simultaneously.

**Variables and Domains:**

| Variable | Domain |
|----------|--------|
| `T` | `{350, 375, 400, ..., 500}` K |
| `F` | `{1, 2, 3, ..., 10}` L/s |
| `Q` | `{0, 500, 1000, ..., 5000}` W |
| `R` | `{0.0, 0.5, 1.0, 1.5, 2.0}` |

**Constraints:**
- `T ≤ 500 K` (safety hard limit)
- `F > 0` (physical feasibility)
- `Q ≥ 0` (no negative cooling)
- `R ≥ 0` (no negative recycle)

**Algorithm:** Backtracking search with constraint checking at each assignment step.

---

### 3. Minimax with Alpha-Beta Pruning — Robust Control (`MinimaxController`)

**Problem:** Design a control policy that is robust to the *worst-case* process disturbances, modelling the environment as an adversary.

**Game formulation:**
- **MAX player (controller):** Selects an action from `{inc_flow, dec_flow, inc_recycle, dec_recycle, inc_cooling, dec_cooling}` to maximise the plant performance score.
- **MIN player (disturbance):** Applies worst-case perturbations — `CA *= 1.05`, `T += 10 K` — to minimise performance.

**Search depth:** 3 (configurable)

**Alpha-Beta pruning** eliminates branches that cannot affect the final decision, significantly reducing the number of states evaluated.

**Evaluation function:**
```python
score = 10·conversion + 5·purity - 0.01·|T - 450| - energy_cost
```

---

### 4. Monte Carlo Tree Search — Stochastic Optimisation (`MCTSController`)

**Problem:** Select actions under stochastic uncertainty where the disturbance model is not known in advance.

**MCTS Phases:**
1. **Selection:** Traverse the tree using the UCT formula to balance exploration vs. exploitation:  
   `UCT = value/visits + √(2·ln(parent_visits)/visits)`
2. **Expansion:** Add a new child node by sampling a random action.
3. **Simulation:** Run a 10-step random rollout from the expanded node.
4. **Backpropagation:** Propagate the rollout reward back up the tree.

**Simulations per decision:** 200 (configurable)

---

### 5. PID Controller — Baseline (`PIDController`)

A standard Proportional-Integral-Derivative controller targeting `T = 450 K`. Serves as the industry-standard baseline for comparison.

```python
adjustment = Kp·e(t) + Ki·∫e(t)dt + Kd·de(t)/dt
```

Parameters: `Kp = 5`, `Ki = 0.1`, `Kd = 1`

---

## Repository Structure

```
Classical_AI-Chemical_Process_Control/
│
├── notebook/
│   └── AIFA.ipynb              # Main Jupyter notebook (all code)
│
├── src/
│   └── main.py                 # Standalone Python script
│
├── results/
│   └── *.png                   # Generated plots and output figures
│
├── documentation/
│   └── report.pdf              # Full project report
│
├── requirements.txt            # Python dependencies
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
jupyter notebook notebook/AIFA.ipynb
```

Or run as a standalone script:

```bash
python src/main.py
```

### 4. Expected Output

Running the notebook executes all four AI methods sequentially and prints:

```
===== STARTUP PLANNER (A*) =====
Startup Order: ('cooling', 'feed', 'reactor', 'separator', 'recycle')

===== CSP SAFE OPERATING POINT =====
One Feasible Solution: {'T': 350, 'F': 1, 'Q': 0, 'R': 0.0}

===== MINIMAX ROBUST CONTROL =====
Best Action (Adversarial): inc_cooling

===== MCTS STOCHASTIC OPTIMIZATION =====
Best State (MCTS): (...)

===== RUNNING CONTROLLER COMPARISON =====
PID Metrics: {...}
Minimax Metrics: {...}
MCTS Metrics: {...}
```

Followed by **15 diagnostic plots** across all three controllers.

---

## Results & Performance Analysis

Controllers are compared over 50 simulation steps starting from `state = (CA=0.8, T=420K, F=5, Q=2000, R=0.5, purity=0.8)`.

### Quantitative Comparison

| Metric | PID | Minimax | MCTS |
|--------|-----|---------|------|
| Avg Temperature (K) | — | — | — |
| Avg Conversion | — | — | — |
| Avg Purity | — | — | — |
| Avg Energy (W) | — | — | — |
| Final Score | — | — | — |
| Max Temperature (K) | — | — | — |
| Std Temperature | — | — | — |

> *(Populate with actual values after running the simulation)*

### Evaluation Metric

All controllers are evaluated on a composite performance score:

```
score = 10·conversion + 5·purity - 0.01·|T - 450| - Q/1000
```

This rewards high conversion and purity, penalises temperature deviation from the setpoint, and penalises high energy usage.

### Plots Generated

For each of PID, Minimax, and MCTS:
- Temperature vs. Time Step
- Conversion vs. Time Step
- Purity vs. Time Step
- Energy Usage vs. Time Step
- Composite Score vs. Time Step

All plots are saved to the `results/` directory.

---

## Concepts & Background

### Why Classical AI for Process Control?

Modern chemical plants use PID controllers for single-loop control and rely on operators for high-level decisions (startup, fault recovery, constraint management). Classical AI provides a principled framework to automate these higher-level decisions:

| Decision Level | Challenge | AI Technique Used |
|----------------|-----------|-------------------|
| Startup sequencing | Dependency ordering, safety | A* Search |
| Operating point selection | Multi-variable constraints | CSP Backtracking |
| Real-time control (adversarial) | Worst-case disturbances | Minimax + Alpha-Beta |
| Real-time control (stochastic) | Unknown disturbance model | MCTS |

### Key References

- Russell, S. & Norvig, P. — *Artificial Intelligence: A Modern Approach* (Chapters 3, 4, 5, 6)
- Seborg, D. E. et al. — *Process Dynamics and Control* (CSTR modelling)
- Coulomb, J. & Chen, W. — *Flash Separator Design and VLE*

---

## Dependencies

```
numpy
matplotlib
```

Full list in `requirements.txt`. No external AI/ML libraries are used — all algorithms are implemented from scratch.

---

## License

This project was developed as a final coursework submission. All code is original work by the project team. Not licensed for commercial use.

---

*Classical AI · Chemical Process Control · Course Project*
