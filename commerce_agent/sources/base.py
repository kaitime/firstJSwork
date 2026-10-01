from dataclasses import dataclass, field

@dataclass
class AdapterResult:
    adapter: str
    status: str                      # ok | unavailable | disabled
    detail: str = ""
    opportunities: list = field(default_factory=list)   # list[Opportunity]
    evidence: list = field(default_factory=list)        # list[Evidence]

class Adapter:
    """Contract: never raise on source failure; return status='unavailable' with the reason."""
    name = "base"
    needs = "public_web"             # public_web | local_data | free_export | free_api | api_key | paid_api
    def __init__(self, cfg, ctx): self.cfg, self.ctx = cfg, ctx
    def run(self, seeds) -> AdapterResult: raise NotImplementedError
