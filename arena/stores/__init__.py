from .json_store import JSON
from .arena_store import Store

STORE_TYPE_MAP = {
    "json": JSON,
    "store": Store,
    "entity": Store,
}
