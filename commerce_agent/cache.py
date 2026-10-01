import hashlib, json, pathlib, time

class Cache:
    def __init__(self, root: pathlib.Path, ttl_hours: float):
        self.dir = root / "data" / "cache"; self.dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_hours * 3600

    def _p(self, key):
        return self.dir / (hashlib.sha1(key.encode()).hexdigest() + ".json")

    def get(self, key):
        p = self._p(key)
        if p.exists() and time.time() - p.stat().st_mtime < self.ttl:
            return json.loads(p.read_text())
        return None

    def put(self, key, value):
        self._p(key).write_text(json.dumps(value))
