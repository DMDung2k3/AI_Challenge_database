#!/usr/bin/env python3
# scripts/fix_database_schema.py

import os
import sys
import logging
from sqlalchemy import text

# Path setup
script_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, repo_root)

from database.connections.metadata_db import metadata_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_schema():
    """Get current table schema to see what columns exist."""
    session = metadata_db.get_session()
    try:
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'video_metadata'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        logger.info("Current video_metadata columns:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} ({'nullable' if col[2] == 'YES' else 'not null'})")
        
        return [col[0] for col in columns]
    finally:
        session.close()

def add_missing_columns():
    """Add missing columns to match the VideoMetadata model."""
    session = metadata_db.get_session()
    
    # Get current columns
    current_columns = get_current_schema()
    
    # Define expected columns from VideoMetadata model
    expected_columns = {
        'title': 'VARCHAR(500)',
        'description': 'TEXT',
        'duration': 'FLOAT',
        'fps': 'FLOAT', 
        'width': 'INTEGER',
        'height': 'INTEGER',
        'file_size': 'INTEGER',
        'file_path': 'VARCHAR(1000)',
        'created_at': 'TIMESTAMP',
        'updated_at': 'TIMESTAMP',
        'extra_metadata': 'JSON',
        'is_processed': 'BOOLEAN'
    }
    
    # Add missing columns
    missing_columns = []
    for col_name, col_type in expected_columns.items():
        if col_name not in current_columns:
            missing_columns.append((col_name, col_type))
    
    if not missing_columns:
        logger.info("All columns already exist!")
        return
    
    try:
        logger.info(f"Adding {len(missing_columns)} missing columns...")
        
        for col_name, col_type in missing_columns:
            # Set appropriate defaults
            default_clause = ""
            if col_name == 'created_at':
                default_clause = " DEFAULT CURRENT_TIMESTAMP"
            elif col_name == 'updated_at':
                default_clause = " DEFAULT CURRENT_TIMESTAMP"
            elif col_name == 'is_processed':
                default_clause = " DEFAULT FALSE"
            elif col_name == 'extra_metadata':
                default_clause = " DEFAULT '{}'"
            
            sql = f"ALTER TABLE video_metadata ADD COLUMN {col_name} {col_type}{default_clause}"
            logger.info(f"Executing: {sql}")
            session.execute(text(sql))
        
        session.commit()
        logger.info("Successfully added missing columns!")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to add columns: {e}")
        raise
    finally:
        session.close()

def update_existing_data():
    """Update existing rows with default values where needed."""
    session = metadata_db.get_session()
    
    try:
        # Update created_at for existing rows that have NULL
        session.execute(text("""
            UPDATE video_metadata 
            SET created_at = CURRENT_TIMESTAMP 
            WHERE created_at IS NULL
        """))
        
        # Update updated_at for existing rows that have NULL
        session.execute(text("""
            UPDATE video_metadata 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE updated_at IS NULL
        """))
        
        # Update is_processed for existing rows that have NULL
        session.execute(text("""
            UPDATE video_metadata 
            SET is_processed = FALSE 
            WHERE is_processed IS NULL
        """))
        
        session.commit()
        logger.info("Updated existing data with default values")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update existing data: {e}")
        raise
    finally:
        session.close()

def main():
    logger.info("Starting database schema fix...")
    
    try:
        # Show current schema
        get_current_schema()
        
        # Add missing columns
        add_missing_columns()
        
        # Update existing data
        update_existing_data()
        
        # Show final schema
        logger.info("Final schema:")
        get_current_schema()
        
        logger.info("Database schema fix completed successfully!")
        
    except Exception as e:
        logger.error(f"Schema fix failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()