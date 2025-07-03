"""
Add pgvector extension and embedding column
Revision ID: 002_add_vectors
Revises: 001_initial_schema
Create Date: 2025-07-02 02:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '002_add_vectors'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    # Add embedding column to store vector embeddings
    op.add_column(
        'video_metadata',
        sa.Column('embedding', sa.dialects.postgresql.VECTOR(384), nullable=True)
    )


def downgrade():
    op.drop_column('video_metadata', 'embedding')