# scripts/test_connections.py

import os
import sys

# 1) Ensure project root is on sys.path so `import database…` works
script_dir   = os.path.dirname(__file__)                # …/AIC-2025-main/scripts
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2) Imports
from sqlalchemy import text
from database.connections import metadata_db, cache_db, bloom_filter, vector_db, graph_db

def test_postgres():
    print("\nTesting Postgres…")
    engine = metadata_db.get_engine()
    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT 1")
        print("  → SELECT 1 returned:", result.scalar())

def test_redis():
    print("\nTesting Redis…")
    pong = cache_db.ping()
    print("  → PING:", pong)
    cache_db.set("test_key", "test_val", ttl=5)
    val = cache_db.get("test_key")
    print("  → GET test_key:", val)
    cache_db.delete("test_key")

def test_bloom():
    print("\nTesting BloomFilter…")
    key = "test_bloom_key"
    before = bloom_filter.exists(key)
    print("  → exists before add:", before)
    bloom_filter.add(key)
    after = bloom_filter.exists(key)
    print("  → exists after add:", after)

def test_vector():
    print("\nTesting VectorDB…")
    conn = vector_db.connection
    print("  → VectorDB connection object:", conn)

def test_graph():
    print("\nTesting GraphDB…")
    with graph_db.driver.session() as session:
        record = session.run("RETURN 1 AS v").single()
        print("  → RETURN 1:", record["v"])

if __name__ == "__main__":
    test_postgres()
    test_redis()
    test_bloom()
    test_vector()
    test_graph()
    print("\n✅ All connections tests passed!")
