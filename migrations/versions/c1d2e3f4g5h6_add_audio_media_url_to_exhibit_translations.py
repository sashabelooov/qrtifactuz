"""add audio_url and media_url to exhibit_translations

Revision ID: c1d2e3f4g5h6
Revises: 81ade7fee947
Create Date: 2026-04-22

"""
from alembic import op
import sqlalchemy as sa

revision = 'c1d2e3f4g5h6'
down_revision = '81ade7fee947'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('exhibit_translations', sa.Column('audio_url', sa.String(500), nullable=True))
    op.add_column('exhibit_translations', sa.Column('media_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('exhibit_translations', 'media_url')
    op.drop_column('exhibit_translations', 'audio_url')
