"""world/world_model.py — In-memory persistent world model."""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
log = logging.getLogger("world.model")

@dataclass
class Structure:
    name: str
    type: str
    workflow_id: str
    location: List[float]
    bounds: dict = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    parent_structure: Optional[str] = None

class WorldModel:
    def __init__(self):
        self._structures: Dict[str, Structure] = {}

    def add_structure(self, s: Structure):
        self._structures[s.name] = s
        log.debug(f"Added: {s.name}")

    def remove_structure(self, name: str):
        self._structures.pop(name, None)

    def get_structure(self, name: str) -> Optional[Structure]:
        return self._structures.get(name)

    def all_structures(self) -> List[Structure]:
        return list(self._structures.values())

    def clear(self):
        self._structures.clear()

    def load_from_scene(self, actors: list):
        """Load existing Gbot actors from UE scene into world model."""
        for a in actors:
            label = a["label"]
            parts = label.split("_")  # Gbot_Tower_XXXXXX
            structure_type = parts[1].lower() if len(parts) > 1 else "unknown"
            s = Structure(
                name=label,
                type=structure_type,
                workflow_id="restored",
                location=a["location"]
            )
            self._structures[s.name] = s
        log.info(f"Loaded {len(actors)} existing structures from scene.")

    def link_structures(self, name_a: str, name_b: str):
        """Create a bidirectional relationship between two structures."""
        a = self.get_structure(name_a)
        b = self.get_structure(name_b)
        if a and name_b not in a.relationships:
            a.relationships.append(name_b)
        if b and name_a not in b.relationships:
            b.relationships.append(name_a)

    def get_group(self, workflow_id: str) -> list:
        """Return all structures belonging to a workflow."""
        return [s for s in self.all_structures() if s.workflow_id == workflow_id]

    def link_workflow_group(self, workflow_id: str):
        """Automatically link all structures in a workflow to each other."""
        group = self.get_group(workflow_id)
        for i, a in enumerate(group):
            for b in group[i+1:]:
                self.link_structures(a.name, b.name)
