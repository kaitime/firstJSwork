import csv, html, json, datetime

def write_all(analyses, adapter_results, root):
    out = root / "output"; out.mkdir(exist_ok=True)
    stamp = datetime.date.today().isoformat()
    rows = []
    for a in analyses:
        for d, evs in a["dims"].items():
            for e in evs: rows.append(e.to_dict())
    (out / "opportunities.json").write_text(json.dumps([
        {**{k: v for k, v in a["opportunity"].__dict__.items() if k != "evidence"},
         "status": a["status"], "unknown": a["unknown"], "econ": a["econ"],
         "evidence": [e.to_dict() for evs in a["dims"].values() for e in evs]} for a in analyses], indent=2))
    with open(out / "evidence.csv", "w", newline="") as f:
        cols = ["id", "opportunity", "dimension", "label", "provenance", "claim", "value", "source_name", "source_url", "collected_at", "adapter"]
        w = csv.DictWriter(f, cols); w.writeheader()
        for r in rows: w.writerow({c: r.get(c, "") for c in cols})
    esc = html.escape
    p = [f"<!doctype html><meta charset=utf-8><title>Commerce Intel Report</title><style>body{{font:15px/1.5 system-ui;max-width:860px;margin:2rem auto;padding:0 1rem}}h2{{margin-top:2.5rem}}.unk{{color:#a00;font-weight:600}}.tag{{font-size:11px;padding:1px 6px;border-radius:8px;background:#eee}}table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:3px 8px}}</style>",
         f"<h1>Commerce Intelligence Report</h1><p>Run date {stamp}. Unit economics are arithmetic, not forecasts. UNKNOWN means no sourced evidence.</p><h3>Sources</h3><ul>"]
    for r in adapter_results:
        p.append(f"<li><b>{esc(r.adapter)}</b>: {r.status} - {esc(r.detail)}</li>")
    p.append("</ul>")
    for a in analyses:
        o = a["opportunity"]
        p.append(f"<h2>{esc(o.title)}</h2><p><b>Status:</b> {esc(a['status'])}</p>")
        for lab, val in (("Buyer", o.buyer), ("Production", o.production), ("Time to launch", o.time_to_launch), ("Distribution", o.distribution), ("Differentiation", o.differentiation)):
            p.append(f"<p><b>{lab}:</b> {esc(val) if val else '<span class=unk>UNKNOWN</span>'}</p>")
        for d in ("search_interest", "buyer_demand", "purchase_evidence", "new_entrant", "competition", "timing", "price", "customer_pain"):
            p.append(f"<h4>{d.replace('_', ' ').upper()}</h4>")
            evs = a["dims"].get(d)
            if not evs: p.append("<p class=unk>UNKNOWN</p>"); continue
            p.append("<ul>" + "".join(f"<li><span class=tag>{e.label}</span> <span class=tag>{e.provenance}</span> {esc(e.claim)} <a href='{esc(e.source_url)}'>{esc(e.source_name or 'source')}</a> ({e.collected_at})</li>" for e in evs) + "</ul>")
        if a["econ"]:
            ec = a["econ"]
            p.append(f"<h4>ECONOMICS (assumed fees)</h4><p>Price {ec['price']} - fees {ec['platform_fees']} - production {ec['production_cost']} = <b>{ec['net_per_sale']}</b> net/sale</p><table><tr><th>Target</th><th>Sales needed</th></tr>" + "".join(f"<tr><td>${r['target']}</td><td>{r['sales_needed']}</td></tr>" for r in ec["rows"]) + "</table>")
        else:
            p.append("<h4>ECONOMICS</h4><p class=unk>UNKNOWN (no price/platform)</p>")
        p.append("<h4>RISKS</h4><ul>" + "".join(f"<li>{esc(x)}</li>" for x in o.risks) + "</ul><h4>FALSIFICATION TEST</h4><ul>" + "".join(f"<li>{esc(x)}</li>" for x in o.falsification) + "</ul>")
    (out / "report.html").write_text("\n".join(p))
    return out
