"""Tier 2/3 of the access hierarchy: existing local data / free exports / evidence collected by any AI session.
Drop JSON files in data/inbox/. Format: {"opportunity": {...}, "evidence": [{...}]}"""
import json
from .base import Adapter, AdapterResult
from ..schema import Evidence, Opportunity

class LocalInbox(Adapter):
    name, needs = "local_inbox", "local_data"
    def run(self, seeds):
        res = AdapterResult(self.name, "ok")
        files = sorted((self.ctx["root"] / "data" / "inbox").glob("*.json"))
        for f in files:
            try:
                d = json.loads(f.read_text())
                o = d["opportunity"]
                opp = Opportunity(**{k: v for k, v in o.items() if k != "evidence"})
                res.opportunities.append(opp)
                for e in d.get("evidence", []):
                    ev = Evidence(opportunity=opp.key, adapter=self.name, **e).validate()
                    res.evidence.append(ev)
            except Exception as e:
                self.ctx["log"].warning("inbox file %s rejected: %s", f.name, e)
                res.detail += f"{f.name} rejected ({e}); "
        res.detail += f"{len(files)} file(s)"
        return res
