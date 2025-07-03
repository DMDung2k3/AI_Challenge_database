#!/usr/bin/env python3
# scripts/test_connections_redis.py

import time
import redis
import sys

def check_redis_info():
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    info = r.info()
    print(f"  Version: {info.get('redis_version')}")
    print(f"  Mode:    {info.get('redis_mode')}")
    print(f"  Clients: {info.get('connected_clients')}")

def test_redis_connection():
    print("\n--- Basic configuration ---")
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True,
                    socket_connect_timeout=5, socket_timeout=5)
    print("✓ PING:", r.ping())
    r.set('test_key', 'test_value')
    print("✓ SET/GET:", r.get('test_key'))
    print("✓ DELETE:", r.delete('test_key'))

    print("\nChecking Redis modules...")
    modules = r.execute_command('MODULE', 'LIST')
    print("✓ Available modules:", modules)

    # Bloom filter test
    try:
        r.execute_command('BF.RESERVE', 'pytest_bloom', '0.01', '100')
    except redis.exceptions.ResponseError:
        pass  # already exists
    r.execute_command('BF.ADD', 'pytest_bloom', 'item1')
    exists = r.execute_command('BF.EXISTS', 'pytest_bloom', 'item1')
    print("✓ BloomFilter operations work:", exists)
    r.delete('pytest_bloom')

    print("\n✓ Redis connection successful!")
    return True

if __name__ == "__main__":
    print("Waiting for Redis to start…")
    time.sleep(2)
    print("Redis version:", redis.__version__)
    print("Python version:", sys.version.split()[0])
    print("\nRedis Server Info:")
    check_redis_info()
    print("\nTesting Redis connection…")
    test_redis_connection()
