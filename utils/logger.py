"""utils/logger.py — Logging setup for all subsystems."""
import logging, os
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_NAMES = ["ai_reasoning","workflow","validation","optimization","persistence","query"]

def setup_logging(level=logging.DEBUG):
    os.makedirs(LOG_DIR, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(level)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)
    for name in LOG_NAMES:
        fh = logging.FileHandler(os.path.join(LOG_DIR,f"{name}.log"))
        fh.setFormatter(fmt)
        logging.getLogger(name).addHandler(fh)
