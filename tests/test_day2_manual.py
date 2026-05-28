"""tests/test_day2_manual.py — Day 2 integration tests. Run inside UE5 only."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio, json
from cmd_parser.command_parser import CommandParser
from planner.goal_interpreter import GoalInterpreter
from planner.strategic_planner import StrategicPlanner
from world.world_model import WorldModel
from query.query_engine import QueryEngine
from spatial.spatial_reasoner import SpatialReasoner
from constraints.collision_validator import CollisionValidator
from constraints.constraint_solver import ConstraintSolver
from engine.bridge import UnrealBridge
from workflows.workflow_engine import WorkflowEngine, Workflow
from evaluation.evaluator import WorkflowEvaluator
from persistence.persistence_manager import PersistenceManager


async def main():
    # ── Test 1: Parser (no UE needed) ────────────────────────────
    try:
        parser = CommandParser()
        cmd = parser.parse("build fortress")
        assert cmd.action == "build"
        assert cmd.target == "fortress"
        assert cmd.parameters.get("count", 1) == 1

        cmd2 = parser.parse("build 3 towers at north")
        assert cmd2.action == "build"
        assert cmd2.parameters.get("count") == 3
        assert cmd2.parameters.get("position") == "north"
        print("PASS: parser")
    except Exception as e:
        print(f"FAIL: parser — {e}")

    # ── Test 2: Bridge connect ────────────────────────────────────
    bridge = UnrealBridge()
    try:
        ok = await bridge.connect()
        assert ok, "connect() returned False"
        print("PASS: bridge connect")
    except Exception as e:
        print(f"FAIL: bridge connect — {e}")
        return

    # ── Test 3: Spawn actor with label ───────────────────────────
    try:
        result = await bridge.spawn_actor(
            location=[1000.0, 0.0, 0.0],
            structure_type="tower"
        )
        assert result["success"], result.get("error")
        print(f"PASS: spawn with label — {result.get('actor_label')}")
    except Exception as e:
        print(f"FAIL: spawn — {e}")

    # ── Test 4: Full workflow pipeline ───────────────────────────
    try:
        world    = WorldModel()
        query    = QueryEngine(world)
        spatial  = SpatialReasoner(query)
        validator = CollisionValidator()
        solver   = ConstraintSolver(validator, spatial)
        wf_engine = WorkflowEngine(bridge, solver, query, world)
        interpreter = GoalInterpreter()
        planner  = StrategicPlanner(query_engine=query, spatial_reasoner=spatial)

        reasoning = {"strategy": "outpost", "steps": [], "optimization_priority": "balanced"}
        goal = interpreter.interpret(reasoning)
        steps = planner.plan(goal)

        wf = Workflow(goal="build outpost")
        wf.steps = steps
        success = await wf_engine.execute(wf)

        assert wf.status == "complete", f"status was {wf.status}"
        assert len(world.all_structures()) >= 1, "no structures in world model"
        print(f"PASS: full workflow — {len(world.all_structures())} structures placed")
    except Exception as e:
        print(f"FAIL: full workflow — {e}")

    # ── Test 5: Autosave ─────────────────────────────────────────
    try:
        persistence = PersistenceManager(world)
        persistence.save("autosave")
        save_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "autosave.json"
        )
        assert os.path.exists(save_path), f"not found: {save_path}"
        with open(save_path) as f:
            data = json.load(f)
        assert len(data["structures"]) >= 1
        print(f"PASS: autosave — {len(data['structures'])} structures saved")
    except Exception as e:
        print(f"FAIL: autosave — {e}")

    bridge.disconnect()
    print("Day 2 complete.")


asyncio.run(main())
