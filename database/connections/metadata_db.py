from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError
import logging
import tenacity
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetadataDB:
    """PostgreSQL client using SQLAlchemy for metadata storage."""
    
    def __init__(self, url: str = None):
        """Initialize PostgreSQL connection with retry logic."""
        self.url = url or os.getenv("POSTGRES_URL", "postgresql+psycopg://ai_user:ai_password@localhost:5432/ai_challenge")
        self.engine = None
        self.Session = None
        self._connect_with_retries()

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        retry=tenacity.retry_if_exception_type(OperationalError),
        before_sleep=lambda retry_state: logger.warning(f"Retrying PostgreSQL connection: attempt {retry_state.attempt_number}")
    )
    def _connect_with_retries(self):
        """Connect to PostgreSQL with connection pooling."""
        try:
            self.engine = create_engine(self.url, pool_size=20, max_overflow=10)
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            logger.info(f"Connected to PostgreSQL at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def get_session(self):
        """Get a new SQLAlchemy session."""
        return self.Session()

    def close(self):
        """Dispose of the engine and close connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL engine disposed")