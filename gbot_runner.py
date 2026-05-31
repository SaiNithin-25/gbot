import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
from engine.bridge import UnrealBridge
from world.world_model import WorldModel
from query.query_engine import QueryEngine
from spatial.spatial_reasoner import SpatialReasoner
from constraints.collision_validator import CollisionValidator
from constraints.constraint_solver import ConstraintSolver
from workflows.workflow_engine import WorkflowEngine, Workflow
from planner.goal_interpreter import GoalInterpreter
from planner.strategic_planner import StrategicPlanner
from persistence.persistence_manager import PersistenceManager
from evaluation.evaluator import WorkflowEvaluator
from ai.orchestrator import AIOrchestrator
from cmd_parser.command_parser import CommandParser

_dashboard = None

# Global state - persists across calls in same UE session
_state = {}

def set_dashboard(dashboard):
    global _dashboard
    _dashboard = dashboard
    import workflows.workflow_engine as workflow_engine
    workflow_engine._dashboard = dashboard

async def _init():
    if _state.get("ready"):
        return
    bridge = UnrealBridge()
    await bridge.connect()
    world = WorldModel()
    existing = await bridge.get_gbot_actors()
    world.load_from_scene(existing)

    query    = QueryEngine(world)
    spatial  = SpatialReasoner(query)
    validator = CollisionValidator()
    solver   = ConstraintSolver(validator, spatial)
    wf_engine = WorkflowEngine(bridge, solver, query, world)
    persistence = PersistenceManager(world)
    evaluator = WorkflowEvaluator()
    ai        = AIOrchestrator()
    interpreter = GoalInterpreter()
    planner   = StrategicPlanner(query_engine=query, spatial_reasoner=spatial)
    parser    = CommandParser()

    _state.update({
        "ready": True, "bridge": bridge, "world": world,
        "query": query, "wf_engine": wf_engine,
        "persistence": persistence, "evaluator": evaluator,
        "ai": ai, "interpreter": interpreter,
        "planner": planner, "parser": parser,
    })
    print(f"[Gbot] Ready. {len(existing)} existing structures loaded.")

async def run_command(raw: str):
    await _init()
    s = _state
    parser = s["parser"]
    cmd = parser.parse(raw)

    if cmd.is_ai_required or (cmd.action == "build" and cmd.target is None):
        structures = s["world"].all_structures()
        type_counts = {}
        for st in structures:
            type_counts[st.type] = type_counts.get(st.type, 0) + 1
        context = {
            "structure_count": len(structures),
            "existing_types": list(type_counts.keys()),
            "type_counts": type_counts,
        }
        reasoning = await s["ai"].reason(raw, context)
        if _dashboard:
            _dashboard.log_ai_reasoning(
                raw,
                reasoning.get("strategy", "?"),
                reasoning.get("reasoning", "none"),
                reasoning.get("optimization_priority", "?")
            )
        print("\n" + "="*50)
        print(f"[Gbot AI] Goal: {raw}")
        print(f"[Gbot AI] Strategy: {reasoning.get('strategy', '?')}")
        print(f"[Gbot AI] Reasoning: {reasoning.get('reasoning', 'none')}")
        print(f"[Gbot AI] Optimization: {reasoning.get('optimization_priority', '?')}")
        print("="*50 + "\n")
        goal = s["interpreter"].interpret(reasoning)
    elif cmd.action == "build" and cmd.target is not None:
        goal = s["interpreter"].interpret({
            "strategy": cmd.target,
            "steps": [],
            "optimization_priority": "balanced"
        })
    else:
        goal = s["interpreter"].interpret({
            "strategy": cmd.target,
            "steps": [],
            "optimization_priority": "balanced"
        })

    steps = s["planner"].plan(goal)
    wf = Workflow(goal=raw)
    wf.steps = steps
    success = await s["wf_engine"].execute(wf)
    if _dashboard:
        _dashboard.log_workflow(wf.workflow_id, wf.status, raw)
    if success:
        s["persistence"].save("autosave")
    report = s["evaluator"].evaluate(wf, s["world"])
    print(f"[Gbot] {report}")
    return report

def gbot(command: str):
    """Entry point - call this from UE Python console."""
    asyncio.run(run_command(command))
