#!/usr/bin/env python3
# scripts/benchmark.py

import os
import sys
import time
import random
import logging
import numpy as np

# ── path hack ──
this_dir = os.path.dirname(__file__)
project_dir = os.path.abspath(os.path.join(this_dir, ".."))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from prometheus_client import Summary, start_http_server

# Database imports (module‐level instances)
from database.connections.metadata_db import metadata_db
from database.connections.cache_db import cache_db
from database.connections.bloom_filter import BloomFilter
from database.connections.vector_db import vector_db
from database.connections.graph_db import graph_db
from database.models.video_metadata import VideoMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

# Prometheus metrics
vector_search_time = Summary("vector_search_seconds", "Time spent on vector search")
graph_query_time = Summary("graph_query_seconds", "Time spent on graph create/delete")
metadata_query_time = Summary("metadata_query_seconds", "Time spent on metadata queries")
cache_check_time = Summary("cache_check_seconds", "Time spent on cache + bloom operations")


class DatabaseBenchmark:
    def __init__(self):
        # Singletons
        self.metadb = metadata_db
        self.cachedb = cache_db
        self.bloom = BloomFilter()
        self.vectordb = vector_db
        self.graphdb = graph_db

    def _ensure_vector_table(self):
        """Ensure vector table exists with some sample data."""
        try:
            # Try to access the table
            table = self.vectordb.table("video_vectors")
            df = table.to_pandas()
            
            # Check if table has data and embedding column
            if len(df) == 0 or 'embedding' not in df.columns:
                logger.info("Creating sample vector data...")
                # Create sample data with embeddings
                sample_data = []
                for i in range(10):
                    sample_data.append({
                        'id': f'video_{i}',
                        'embedding': np.random.rand(128).tolist(),  # 128-dim random vector
                        'title': f'Sample Video {i}'
                    })
                
                # If table exists but empty, add data
                if len(df) == 0:
                    table.add(sample_data)
                else:
                    # Table exists but no embedding column, recreate
                    # Delete and recreate table
                    try:
                        self.vectordb.connection.drop_table("video_vectors")
                    except:
                        pass
                    
                    # Create new table with proper schema
                    import pyarrow as pa
                    schema = pa.schema([
                        pa.field('id', pa.string()),
                        pa.field('embedding', pa.list_(pa.float32(), 128)),
                        pa.field('title', pa.string())
                    ])
                    table = self.vectordb.connection.create_table("video_vectors", sample_data, schema=schema)
                    
                logger.info("Sample vector data created successfully")
                return table
            else:
                logger.info(f"Vector table exists with {len(df)} records")
                return table
                
        except Exception as e:
            logger.info(f"Vector table doesn't exist, creating it: {e}")
            # Create table with sample data
            sample_data = []
            for i in range(10):
                sample_data.append({
                    'id': f'video_{i}',
                    'embedding': np.random.rand(128).tolist(),  # 128-dim random vector
                    'title': f'Sample Video {i}'
                })
            
            try:
                import pyarrow as pa
                schema = pa.schema([
                    pa.field('id', pa.string()),
                    pa.field('embedding', pa.list_(pa.float32(), 128)),
                    pa.field('title', pa.string())
                ])
                table = self.vectordb.connection.create_table("video_vectors", sample_data, schema=schema)
                logger.info("Vector table created with sample data")
                return table
            except Exception as create_error:
                logger.error(f"Failed to create vector table: {create_error}")
                return None

    @vector_search_time.time()
    def vector_benchmark(self, num_queries: int = 50, limit: int = 5) -> dict:
        """Chạy search trên vectordb với các vector ngẫu nhiên."""
        try:
            # Ensure table exists
            table = self._ensure_vector_table()
            if table is None:
                return {"error": "Could not create/access vector table", "num_queries": 0, "avg_time": 0}
            
            # Get sample embedding or create random one
            try:
                df = table.to_pandas()
                if len(df) > 0 and 'embedding' in df.columns:
                    sample = df.iloc[0]["embedding"]
                    if isinstance(sample, list):
                        sample = np.array(sample)
                else:
                    sample = np.random.rand(128).astype(np.float32)
            except Exception as e:
                logger.warning(f"Could not get sample embedding: {e}, using random")
                sample = np.random.rand(128).astype(np.float32)
            
            # Run benchmark
            start = time.time()
            for _ in range(num_queries):
                try:
                    # Use LanceDB's search method
                    _ = table.search(sample).limit(limit).to_pandas()
                except Exception as search_error:
                    logger.warning(f"Search failed: {search_error}")
                    continue
                    
            elapsed = time.time() - start
            return {"num_queries": num_queries, "avg_time": elapsed / num_queries}
            
        except Exception as e:
            logger.error(f"Vector benchmark failed: {e}")
            return {"error": str(e), "num_queries": 0, "avg_time": 0}

    @graph_query_time.time()
    def graph_benchmark(self, num_ops: int = 50) -> dict:
        """Tạo và xóa node benchmark trên neo4j."""
        try:
            start = time.time()
            for i in range(num_ops):
                node_id = f"bench_{i}_{random.randint(0,1000000)}"
                try:
                    _ = self.graphdb.create_node("Bench", {"id": node_id})
                    _ = self.graphdb.delete_node("Bench", {"id": node_id})
                except Exception as e:
                    logger.warning(f"Graph operation failed: {e}")
                    continue
                    
            elapsed = time.time() - start
            return {"num_ops": num_ops, "avg_time": elapsed / num_ops}
        except Exception as e:
            logger.error(f"Graph benchmark failed: {e}")
            return {"error": str(e), "num_ops": 0, "avg_time": 0}

    @metadata_query_time.time()
    def metadata_benchmark(self, num_queries: int = 50) -> dict:
        """Chạy COUNT và sample query trên Postgres."""
        try:
            start = time.time()
            session = self.metadb.get_session()
            try:
                for _ in range(num_queries):
                    session.query(VideoMetadata).count()
            finally:
                session.close()
            elapsed = time.time() - start
            return {"num_queries": num_queries, "avg_time": elapsed / num_queries}
        except Exception as e:
            logger.error(f"Metadata benchmark failed: {e}")
            return {"error": str(e), "num_queries": 0, "avg_time": 0}

    @cache_check_time.time()
    def cache_benchmark(self, key: str, value: dict) -> dict:
        """
        1) Kiểm tra Bloom filter
        2) Nếu chưa có, thêm vào Bloom filter + Redis
        3) Đọc lại từ cache
        """
        try:
            start = time.time()
            before = self.bloom.exists(key)
            if not before:
                self.bloom.add(key)
                # Redis only supports str/int/bytes -> chuyển dict thành str
                self.cachedb.set(key, str(value))
            cached = self.cachedb.get(key)
            elapsed = time.time() - start
            return {"key": key, "bloom_before": before, "cached": cached, "time": elapsed}
        except Exception as e:
            logger.error(f"Cache benchmark failed: {e}")
            return {"error": str(e), "key": key, "time": 0}

    def run_all(self):
        # Khởi chạy Prometheus trên 9090
        try:
            start_http_server(9090)
            logger.info("Prometheus metrics on :9090")
        except Exception as e:
            logger.warning(f"Could not start Prometheus server: {e}")

        # Vector
        try:
            vec_res = self.vector_benchmark()
            logger.info("Vector benchmark: %s", vec_res)
        except Exception as e:
            logger.error("Vector benchmark failed: %s", e)

        # Graph
        try:
            graph_res = self.graph_benchmark()
            logger.info("Graph benchmark: %s", graph_res)
        except Exception as e:
            logger.error("Graph benchmark failed: %s", e)

        # Metadata
        try:
            meta_res = self.metadata_benchmark()
            logger.info("Metadata benchmark: %s", meta_res)
        except Exception as e:
            logger.error("Metadata benchmark failed: %s", e)

        # Cache + Bloom
        try:
            test_key = f"video:{random.randint(1,1000)}"
            test_val = {"ts": time.time()}
            cache_res = self.cache_benchmark(test_key, test_val)
            logger.info("Cache+Bloom benchmark: %s", cache_res)
        except Exception as e:
            logger.error("Cache+Bloom benchmark failed: %s", e)

        logger.info("All benchmarks completed.")


if __name__ == "__main__":
    bench = DatabaseBenchmark()
    bench.run_all()