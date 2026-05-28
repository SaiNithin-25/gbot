"""persistence/persistence_manager.py — Autosave and recovery."""
import json, logging, os
from datetime import datetime
log = logging.getLogger("persistence")
SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

class PersistenceManager:
    def __init__(self, world_model):
        self._world = world_model
        os.makedirs(SAVE_DIR, exist_ok=True)

    def save(self, tag: str = "autosave"):
        path = os.path.join(SAVE_DIR, f"{tag}.json")
        state = {
            "saved_at": datetime.utcnow().isoformat(),
            "structures": [
                {"name":s.name,"type":s.type,"location":s.location,"workflow_id":s.workflow_id}
                for s in self._world.all_structures()
            ]
        }
        with open(path,"w") as f:
            json.dump(state,f,indent=2)
        log.info(f"Saved -> {path}")

    def load(self, tag: str = "autosave") -> bool:
        path = os.path.join(SAVE_DIR, f"{tag}.json")
        if not os.path.exists(path):
            log.warning(f"No save at {path}")
            return False
        with open(path) as f:
            state = json.load(f)
        log.info(f"Loaded {len(state['structures'])} structures.")
        # TODO: re-hydrate WorldModel
        return True
