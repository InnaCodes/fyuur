"""empty message

Revision ID: 0793e47f077f
Revises: ee45135d01b3
Create Date: 2022-06-04 18:34:42.495563

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0793e47f077f'
down_revision = 'ee45135d01b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'created_at')
    op.drop_column('Venue', 'created_at')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.add_column('Artist', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###