import os
import logging
from sqlalchemy import create_engine as _create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError
import tenacity

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MetadataDB:
    """PostgreSQL client using SQLAlchemy for metadata storage."""
    def __init__(self, url: str = None):
        self.url = url or os.getenv(
            "POSTGRES_URL",
            "postgresql+psycopg2://ai_user:ai_password@localhost:5432/ai_challenge"
        )
        self.engine = None
        self.Session = None
        self._connect_with_retries()

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(min=1, max=10),
        retry=tenacity.retry_if_exception_type(OperationalError),
        before_sleep=lambda state: logger.warning(
            f"Retrying Postgres connection (attempt {state.attempt_number})"
        )
    )
    def _connect_with_retries(self):
        logger.info(f"Connecting to Postgres at {self.url}")
        self.engine = _create_engine(self.url, pool_size=20, max_overflow=10)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        logger.info("Postgres connected")

    def get_engine(self):
        """Return the SQLAlchemy Engine."""
        return self.engine

    def get_session(self):
        """Return a new SQLAlchemy Session."""
        return self.Session()

    def close(self):
        """Dispose engine."""
        if self.engine:
            self.engine.dispose()
            logger.info("Postgres engine disposed")

# module‐level instance & aliases
metadata_db  = MetadataDB()
get_engine   = metadata_db.get_engine
get_session  = metadata_db.get_session
close        = metadata_db.close
