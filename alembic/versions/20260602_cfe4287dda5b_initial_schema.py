"""initial_schema

Revision ID: cfe4287dda5b
Revises: 
Create Date: 2026-06-02 22:13:50.246792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfe4287dda5b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'youth_centers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('wilaya', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('languages', sa.String(), nullable=False, server_default='fr'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_youthcenter_wilaya', 'youth_centers', ['wilaya'])
    op.create_index('ix_youthcenter_is_active', 'youth_centers', ['is_active'])

    op.create_table(
        'programs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('center_id', sa.Integer(), sa.ForeignKey('youth_centers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_program_center_id', 'programs', ['center_id'])
    op.create_index('ix_program_category', 'programs', ['category'])
    op.create_index('ix_program_language', 'programs', ['language'])
    op.create_index('ix_program_is_active', 'programs', ['is_active'])

    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='editor'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_table(
        'query_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('query_text', sa.String(), nullable=False),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('wilaya_filter', sa.String(), nullable=True),
        sa.Column('cache_hit', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_querylog_created_at', 'query_logs', ['created_at'])
    op.create_index('ix_querylog_cache_hit', 'query_logs', ['cache_hit'])


def downgrade() -> None:
    op.drop_index('ix_querylog_cache_hit', table_name='query_logs')
    op.drop_index('ix_querylog_created_at', table_name='query_logs')
    op.drop_table('query_logs')

    op.drop_table('admin_users')

    op.drop_index('ix_program_is_active', table_name='programs')
    op.drop_index('ix_program_language', table_name='programs')
    op.drop_index('ix_program_category', table_name='programs')
    op.drop_index('ix_program_center_id', table_name='programs')
    op.drop_table('programs')

    op.drop_index('ix_youthcenter_is_active', table_name='youth_centers')
    op.drop_index('ix_youthcenter_wilaya', table_name='youth_centers')
    op.drop_table('youth_centers')
