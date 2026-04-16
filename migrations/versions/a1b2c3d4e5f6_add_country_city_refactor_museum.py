"""add country city refactor museum

Revision ID: a1b2c3d4e5f6
Revises: b0d5b2085f6a
Create Date: 2026-04-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a1b2c3d4e5f6'
down_revision = '81ade7fee947'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'countries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('code', sa.String(3), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'cities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('country_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('countries.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.add_column('museums', sa.Column('city_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cities.id', ondelete='SET NULL'), nullable=True, index=True))
    op.drop_column('museums', 'city')
    op.drop_column('museums', 'country')


def downgrade() -> None:
    op.add_column('museums', sa.Column('country', sa.String(100), nullable=True, server_default='Uzbekistan'))
    op.add_column('museums', sa.Column('city', sa.String(100), nullable=True))
    op.drop_column('museums', 'city_id')
    op.drop_table('cities')
    op.drop_table('countries')
