"""Normalized data model. Every datum is labeled FACT / INFERENCE / HYPOTHESIS and keeps its source."""
from dataclasses import dataclass, field, asdict
import hashlib

LABELS = ("FACT", "INFERENCE", "HYPOTHESIS")
# The four things the system must never conflate, plus supporting dimensions.
DIMENSIONS = (
    "search_interest", "buyer_demand", "purchase_evidence", "new_entrant",
    "customer_pain", "competition", "timing", "price", "differentiation",
)
CORE = ("search_interest", "buyer_demand", "purchase_evidence", "new_entrant")
# FIRST_PARTY = observed directly on the source page; THIRD_PARTY = someone else's claim about it.
PROVENANCE = ("FIRST_PARTY", "THIRD_PARTY")


@dataclass
class Evidence:
    opportunity: str
    dimension: str
    label: str
    claim: str
    source_url: str
    collected_at: str
    source_name: str = ""
    provenance: str = "THIRD_PARTY"
    value: str = ""
    adapter: str = ""

    def validate(self):
        if self.dimension not in DIMENSIONS:
            raise ValueError(f"bad dimension {self.dimension!r}")
        if self.label not in LABELS:
            raise ValueError(f"bad label {self.label!r}")
        if self.provenance not in PROVENANCE:
            raise ValueError(f"bad provenance {self.provenance!r}")
        if not self.claim.strip():
            raise ValueError("empty claim")
        if self.label == "FACT" and not (self.source_url and self.collected_at):
            raise ValueError("FACT requires source_url and collected_at")
        return self

    @property
    def id(self):
        key = f"{self.opportunity}|{self.dimension}|{self.claim.lower().strip()}|{self.source_url}"
        return hashlib.sha1(key.encode()).hexdigest()[:10]

    def to_dict(self):
        d = asdict(self); d["id"] = self.id; return d


@dataclass
class Opportunity:
    key: str
    title: str
    buyer: str = ""
    production: str = ""
    time_to_launch: str = ""
    distribution: str = ""
    differentiation: str = ""
    risks: list = field(default_factory=list)
    falsification: list = field(default_factory=list)
    price_low: float | None = None
    price_high: float | None = None
    platform: str = ""
    production_cost: float = 0.0
    evidence: list = field(default_factory=list)
