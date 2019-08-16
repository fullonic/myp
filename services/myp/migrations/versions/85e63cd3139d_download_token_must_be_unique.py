"""download token must be unique.

Revision ID: 85e63cd3139d
Revises: cffc723ae91d
Create Date: 2019-08-16 18:54:38.108841

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85e63cd3139d'
down_revision = 'cffc723ae91d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'download', ['token'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'download', type_='unique')
    # ### end Alembic commands ###
