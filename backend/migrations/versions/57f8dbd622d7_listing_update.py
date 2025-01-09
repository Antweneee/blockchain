"""listing update

Revision ID: 57f8dbd622d7
Revises: fa35054c23ca
Create Date: 2025-01-07 13:11:17.966193

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57f8dbd622d7'
down_revision = 'fa35054c23ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('listings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('offer_id', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('listings', schema=None) as batch_op:
        batch_op.drop_column('offer_id')

    # ### end Alembic commands ###