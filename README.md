# Gbot V1 — AI Procedural Worldbuilding Assistant for Unreal Engine 5

> **Describe your world. Watch it build itself.**

Gbot is a fully local AI-assisted procedural world-construction tool for Unreal Engine 5. Type a natural language goal — "build something defendable" or "build a fortress" — and Gbot reasons about it using a local LLM, plans a spatial strategy, validates placements, and spawns real persistent actors directly in your UE5 level.

No cloud. No API keys. No Blueprint scripting. Just plain language and real geometry.

---

## Demo

```
Gbot> build something defendable

==================================================
[Gbot AI] Goal: build something defendable
[Gbot AI] Strategy: fortress
[Gbot AI] Reasoning: Defending the area requires a hard perimeter boundary.
[Gbot AI] Optimization: defense
==================================================

✓ Gbot_Tower_A3F2 placed at (-4500, 1500, 0)
✓ Gbot_Tower_B1C4 placed at (-5500, 1500, 0)
✓ Gbot_Wall_D9E1  placed at (-5000, 1500, 0)
✓ Gbot_Tower_F2A7 placed at (-4500, 500, 0)
✓ Gbot_Tower_G0B3 placed at (-5500, 500, 0)
✓ Gbot_Wall_H5K2  placed at (-5000, 500, 0)

6 structures placed. Autosaved.
```

---

## Features

- **Natural language commands** — deterministic parser handles known commands instantly, AI handles everything else
- **Local AI reasoning** — Ollama + qwen3.5:0.8b reasons about goals and returns structured spatial strategies
- **Spatial intelligence** — bucket index finds open space, avoids overlaps across sessions
- **Persistent actors** — structures saved as real `.uasset` files, survive UE restarts
- **Session memory** — on startup, Gbot scans the level for existing `Gbot_` actors and restores them into the world model
- **Constraint validation** — spacing violations auto-relocate, never crash
- **Async-safe execution** — 50ms guard delays prevent game-thread freeze
- **Observability dashboard** — PyQt6 UI showing AI reasoning, workflow steps, and structure list in real time
- **Autosave** — world state written to `data/autosave.json` after every workflow

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Engine | Unreal Engine 5.6 + Python API |
| AI Runtime | Ollama · qwen3.5:0.8b (local LLM) |
| Language | Python 3.11 · asyncio |
| UI | PyQt6 |
| Persistence | JSON · UE .uasset files |
| Spatial | Custom bucket index + traversal analysis |

---

## Project Structure

```
gbot/
|-- start_gbot.py          # UE console bootstrap; paste/run this inside Unreal
|-- gbot_server.py         # TCP server that runs inside UE and executes commands
|-- gbot_client.py         # Pure-Python socket client for standalone tools
|-- demo_app.py            # PyQt6 standalone app for sending commands to UE
|-- gbot_runner.py         # UE-safe command runner used by the server
|-- main.py                # Local CLI entry point
|-- demo.py                # Demo helper script
|-- requirements.txt       # Python dependencies
|-- ai/                    # Ollama orchestration + reasoning
|-- cmd_parser/            # Deterministic command parser
|-- planner/               # Goal interpreter + strategic planner
|-- workflows/             # Workflow engine + step handlers
|-- world/                 # Persistent world model
|-- query/                 # Spatial query engine (bucket index)
|-- spatial/               # Spatial reasoning + placement
|-- constraints/           # Collision validator + constraint solver
|-- optimization/          # Layout optimizer
|-- persistence/           # Autosave + recovery
|-- evaluation/            # Workflow evaluator
|-- engine/                # Unreal Engine bridge + listener
|-- ui/                    # PyQt6 observability dashboard
|-- tests/                 # Manual and integration test scripts
|-- data/                  # Autosave JSON files
|-- logs/                  # Per-system log files
```

---

## Requirements

