"""Initial database schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-12-08 00:00:00.000000

Creates initial tables:
- users: User accounts with authentication
- tasks: Todo items with status and priority
- task_shares: Shared task permissions
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    # Create indexes on users table
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_is_active', 'users', ['is_active'])

    # Create task status and priority enums
    task_status_enum = postgresql.ENUM('pending', 'in_progress', 'completed', name='taskstatus')
    task_status_enum.create(op.get_bind())

    task_priority_enum = postgresql.ENUM('low', 'medium', 'high', 'urgent', name='taskpriority')
    task_priority_enum.create(op.get_bind())

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', name='taskstatus'),
                  nullable=False, server_default='pending'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='taskpriority'),
                  nullable=False, server_default='medium'),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ai_priority', sa.Enum('low', 'medium', 'high', 'urgent', name='taskpriority'),
                  nullable=True),
        sa.Column('ai_estimated_duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create indexes on tasks table
    op.create_index('idx_task_owner_id', 'tasks', ['owner_id'])
    op.create_index('idx_task_status', 'tasks', ['status'])
    op.create_index('idx_task_deadline', 'tasks', ['deadline'])
    op.create_index('idx_task_owner_status', 'tasks', ['owner_id', 'status'])
    op.create_index('idx_task_created_at', 'tasks', ['created_at'])

    # Create share_role enum
    share_role_enum = postgresql.ENUM('viewer', 'editor', name='sharerole')
    share_role_enum.create(op.get_bind())

    # Create task_shares table
    op.create_table(
        'task_shares',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('viewer', 'editor', name='sharerole'),
                  nullable=False, server_default='viewer'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('shared_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create indexes on task_shares table
    op.create_index('idx_task_share_task_id', 'task_shares', ['task_id'])
    op.create_index('idx_task_share_user_id', 'task_shares', ['user_id'])
    op.create_index('idx_task_share_created_by', 'task_shares', ['created_by'])
    op.create_index('idx_task_share_task_user', 'task_shares', ['task_id', 'user_id'])


def downgrade() -> None:
    """Drop initial database schema."""

    # Drop task_shares table and indexes
    op.drop_index('idx_task_share_task_user', 'task_shares')
    op.drop_index('idx_task_share_created_by', 'task_shares')
    op.drop_index('idx_task_share_user_id', 'task_shares')
    op.drop_index('idx_task_share_task_id', 'task_shares')
    op.drop_table('task_shares')

    # Drop tasks table and indexes
    op.drop_index('idx_task_created_at', 'tasks')
    op.drop_index('idx_task_owner_status', 'tasks')
    op.drop_index('idx_task_deadline', 'tasks')
    op.drop_index('idx_task_status', 'tasks')
    op.drop_index('idx_task_owner_id', 'tasks')
    op.drop_table('tasks')

    # Drop users table and indexes
    op.drop_index('idx_user_is_active', 'users')
    op.drop_index('idx_user_email', 'users')
    op.drop_table('users')

    # Drop enums
    sa.Enum(name='sharerole').drop(op.get_bind())
    sa.Enum(name='taskpriority').drop(op.get_bind())
    sa.Enum(name='taskstatus').drop(op.get_bind())
