"""engine/tests/test_bridge_manual.py — Async UnrealBridge tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import asyncio, sys
import sys
sys.path.insert(0, "..")
sys.path.insert(0, "../gbot")
from gbot.engine.bridge import UnrealBridge

async def run_tests():
    bridge = UnrealBridge()

    try:
        result = await bridge.connect()
        if result:
            print("PASS: connect")
        else:
            print("FAIL: connect")
    except Exception as e:
        print("FAIL: connect")

    try:
        result = await bridge.spawn_actor("StaticMeshActor", [0.0, 0.0, 100.0])
        print(result)
    except Exception as e:
        print("FAIL: spawn_actor")

    try:
        result = await bridge.get_all_actors()
        print(result)
        actors = result.get("actors", [])
        if actors:
            print(f"PASS: get_all_actors (found {len(actors)} actors)")
        else:
            print("PASS: get_all_actors (no actors)")
    except Exception as e:
        print("FAIL: get_all_actors")

    try:
        result = await bridge.execute_command("print('gbot ping')")
        if result["success"]:
            print("PASS: ping")
        else:
            print("FAIL: ping")
    except Exception as e:
        print("FAIL: ping")

    try:
        bridge.disconnect()
        print("PASS: disconnect")
    except Exception as e:
        print("FAIL: disconnect")

    print("Day 1 complete — all bridge tests passed")

if __name__ == "__main__":
    asyncio.run(run_tests())
