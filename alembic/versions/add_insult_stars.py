"""add insult_stars (estrellita por usuario por insulto)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tables = insp.get_table_names()
    if "insult_stars" not in tables:
        op.create_table(
            "insult_stars",
            sa.Column("insult_id", sa.Integer(), sa.ForeignKey("insults.id"), primary_key=True),
            sa.Column("user_id", sa.String(255), sa.ForeignKey("users.id"), primary_key=True),
        )


def downgrade() -> None:
    op.drop_table("insult_stars")
