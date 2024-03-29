"""empty message

Revision ID: 0d86c85f3e38
Revises: 6035206527cb
Create Date: 2019-08-16 17:49:17.100544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d86c85f3e38'
down_revision = '6035206527cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('download', sa.Column('project_name', sa.String(length=64), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('download', 'project_name')
    # ### end Alembic commands ###
