# AI-Driven Autonomous Process Control & Startup Planning

## 📌 Project Overview
This project applies **Classical Artificial Intelligence** techniques to solve complex operational challenges in a Chemical Process Plant. [cite_start]We bridge the gap between **Chemical Engineering** and **AI** by automating the startup sequence, finding safe operating points, and implementing robust control against disturbances. [cite: 466, 469]

### 🧪 Domain: Chemical Process Engineering
The system models a **Multi-Unit Plant** consisting of:
* [cite_start]**CSTR (Reactor):** Non-isothermal reaction kinetics. [cite: 30]
* [cite_start]**Heat Exchanger:** Temperature regulation via coolant flow. [cite: 38]
* [cite_start]**Separator:** Component purification based on relative volatility. [cite: 46]

---

## 🤖 AI Techniques Implemented
[cite_start]To meet the "Classical AI" requirement, this project implements four distinct methodologies:

### 1. State-Space Search (A* Algorithm)
* [cite_start]**Problem:** Optimizing the startup sequence of plant units. [cite: 90]
* [cite_start]**Heuristic:** A cost-to-go estimate based on remaining units to be activated. [cite: 107]
* [cite_start]**Goal:** Find the most efficient order (Cooling → Feed → Reactor → Recycle → Separator). [cite: 357]

### 2. Constraint Satisfaction Problem (CSP)
* [cite_start]**Problem:** Identifying a "Safe Operating Point" that satisfies physical and safety limits. [cite: 128]
* [cite_start]**Variables:** Temperature ($T$), Flow ($F$), Cooling ($Q$), and Recycle ($R$). [cite: 133]
* [cite_start]**Constraints:** Safety bounds such as $T \le 500$ K and $Q \ge 0$. [cite: 147, 153]

### 3. Adversarial Search (Minimax with Alpha-Beta Pruning)
* [cite_start]**Problem:** Robust control against "Adversarial" environmental disturbances (e.g., sudden concentration spikes). [cite: 177, 190]
* [cite_start]**Logic:** The controller treats disturbances as an opponent trying to minimize the plant's performance score. [cite: 219]

### 4. Stochastic Optimization (Monte Carlo Tree Search - MCTS)
* [cite_start]**Problem:** Decision-making under uncertainty for long-term state optimization. [cite: 236]
* [cite_start]**Process:** Uses Selection (UCT), Expansion, Simulation (Rollouts), and Backpropagation to find the best control actions. [cite: 270, 273, 279, 292]

---

## 📊 Performance Analysis
[cite_start]We compare our AI controllers against a traditional **PID Controller**. [cite: 324, 418]

| Metric | PID | Minimax (Robust) | MCTS (Stochastic) |
| :--- | :--- | :--- | :--- |
| **Avg Conversion** | [cite_start]64.69% [cite: 440] | [cite_start]**80.49%** [cite: 440] | [cite_start]64.96% [cite: 440] |
| **Avg Temp** | [cite_start]374.08 K [cite: 440] | [cite_start]383.99 K [cite: 440] | [cite_start]373.89 K [cite: 440] |

---

## 🚀 How to Run
1.  **Clone the Repo:** `git clone https://github.com/yourusername/aifa-process-control.git`
2.  **Install Dependencies:** `pip install -r requirements.txt`
3.  **Run Simulation:** `python src/main.py`

## 👥 Team Details
* **Lakshay Gupta** -- 23CH10037 -- (Chemical Engineering, IIT Kharagpur)
* **Muhammad Hamza** 23CH30019 -- (Chemical Engineering, IIT Kharagpur)
* **Ayush Goel** - 23CH10092 -- (Chemical Engineering, IIT Kharagpur)
* **Krishna Rai** - 23CH3FP03 -- (Chemical Engineering, IIT Kharagpur)
* # Classical_AI-Chemical_Process_Control
