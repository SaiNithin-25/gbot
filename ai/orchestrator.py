"""ai/orchestrator.py — Local Ollama AI orchestration. Output always validated before execution."""
import asyncio, json, logging
log = logging.getLogger("ai.orchestrator")

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen3.5:0.8b"

class AIOrchestrator:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    async def reason(self, goal: str, context: dict) -> dict:
        prompt = self._build_prompt(goal, context)
        raw = await self._call_ollama(prompt)
        result = self._parse_response(raw)
        self.print_reasoning(goal, result)
        return result

    def print_reasoning(self, goal: str, result: dict):
        print("\n" + "="*50)
        print(f"[Gbot AI] Goal: {goal}")
        print(f"[Gbot AI] Strategy: {result.get('strategy', '?')}")
        print(f"[Gbot AI] Reasoning: {result.get('reasoning', 'none')}")
        print(f"[Gbot AI] Optimization: {result.get('optimization_priority', '?')}")
        print("="*50 + "\n")

    def _build_prompt(self, goal: str, context: dict) -> str:
        structure_count = context.get("structure_count", 0)
        existing_types = context.get("existing_types", [])
        return (
            f"You are Gbot, an AI that plans procedural structures for Unreal Engine.\n"
            f"Current world: {structure_count} structures already placed. "
            f"Existing types: {existing_types if existing_types else 'none'}.\n\n"
            f"User goal: {goal}\n\n"
            f"Respond with ONLY a JSON object, no markdown, no explanation:\n"
            f"{{\n"
            f'  "strategy": "fortress" or "outpost" or "tower",\n'
            f'  "steps": [],\n'
            f'  "optimization_priority": "defense" or "coverage" or "balanced",\n'
            f'  "reasoning": "one sentence explaining your choice"\n'
            f"}}\n"
            f"Choose strategy based on the goal. Defend/fortress/protect = fortress. "
            f"Scout/watch/observe = outpost. Single/tower/beacon = tower."
        )

    async def _call_ollama(self, prompt: str) -> str:
        import subprocess
        import json as json_lib

        payload = json_lib.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"think": False}
        })

        for attempt in range(3):
            try:
                proc = await asyncio.create_subprocess_exec(
                    "curl", "-s", "-X", "POST",
                    "http://localhost:11434/api/generate",
                    "-H", "Content-Type: application/json",
                    "-d", payload,
                    "--max-time", "25",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    creationflags=0x08000000  # WIN32: CREATE_NO_WINDOW
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=30
                )
                if stdout:
                    data = json_lib.loads(stdout.decode("utf-8"))
                    raw = data.get("response", "")
                    log.debug(f"Ollama raw: {raw[:200]}")
                    return raw
            except asyncio.TimeoutError:
                log.error(f"Ollama call timed out (attempt {attempt+1})")
            except Exception as e:
                log.error(f"Ollama call failed (attempt {attempt+1}): {e}")
            await asyncio.sleep(1)
        return ""

    def _parse_response(self, raw: str) -> dict:
        try:
            import re
            # Extract first JSON object found anywhere in the response
            match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        log.warning("AI response not valid JSON.")
        return {"strategy": "fortress", "steps": [],
                "optimization_priority": "defense",
                "reasoning": "defaulting to fortress strategy"}
