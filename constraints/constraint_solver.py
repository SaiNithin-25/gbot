"""constraints/constraint_solver.py — Resolves constraint violations."""
import logging
log = logging.getLogger("constraints.solver")

class ConstraintSolver:
    def __init__(self, validator, spatial_reasoner):
        self._validator = validator
        self._spatial = spatial_reasoner

    def solve(self, location: list, structure_type: str, query_engine) -> list:
        result = self._validator.validate_placement(location, query_engine)
        if result.valid:
            return location
        log.debug(f"Violation at {location}: {result.details}")
        return self._spatial.suggest_placement(structure_type, location)
