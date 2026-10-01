import logging, pathlib

def setup(root: pathlib.Path):
    (root / "logs").mkdir(exist_ok=True)
    log = logging.getLogger("commerce")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    for h in (logging.FileHandler(root / "logs" / "run.log"), logging.StreamHandler()):
        h.setFormatter(fmt); log.addHandler(h)
    return log
