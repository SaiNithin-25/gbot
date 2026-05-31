"""tests/test_day3_manual.py - Day 3 spatial integration tests. Run inside UE5 for Test 4."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import math

from world.world_model import WorldModel, Structure
from query.query_engine import QueryEngine
from spatial.spatial_reasoner import SpatialReasoner
from constraints.collision_validator import CollisionValidator
from constraints.constraint_solver import ConstraintSolver
from engine.bridge import UnrealBridge
from workflows.workflow_engine import WorkflowEngine, Workflow
from planner.goal_interpreter import GoalInterpreter
from planner.strategic_planner import StrategicPlanner


def dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(min(len(a), len(b)))))


async def main():
    # Test 1: Spatial index (no UE needed)
    world = WorldModel()
    world.add_structure(Structure("near_origin", "tower", "wf_index", [100.0, 0.0, 0.0]))
    world.add_structure(Structure("north", "tower", "wf_index", [0.0, 1000.0, 0.0]))
    world.add_structure(Structure("southwest", "wall", "wf_index", [-1000.0, -1000.0, 0.0]))

    query = QueryEngine(world)
    query.reindex()
    open_location = query.find_open_space(min_radius=300.0)
    assert all(
        dist(open_location, s.location) >= 300.0
        for s in world.all_structures()
    ), f"open location overlaps existing structure: {open_location}"
    print("PASS: spatial index")

    # Test 2: Traversal (no UE needed)
    clear = query.check_traversal([0, 0, 0], [2000, 0, 0])
    assert clear["passable"], clear

    blocked = query.check_traversal([0, 0, 0], [100, 0, 0])
    assert not blocked["passable"], blocked
    assert "near_origin" in blocked["blocked_by"], blocked
    print("PASS: traversal")

    # Test 3: Relationships (no UE needed)
    relation_world = WorldModel()
    relation_world.add_structure(Structure("a", "tower", "wf_test", [0, 0, 0]))
    relation_world.add_structure(Structure("b", "wall", "wf_test", [500, 0, 0]))
    relation_world.add_structure(Structure("c", "outpost", "wf_test", [1000, 0, 0]))
    relation_world.link_workflow_group("wf_test")
    assert all(
        len(s.relationships) == 2
        for s in relation_world.get_group("wf_test")
    ), [s.relationships for s in relation_world.get_group("wf_test")]
    print("PASS: relationships")

    # Test 4: Full spatial workflow (UE needed)
    bridge = UnrealBridge()
    connected = await bridge.connect()
    assert connected, "bridge failed to connect; run this test inside UE5"

    try:
        spatial_world = WorldModel()
        existing = await bridge.get_gbot_actors()
        spatial_world.load_from_scene(existing)
        print(f"Restored {len(existing)} existing structures from scene.")
        spatial_query = QueryEngine(spatial_world)
        spatial = SpatialReasoner(spatial_query)
        validator = CollisionValidator()
        solver = ConstraintSolver(validator, spatial)
        wf_engine = WorkflowEngine(bridge, solver, spatial_query, spatial_world)
        interpreter = GoalInterpreter()
        planner = StrategicPlanner(query_engine=spatial_query, spatial_reasoner=spatial)

        goal = interpreter.interpret({
            "strategy": "fortress",
            "steps": [],
            "optimization_priority": "balanced"
        })
        wf = Workflow(goal="build fortress")
        wf.steps = planner.plan(goal)
        success = await wf_engine.execute(wf)

        assert success, "workflow execution failed"
        group = spatial_world.get_group(wf.workflow_id)
        assert len(group) == 6, f"expected 6 structures, got {len(group)}"
        assert all(s.relationships for s in group), [s.relationships for s in group]

        open_after = spatial_query.find_open_space(min_radius=300.0)
        assert all(
            dist(open_after, s.location) >= 300.0
            for s in spatial_world.all_structures()
        ), f"open location overlaps existing structure: {open_after}"
        print("PASS: spatial fortress")
    finally:
        bridge.disconnect()

    print("Day 3 complete")


asyncio.run(main())
