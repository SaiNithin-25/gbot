"""main.py — Gbot V1 entry point. Wires all subsystems."""
import asyncio, logging

from utils.logger import setup_logging
from engine.bridge import UnrealBridge
from engine.listener import UnrealListener
from cmd_parser.command_parser import CommandParser
from ai.orchestrator import AIOrchestrator
from planner.goal_interpreter import GoalInterpreter
from planner.strategic_planner import StrategicPlanner
from world.world_model import WorldModel
from query.query_engine import QueryEngine
from spatial.spatial_reasoner import SpatialReasoner
from constraints.collision_validator import CollisionValidator
from constraints.constraint_solver import ConstraintSolver
from optimization.layout_optimizer import LayoutOptimizer
from workflows.workflow_engine import WorkflowEngine, Workflow
from persistence.persistence_manager import PersistenceManager
from evaluation.evaluator import WorkflowEvaluator

setup_logging()
log = logging.getLogger("main")

async def main():
    log.info("=== Gbot V1 Starting ===")

    bridge      = UnrealBridge()
    world       = WorldModel()
    query       = QueryEngine(world)
    spatial     = SpatialReasoner(query)
    validator   = CollisionValidator()
    solver      = ConstraintSolver(validator, spatial)
    optimizer   = LayoutOptimizer()
    wf_engine   = WorkflowEngine(bridge, solver, query, world)
    persistence = PersistenceManager(world)
    evaluator   = WorkflowEvaluator()
    ai          = AIOrchestrator()
    interpreter = GoalInterpreter()
    planner     = StrategicPlanner(query_engine=query, spatial_reasoner=spatial)
    parser      = CommandParser()
    listener    = UnrealListener(bridge)

    connected = await bridge.connect()
    if not connected:
        log.warning("Unreal not connected - offline mode.")
    existing = await bridge.get_gbot_actors()
    world.load_from_scene(existing)
    log.info(f"Restored {len(existing)} structures from scene.")

    listener_task = asyncio.create_task(listener.start())

    log.info("Gbot ready. Type a command (or 'quit' to exit).")
    while True:
        try:
            raw = await asyncio.get_event_loop().run_in_executor(None, input, "\nGbot> ")
        except (EOFError, KeyboardInterrupt):
            break
        if raw.strip().lower() in ("quit","exit"):
            break

        cmd = parser.parse(raw)
        if cmd.is_ai_required:
            structures = world.all_structures()
            type_counts = {}
            for s in structures:
                type_counts[s.type] = type_counts.get(s.type, 0) + 1
            context = {
                "structure_count": len(structures),
                "existing_types": list(type_counts.keys()),
                "type_counts": type_counts,
            }
            reasoning = await ai.reason(raw, context)
            goal = interpreter.interpret(reasoning)
            from workflows.workflow_engine import Workflow
            steps = planner.plan(goal)
            wf = Workflow(goal=raw)
            wf.steps = steps
            success = await wf_engine.execute(wf)
            if success:
                persistence.save("autosave")
            report = evaluator.evaluate(wf, world)
            log.info(f"Result: {report}")
        else:
            if cmd.action == "build" and cmd.target:
                count = cmd.parameters.get("count", 1)
                for i in range(count):
                    wf = Workflow(goal=f"{cmd.action} {cmd.target}")
                    wf.steps = planner.plan(
                        interpreter.interpret({"strategy": cmd.target, "steps": [], "optimization_priority": "balanced"})
                    )
                    success = await wf_engine.execute(wf)
                    if success:
                        persistence.save("autosave")
                    report = evaluator.evaluate(wf, world)
                    log.info(f"Result: {report}")

    listener.stop()
    listener_task.cancel()
    persistence.save("shutdown")
    bridge.disconnect()
    log.info("=== Gbot V1 Shutdown ===")

if __name__ == "__main__":
    asyncio.run(main())
