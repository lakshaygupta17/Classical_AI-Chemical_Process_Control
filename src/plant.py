"""
plant.py — Multi-unit chemical plant model
CSTR + Heat Exchanger + Flash Separator

State vector: (CA [mol/L], T [K], F [L/min], Q [J/min], R [-], purity [-])
"""


class MultiUnitPlant:
    """
    Multi-unit chemical plant: CSTR + heat exchanger + separator.

    State: (CA [mol/L], T [K], F [L/min], Q [J/min], R [-], purity [-])
    """

    def __init__(self):
        # Reactor
        self.V      = 100        # volume [L]
        self.k      = 0.15       # rate constant [1/min]
        self.deltaH = -5000      # heat of reaction [J/mol]
        self.rhoCp  = 500        # heat capacity [J/(L·K)]
        self.CA0    = 1.0        # feed concentration [mol/L]
        self.T0     = 350        # feed temperature [K]
        # Heat exchanger
        self.UA     = 4000       # UA coefficient [J/(min·K)]
        # Separator
        self.alpha  = 2.5        # relative volatility
        # Safety
        self.T_max  = 500        # max allowable temperature [K]
        self.T_target = 450      # control setpoint [K]

    def reactor_step(self, CA, T, F_eff, Q):
        """Euler integration of CSTR mass & energy balances."""
        dCA = (F_eff / self.V) * (self.CA0 - CA) - self.k * CA
        dT  = (F_eff / self.V) * (self.T0  - T) + \
              (-self.deltaH / self.rhoCp) * self.k * CA - \
              (Q / (self.rhoCp * self.V))
        return CA + dCA, T + dT

    def heat_exchanger(self, T_reactor, T_coolant=300):
        """Q = UA * (T_reactor - T_coolant)"""
        return self.UA * (T_reactor - T_coolant)

    def separator(self, x):
        """VLE: y = alpha*x / [1 + (alpha-1)*x]"""
        x = max(1e-9, min(x, 1 - 1e-9))
        return (self.alpha * x) / (1 + (self.alpha - 1) * x)

    def plant_step(self, state, action):
        CA, T, F, Q, R, purity = state
        delta = {
            "inc_flow":    ("F",  0.5),
            "dec_flow":    ("F", -0.5),
            "inc_recycle": ("R",  0.1),
            "dec_recycle": ("R", -0.1),
            "inc_cooling": ("Q",  200),
            "dec_cooling": ("Q", -200),
            "hold":        (None, 0),
        }
        var, step = delta.get(action, (None, 0))
        if   var == "F": F += step
        elif var == "Q": Q += step
        elif var == "R": R += step
        F = max(1.0,  min(F, 10.0))
        R = max(0.0,  min(R,  2.0))
        Q = max(0.0,  min(Q, 5000.0))
        CA, T = self.reactor_step(CA, T, F * (1 + R), Q)
        purity = self.separator(max(1e-9, min(1 - CA, 1 - 1e-9)))
        T  = min(T,  self.T_max + 50)
        CA = max(0.0, min(CA, self.CA0))
        return (CA, T, F, Q, R, purity)

    def evaluate(self, state):
        """Multi-objective score: conversion + purity - temp deviation - energy cost."""
        CA, T, F, Q, R, purity = state
        return (10 * (1 - CA / self.CA0)
                + 5  * purity
                - 0.02 * abs(T - self.T_target)
                - Q / 1000.0)

    def safe(self, state):
        return state[1] <= self.T_max

    def conversion(self, state):
        return 1 - state[0] / self.CA0
