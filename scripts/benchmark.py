from database.connections.vector_db import VectorDB
from database.connections.graph_db import GraphDB
from database.connections.metadata_db import MetadataDB
from database.connections.cache_db import CacheDB
from prometheus_client import Summary, start_http_server
import time
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
vector_search_time = Summary("vector_search_seconds", "Time spent on vector search")
graph_query_time = Summary("graph_query_seconds", "Time spent on graph query")
metadata_query_time = Summary("metadata_query_seconds", "Time spent on metadata query")
cache_check_time = Summary("cache_check_seconds", "Time spent on cache check")

class DatabaseBenchmark:
    """Benchmark database performance and Bloom filter."""
    
    def __init__(self):
        self.vector_db = VectorDB(uri="./data/lancedb")
        self.graph_db = GraphDB(uri="bolt://localhost:7687")
        self.metadata_db = MetadataDB(url="postgresql+psycopg://ai:ai@localhost:5532/ai")
        self.cache_db = CacheDB(url="redis://localhost:6379/0")

    @vector_search_time.time()
    def benchmark_vector_search(self, query: str, limit: int = 5) -> Dict:
        """Benchmark vector search performance."""
        start_time = time.time()
        results = self.vector_db.search("video_vectors", query, limit)
        return {"time": time.time() - start_time, "results": len(results)}

    @graph_query_time.time()
    def benchmark_graph_query(self) -> Dict:
        """Benchmark graph query performance."""
        start_time = time.time()
        result = self.graph_db.create_node("TestNode", {"id": "test", "name": "Benchmark"})
        return {"time": time.time() - start_time, "nodes": 1}

    @metadata_query_time.time()
    def benchmark_metadata_query(self) -> Dict:
        """Benchmark metadata query performance."""
        start_time = time.time()
        session = self.metadata_db.get_session()
        count = session.query(VideoMetadata).count()
        session.commit()
        return {"time": time.time() - start_time, "count": count}

    @cache_check_time.time()
    def benchmark_cache_check(self, key: str) -> Dict:
        """Benchmark Bloom filter check."""
        start_time = time.time()
        exists = self.cache_db.check_bloom(key)
        return {"time": time.time() - start_time, "exists": exists}

if __name__ == "__main__":
    start_http_server(9090)  # Expose metrics for Prometheus
    benchmark = DatabaseBenchmark()
    logger.info(benchmark.benchmark_vector_search("chicken coconut soup"))
    logger.info(benchmark.benchmark_graph_query())
    logger.info(benchmark.benchmark_metadata_query())
    logger.info(benchmark.benchmark_cache_check("test_video"))