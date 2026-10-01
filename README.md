# Commerce Intelligence Agent (Phase 1: research engine only)

Finds what people already spend money on and checks whether a solo operator can enter. Stdlib Python 3.11+, no API keys, no paid services.

    python run.py "halloween svg"     # collect -> normalize -> dedupe -> analyze -> report
    python -m unittest discover tests

Outputs in `output/`: `report.html`, `opportunities.json`, `evidence.csv`, `synthesis_prompt.md`. Logs in `logs/run.log`. Cache in `data/cache/`.

## Design
- **Evidence model** (`schema.py`): every row has dimension (search_interest / buyer_demand / purchase_evidence / new_entrant / ...), label (FACT / INFERENCE / HYPOTHESIS), provenance (FIRST_PARTY observed vs THIRD_PARTY claim), source URL and collection date. A FACT without source+date is rejected.
- **No scores.** `analyze.py` reports per opportunity which dimensions are UNKNOWN. An opportunity is "ready for human investigation" only when all four core dimensions have a sourced FACT and at least one is first-party.
- **Access hierarchy**: adapters declare `needs`. Shipped: `local_inbox` (drop JSON evidence in `data/inbox/`; works with anything an AI session collected or you exported) and `suggest` (autocomplete = search interest only). Fetching honors robots.txt, rate-limits, caches, and marks a blocked host unavailable instead of fighting it.
- **Add a source** (browser/Playwright, an API later): subclass `Adapter`, register in `sources/__init__.py`. Nothing else changes.
- **Model roles** (`config.json` -> `models`): `none` or `manual` (writes a prompt for any authenticated AI). Providers can be added in `models/`.
- **Economics** (`economics.py`): fee numbers in config are assumptions; verify before relying on them. Output is unit arithmetic, not forecasts.

## Status
`data/inbox/pipeline_test_halloween_svg.json` is a pipeline test record built from third-party search snippets. It is not a recommendation.
