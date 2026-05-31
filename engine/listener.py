"""engine/listener.py — Background async Unreal event listener."""
import asyncio, logging
log = logging.getLogger("engine.listener")

class UnrealListener:
    def __init__(self, bridge):
        self._bridge = bridge
        self._running = False
        self._poll_interval = 1.0
        self._last_actor_count = 0

    async def start(self):
        self._running = True
        log.info("UnrealListener started.")
        while self._running:
            await asyncio.sleep(self._poll_interval)
            result = await self._bridge.execute_command("import unreal; print(len(unreal.EditorLevelLibrary.get_all_level_actors()))")
            if not result["success"]:
                log.error(f"Failed to get actor count: {result}")
                continue
            actor_count = int(result["result"])
            if actor_count != self._last_actor_count:
                log.info(f"Actor count changed: {self._last_actor_count} -> {actor_count}")
            self._last_actor_count = actor_count

    def stop(self):
        self._running = False
        log.info("UnrealListener stopped.")
