from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, JSON
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Create user_sessions and conversations tables."""
    op.create_table(
        "user_sessions",
        sa.Column("session_id", sa.String, primary_key=True),
        sa.Column("user_id", sa.String, index=True),
        sa.Column("start_time", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_active", sa.DateTime, server_default=sa.func.now())
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("session_id", sa.String, index=True),
        sa.Column("messages", sa.JSON),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now())
    )

def downgrade():
    """Drop user_sessions and conversations tables."""
    op.drop_table("conversations")
    op.drop_table("user_sessions")