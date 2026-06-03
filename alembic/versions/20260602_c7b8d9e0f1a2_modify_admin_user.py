"""modify_admin_user

Revision ID: c7b8d9e0f1a2
Revises: cfe4287dda5b
Create Date: 2026-06-02 23:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7b8d9e0f1a2'
down_revision = 'cfe4287dda5b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add admin_slug column as nullable first
    op.add_column('admin_users', sa.Column('admin_slug', sa.String(), nullable=True))

    # 2. Copy username values to admin_slug for existing records
    op.execute("UPDATE admin_users SET admin_slug = username")

    # 3. Alter admin_slug to be non-nullable
    op.alter_column('admin_users', 'admin_slug', nullable=False)

    # 4. Create unique index for admin_slug
    op.create_index('ix_admin_users_admin_slug', 'admin_users', ['admin_slug'], unique=True)

    # 5. Drop role column
    op.drop_column('admin_users', 'role')

    # 6. Drop username column
    op.drop_column('admin_users', 'username')

    # 7. Add last_login column
    op.add_column('admin_users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('admin_users', 'last_login')
    
    # Re-add username as nullable first
    op.add_column('admin_users', sa.Column('username', sa.String(), nullable=True))
    # Copy admin_slug back to username
    op.execute("UPDATE admin_users SET username = admin_slug")
    # Make username non-nullable
    op.alter_column('admin_users', 'username', nullable=False)
    op.create_unique_constraint('admin_users_username_key', 'admin_users', ['username'])
    
    # Drop index and admin_slug column
    op.drop_index('ix_admin_users_admin_slug', table_name='admin_users')
    op.drop_column('admin_users', 'admin_slug')
    
    # Re-add role column
    op.add_column('admin_users', sa.Column('role', sa.String(), nullable=False, server_default='editor'))
