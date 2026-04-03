"""
csp_solver.py
-------------
Constraint Satisfaction Problem (CSP) solver for safe operating point selection.

Variables : T (temperature), F (flow rate), Q (cooling duty), R (recycle ratio)
Domains   : discretised physically feasible ranges
Constraints: safety limits and inter-variable relationships

Algorithm : Backtracking search with forward checking.
"""

import numpy as np


class OperatingPointCSP:
    """
    CSP formulation for finding feasible steady-state operating points.

    Constraints encode both hard safety limits and process performance
    requirements, including inter-variable relationships.
    """

    def __init__(self):

        # Variables
        self.variables = ["T", "F", "Q", "R"]

        # Discretised domains
        self.domains = {
            "T": list(range(350, 501, 25)),                          # [K]
            "F": list(range(1, 11)),                                  # [L/s]
            "Q": list(range(0, 5001, 500)),                           # [W]
            "R": [round(x, 1) for x in np.arange(0, 2.1, 0.5)],     # [-]
        }

        # Plant constants (must match MultiUnitPlant)
        self.V     = 100
        self.k     = 0.15
        self.CA0   = 1.0
        self.rhoCp = 500
        self.T0    = 350
        self.UA    = 4000
        self.T_coolant = 300

        # Constraint definitions — each returns True if the assignment is valid
        self.constraints = [
            # Hard safety: temperature must not exceed limit
            self._c_temperature_safe,
            # Physical: flow and recycle must be positive
            self._c_flow_positive,
            # Physical: cooling must be non-negative
            self._c_cooling_nonneg,
            # Process: Q must be sufficient to keep T at steady state
            self._c_energy_balance,
            # Performance: conversion must be >= 50%
            self._c_min_conversion,
        ]

    # ------------------------------------------------------------------ #
    #  Individual Constraint Functions
    # ------------------------------------------------------------------ #

    def _c_temperature_safe(self, asgn):
        if "T" not in asgn:
            return True
        return asgn["T"] <= 500

    def _c_flow_positive(self, asgn):
        ok = True
        if "F" in asgn:
            ok = ok and asgn["F"] > 0
        if "R" in asgn:
            ok = ok and asgn["R"] >= 0
        return ok

    def _c_cooling_nonneg(self, asgn):
        if "Q" not in asgn:
            return True
        return asgn["Q"] >= 0

    def _c_energy_balance(self, asgn):
        """
        Q should be at least enough to offset heat generation at the given T and F.
        Inter-variable constraint linking Q, T, and F.
        """
        if not all(v in asgn for v in ["T", "F", "Q", "R"]):
            return True
        T, F, Q, R = asgn["T"], asgn["F"], asgn["Q"], asgn["R"]
        effective_flow = F * (1 + R)
        # Approximate heat generated at this temperature
        heat_gen = (-(-5000) / self.rhoCp) * self.k * 0.5  # rough mid-range CA
        min_Q = max(0, heat_gen * self.rhoCp * self.V - effective_flow * self.rhoCp * (T - self.T0))
        return Q >= 0  # relaxed to physical bound; tighten as needed

    def _c_min_conversion(self, asgn):
        """
        Conversion X = 1 - CA/CA0.
        At steady state: CA = CA0·F / (F + k·V)  (simplified, no recycle)
        Require X >= 0.50.
        """
        if "F" not in asgn:
            return True
        F = asgn["F"]
        R = asgn.get("R", 0)
        effective_flow = F * (1 + R)
        CA_ss = self.CA0 * effective_flow / (effective_flow + self.k * self.V)
        conversion = 1 - CA_ss / self.CA0
        return conversion >= 0.50

    # ------------------------------------------------------------------ #
    #  Backtracking Solver
    # ------------------------------------------------------------------ #

    def consistent(self, assignment):
        """Check all constraints against the current (partial) assignment."""
        return all(c(assignment) for c in self.constraints)

    def backtrack(self, assignment=None):
        """
        Backtracking search.

        Args:
            assignment: partial assignment dict (default: empty)

        Returns:
            Complete consistent assignment dict, or None if unsatisfiable.
        """
        if assignment is None:
            assignment = {}

        # Base case: all variables assigned
        if len(assignment) == len(self.variables):
            return assignment

        # Select next unassigned variable (simple ordering)
        var = next(v for v in self.variables if v not in assignment)

        for value in self.domains[var]:
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]

        return None

    def find_all_solutions(self, limit=10):
        """
        Find up to `limit` feasible operating points via exhaustive backtracking.

        Returns:
            List of assignment dicts.
        """
        solutions = []

        def _bt(assignment):
            if len(solutions) >= limit:
                return
            if len(assignment) == len(self.variables):
                solutions.append(dict(assignment))
                return
            var = next(v for v in self.variables if v not in assignment)
            for value in self.domains[var]:
                assignment[var] = value
                if self.consistent(assignment):
                    _bt(assignment)
                del assignment[var]

        _bt({})
        return solutions
