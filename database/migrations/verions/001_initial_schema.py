"""
Initial schema - create core tables
Revision ID: 001_initial_schema
Revises: None
Create Date: 2025-07-02 01:10:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # video_metadata
    op.create_table(
        'video_metadata',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('video_id', sa.String(255), unique=True, nullable=False),
        sa.Column('video_path', sa.String(500), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('duration', sa.Float),
        sa.Column('fps', sa.Float),
        sa.Column('resolution', sa.String(50)),
        sa.Column('file_size', sa.Integer),
        sa.Column('processing_status', sa.String(50), server_default='pending'),
        sa.Column('pipeline_id', sa.String(255)),
        sa.Column('overall_quality_score', sa.Float),
        sa.Column('scenes_detected', sa.Integer),
        sa.Column('keyframes_extracted', sa.Boolean, server_default=sa.text('false')),
        sa.Column('features_extracted', sa.Boolean, server_default=sa.text('false')),
        sa.Column('indexed', sa.Boolean, server_default=sa.text('false')),
        sa.Column('uploaded_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('processing_started_at', sa.DateTime),
        sa.Column('processing_completed_at', sa.DateTime),
        sa.Column('video_processing_result', JSON, server_default=sa.text("'{}'")),
        sa.Column('feature_extraction_result', JSON, server_default=sa.text("'{}'")),
        sa.Column('knowledge_graph_result', JSON, server_default=sa.text("'{}'")),
        sa.Column('indexing_result', JSON, server_default=sa.text("'{}'")),
    )

    # user_sessions
    op.create_table(
        'user_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.String(255), unique=True, nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('current_topic', sa.String(500)),
        sa.Column('current_video', sa.String(255)),
        sa.Column('current_timestamp', sa.Float),
        sa.Column('active_entities', JSON, server_default=sa.text("'[]'")),
        sa.Column('mentioned_videos', JSON, server_default=sa.text("'[]'")),
        sa.Column('search_history', JSON, server_default=sa.text("'[]'")),
        sa.Column('user_preferences', JSON, server_default=sa.text("'{}'")),
        sa.Column('start_time', sa.DateTime, server_default=sa.func.now()),
        sa.Column('last_activity', sa.DateTime, server_default=sa.func.now()),
        sa.Column('conversation_turns', sa.Integer, server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('true')),
    )

    # conversation_history
    op.create_table(
        'conversation_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.String(255), nullable=False),
        sa.Column('turn_id', sa.String(255), nullable=False),
        sa.Column('user_message', sa.Text, nullable=False),
        sa.Column('assistant_response', sa.Text, nullable=False),
        sa.Column('intent', sa.String(100)),
        sa.Column('entities', JSON, server_default=sa.text("'[]'")),
        sa.Column('topics', JSON, server_default=sa.text("'[]'")),
        sa.Column('video_references', JSON, server_default=sa.text("'[]'")),
        sa.Column('satisfaction_score', sa.Float),
        sa.Column('resolved', sa.Boolean, server_default=sa.text('false')),
        sa.Column('processing_time', sa.Float, server_default='0'),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
    )

    # processing_jobs
    op.create_table(
        'processing_jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', sa.String(255), unique=True, nullable=False),
        sa.Column('job_type', sa.String(100), nullable=False),
        sa.Column('input_data', JSON, server_default=sa.text("'{}'")),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('progress', sa.Float, server_default='0.0'),
        sa.Column('result_data', JSON, server_default=sa.text("'{}'")),
        sa.Column('error_message', sa.Text),
        sa.Column('total_items', sa.Integer),
        sa.Column('processed_items', sa.Integer, server_default='0'),
        sa.Column('failed_items', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
    )

def downgrade():
    op.drop_table('processing_jobs')
    op.drop_table('conversation_history')
    op.drop_table('user_sessions')
    op.drop_table('video_metadata')