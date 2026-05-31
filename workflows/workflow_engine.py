"""workflows/workflow_engine.py — Deterministic workflow execution."""
import asyncio, logging, uuid
from dataclasses import dataclass, field
from typing import List
from world.world_model import Structure, WorldModel
log = logging.getLogger("workflows.engine")
_dashboard = None

@dataclass
class Workflow:
    workflow_id: str = field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:8]}")
    goal: str = ""
    steps: List[dict] = field(default_factory=list)
    status: str = "pending"

class WorkflowEngine:
    def __init__(self, bridge, constraint_solver, query_engine, world_model):
        self._bridge = bridge
        self._solver = constraint_solver
        self._query = query_engine
        self._world = world_model
        self._workflow = None

    async def execute(self, workflow: Workflow) -> bool:
        self._workflow = workflow
        workflow.status = "running"
        log.info(f"Workflow {workflow.workflow_id}: {workflow.goal}")
        success = True
        for step in workflow.steps:
            if not await self._execute_step(step):
                success = False
                break
        workflow.status = "complete" if success else "failed"
        if success:
            self._world.link_workflow_group(workflow.workflow_id)
            log.debug(f"Linked {len(self._world.get_group(workflow.workflow_id))} structures in group {workflow.workflow_id}")
        log.info(f"Workflow {workflow.workflow_id} -> {workflow.status}")
        return success

    async def _spawn_tower(self, step: dict, workflow_id: str) -> bool:
        location = step["parameters"].get("location", [0.0, 0.0, 0.0])
        result = await self._bridge.spawn_actor(location=location, structure_type="Tower")
        if result["success"]:
            self._world.add_structure(Structure(
                name=result["actor_label"],
                type="tower",
                workflow_id=workflow_id,
                location=location
            ))
            if _dashboard:
                _dashboard.log_structure(result["actor_label"], "spawn_tower", location)
            log.info(f"Tower spawned: {result['actor_label']}")
            return True
        log.error("Failed to spawn tower")
        return False

    async def _spawn_wall(self, step: dict, workflow_id: str) -> bool:
        location = step["parameters"].get("location", [0.0, 0.0, 0.0])
        result = await self._bridge.spawn_actor(location=location, structure_type="Wall")
        if result["success"]:
            self._world.add_structure(Structure(
                name=result["actor_label"],
                type="wall",
                workflow_id=workflow_id,
                location=location
            ))
            if _dashboard:
                _dashboard.log_structure(result["actor_label"], "spawn_wall", location)
            log.info(f"Wall spawned: {result['actor_label']}")
            return True
        log.error("Failed to spawn wall")
        return False

    async def _spawn_outpost(self, step: dict, workflow_id: str) -> bool:
        location = step["parameters"].get("location", [0.0, 0.0, 0.0])
        result = await self._bridge.spawn_actor(location=location, structure_type="Outpost")
        if result["success"]:
            self._world.add_structure(Structure(
                name=result["actor_label"],
                type="outpost",
                workflow_id=workflow_id,
                location=location
            ))
            if _dashboard:
                _dashboard.log_structure(result["actor_label"], "spawn_outpost", location)
            log.info(f"Outpost spawned: {result['actor_label']}")
            return True
        log.error("Failed to spawn outpost")
        return False

    async def _execute_step(self, step: dict) -> bool:
        step_type = step.get("type", "unknown")
        await asyncio.sleep(0.1)  # guard delay
        workflow_id = self._workflow.workflow_id
        if step_type == "spawn_tower":
            return await self._spawn_tower(step, workflow_id)
        elif step_type == "spawn_wall":
            return await self._spawn_wall(step, workflow_id)
        elif step_type == "spawn_outpost":
            return await self._spawn_outpost(step, workflow_id)
        else:
            log.warning(f"Unknown step type: {step_type}")
            return True
