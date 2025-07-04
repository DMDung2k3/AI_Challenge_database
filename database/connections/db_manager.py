# database/connections/db_manager.py

import os
import asyncio
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import text
from neo4j import AsyncGraphDatabase
import lancedb
from prometheus_client import Counter, Histogram, Gauge, Info
from tenacity import retry, stop_after_attempt, wait_exponential

# Metrics
db_connections_total = Counter(
    'db_connections_total',
    'Total database connections',
    ['database', 'status']
)
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['database', 'operation']
)
db_active_connections = Gauge(
    'db_active_connections',
    'Active database connections',
    ['database']
)
db_info = Info('database_info', 'Database connection information')

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration with connection pooling settings"""
    postgres_url: str = field(default_factory=lambda: os.getenv(
        "POSTGRES_URL",
        "postgresql+asyncpg://ai_user:ai_password@localhost:5432/ai_challenge"
    ))
    redis_url: str = field(default_factory=lambda: os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    ))
    neo4j_uri: str = field(default_factory=lambda: os.getenv(
        "NEO4J_URI",
        "bolt://localhost:7687"
    ))
    neo4j_user: str = field(default_factory=lambda: os.getenv("NEO4J_USERNAME", "neo4j"))
    neo4j_password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "ai_password"))
    lancedb_path: str = field(default_factory=lambda: os.getenv("LANCEDB_PATH", "./data/lancedb"))

    # Connection pool settings
    postgres_pool_size: int = 50
    postgres_max_overflow: int = 100
    postgres_pool_timeout: int = 30
    postgres_pool_recycle: int = 3600

    redis_pool_size: int = 50
    redis_socket_timeout: int = 30
    redis_socket_connect_timeout: int = 10
    redis_retry_on_timeout: bool = True

    neo4j_max_connection_pool_size: int = 50
    neo4j_max_connection_lifetime: int = 3600
    neo4j_connection_timeout: int = 30


class DatabaseManager:
    """Centralized database connection manager with advanced features"""

    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self._postgres_engine = None
        self._postgres_session_maker = None
        self._redis_pool = None
        self._neo4j_driver = None
        self._lancedb_conn = None
        self._health_check_tasks = []

    async def initialize(self):
        """Initialize all database connections"""
        logger.info("Initializing database connections...")
        results = await asyncio.gather(
            self._init_postgres(),
            self._init_redis(),
            self._init_neo4j(),
            self._init_lancedb(),
            return_exceptions=True
        )
        
        # Log any initialization errors but don't fail completely
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                db_names = ['postgres', 'redis', 'neo4j', 'lancedb']
                logger.error(f"Failed to initialize {db_names[i]}: {result}")
        
        self._start_health_checks()
        logger.info("Database connections initialized successfully")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _init_postgres(self):
        """Initialize PostgreSQL connection with async pooling"""
        try:
            self._postgres_engine = create_async_engine(
                self.config.postgres_url,
                pool_size=self.config.postgres_pool_size,
                max_overflow=self.config.postgres_max_overflow,
                pool_timeout=self.config.postgres_pool_timeout,
                pool_recycle=self.config.postgres_pool_recycle,
                pool_pre_ping=True,
                echo=False,
                future=True
            )
            self._postgres_session_maker = async_sessionmaker(
                bind=self._postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            # Test connection - FIXED: wrap SQL string with text()
            async with self._postgres_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            db_connections_total.labels(database='postgres', status='success').inc()
            logger.info("PostgreSQL connection initialized")
        except Exception as e:
            db_connections_total.labels(database='postgres', status='error').inc()
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _init_redis(self):
        """Initialize Redis connection with pooling support"""
        try:
            self._redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.redis_pool_size,
                socket_timeout=self.config.redis_socket_timeout,
                socket_connect_timeout=self.config.redis_socket_connect_timeout,
                retry_on_timeout=self.config.redis_retry_on_timeout,
                health_check_interval=30,
                socket_keepalive=True,
                decode_responses=True
            )
            # Test connection
            async with redis.Redis(connection_pool=self._redis_pool) as client:
                await client.ping()
            db_connections_total.labels(database='redis', status='success').inc()
            logger.info("Redis connection initialized")
        except Exception as e:
            db_connections_total.labels(database='redis', status='error').inc()
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _init_neo4j(self):
        """Initialize Neo4j connection with advanced settings"""
        try:
            self._neo4j_driver = AsyncGraphDatabase.driver(
                self.config.neo4j_uri,
                auth=(self.config.neo4j_user, self.config.neo4j_password),
                max_connection_pool_size=self.config.neo4j_max_connection_pool_size,
                max_connection_lifetime=self.config.neo4j_max_connection_lifetime,
                connection_timeout=self.config.neo4j_connection_timeout,
                keep_alive=True
            )
            await self._neo4j_driver.verify_connectivity()
            db_connections_total.labels(database='neo4j', status='success').inc()
            logger.info("Neo4j connection initialized")
        except Exception as e:
            db_connections_total.labels(database='neo4j', status='error').inc()
            logger.error(f"Failed to initialize Neo4j: {e}")
            raise

    async def _init_lancedb(self):
        """Initialize LanceDB connection"""
        try:
            self._lancedb_conn = lancedb.connect(self.config.lancedb_path)
            tables = self._lancedb_conn.table_names()
            db_connections_total.labels(database='lancedb', status='success').inc()
            logger.info(f"LanceDB connection initialized with {len(tables)} tables")
        except Exception as e:
            db_connections_total.labels(database='lancedb', status='error').inc()
            logger.error(f"Failed to initialize LanceDB: {e}")
            raise

    def _start_health_checks(self):
        """Start periodic health check tasks"""
        self._health_check_tasks = [
            asyncio.create_task(self._postgres_health_check()),
            asyncio.create_task(self._redis_health_check()),
            asyncio.create_task(self._neo4j_health_check()),
        ]

    async def _postgres_health_check(self):
        """PostgreSQL health check loop"""
        while True:
            try:
                if self._postgres_engine:
                    async with self._postgres_engine.begin() as conn:
                        await conn.execute(text("SELECT 1"))
                    db_active_connections.labels(database='postgres').set(1)
                else:
                    db_active_connections.labels(database='postgres').set(0)
            except Exception as e:
                logger.warning(f"PostgreSQL health check failed: {e}")
                db_active_connections.labels(database='postgres').set(0)
            await asyncio.sleep(30)

    async def _redis_health_check(self):
        """Redis health check loop"""
        while True:
            try:
                if self._redis_pool:
                    async with redis.Redis(connection_pool=self._redis_pool) as client:
                        await client.ping()
                    db_active_connections.labels(database='redis').set(1)
                else:
                    db_active_connections.labels(database='redis').set(0)
            except Exception as e:
                logger.warning(f"Redis health check failed: {e}")
                db_active_connections.labels(database='redis').set(0)
            await asyncio.sleep(30)

    async def _neo4j_health_check(self):
        """Neo4j health check loop"""
        while True:
            try:
                if self._neo4j_driver:
                    await self._neo4j_driver.verify_connectivity()
                    db_active_connections.labels(database='neo4j').set(1)
                else:
                    db_active_connections.labels(database='neo4j').set(0)
            except Exception as e:
                logger.warning(f"Neo4j health check failed: {e}")
                db_active_connections.labels(database='neo4j').set(0)
            await asyncio.sleep(30)

    @asynccontextmanager
    async def get_postgres_session(self):
        """Get a PostgreSQL AsyncSession"""
        if not self._postgres_session_maker:
            raise RuntimeError("PostgreSQL not initialized")
        async with self._postgres_session_maker() as session:
            try:
                yield session
            except:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_redis_client(self):
        """Get a Redis client"""
        if not self._redis_pool:
            raise RuntimeError("Redis not initialized")
        async with redis.Redis(connection_pool=self._redis_pool) as client:
            yield client

    @asynccontextmanager
    async def get_neo4j_session(self):
        """Get a Neo4j session"""
        if not self._neo4j_driver:
            raise RuntimeError("Neo4j not initialized")
        async with self._neo4j_driver.session() as session:
            yield session

    def get_lancedb_connection(self):
        """Get the LanceDB connection"""
        if not self._lancedb_conn:
            raise RuntimeError("LanceDB not initialized")
        return self._lancedb_conn

    async def close_all(self):
        """Close all database connections and cancel health checks"""
        logger.info("Closing all database connections...")
        
        # Cancel health check tasks
        for task in self._health_check_tasks:
            task.cancel()
        
        # Wait for tasks to be cancelled
        if self._health_check_tasks:
            await asyncio.gather(*self._health_check_tasks, return_exceptions=True)
        
        # Close connections
        if self._postgres_engine:
            await self._postgres_engine.dispose()
        if self._redis_pool:
            await self._redis_pool.disconnect()
        if self._neo4j_driver:
            await self._neo4j_driver.close()
        
        logger.info("All database connections closed")

    async def get_database_health(self) -> Dict[str, Any]:
        """Get health status for all databases"""
        status: Dict[str, Any] = {}
        
        # PostgreSQL
        try:
            if self._postgres_engine:
                async with self._postgres_engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                status['postgres'] = {'status': 'healthy'}
            else:
                status['postgres'] = {'status': 'unhealthy', 'error': 'Engine not initialized'}
        except Exception as e:
            status['postgres'] = {'status': 'unhealthy', 'error': str(e)}
            
        # Redis
        try:
            if self._redis_pool:
                async with redis.Redis(connection_pool=self._redis_pool) as client:
                    await client.ping()
                status['redis'] = {'status': 'healthy'}
            else:
                status['redis'] = {'status': 'unhealthy', 'error': 'Pool not initialized'}
        except Exception as e:
            status['redis'] = {'status': 'unhealthy', 'error': str(e)}
            
        # Neo4j
        try:
            if self._neo4j_driver:
                await self._neo4j_driver.verify_connectivity()
                status['neo4j'] = {'status': 'healthy'}
            else:
                status['neo4j'] = {'status': 'unhealthy', 'error': 'Driver not initialized'}
        except Exception as e:
            status['neo4j'] = {'status': 'unhealthy', 'error': str(e)}
            
        # LanceDB
        try:
            if self._lancedb_conn:
                tables = self._lancedb_conn.table_names()
                status['lancedb'] = {'status': 'healthy', 'tables': len(tables)}
            else:
                status['lancedb'] = {'status': 'unhealthy', 'error': 'Connection not initialized'}
        except Exception as e:
            status['lancedb'] = {'status': 'unhealthy', 'error': str(e)}
            
        return status


# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for dependency injection
async def initialize_databases():
    await db_manager.initialize()

async def close_databases():
    await db_manager.close_all()

async def get_database_health():
    return await db_manager.get_database_health()

async def get_postgres_session():
    return db_manager.get_postgres_session()

async def get_redis_client():
    return db_manager.get_redis_client()

async def get_neo4j_session():
    return db_manager.get_neo4j_session()

def get_lancedb_connection():
    return db_manager.get_lancedb_connection()