"""Polite public-web fetcher: robots.txt honored, rate limited, cached. A block is a final answer, never fought."""
import time, urllib.request, urllib.error, urllib.robotparser, urllib.parse

class Unavailable(Exception):
    pass

class Fetcher:
    def __init__(self, cfg, cache, log):
        self.ua, self.gap, self.cache, self.log = cfg["user_agent"], cfg["min_seconds_between_requests"], cache, log
        self._last = 0.0; self._robots = {}; self.dead_hosts = set()

    def _allowed(self, url):
        host = urllib.parse.urlsplit(url)
        base = f"{host.scheme}://{host.netloc}"
        if base not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                req = urllib.request.Request(base + "/robots.txt", headers={"User-Agent": self.ua})
                rp.parse(urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "replace").splitlines())
            except Exception as e:
                raise Unavailable(f"robots.txt unreachable for {host.netloc}: {e}")
            self._robots[base] = rp
        return self._robots[base].can_fetch(self.ua, url)

    def get(self, url):
        hit = self.cache.get(url)
        if hit is not None:
            return hit["body"]
        host = urllib.parse.urlsplit(url).netloc
        if host in self.dead_hosts:
            raise Unavailable(f"{host} already marked unavailable this run")
        try:
            if not self._allowed(url):
                raise Unavailable(f"robots.txt disallows {url}")
            wait = self.gap - (time.time() - self._last)
            if wait > 0: time.sleep(wait)
            self._last = time.time()
            body = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": self.ua}), timeout=15).read().decode("utf-8", "replace")
        except Unavailable:
            self.dead_hosts.add(host); raise
        except Exception as e:
            self.dead_hosts.add(host); raise Unavailable(f"{host}: {e}")
        self.cache.put(url, {"body": body})
        return body
