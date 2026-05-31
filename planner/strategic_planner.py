"""planner/strategic_planner.py — Sequences workflows from goals."""
import logging
log = logging.getLogger("planner.strategic_planner")

class StrategicPlanner:
    def __init__(self, query_engine=None, spatial_reasoner=None):
        self._query = query_engine
        self._spatial = spatial_reasoner

    def _find_location(self, offset: list) -> list:
        if self._spatial is None:
            return offset
        base = self._spatial.suggest_placement("structure", [0.0, 0.0, 0.0])
        return [base[0] + offset[0], base[1] + offset[1], 0.0]

    def plan(self, goal) -> list:
        strategy = (goal.strategy or "tower").lower()
        steps = []
        if strategy in ["perimeter_defense", "fortress"]:
            steps = [
                {"type": "spawn_tower", "parameters": {"location": self._find_location([500, 500, 0])}},
                {"type": "spawn_tower", "parameters": {"location": self._find_location([-500, 500, 0])}},
                {"type": "spawn_tower", "parameters": {"location": self._find_location([500, -500, 0])}},
                {"type": "spawn_tower", "parameters": {"location": self._find_location([-500, -500, 0])}},
                {"type": "spawn_wall", "parameters": {"location": self._find_location([0, 500, 0])}},
                {"type": "spawn_wall", "parameters": {"location": self._find_location([0, -500, 0])}},
            ]
        elif strategy in ["outpost"]:
            steps = [
                {"type": "spawn_outpost", "parameters": {"location": self._find_location([0, 0, 0])}},
                {"type": "spawn_tower", "parameters": {"location": self._find_location([300, 0, 0])}},
                {"type": "spawn_tower", "parameters": {"location": self._find_location([-300, 0, 0])}},
            ]
        elif strategy in ["tower"]:
            steps = [
                {"type": "spawn_tower", "parameters": {"location": self._find_location([0, 0, 0])}},
            ]
        log.debug(f"Planned {len(steps)} steps for strategy: {strategy}")
        return steps
