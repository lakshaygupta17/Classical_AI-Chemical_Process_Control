"""
pid.py — PID Controller (Classical Baseline)

Standard PID temperature controller used for comparative benchmarking.

  Proportional : corrects present error
  Integral     : corrects accumulated past error (anti-windup clamped)
  Derivative   : dampens rapid change

Output u(t) directly adjusts cooling duty Q.
Flow is adjusted heuristically based on conversion deficit.
"""

import numpy as np


class PIDController:
    """
    PID temperature controller (baseline).
    Anti-windup via integral clamping.

    Output  : Q adjustment.
    Flow    : adjusted by conversion heuristic (inc if conv < 0.75,
              dec if conv > 0.90, hold otherwise).
    """

    def __init__(self, plant, Kp=6.0, Ki=0.05, Kd=1.5, T_target=450):
        self.plant    = plant
        self.Kp       = Kp
        self.Ki       = Ki
        self.Kd       = Kd
        self.T_target = T_target

        self.integral       = 0.0
        self.prev_error     = 0.0
        self.integral_limit = 5000

    def control(self, state):
        """Compute PID output and return the next plant state."""
        CA, T, F, Q, R, purity = state

        error = self.T_target - T
        self.integral = float(
            np.clip(self.integral + error, -self.integral_limit, self.integral_limit)
        )
        dQ = (
            self.Kp * error
            + self.Ki * self.integral
            + self.Kd * (error - self.prev_error)
        )
        self.prev_error = error

        Q = float(np.clip(Q + dQ, 0, 5000))

        conv   = 1 - CA / self.plant.CA0
        action = (
            "inc_flow" if conv < 0.75
            else ("dec_flow" if conv > 0.90 else "hold")
        )

        return self.plant.plant_step((CA, T, F, Q, R, purity), action)


if __name__ == "__main__":
    from plant import MultiUnitPlant
    plant = MultiUnitPlant()
    ctrl  = PIDController(plant)
    state = (0.8, 420.0, 5.0, 2000.0, 0.5, 0.8)
    print("Next state:", ctrl.control(state))
