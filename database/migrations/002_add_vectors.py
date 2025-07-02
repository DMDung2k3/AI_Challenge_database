from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add vector support to video_metadata."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("video_metadata", sa.Column("embedding", sa.dialects.postgresql.VECTOR(384)))

def downgrade():
    """Remove vector column."""
    op.drop_column("video_metadata", "embedding")