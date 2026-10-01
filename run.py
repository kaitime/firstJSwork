#!/usr/bin/env python3
"""Usage: python run.py [seed query ...]   Runs collect -> normalize -> dedupe -> analyze -> report."""
import json, pathlib, sys
from commerce_agent import log as logmod, models
from commerce_agent.cache import Cache
from commerce_agent.http import Fetcher
from commerce_agent.sources import REGISTRY
from commerce_agent.analyze import analyze, dedupe
from commerce_agent.report import write_all

def main(argv):
    root = pathlib.Path(__file__).parent
    cfg = json.loads((root / "config.json").read_text())
    log = logmod.setup(root)
    cache = Cache(root, cfg["cache_ttl_hours"])
    ctx = {"root": root, "log": log, "fetcher": Fetcher(cfg, cache, log)}
    seeds = argv or ["halloween svg"]
    results, opps, evidence = [], {}, []
    for name, acfg in cfg["adapters"].items():
        if not acfg.get("enabled"): continue
        try:
            r = REGISTRY[name](acfg, ctx).run(seeds)
        except Exception as e:                      # adapters must not kill the run
            from commerce_agent.sources.base import AdapterResult
            r = AdapterResult(name, "unavailable", f"crashed: {e}")
        log.info("adapter %-12s %-11s %s", name, r.status, r.detail)
        results.append(r)
        for o in r.opportunities: opps.setdefault(o.key, o)
        evidence += r.evidence
    evidence = dedupe(evidence)
    for e in evidence:                              # evidence from seed-only adapters attaches to a stub opportunity
        if e.opportunity not in opps:
            from commerce_agent.schema import Opportunity
            opps[e.opportunity] = Opportunity(key=e.opportunity, title=e.opportunity.replace("-", " "))
    analyses = analyze(opps, evidence, cfg)
    models.synthesize(cfg["models"]["synthesis"], analyses, root)
    out = write_all(analyses, results, root)
    log.info("wrote %s (%d opportunities, %d evidence rows)", out, len(analyses), len(evidence))

if __name__ == "__main__":
    main(sys.argv[1:])
