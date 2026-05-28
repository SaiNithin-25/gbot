"""
engine/bridge.py — Async-safe Unreal Engine communication bridge.
Runs INSIDE UE's Python environment — uses unreal module directly.
No remote_execution needed when invoked via UE's py command.
"""
import asyncio, ast, uuid
import logging

log = logging.getLogger("engine.bridge")


class UnrealBridge:
    CALL_GUARD_DELAY = 0.05

    def __init__(self):
        self._connected = False
        self._last_actor_count = 0

    async def connect(self) -> bool:
        try:
            import unreal
            # Verify unreal is functional by calling a simple API
            actors = unreal.EditorLevelLibrary.get_all_level_actors()
            self._connected = True
            log.info(f"UnrealBridge connected. {len(actors)} actors in level.")
            return True
        except Exception as e:
            log.error(f"Connect failed: {e}")
            return False

    async def execute_command(self, command: str) -> dict:
        if not self._connected:
            log.warning("Not connected.")
            return {"success": False, "error": "not_connected"}
        await asyncio.sleep(self.CALL_GUARD_DELAY)
        try:
            import unreal
            # Execute via unreal.PythonScriptLibrary for dynamic commands
            result = unreal.PythonScriptLibrary.execute_python_command(command)
            log.debug(f"CMD OK: {command[:60]}")
            return {"success": True, "result": result}
        except Exception as e:
            log.error(f"Command failed: {e}")
            return {"success": False, "error": str(e)}

    async def spawn_actor(self, location: list, structure_type: str = "Structure", rotation: list = None) -> dict:
        rotation = rotation or [0, 0, 0]
        try:
            await asyncio.sleep(self.CALL_GUARD_DELAY)
            import unreal
            loc = unreal.Vector(location[0], location[1], location[2])
            rot = unreal.Rotator(rotation[0], rotation[1], rotation[2])
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor, loc, rot
            )
            if actor:
                name = actor.get_name()
                actor.set_actor_label(f"Gbot_{structure_type}_{uuid.uuid4().hex[:6].upper()}")
                # Assign appropriate mesh based on structure type
                MESH_MAP = {
                    "Tower":   "/Engine/BasicShapes/Cylinder",
                    "Wall":    "/Engine/BasicShapes/Cube",
                    "Outpost": "/Engine/BasicShapes/Cone",
                }
                mesh_path = MESH_MAP.get(structure_type, "/Engine/BasicShapes/Cube")
                mesh = unreal.load_asset(mesh_path)
                if mesh:
                    static_mesh_comp = actor.static_mesh_component
                    static_mesh_comp.set_static_mesh(mesh)

                # Set scale based on structure type
                SCALE_MAP = {
                    "Tower":   unreal.Vector(2.0, 2.0, 6.0),
                    "Wall":    unreal.Vector(8.0, 1.0, 4.0),
                    "Outpost": unreal.Vector(3.0, 3.0, 3.0),
                }
                scale = SCALE_MAP.get(structure_type, unreal.Vector(2.0, 2.0, 2.0))
                actor.set_actor_scale3d(scale)
                unreal.EditorLoadingAndSavingUtils.save_current_level()

                log.info(f"Spawned: {name} at {location}")
                return {"success": True, "actor_name": name, "actor_label": actor.get_actor_label()}
            return {"success": False, "error": "spawn returned None"}
        except Exception as e:
            log.error(f"spawn_actor failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_all_actors(self) -> dict:
        try:
            await asyncio.sleep(self.CALL_GUARD_DELAY)
            import unreal
            actors = unreal.EditorLevelLibrary.get_all_level_actors()
            names = [a.get_name() for a in actors]
            log.debug(f"get_all_actors: {len(names)} actors")
            return {"success": True, "actors": names}
        except Exception as e:
            log.error(f"get_all_actors failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_gbot_actors(self) -> list:
        """Return all actors in the level whose label starts with 'Gbot_'."""
        await asyncio.sleep(self.CALL_GUARD_DELAY)
        try:
            import unreal
            actors = unreal.EditorLevelLibrary.get_all_level_actors()
            gbot_actors = []
            for actor in actors:
                label = actor.get_actor_label()
                if label.startswith("Gbot_"):
                    loc = actor.get_actor_location()
                    gbot_actors.append({
                        "label": label,
                        "location": [loc.x, loc.y, loc.z]
                    })
            return gbot_actors
        except Exception as e:
            log.error(f"get_gbot_actors failed: {e}")
            return []

    async def reconnect(self) -> bool:
        self.disconnect()
        await asyncio.sleep(2.0)
        return await self.connect()

    def disconnect(self):
        self._connected = False
        log.info("UnrealBridge disconnected.")
