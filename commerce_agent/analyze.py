"""Evidence-coverage analysis. No arbitrary scores: for each opportunity, state what is known per dimension and what is UNKNOWN."""
from collections import defaultdict
from .schema import CORE, DIMENSIONS
from . import economics

def dedupe(evidence):
    seen, out = set(), []
    for e in evidence:
        if e.id not in seen:
            seen.add(e.id); out.append(e)
    return out

def analyze(opps, evidence, cfg):
    by = defaultdict(list)
    for e in evidence: by[e.opportunity].append(e)
    out = []
    for o in opps.values():
        dims = defaultdict(list)
        for e in by.get(o.key, []): dims[e.dimension].append(e)
        unknown = [d for d in DIMENSIONS if not dims.get(d)]
        # An opportunity is only 'investigable' when every core dimension has at least one sourced FACT;
        # first-party facts are called out separately from third-party claims.
        core_gaps = [d for d in CORE if not any(e.label == "FACT" for e in dims.get(d, []))]
        first_party = sum(1 for e in by.get(o.key, []) if e.provenance == "FIRST_PARTY")
        econ = None
        if o.price_low and o.platform in cfg["fees"]:
            mid = round((o.price_low + (o.price_high or o.price_low)) / 2, 2)
            econ = economics.table(mid, o.production_cost, o.platform, cfg["fees"], cfg["revenue_targets"])
        status = ("READY FOR HUMAN INVESTIGATION" if not core_gaps and first_party else
                  "INSUFFICIENT EVIDENCE - core gaps: " + ", ".join(core_gaps))
        out.append({"opportunity": o, "dims": dict(dims), "unknown": unknown, "core_gaps": core_gaps,
                    "first_party_count": first_party, "econ": econ, "status": status})
    return out
