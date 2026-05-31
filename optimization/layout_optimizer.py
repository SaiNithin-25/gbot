"""optimization/layout_optimizer.py — Layout scoring and optimization."""
import logging
log = logging.getLogger("optimization.layout")

class LayoutOptimizer:
    def score(self, locations: list, query_engine) -> float:
        if not locations: return 0.0
        densities = [query_engine.density_at(loc,500.0) for loc in locations]
        score = max(0.0, 1.0-(sum(densities)/len(densities))*10)
        log.debug(f"Layout score: {score:.3f}")
        return score

    def optimize(self, locations: list, query_engine) -> list:
        return locations  # TODO: adaptive repair
