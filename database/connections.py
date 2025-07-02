# connections.py - Database connections cho agents
import os
from typing import Optional
import lancedb
from neo4j import GraphDatabase
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
    """Quản lý tất cả database connections cho agents"""
    
    def __init__(self):
        # Load database URLs từ environment
        self.postgres_url = os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost/ai_challenge")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.lancedb_path = os.getenv("LANCEDB_PATH", "./data/lancedb")
        
        # Initialize connections
        self._vector_db = None
        self._graph_db = None
        self._redis_client = None
        self._sql_engine = None
        self._sql_session = None
    
    def get_vector_db(self) -> lancedb.DBConnection:
        """
        Lấy LanceDB connection cho vector storage
        Sử dụng bởi VectorIndexerAgent và VideoRetrievalAgent
        """
        if self._vector_db is None:
            self._vector_db = lancedb.connect(self.lancedb_path)
        return self._vector_db
    
    def get_graph_db(self) -> GraphDatabase.driver:
        """
        Lấy Neo4j connection cho knowledge graph
        Sử dụng bởi KnowledgeGraphAgent
        """
        if self._graph_db is None:
            # Configure authentication nếu cần
            username = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            self._graph_db = GraphDatabase.driver(
                self.neo4j_uri, 
                auth=(username, password)
            )
        return self._graph_db
    
    def get_redis_client(self) -> redis.Redis:
        """
        Lấy Redis client cho caching và session storage
        Sử dụng bởi ContextManagerAgent
        """
        if self._redis_client is None:
            self._redis_client = redis.from_url(self.redis_url)
        return self._redis_client
    
    def get_sql_engine(self):
        """
        Lấy SQLAlchemy engine cho metadata storage
        Sử dụng bởi tất cả agents cho persistence
        """
        if self._sql_engine is None:
            self._sql_engine = create_engine(self.postgres_url)
        return self._sql_engine
    
    def get_sql_session(self):
        """Lấy SQLAlchemy session"""
        if self._sql_session is None:
            engine = self.get_sql_engine()
            SessionLocal = sessionmaker(bind=engine)
            self._sql_session = SessionLocal()
        return self._sql_session
    
    def test_all_connections(self) -> dict:
        """Test tất cả database connections"""
        results = {}
        
        # Test PostgreSQL
        try:
            engine = self.get_sql_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            results["postgresql"] = "connected"
        except Exception as e:
            results["postgresql"] = f"error: {str(e)}"
        
        # Test Redis
        try:
            redis_client = self.get_redis_client()
            redis_client.ping()
            results["redis"] = "connected"
        except Exception as e:
            results["redis"] = f"error: {str(e)}"
        
        # Test Neo4j
        try:
            driver = self.get_graph_db()
            with driver.session() as session:
                session.run("RETURN 1")
            results["neo4j"] = "connected"
        except Exception as e:
            results["neo4j"] = f"error: {str(e)}"
        
        # Test LanceDB
        try:
            db = self.get_vector_db()
            # LanceDB tự create database nếu không tồn tại
            results["lancedb"] = "connected"
        except Exception as e:
            results["lancedb"] = f"error: {str(e)}"
        
        return results
    
    def close_all_connections(self):
        """Đóng tất cả connections"""
        if self._graph_db:
            self._graph_db.close()
        if self._redis_client:
            self._redis_client.close()
        if self._sql_session:
            self._sql_session.close()
        if self._sql_engine:
            self._sql_engine.dispose()

# Global database manager instance
db_manager = DatabaseManager()