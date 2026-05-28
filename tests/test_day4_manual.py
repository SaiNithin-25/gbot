"""tests/test_day4_manual.py - Day 4 AI integration tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio

from ai.orchestrator import AIOrchestrator
from engine.bridge import UnrealBridge
from world.world_model import WorldModel
from gbot_runner import run_command


async def main():
    try:
        ai = AIOrchestrator()
        prompt = ai._build_prompt(
            "build a watchtower",
            {"structure_count": 3, "existing_types": ["tower"]}
        )
        assert "fortress" in prompt
        assert "structure_count" not in prompt
        print("PASS: prompt builder")
    except Exception as e:
        print(f"FAIL: prompt builder - {e}")

    try:
        ai = AIOrchestrator()
        result = ai._parse_response('{"strategy":"tower","steps":[],"optimization_priority":"defense","reasoning":"user wants defense"}')
        assert result["strategy"] == "tower"
        assert result["reasoning"] is not None
        print("PASS: response parser")
    except Exception as e:
        print(f"FAIL: response parser - {e}")

    try:
        ai = AIOrchestrator()
        result = await ai.reason(
            "build something to defend this area",
            {"structure_count": 0, "existing_types": []}
        )
        assert result["strategy"] in ["fortress", "outpost", "tower"]
        assert result["reasoning"] is not None
        print(f"PASS: ollama live — strategy={result['strategy']}, reasoning={result['reasoning']}")
    except Exception as e:
        print(f"FAIL: ollama live - {e}")

    bridge = None
    try:
        bridge = UnrealBridge()
        connected = await bridge.connect()
        assert connected, "bridge failed to connect; run this test inside UE5"
        world = WorldModel()
        existing = await bridge.get_gbot_actors()
        world.load_from_scene(existing)

        report = await run_command("build something defendable")
        assert report.get("passed"), report
        print("PASS: full AI pipeline")
    except Exception as e:
        print(f"FAIL: full AI pipeline - {e}")
    finally:
        if bridge:
            bridge.disconnect()

    print("Day 4 complete")


asyncio.run(main())
