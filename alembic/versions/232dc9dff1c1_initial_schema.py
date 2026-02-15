"""initial_schema

Revision ID: 232dc9dff1c1
Revises: 
Create Date: 2026-02-14 23:35:04.256232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '232dc9dff1c1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('language', sa.String(), server_default='uz', nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('is_staff', sa.Boolean(), nullable=True),
        sa.Column('balance', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('is_anipass', sa.Boolean(), nullable=True),
        sa.Column('is_lux', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Media Table
    op.create_table(
        'media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('original_name', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('genre', sa.String(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('dubbing', sa.String(), nullable=True),
        sa.Column('poster_file_id', sa.String(), nullable=True),
        sa.Column('trailer_file_id', sa.String(), nullable=True),
        sa.Column('views', sa.BigInteger(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('is_vip', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_media_code'), 'media', ['code'], unique=True)
    op.create_index(op.f('ix_media_id'), 'media', ['id'], unique=False)
    op.create_index(op.f('ix_media_name'), 'media', ['name'], unique=False)

    # Episodes Table
    op.create_table(
        'episodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('media_id', sa.Integer(), nullable=True),
        sa.Column('episode_number', sa.Integer(), nullable=True),
        sa.Column('episode_file_id', sa.String(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['media_id'], ['media.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_episodes_id'), 'episodes', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_episodes_id'), table_name='episodes')
    op.drop_table('episodes')
    op.drop_index(op.f('ix_media_name'), table_name='media')
    op.drop_index(op.f('ix_media_id'), table_name='media')
    op.drop_index(op.f('ix_media_code'), table_name='media')
    op.drop_table('media')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
