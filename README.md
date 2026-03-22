# AI-Driven Autonomous Process Control & Startup Planning

## Project Overview

This project applies **Classical Artificial Intelligence techniques** to solve real-world operational challenges in a **multi-unit chemical process plant**.

It integrates Chemical Engineering principles with AI-based decision-making to:

- Automate optimal plant startup sequencing
- Identify safe and feasible operating regions
- Ensure robust control under disturbances
- Optimize performance metrics (conversion, purity, energy efficiency)

The project demonstrates how **state-space search, constraint reasoning, and adversarial decision-making** can be applied to industrial process systems.

---

## System Description

The plant consists of the following interconnected process units:

### Continuous Stirred Tank Reactor (CSTR)

- Non-isothermal reaction: `A → B`
- Governed by coupled mass and energy balances
- Key state variables: Temperature (`T`), Reactant Concentration (`C_A`)

### Heat Exchanger

- Controls reactor temperature via cooling duty (`Q`)
- Energy cost is directly proportional to cooling load

### Flash Separator

- Separates components based on relative volatility
- Enforces downstream product purity constraints

### Recycle Loop

- Reintroduces unreacted feed material
- Improves overall conversion efficiency while increasing system complexity

---

## System Architecture

```
Feed → Reactor → Heat Exchanger → Separator → Recycle
```

This forms a **closed-loop system** with nonlinear dynamics and tightly coupled decision variables.

---

## AI Techniques Implemented

All methods are grounded in **Classical AI**, with one advanced extension noted below.

### 1. State-Space Search — A* Algorithm

**Objective:** Optimize plant startup sequence

- **State representation:** Activated units and current operating conditions
- **Actions:** Activate units in a valid, dependency-respecting order
- **Heuristic:** Count of remaining inactive units

Finds the optimal startup path while minimizing unsafe operational transitions.

---

### 2. Constraint Satisfaction Problem (CSP)

**Objective:** Identify the safe and feasible operating region

**Decision variables:**

| Variable | Description |
|---|---|
| `T` | Reactor temperature |
| `F` | Feed flow rate |
| `Q` | Cooling duty |
| `R` | Recycle ratio |

**Constraints:**

- `T ≤ 500 K`
- Conversion ≥ 85%
- Product purity ≥ 95%
- Physical bounds on all variables

Solved using **Backtracking with AC-3 arc consistency**, producing a complete feasible operating envelope.

---

### 3. Adversarial Search — Minimax with Alpha-Beta Pruning

**Objective:** Achieve robust control under worst-case disturbances

- **Controller (MAX player):** Maximizes plant performance metrics
- **Disturbance (MIN player):** Destabilizes the system

Disturbance scenarios modelled:

- Feed flow fluctuations
- Temperature spikes
- Cooling system inefficiencies

Alpha-Beta pruning reduces the search space while guaranteeing worst-case robustness.

---

### 4. Monte Carlo Tree Search (MCTS)

**Objective:** Decision-making under stochastic uncertainty

Phases: Selection (UCT) → Expansion → Simulation (random rollouts) → Backpropagation

Handles probabilistic disturbances and optimizes long-term cumulative performance.

> **Note:** MCTS is included as an advanced extension beyond strict Classical AI.

---

### 5. Baseline PID Controller

A standard PID controller is implemented as a performance benchmark, representing the current industry-standard control approach and providing a direct comparison against AI-based methods.

---

## Performance Results

Controllers are evaluated on four metrics: conversion rate, temperature stability, energy consumption, and overall performance score.

| Metric | PID | Minimax (Robust) | MCTS (Stochastic) |
|---|---|---|---|
| Average Conversion | 64.7% | **80.5%** | 65.0% |
| Average Temperature | 374 K | 384 K | 374 K |
| Robustness | Low | **High** | Medium |

---

## Visualization

The project generates 15+ diagnostic plots, including:

- Temperature vs. Time
- Conversion vs. Time
- Purity vs. Time
- Energy Consumption profiles
- Side-by-side Controller Comparison

Each controller is analysed independently to enable clear and reproducible performance comparison.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/lakshaygupta17/classical-ai-chemical-process-control.git
cd classical-ai-chemical-process-control
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Simulation

```bash
python src/main.py
```
