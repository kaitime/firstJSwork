"""Marketplace autocomplete = SEARCH INTEREST only (what people type), never buyer demand."""
import json, datetime
from urllib.parse import quote
from .base import Adapter, AdapterResult
from ..http import Unavailable
from ..schema import Evidence

class Suggest(Adapter):
    name, needs = "suggest", "public_web"
    def run(self, seeds):
        res = AdapterResult(self.name, "ok")
        tmpl = self.cfg["endpoint"]
        for s in seeds:
            url = tmpl.replace("{q}", quote(s))
            try:
                body = self.ctx["fetcher"].get(url)
                sugg = [x.get("value") for x in json.loads(body).get("suggestions", [])][:10]
            except Unavailable as e:
                res.status, res.detail = "unavailable", str(e); return res
            except Exception as e:
                res.status, res.detail = "unavailable", f"parse error: {e}"; return res
            if sugg:
                res.evidence.append(Evidence(
                    opportunity=s.lower().replace(" ", "-"), dimension="search_interest", label="FACT",
                    claim=f"Autocomplete for '{s}' returned: {', '.join(sugg)}",
                    source_url=url, source_name="Amazon autocomplete", provenance="FIRST_PARTY",
                    collected_at=datetime.date.today().isoformat(), adapter=self.name).validate())
        return res
