import numpy as np

class MultiUnitPlant:
    def __init__(self):
        # Reactor Parameters
        self.V = 100
        self.k = 0.15
        self.deltaH = -5000
        self.rhoCp = 500
        self.CA0 = 1.6
        self.T0 = 350
        
        # Heat exchanger
        self.UA = 4000
        
        # Separator
        self.alpha = 2.5
        
        # Safety
        self.T_max = 500
        self.P_max = 5

    def reactor_step(self, CA, T, F, Q):
        dCA = (F / self.V) * (self.CA0 - CA) - self.k * CA
        dT = (F / self.V) * (self.T0 - T) + (-self.deltaH / self.rhoCp) * self.k * CA - (Q / (self.rhoCp * self.V))
        return CA + dCA, T + dT

    def heat_exchanger(self, T_reactor, T_coolant=300):
        Q = self.UA * (T_reactor - T_coolant)
        return Q

    def separator(self, x):
        y = (self.alpha * x) / (1 + (self.alpha - 1) * x)
        return y

    def plant_step(self, state, action):
        CA, T, F, Q, R, purity = state 
        
        # Control Actions
        if action == "inc_flow":
            F += 0.5
        elif action == "dec_flow":
            F -= 0.5
        elif action == "inc_recycle":
            R += 0.1
        elif action == "dec_recycle":
            R -= 0.1
        elif action == "inc_cooling":
            Q += 200
        elif action == "dec_cooling":
            Q -= 200
            
        F = max(1, min(F, 10))
        R = max(0, min(R, 2))
        Q = max(0, min(Q, 5000))

        CA, T = self.reactor_step(CA, T, F * (1 + R), Q)
        purity = self.separator(1 - CA)
        return (CA, T, F, Q, R, purity)

    def evaluate(self, state):
        CA, T, F, Q, R, purity = state
        conversion = 1 - (CA / self.CA0)
        energy_cost = Q / 1000
        score = 10 * conversion + 5 * purity - 0.01 * abs(T - 450) - energy_cost
        return score

    def safe(self, state):
        CA, T, F, Q, R, purity = state
        return T <= self.T_max
