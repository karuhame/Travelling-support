"""create tag and destination_tag table

Revision ID: 2e3cd4790002
Revises: 
Create Date: 2024-11-12 00:37:21.941881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '2e3cd4790002'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('destination_tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('destination_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['destination_id'], ['destination.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_destination_tag_id'), 'destination_tag', ['id'], unique=False)
    op.drop_constraint('tag_ibfk_1', 'tag', type_='foreignkey')
    op.drop_column('tag', 'destination_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tag', sa.Column('destination_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('tag_ibfk_1', 'tag', 'destination', ['destination_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_destination_tag_id'), table_name='destination_tag')
    op.drop_table('destination_tag')
    # ### end Alembic commands ###