"""tests/test_demo_rehearsal.py - Demo rehearsal command sequence."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import contextlib
import io

import gbot_runner


async def main():
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        report = await gbot_runner.run_command("build something defendable")
    printed = output.getvalue()
    print(printed, end="")
    assert report.get("passed"), report
    assert "[Gbot AI] Strategy:" in printed
    assert "[Gbot AI] Strategy: unknown" not in printed
    print("PASS: demo command 1")

    report = await gbot_runner.run_command("build a watchtower")
    assert report.get("passed"), report
    print("PASS: demo command 2")

    report = await gbot_runner.run_command("build fortress")
    assert report.get("passed"), report
    group = gbot_runner._state["world"].get_group(report["workflow_id"])
    assert len(group) == 6, f"expected 6 structures, got {len(group)}"
    print("PASS: demo command 3")

    total = len(gbot_runner._state["world"].all_structures())
    print(f"Total structures: {total}")
    print("Demo rehearsal complete — ready to present.")


asyncio.run(main())
