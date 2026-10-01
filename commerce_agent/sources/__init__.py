from .base import Adapter, AdapterResult
from .local_inbox import LocalInbox
from .suggest import Suggest

# Adding a source (or an API-backed one later) = one class + one line here.
REGISTRY = {"local_inbox": LocalInbox, "suggest": Suggest}
