"""
plant.py
--------
Multi-unit chemical process plant simulation.

Models a CSTR reactor coupled with a heat exchanger,
flash separator, and recycle loop.
"""

import numpy as np


class MultiUnitPlant:
    """
    Simulates a multi-unit chemical process plant consisting of:
      - A non-isothermal CSTR (reaction A -> B)
      - A shell-and-tube heat exchanger
      - A flash separator (VLE model)
      - A recycle loop

    State vector: (CA, T, F, Q, R, purity)
      CA     -- reactant concentration [mol/L]
      T      -- reactor temperature [K]
      F      -- feed flow rate [L/s]
      Q      -- cooling duty [W]
      R      -- recycle ratio [-]
      purity -- separator product purity [-]
    """

    # ------------------------------------------------------------------ #
    #  Plant Parameters
    # ------------------------------------------------------------------ #

    # Reactor
    V      = 100      # reactor volume [L]
    k      = 0.15     # first-order rate constant [1/s]
    deltaH = -5000    # heat of reaction [J/mol]
    rhoCp  = 500      # volumetric heat capacity [J/(L·K)]
    CA0    = 1.0      # feed concentration [mol/L]
    T0     = 350      # feed temperature [K]

    # Heat exchanger
    UA         = 4000  # overall heat transfer coefficient x area [W/K]
    T_coolant  = 300   # coolant inlet temperature [K]

    # Separator
    alpha = 2.5  # relative volatility [-]

    # Safety limits
    T_max = 500  # maximum allowable temperature [K]
    P_max = 5    # maximum allowable pressure [bar]

    # Control action step sizes
    DELTA_F = 0.5
    DELTA_R = 0.1
    DELTA_Q = 200

    # Variable bounds
    F_bounds = (1, 10)
    R_bounds = (0, 2)
    Q_bounds = (0, 5000)

    # Available discrete control actions
    ACTIONS = [
        "inc_flow", "dec_flow",
        "inc_recycle", "dec_recycle",
        "inc_cooling", "dec_cooling",
    ]

    # ------------------------------------------------------------------ #
    #  Unit Models
    # ------------------------------------------------------------------ #

    def reactor_step(self, CA, T, F, Q):
        """
        One Euler integration step for the CSTR.

        Returns updated (CA, T) after applying mass and energy balances.
        """
        dCA = (F / self.V) * (self.CA0 - CA) - self.k * CA
        dT  = (F / self.V) * (self.T0 - T) \
              + (-self.deltaH / self.rhoCp) * self.k * CA \
              - (Q / (self.rhoCp * self.V))
        return CA + dCA, T + dT

    def heat_exchanger(self, T_reactor):
        """
        Compute heat removal duty Q [W] given reactor temperature.
        """
        return self.UA * (T_reactor - self.T_coolant)

    def separator(self, x):
        """
        VLE flash separator model.

        Args:
            x: liquid-phase mole fraction of product B

        Returns:
            y: vapour-phase mole fraction (purity)
        """
        return (self.alpha * x) / (1 + (self.alpha - 1) * x)

    # ------------------------------------------------------------------ #
    #  Full Plant Step
    # ------------------------------------------------------------------ #

    def plant_step(self, state, action):
        """
        Apply a discrete control action and advance the plant by one time step.

        Args:
            state:  (CA, T, F, Q, R, purity)
            action: one of ACTIONS

        Returns:
            new_state: (CA, T, F, Q, R, purity)
        """
        CA, T, F, Q, R, purity = state

        # Apply control action
        if action == "inc_flow":
            F += self.DELTA_F
        elif action == "dec_flow":
            F -= self.DELTA_F
        elif action == "inc_recycle":
            R += self.DELTA_R
        elif action == "dec_recycle":
            R -= self.DELTA_R
        elif action == "inc_cooling":
            Q += self.DELTA_Q
        elif action == "dec_cooling":
            Q -= self.DELTA_Q

        # Enforce variable bounds
        F = max(self.F_bounds[0], min(F, self.F_bounds[1]))
        R = max(self.R_bounds[0], min(R, self.R_bounds[1]))
        Q = max(self.Q_bounds[0], min(Q, self.Q_bounds[1]))

        # Advance reactor (effective flow includes recycle)
        CA, T = self.reactor_step(CA, T, F * (1 + R), Q)

        # Update separator purity
        purity = self.separator(1 - CA)

        return (CA, T, F, Q, R, purity)

    # ------------------------------------------------------------------ #
    #  Evaluation & Safety
    # ------------------------------------------------------------------ #

    def evaluate(self, state):
        """
        Composite performance score.

        Rewards conversion and purity; penalises temperature deviation
        from setpoint (450 K) and high energy use.
        """
        CA, T, F, Q, R, purity = state
        conversion   = 1 - CA / self.CA0
        energy_cost  = Q / 1000
        score = (
            10 * conversion
            + 5  * purity
            - 0.01 * abs(T - 450)
            - energy_cost
        )
        return score

    def safe(self, state):
        """Return True if the current state is within safety limits."""
        _, T, *_ = state
        return T <= self.T_max

    def get_metrics(self, state):
        """Return a human-readable dict of key performance indicators."""
        CA, T, F, Q, R, purity = state
        return {
            "CA"         : round(CA, 4),
            "T"          : round(T, 2),
            "F"          : round(F, 2),
            "Q"          : round(Q, 1),
            "R"          : round(R, 2),
            "purity"     : round(purity, 4),
            "conversion" : round(1 - CA / self.CA0, 4),
            "score"      : round(self.evaluate(state), 4),
            "safe"       : self.safe(state),
        }
