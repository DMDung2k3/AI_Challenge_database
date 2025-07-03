from .metadata_db import metadata_db, get_engine, get_session, close
from .cache_db import cache_db
from .bloom_filter import BloomFilter
from .vector_db import vector_db
from .graph_db import graph_db

# proxy để lazy-init BloomFilter khi lần đầu dùng
class _BloomProxy:
    def __init__(self):
        self._bf = None
    def __getattr__(self, name):
        if self._bf is None:
            self._bf = BloomFilter()
        return getattr(self._bf, name)

bloom_filter = _BloomProxy()

__all__ = [
    "metadata_db", "get_engine", "get_session", "close",
    "cache_db", "bloom_filter", "vector_db", "graph_db", "get_vector_db",
]
