"""add content column to table

Revision ID: 790d8ac6b4d4
Revises: aa0babb4cf16
Create Date: 2021-11-11 01:48:01.781170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '790d8ac6b4d4'
down_revision = 'aa0babb4cf16'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
