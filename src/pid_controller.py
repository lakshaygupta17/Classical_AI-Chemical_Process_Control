"""
pid_controller.py
-----------------
Standard PID controller for reactor temperature regulation.

Used as the industry-standard baseline against which the AI controllers
(Minimax, MCTS) are benchmarked.

The PID output adjusts cooling duty Q to drive reactor temperature
towards a user-defined setpoint.
"""

import random
from plant import MultiUnitPlant


class PIDController:
    """
    Proportional-Integral-Derivative temperature controller.

    Targets a reactor temperature setpoint by modulating cooling duty Q.
    Flow adjustments are made randomly as a simple disturbance model.

    Args:
        plant:       MultiUnitPlant instance
        Kp:          proportional gain
        Ki:          integral gain
        Kd:          derivative gain
        setpoint:    target reactor temperature [K]
    """

    def __init__(
        self,
        plant: MultiUnitPlant,
        Kp: float       = 5.0,
        Ki: float       = 0.1,
        Kd: float       = 1.0,
        setpoint: float = 450.0,
    ):
        self.plant    = plant
        self.Kp       = Kp
        self.Ki       = Ki
        self.Kd       = Kd
        self.setpoint = setpoint

        # Controller state
        self.integral   = 0.0
        self.prev_error = 0.0

    def reset(self):
        """Reset integral and derivative memory (call before new simulation)."""
        self.integral   = 0.0
        self.prev_error = 0.0

    def control(self, state):
        """
        Compute PID output and advance the plant one step.

        Args:
            state: current plant state (CA, T, F, Q, R, purity)

        Returns:
            new_state after applying the PID adjustment
        """
        CA, T, F, Q, R, purity = state

        # PID error terms
        error            = self.setpoint - T
        self.integral   += error
        derivative       = error - self.prev_error
        self.prev_error  = error

        # Compute cooling adjustment
        adjustment = (
            self.Kp * error
            + self.Ki * self.integral
            + self.Kd * derivative
        )

        # Apply adjustment and clip to bounds
        Q = Q + adjustment
        Q = max(self.plant.Q_bounds[0], min(Q, self.plant.Q_bounds[1]))

        # Random flow disturbance (models feed variation)
        flow_action = "inc_flow" if random.random() > 0.5 else "dec_flow"

        # Advance plant
        new_state = self.plant.plant_step((CA, T, F, Q, R, purity), flow_action)
        return new_state
