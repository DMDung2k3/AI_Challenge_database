import os
from alembic.config import Config
from alembic import command
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run Alembic migrations to set up the database schema."""
    try:
        # Load Alembic configuration
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        
        # Ensure database connection
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            os.getenv("POSTGRES_URL", "postgresql+psycopg://ai_user:ai_password@localhost:5432/ai_challenge")
        )
        
        # Apply migrations
        logger.info("Applying migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully.")
    except Exception as e:
        logger.error(f"Error applying migrations: {e}")
        raise

if __name__ == "__main__":
    run_migrations()