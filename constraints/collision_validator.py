"""constraints/collision_validator.py — Placement validation."""
import logging
from enum import Enum
from dataclasses import dataclass
log = logging.getLogger("constraints.collision")

class CollisionCategory(Enum):
    VALID_TOUCH         = "VALID_TOUCH"
    VALID_ADJACENCY     = "VALID_ADJACENCY"
    INVALID_PENETRATION = "INVALID_PENETRATION"
    SPACING_VIOLATION   = "SPACING_VIOLATION"

@dataclass
class ValidationResult:
    valid: bool
    category: CollisionCategory
    details: str = ""

class CollisionValidator:
    MIN_SPACING = 100.0

    def validate_placement(self, location: list, query_engine) -> ValidationResult:
        nearby = query_engine.structures_in_radius(location, self.MIN_SPACING)
        if nearby:
            return ValidationResult(False, CollisionCategory.SPACING_VIOLATION,
                                    f"{len(nearby)} structure(s) within min spacing.")
        return ValidationResult(True, CollisionCategory.VALID_ADJACENCY)
