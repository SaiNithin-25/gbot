"""spatial/spatial_reasoner.py — High-level spatial reasoning."""
import logging
log = logging.getLogger("spatial.reasoner")

class SpatialReasoner:
    def __init__(self, query_engine):
        self._query = query_engine

    def suggest_placement(self, structure_type: str, preferred: list) -> list:
        spot = self._query.find_open_space(min_radius=1500.0)
        if spot:
            log.debug(f"Open space: {spot}")
            return spot
        log.warning("No open space — using preferred.")
        return preferred
