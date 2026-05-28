"""
gbot/demo.py
Demo launcher — runs dashboard + demo commands together.
Run this from UE Python console for the hackathon demo.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
from PyQt6.QtWidgets import QApplication
from ui.gbot_dashboard import GbotDashboard
import gbot_runner

DEMO_COMMANDS = [
    "build something defendable",
    "build a watchtower",
    "build fortress",
]

async def run_demo(dashboard):
    gbot_runner.set_dashboard(dashboard)
    await gbot_runner._init()
    for cmd in DEMO_COMMANDS:
        print(f"\n>>> {cmd}")
        await gbot_runner.run_command(cmd)
        await asyncio.sleep(2)  # pause between commands

def launch():
    app = QApplication(sys.argv)
    dashboard = GbotDashboard()
    dashboard.show()

    # Run demo commands in background
    loop = asyncio.new_event_loop()
    import threading
    def run():
        loop.run_until_complete(run_demo(dashboard))
    t = threading.Thread(target=run, daemon=True)
    t.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    launch()
