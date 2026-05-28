"""query/query_engine.py — Spatial queries: nearest, radius, density, open-space."""
import math, logging
from typing import List, Optional
log = logging.getLogger("query.engine")

class QueryEngine:
    def __init__(self, world_model):
        self._world = world_model
        self._bucket_size = 500.0
        self._buckets = {}

    def _bucket_key(self, location) -> tuple:
        return (
            int(location[0] // self._bucket_size),
            int(location[1] // self._bucket_size),
        )

    def index_structure(self, structure):
        key = self._bucket_key(structure.location)
        if key not in self._buckets:
            self._buckets[key] = []
        self._buckets[key].append(structure)

    def reindex(self):
        self._buckets = {}
        for s in self._world.all_structures():
            self.index_structure(s)

    def nearest_structure(self, location: List[float], exclude: List[str] = None):
        exclude = exclude or []
        best, best_dist = None, float("inf")
        for s in self._world.all_structures():
            if s.name in exclude: continue
            d = self._dist(location, s.location)
            if d < best_dist: best, best_dist = s, d
        return best

    def structures_in_radius(self, center: List[float], radius: float) -> List:
        return [s for s in self._world.all_structures() if self._dist(center,s.location)<=radius]

    def density_at(self, center: List[float], radius: float) -> float:
        count = len(self.structures_in_radius(center,radius))
        area = math.pi*radius**2
        return count/area if area else 0.0

    def find_open_space(self, min_radius: float=1500.0, step: float=1000.0) -> list:
        self.reindex()
        for x in range(-5000,5001,int(step)):
            for y in range(-5000,5001,int(step)):
                candidate = [float(x),float(y),0.0]
                bx, by = self._bucket_key(candidate)
                # Only check nearby buckets
                nearby = []
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nearby += self._buckets.get((bx+dx, by+dy), [])
                conflict = any(
                    self._dist(candidate, s.location) < min_radius
                    for s in nearby
                )
                if not conflict:
                    return candidate
        return [0.0,0.0,0.0]

    def check_traversal(self, from_loc: list, to_loc: list, gap_threshold: float = 150.0) -> dict:
        """
        Check if a path between two locations is clear.
        Samples 5 points along the line and checks for structures within gap_threshold.
        Returns {"passable": bool, "blocked_by": list of structure names}
        """
        blocked_by = []
        for i in range(1, 5):
            t = i / 5.0
            sample = [
                from_loc[0] + (to_loc[0] - from_loc[0]) * t,
                from_loc[1] + (to_loc[1] - from_loc[1]) * t,
                0.0
            ]
            nearby = self.structures_in_radius(sample, gap_threshold)
            for s in nearby:
                if s.name not in blocked_by:
                    blocked_by.append(s.name)
        return {"passable": len(blocked_by) == 0, "blocked_by": blocked_by}

    @staticmethod
    def _dist(a,b):
        return math.sqrt(sum((a[i]-b[i])**2 for i in range(min(len(a),len(b)))))
