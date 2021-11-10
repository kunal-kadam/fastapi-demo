"""add foriegn key to post table

Revision ID: 249b3a8255ea
Revises: e852f2766f0d
Create Date: 2021-11-11 01:58:26.290950

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import null


# revision identifiers, used by Alembic.
revision = '249b3a8255ea'
down_revision = 'e852f2766f0d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_user_fkey', source_table="posts", referent_table="users",
    local_cols=['owner_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint('post_user_fkey', table_name="posts")
    op.drop_column('posts', 'owner_id')
    pass
