"""planner/goal_interpreter.py — AI reasoning -> ProceduralGoal."""
import logging
from dataclasses import dataclass, field
log = logging.getLogger("planner.goal_interpreter")

@dataclass
class ProceduralGoal:
    strategy: str
    steps: list = field(default_factory=list)
    optimization_priority: str = "balanced"

class GoalInterpreter:
    def interpret(self, ai_reasoning: dict) -> ProceduralGoal:
        g = ProceduralGoal(
            strategy=ai_reasoning.get("strategy","default"),
            steps=ai_reasoning.get("steps",[]),
            optimization_priority=ai_reasoning.get("optimization_priority","balanced"),
        )
        log.debug(f"Goal: {g.strategy} | {len(g.steps)} steps")
        return g