- Unreal Engine 5.6
- Python 3.11+ (bundled with UE5)
- [Ollama](https://ollama.ai) installed and running
- qwen3.5:0.8b model pulled
- PyQt6 (for dashboard)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/gbot.git
cd gbot
```

### 2. Install Ollama and pull the model

```bash
# Install Ollama from https://ollama.ai
ollama pull qwen3.5:0.8b
```

### 3. Enable Python in Unreal Engine 5

- Edit → Plugins → Python Editor Script Plugin → Enable
- Edit → Project Settings → Plugins → Python → Enable Remote Execution → True
- Edit → Project Settings → Plugins → Python → Additional Paths → add your `gbot/` parent folder

### 4. Set your default level

- File → Save Current Level As → name it `GbotWorld`
- Edit → Project Settings → Maps & Modes → Default Maps → set both to `GbotWorld`

### 5. Start Ollama

```bash
ollama serve
```

Keep this terminal open while using Gbot.

---

## Usage

### Step 1  Start Ollama
Open a terminal:
    ollama serve

### Step 2  Start Gbot server inside UE
Open UE5, open GbotWorld level.
In UE's Python console paste:
    exec(open("D:/Collage/gbot/start_gbot.py").read())

You should see:
    [Gbot Server] Listening on localhost:8765

### Step 3  Run the standalone app
Open a new terminal or run from VS Code:
    python D:/Collage/gbot/demo_app.py

The Gbot window opens. The connection indicator turns green
when UE is connected.

### Step 4  Send commands
Type in the command box or click Send:
    build fortress
    build something defendable
    build a watchtower
    grill_the_world

Click "Grill the World" to get an AI summary of your entire level.

---

## Supported Commands

| Command | Strategy | Structures |
|---------|----------|-----------|
| `build fortress` | Fortress perimeter | 4 towers + 2 walls |
| `build outpost` | Outpost cluster | 1 outpost + 2 towers |
| `build tower` | Single tower | 1 tower |
| `build something defendable` | AI decides (fortress) | 4 towers + 2 walls |
| `build a watchtower` | AI decides (tower) | 1 tower |
| `build 3 towers` | Repeated tower | 3 towers |
| `build towers at north` | Positioned tower | 1 tower (north offset) |

---

## Architecture

```
User Input
    
CommandParser (deterministic first)
    
AIOrchestrator (Ollama — vague goals only)
    
GoalInterpreter → StrategicPlanner
    
QueryEngine (spatial index — find open space)
    
ConstraintSolver (validate + relocate)
   
WorkflowEngine (step handlers)
    
UnrealBridge (async-safe UE5 calls)
   
Actors spawned + saved as .uasset

WorldModel updated + autosaved
```

---

## Implementation Progress

| Phase | Status | Description |
|-------|--------|-------------|
| 1 — Unreal Execution Layer | ✅ Complete | Bridge, spawn, listener, watchdog |
| 2 — Workflow + Parser | ✅ Complete | Step handlers, param extraction, autosave |
| 3 — Spatial Intelligence | ✅ Complete | Bucket index, open-space detection, relationships |
| 4 — AI Orchestration | ✅ Complete | Ollama integration, reasoning trace, dashboard |
| 5 — Observability UI | ✅ Complete | PyQt6 dashboard, demo runner |
| 6 — Persistence + Recovery | ✅ Complete | .uasset saves, session restore |
| 7 — Learning System | 🔜 Planned | Strategy memory, outcome analysis |
| 8 — Emergent Worldbuilding | 🔜 Future | Autonomous goal generation |

---

## Design Principles

**Local-first** — no cloud dependency, no API keys, works offline on any machine with Ollama.

**Deterministic safety** — AI output is never executed directly. Every plan passes through validation and constraint solving before touching Unreal.

**Async-safe** — all Unreal calls include guard delays. The game thread is never blocked.

**Session-aware** — Gbot always knows what's already in the level before placing anything new.

---

## Built For

OpenAI × Outskill AI Builders Hackathon

**Developer:** E. Sai Nithin Ramanujan
