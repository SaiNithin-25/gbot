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
├── ai/              # Ollama orchestration + reasoning
├── cmd_parser/      # Deterministic command parser
├── planner/         # Goal interpreter + strategic planner
├── workflows/       # Workflow engine + step handlers
├── world/           # Persistent world model
├── query/           # Spatial query engine (bucket index)
├── spatial/         # Spatial reasoning + placement
├── constraints/     # Collision validator + constraint solver
├── optimization/    # Layout optimizer
├── persistence/     # Autosave + recovery
├── evaluation/      # Workflow evaluator
├── engine/          # Unreal Engine bridge + listener
├── ui/              # PyQt6 observability dashboard
├── tests/           # Integration test suite
├── data/            # Autosave JSON files
├── logs/            # Per-system log files
├── gbot_runner.py   # UE-safe interactive runner
└── main.py          # Entry point
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

### Option A — Run a single command in UE's Python console

```python
import sys, importlib.util, asyncio
sys.path.insert(0, "D:/path/to/gbot")

spec = importlib.util.spec_from_file_location("gbot_runner", "D:/path/to/gbot/gbot_runner.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

mod.gbot("build something defendable")
mod.gbot("build a watchtower")
mod.gbot("build fortress")
```

### Option B — Run the integration tests

```
py "D:/path/to/gbot/tests/test_demo_rehearsal.py"
```

### Option C — Run the observability dashboard

```bash
python gbot/ui/gbot_dashboard.py
```

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
    ↓
CommandParser (deterministic first)
    ↓
AIOrchestrator (Ollama — vague goals only)
    ↓
GoalInterpreter → StrategicPlanner
    ↓
QueryEngine (spatial index — find open space)
    ↓
ConstraintSolver (validate + relocate)
    ↓
WorkflowEngine (step handlers)
    ↓
UnrealBridge (async-safe UE5 calls)
    ↓
Actors spawned + saved as .uasset
    ↓
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
| 7 — Learning System | 🔄 Planned | Strategy memory, outcome analysis |
| 8 — Emergent Worldbuilding | 🔄 Future | Autonomous goal generation |

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
