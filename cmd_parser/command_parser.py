"""parser/command_parser.py — Deterministic command parser."""
import logging
import re
from dataclasses import dataclass, field
from typing import Optional
log = logging.getLogger("parser")

KNOWN_COMMANDS = {
    "build":    ["fortress", "tower", "wall", "arena", "outpost"],
    "query":    ["nearest", "density", "open_space"],
    "optimize": ["layout", "traversal"],
    "clear":    ["all", "selection"],
}

@dataclass
class ParsedCommand:
    raw: str
    action: Optional[str] = None
    target: Optional[str] = None
    parameters: dict = field(default_factory=dict)
    is_ai_required: bool = False

class CommandParser:
    def parse(self, raw_input: str) -> ParsedCommand:
        text = raw_input.strip().lower()
        cmd = ParsedCommand(raw=raw_input)
        for action, targets in KNOWN_COMMANDS.items():
            if text.startswith(action):
                cmd.action = action
                for t in targets:
                    if t in text:
                        cmd.target = t
                        break
                break
        if cmd.action is None:
            cmd.is_ai_required = True
            log.debug(f"No match, forwarding to AI: '{raw_input}'")
        else:
            # Extract optional parameters
            count_match = re.search(r'\b(\d+)\b', text)
            cmd.parameters["count"] = int(count_match.group(1)) if count_match else 1
            if "position" not in cmd.parameters:
                if "north" in text:
                    cmd.parameters["position"] = "north"
                elif "south" in text:
                    cmd.parameters["position"] = "south"
                elif "east" in text:
                    cmd.parameters["position"] = "east"
                elif "west" in text:
                    cmd.parameters["position"] = "west"
            log.debug(f"Parsed: {cmd.action} -> {cmd.target}, params={cmd.parameters}")
        return cmd
