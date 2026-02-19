"""add is_active to words, word_examples, insults, insult_examples

Revision ID: a1b2c3d4e5f6
Revises: efdf3b7a88d0
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'efdf3b7a88d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('words', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('word_examples', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('insults', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('insult_examples', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('insult_examples', 'is_active')
    op.drop_column('insults', 'is_active')
    op.drop_column('word_examples', 'is_active')
    op.drop_column('words', 'is_active')
