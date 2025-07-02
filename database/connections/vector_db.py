import lancedb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import tenacity
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDB:
    """LanceDB client for multi-modal vector storage."""
    
    def __init__(self, uri: str = None):
        """Initialize LanceDB connection with retry logic."""
        self.uri = uri or os.getenv("LANCEDB_PATH", "./data/lancedb")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.connection = None
        self._connect_with_retries()

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        retry=tenacity.retry_if_exception_type(lancedb.LanceDBConnectionError),
        before_sleep=lambda retry_state: logger.warning(f"Retrying LanceDB connection: attempt {retry_state.attempt_number}")
    )
    def _connect_with_retries(self):
        """Connect to LanceDB with retries."""
        try:
            self.connection = lancedb.connect(self.uri)
            logger.info(f"Connected to LanceDB at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to LanceDB: {e}")
            raise

    def create_table(self, table_name: str, schema: Dict[str, Any]):
        """Create or update LanceDB table."""
        try:
            table = self.connection.create_table(table_name, schema=schema, mode="overwrite")
            logger.info(f"Created table {table_name}")
            return table
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            raise

    def add_vectors(self, table_name: str, data: List[Dict[str, Any]]):
        """Add vectors and metadata to table."""
        try:
            table = self.connection.open_table(table_name)
            embeddings = [self.embedder.encode(item["content"]).tolist() for item in data]
            for item, embedding in zip(data, embeddings):
                item["vector"] = embedding
            table.add(data)
            logger.info(f"Added {len(data)} vectors to {table_name}")
        except Exception as e:
            logger.error(f"Error adding vectors to {table_name}: {e}")
            raise

    def search(self, table_name: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform hybrid search on table."""
        try:
            table = self.connection.open_table(table_name)
            query_vector = self.embedder.encode(query).tolist()
            results = table.search(query_vector).limit(limit).to_list()
            logger.info(f"Retrieved {len(results)} results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching {table_name}: {e}")
            raise