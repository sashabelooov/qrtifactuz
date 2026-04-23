"""remove halls

Revision ID: 127f61cab0b3
Revises: 3c9430648c8d
Create Date: 2026-04-23 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '127f61cab0b3'
down_revision: Union[str, None] = '3c9430648c8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('ix_exhibits_hall_id', table_name='exhibits')
    op.drop_constraint('exhibits_hall_id_fkey', 'exhibits', type_='foreignkey')
    op.drop_column('exhibits', 'hall_id')
    op.drop_index(op.f('ix_halls_museum_id'), table_name='halls')
    op.drop_table('halls')


def downgrade() -> None:
    op.create_table('halls',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('museum_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('floor', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.String(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.String(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['museum_id'], ['museums.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_halls_museum_id'), 'halls', ['museum_id'], unique=False)
    op.add_column('exhibits', sa.Column('hall_id', sa.UUID(), nullable=True))
    op.create_foreign_key('exhibits_hall_id_fkey', 'exhibits', 'halls', ['hall_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_exhibits_hall_id', 'exhibits', ['hall_id'], unique=False)
