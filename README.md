# 🧠 AI-Driven Autonomous Process Control & Startup Planning

## 📌 Project Overview
This project applies **Classical Artificial Intelligence techniques** to solve real-world operational challenges in a **multi-unit chemical process plant**.

We integrate **Chemical Engineering principles** with **AI-based decision-making** to:

- Automate optimal plant startup sequencing  
- Identify safe and feasible operating regions  
- Ensure robust control under disturbances  
- Optimize performance metrics (conversion, purity, energy)  

This project demonstrates how **state-space search, constraint reasoning, and adversarial decision-making** can be applied to industrial process systems.

---

## 🧪 System Description (Chemical Process)

The plant consists of the following interconnected units:

### 🔹 Continuous Stirred Tank Reactor (CSTR)
- Non-isothermal reaction: \( A \rightarrow B \)  
- Governed by mass and energy balances  
- Key variables: Temperature (T), Concentration (C_A)

### 🔹 Heat Exchanger
- Controls reactor temperature via cooling duty (Q)  
- Energy cost directly linked to cooling load  

### 🔹 Flash Separator
- Separates components using relative volatility  
- Ensures product purity constraints  

### 🔹 Recycle Loop
- Reintroduces unreacted material  
- Improves conversion efficiency but increases complexity  

---

## ⚙️ System Architecture
Feed → Reactor → Heat Exchanger → Separator → Recycle


This creates a **closed-loop system** with nonlinear dynamics and coupled decision variables.

---

## 🤖 AI Techniques Implemented

To strictly comply with **Classical AI**, we implement the following:

---

### 🔵 1. State-Space Search (A* Algorithm)

**Objective:** Optimize plant startup sequence  

- State: Activated units + operating conditions  
- Actions: Activate units in valid order  
- Heuristic: Remaining inactive units  

✔ Finds optimal startup path  
✔ Minimizes unsafe transitions  

---

### 🟢 2. Constraint Satisfaction Problem (CSP)

**Objective:** Identify safe operating region  

- Variables:
  - Temperature (T)
  - Flow rate (F)
  - Cooling duty (Q)
  - Recycle ratio (R)

- Constraints:
  - \( T \le 500K \)
  - Conversion ≥ 85%
  - Purity ≥ 95%
  - Physical bounds on variables  

✔ Solved using Backtracking + AC-3  
✔ Produces feasible operating envelope  

---

### 🔴 3. Adversarial Search (Minimax + Alpha-Beta)

**Objective:** Robust control under disturbances  

- Controller → maximizes performance  
- Disturbance → destabilizes system  

Disturbances include:
- Feed fluctuations  
- Temperature spikes  
- Cooling inefficiencies  

✔ Guarantees worst-case robustness  
✔ Uses Alpha-Beta pruning for efficiency  

---

### 🟡 4. Monte Carlo Tree Search (MCTS)

**Objective:** Decision-making under uncertainty  

- Selection (UCT)
- Expansion
- Simulation (random rollouts)
- Backpropagation  

✔ Handles stochastic disturbances  
✔ Optimizes long-term performance  

> ⚠ Note: MCTS is included as an advanced extension beyond strict classical AI.

---

### ⚙️ 5. Baseline PID Controller

Used for comparison against AI-based controllers.

✔ Provides industry-standard benchmark  
✔ Highlights advantages of AI methods  

---

## 📊 Performance Analysis

We evaluate controllers on:

- Conversion  
- Temperature stability  
- Energy consumption  
- Overall performance score  

### 📈 Sample Results

| Metric | PID | Minimax (Robust) | MCTS (Stochastic) |
|--------|-----|------------------|-------------------|
| Avg Conversion | 64.7% | **80.5%** | 65.0% |
| Avg Temperature | 374 K | 384 K | 374 K |
| Robustness | Low | **High** | Medium |

---

## 📊 Visualization Dashboard

The project generates **15+ plots**, including:

- Temperature vs Time  
- Conversion vs Time  
- Purity vs Time  
- Energy Consumption  
- Controller Comparison  

✔ Each controller is analyzed independently  
✔ Enables clear performance comparison  

---

## 🚀 How to Run

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
