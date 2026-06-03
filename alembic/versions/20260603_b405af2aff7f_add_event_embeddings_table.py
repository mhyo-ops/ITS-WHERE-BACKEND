"""add event_embeddings table

Revision ID: b405af2aff7f
Revises: 23cfb882c0db
Create Date: 2026-06-03 10:36:43.042440

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = 'b405af2aff7f'
down_revision = '23cfb882c0db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'event_embeddings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('event_id', sa.Integer,
            sa.ForeignKey('events.id', ondelete='CASCADE'),
            nullable=False, unique=True),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
            server_default=sa.func.now())
    )
    op.create_index(
        'ix_event_embeddings_event_id',
        'event_embeddings', ['event_id']
    )


def downgrade() -> None:
    op.drop_table('event_embeddings')
