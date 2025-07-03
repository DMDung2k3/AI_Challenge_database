import os
import logging
import redis
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CacheDB:
    """Redis caching wrapper."""

    def __init__(self, url: str = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = None
        self._connect()

    def _connect(self):
        """Establish Redis connection with retries."""
        try:
            # Create Redis client with simplified configuration
            self.client = redis.Redis.from_url(
                self.url,
                decode_responses=True,
                socket_connect_timeout=10,      # increased timeout
                socket_timeout=10,              # increased timeout
                socket_keepalive=True,
                socket_keepalive_options={},
                retry_on_timeout=True,
                health_check_interval=30,       # enable with longer interval
                max_connections=20,
            )
            
            # Test the connection
            self.client.ping()
            logger.info(f"Connected to Redis at {self.url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def _ensure_connected(self):
        """Ensure Redis connection is alive."""
        if self.client is None:
            self._connect()
        
        try:
            self.client.ping()
        except (ConnectionError, TimeoutError, AttributeError):
            logger.warning("Redis connection lost, reconnecting...")
            self._connect()

    def ping(self) -> bool:
        """Check if Redis is alive."""
        try:
            self._ensure_connected()
            if self.client is None:
                return False
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set a key-value pair in Redis."""
        try:
            self._ensure_connected()
            if self.client is None:
                return False
            
            if ttl:
                return self.client.set(key, value, ex=ttl)
            return self.client.set(key, value)
        except Exception as e:
            logger.error(f"Redis set failed for key {key}: {e}")
            return False

    def get(self, key: str) -> str:
        """Get a value from Redis."""
        try:
            self._ensure_connected()
            if self.client is None:
                return None
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get failed for key {key}: {e}")
            return None

    def delete(self, key: str) -> int:
        """Delete a key from Redis."""
        try:
            self._ensure_connected()
            if self.client is None:
                return 0
            return self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete failed for key {key}: {e}")
            return 0

    def flushdb(self) -> bool:
        """Clear all keys from the current database."""
        try:
            self._ensure_connected()
            if self.client is None:
                return False
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis flushdb failed: {e}")
            return False

# module‐level instance
cache_db = CacheDB()