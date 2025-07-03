
import logging
from sqlalchemy import Engine
from database.models.base import Base

# Import all models so they're registered with Base
from database.models.video_metadata import VideoMetadata
# Import other models here as needed

logger = logging.getLogger(__name__)

def create_all_tables(engine: Engine):
    """Create all tables defined in models."""
    logger.info("Creating all tables...")
    Base.metadata.create_all(engine)
    logger.info("All tables created successfully")