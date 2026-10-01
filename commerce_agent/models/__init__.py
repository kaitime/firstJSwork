"""Swappable model roles. 'none' = rule-based. 'manual' = write a self-contained prompt file that any
authenticated AI environment (e.g. this coding agent) can answer; no paid API required."""
import pathlib

def synthesize(provider, analyses, root: pathlib.Path):
    if provider != "manual":
        return None
    lines = ["# Synthesis request (paste into any capable model)\n",
             "Use ONLY the evidence below. Label output FACT/INFERENCE/HYPOTHESIS. Write UNKNOWN where evidence is missing. No invented numbers.\n"]
    for a in analyses:
        o = a["opportunity"]
        lines.append(f"\n## {o.title}\nStatus: {a['status']}\nUNKNOWN dimensions: {', '.join(a['unknown'])}")
        for d, evs in a["dims"].items():
            for e in evs:
                lines.append(f"- [{d}] [{e.label}/{e.provenance}] {e.claim} ({e.source_url}, {e.collected_at})")
    p = root / "output" / "synthesis_prompt.md"; p.write_text("\n".join(lines)); return p
