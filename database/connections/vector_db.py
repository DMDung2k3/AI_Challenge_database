# database/connections/vector_db.py
import os
import logging
import lancedb

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class VectorDB:
    """LanceDB wrapper for vector storage."""

    def __init__(self, path: str = None):
        self.path = path or os.getenv("LANCEDB_PATH", "./data/lancedb")
        # lazy connect
        self._conn = None

    @property
    def connection(self):
        """Return a LanceDB connection, create if needed."""
        if self._conn is None:
            self._conn = lancedb.connect(self.path)
            logger.info(f"Connected to LanceDB at {self.path}")
        return self._conn

    def create_table(self, name: str, schema: dict):
        return self.connection.create_table(name, schema)

    def table(self, name: str):
        return self.connection.open_table(name)
    
    def search(self, collection_name: str, vector, limit: int = 10):
        """
        Run a k-NN search on the given collection.
        Returns list of results.
        """
        coll = self.get_collection(collection_name)
        # assumes you already have indexed a field named 'embedding'
        return coll.find({"embedding": vector}, limit=limit)

# module‐level instance
vector_db = VectorDB()
