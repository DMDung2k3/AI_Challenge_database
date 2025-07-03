import os
import logging
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GraphDB:
    """Neo4j driver wrapper for knowledge graph."""

    def __init__(self, uri: str = None):
        self.uri      = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self._driver  = None

    @property
    def driver(self):
        """Return a Neo4j driver, create if needed."""
        if self._driver is None:
            user = os.getenv("NEO4J_USERNAME", "neo4j")
            pwd  = os.getenv("NEO4J_PASSWORD", "ai_password")
            self._driver = GraphDatabase.driver(self.uri, auth=(user, pwd))
            logger.info(f"Connected to Neo4j at {self.uri}")
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            logger.info("Neo4j driver closed")
            
    def create_node(self, label: str, properties: dict) -> str:
        """Create a node with given label and properties. Returns elementId."""
        with self.driver.session() as session:
            # Sử dụng elementId() thay vì id() để tránh deprecated warning
            result = session.run(
                f"CREATE (n:{label} $props) RETURN elementId(n) AS node_id",
                props=properties
            )
            return result.single()["node_id"]

    def delete_node(self, label: str, properties: dict) -> int:
        """Delete nodes matching label + properties. Returns count of deleted nodes."""
        with self.driver.session() as session:
            # Tạo WHERE clause từ properties dict
            where_parts = []
            params = {}
            
            for key, value in properties.items():
                param_key = f"prop_{key}"
                where_parts.append(f"n.{key} = ${param_key}")
                params[param_key] = value
            
            where_clause = " AND ".join(where_parts)
            
            query = f"MATCH (n:{label}) WHERE {where_clause} DELETE n RETURN count(n) as deleted_count"
            
            result = session.run(query, **params)
            return result.single()["deleted_count"]

    def find_nodes(self, label: str, properties: dict = None) -> list:
        """Find nodes matching label and optional properties."""
        with self.driver.session() as session:
            if properties:
                where_parts = []
                params = {}
                
                for key, value in properties.items():
                    param_key = f"prop_{key}"
                    where_parts.append(f"n.{key} = ${param_key}")
                    params[param_key] = value
                
                where_clause = " AND ".join(where_parts)
                query = f"MATCH (n:{label}) WHERE {where_clause} RETURN n"
                
                result = session.run(query, **params)
            else:
                query = f"MATCH (n:{label}) RETURN n"
                result = session.run(query)
            
            return [record["n"] for record in result]

# module‐level instance
graph_db = GraphDB()