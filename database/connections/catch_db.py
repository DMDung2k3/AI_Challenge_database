import redis
from redisbloom.client import Client as RedisBloomClient
from typing import Optional
import logging
import tenacity
import os
from prometheus_client import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
bloom_hits = Counter("bloom_filter_hits", "Number of Bloom filter hits")
bloom_misses = Counter("bloom_filter_misses", "Number of Bloom filter misses")

class CacheDB:
    """Redis client with Bloom filter for fast membership tests."""
    
    def __init__(self, url: str = None, bloom_size: int = 1000000, error_rate: float = 0.01):
        """Initialize Redis and Bloom filter with retry logic."""
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.bloom_size = bloom_size
        self.error_rate = error_rate
        self.client = None
        self.bloom_client = None
        self._connect_with_retries()

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        retry=tenacity.retry_if_exception_type(redis.ConnectionError),
        before_sleep=lambda retry_state: logger.warning(f"Retrying Redis connection: attempt {retry_state.attempt_number}")
    )
    def _connect_with_retries(self):
        """Connect to Redis with retries."""
        try:
            self.client = redis.Redis.from_url(self.url, max_connections=50)
            self.bloom_client = RedisBloomClient.from_url(self.url)
            self.bloom_client.bfCreate("video_exists", self.error_rate, self.bloom_size)
            logger.info(f"Connected to Redis at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def add_to_bloom(self, key: str) -> bool:
        """Add a key to Bloom filter."""
        try:
            added = self.bloom_client.bfAdd("video_exists", key)
            if added:
                bloom_hits.inc()
            else:
                bloom_misses.inc()
            return added
        except Exception as e:
            logger.error(f"Error adding to Bloom filter: {e}")
            raise

    def check_bloom(self, key: str) -> bool:
        """Check if key exists in Bloom filter."""
        try:
            exists = self.bloom_client.bfExists("video_exists", key)
            if exists:
                bloom_hits.inc()
            else:
                bloom_misses.inc()
            return exists
        except Exception as e:
            logger.error(f"Error checking Bloom filter: {e}")
            raise

    def set_cache(self, key: str, value: str, ttl: int = 86400):
        """Set key-value in Redis with TTL."""
        try:
            self.client.setex(key, ttl, value)
            logger.info(f"Set cache key {key}")
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            raise

    def get_cache(self, key: str) -> Optional[str]:
        """Get value from Redis cache."""
        try:
            value = self.client.get(key)
            return value.decode() if value else None
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            raise