from neo4j import GraphDatabase
import logging
import tenacity
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphDB:
    """Neo4j client for knowledge graph storage."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """Initialize Neo4j connection with retry logic."""
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "ai_password")
        self.driver = None
        self._connect_with_retries()

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        retry=tenacity.retry_if_exception_type(neo4j.exceptions.ServiceUnavailable),
        before_sleep=lambda retry_state: logger.warning(f"Retrying Neo4j connection: attempt {retry_state.attempt_number}")
    )
    def _connect_with_retries(self):
        """Connect to Neo4j with retries."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password), max_connection_pool_size=50)
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close Neo4j driver."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver closed")

    def create_node(self, label: str, properties: Dict[str, Any]):
        """Create a node in the graph."""
        with self.driver.session() as session:
            try:
                query = f"CREATE (n:{label} {{ {', '.join(f'{k}: ${k}' for k in properties)} }}) RETURN n"
                result = session.run(query, **properties)
                logger.info(f"Created node with label {label}")
                return result.single()[0]
            except Exception as e:
                logger.error(f"Error creating node: {e}")
                raise

    def create_relationship(self, source_label: str, source_id: str, target_label: str, target_id: str, rel_type: str):
        """Create a relationship between nodes."""
        with self.driver.session() as session:
            try:
                query = f"""
                MATCH (source:{source_label} {{id: $source_id}}),
                      (target:{target_label} {{id: $target_id}})
                CREATE (source)-[:{rel_type}]->(target)
                RETURN source, target
                """
                result = session.run(query, source_id=source_id, target_id=target_id)
                logger.info(f"Created relationship {rel_type}")
                return result.single()
            except Exception as e:
                logger.error(f"Error creating relationship: {e}")
                raise