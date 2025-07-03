import os
import logging
from redis import Redis
from redis.exceptions import ResponseError
from prometheus_client import Counter

logger = logging.getLogger(__name__)
bloom_hits   = Counter("bloom_filter_hits", "Bloom filter positive hits")
bloom_misses = Counter("bloom_filter_misses", "Bloom filter negative misses")

class BloomFilter:
    """Bloom filter wrapper for Redis Stack (includes RedisBloom)."""

    def __init__(
        self,
        url: str = None,
        filter_name: str = "default_filter",
        capacity: int = 1_000_000,
        error_rate: float = 0.01
    ):
        self.url         = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.filter_name = filter_name
        self.capacity    = capacity
        self.error_rate  = error_rate
        self.client      = Redis.from_url(self.url, decode_responses=True)
        self._reserved   = False

    def _reserve_if_needed(self):
        if self._reserved:
            return
        try:
            self.client.execute_command(
                "BF.RESERVE",
                self.filter_name,
                str(self.error_rate),
                str(self.capacity),
            )
            logger.info(f"Bloom filter '{self.filter_name}' created")
        except ResponseError as e:
            msg = str(e).lower()
            # Cho phép cả "filter exists" và "item exists"
            if "filter exists" in msg or "item exists" in msg:
                logger.debug(f"Bloom filter '{self.filter_name}' already exists")
            else:
                logger.error(f"Error reserving bloom filter: {e}")
                raise
        self._reserved = True


    def add(self, key: str) -> bool:
        self._reserve_if_needed()
        res = self.client.execute_command("BF.ADD", self.filter_name, key)
        if res == 1:
            bloom_hits.inc()
            return True
        bloom_misses.inc()
        return False

    def exists(self, key: str) -> bool:
        self._reserve_if_needed()
        res = self.client.execute_command("BF.EXISTS", self.filter_name, key)
        if res == 1:
            bloom_hits.inc()
            return True
        bloom_misses.inc()
        return False
