#!/usr/bin/env python3
# scripts/migrate_database.py

import os
import sys
import logging
from subprocess import run, CalledProcessError

logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(message)s")
logger = logging.getLogger(__name__)

# Fix path setup - add project root to sys.path
script_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, repo_root)  # Add repo root instead of database folder

def run_alembic():
    """Try running Alembic migrations if env.py exists."""
    migrations_dir = os.path.join(repo_root, "database", "migrations")
    env_py = os.path.join(migrations_dir, "env.py")
    if not os.path.isfile(env_py):
        logger.info("No Alembic env.py found, skipping Alembic.")
        return False

    alembic_ini = os.path.join(repo_root, "alembic.ini")
    if not os.path.isfile(alembic_ini):
        logger.info("No alembic.ini found, skipping Alembic.")
        return False

    # Set database URL via environment variable instead of --url flag
    db_url = os.getenv(
        "POSTGRES_URL",
        "postgresql+psycopg2://ai_user:ai_password@localhost:5432/ai_challenge"
    )
    
    # Set environment variable for Alembic
    env = os.environ.copy()
    env["POSTGRES_URL"] = db_url
    
    cmd = [
        "alembic", "-c", alembic_ini,
        "--raiseerr",
        "upgrade", "head"
    ]
    
    logger.info("Running Alembic: %s", " ".join(cmd))
    logger.info("Database URL: %s", db_url)
    
    try:
        run(cmd, check=True, cwd=repo_root, env=env)
        logger.info("Alembic migrations applied.")
        return True
    except (CalledProcessError, FileNotFoundError) as e:
        logger.warning("Alembic failed: %s", e)
        return False

def run_sqlalchemy_create_all():
    """Fallback: create all tables via metadata.create_all()."""
    logger.info("Falling back to SQLAlchemy create_all()...")
    
    try:
        # Import after path is set up
        from database.connections.metadata_db import MetadataDB
        
        db_url = os.getenv(
            "POSTGRES_URL",
            "postgresql+psycopg2://ai_user:ai_password@localhost:5432/ai_challenge"
        )
        
        logger.info("Connecting to database: %s", db_url)
        client = MetadataDB(db_url)
        
        # Check if we have an init_db module
        try:
            from database.init_db import create_all_tables
            create_all_tables(client.engine)
            logger.info("All tables created via init_db.create_all_tables()")
        except ImportError:
            # Fallback: create tables directly from models
            logger.info("No init_db module found, creating tables from models...")
            from database.models.base import Base
            Base.metadata.create_all(client.engine)
            logger.info("All tables created via Base.metadata.create_all()")
            
    except Exception as e:
        logger.error("Failed to create tables: %s", e, exc_info=True)
        raise

def test_database_connection():
    """Test database connection before migration."""
    try:
        from database.connections.metadata_db import MetadataDB
        from sqlalchemy import text
        
        db_url = os.getenv(
            "POSTGRES_URL",
            "postgresql+psycopg2://ai_user:ai_password@localhost:5432/ai_challenge"
        )
        
        client = MetadataDB(db_url)
        with client.get_session() as session:
            # Test connection with proper text() wrapper
            session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error("Database connection test failed: %s", e)
        return False

def main():
    logger.info("Starting database migration...")
    
    # Test connection first
    if not test_database_connection():
        logger.error("Cannot connect to database, aborting migration")
        sys.exit(1)
    
    # Try Alembic first
    if run_alembic():
        logger.info("Database migration completed successfully via Alembic")
        sys.exit(0)
    
    # Fallback to SQLAlchemy
    try:
        run_sqlalchemy_create_all()
        logger.info("Database migration completed successfully via SQLAlchemy")
        sys.exit(0)
    except Exception as e:
        logger.error("Could not initialize database schema: %s", e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()