"""likes en comentarios de insulto (quitar likes de insultos)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear comment_likes (like por usuario por comentario)
    bind = op.get_bind()
    insp = inspect(bind)
    tables = insp.get_table_names()
    if "comment_likes" not in tables:
        op.create_table(
            "comment_likes",
            sa.Column("comment_id", sa.Integer(), sa.ForeignKey("insult_comments.id"), primary_key=True),
            sa.Column("user_id", sa.String(255), sa.ForeignKey("users.id"), primary_key=True),
        )
    # Eliminar insult_likes (los likes ya no son por insulto sino por comentario)
    if "insult_likes" in tables:
        op.drop_table("insult_likes")


def downgrade() -> None:
    op.drop_table("comment_likes")
    op.create_table(
        "insult_likes",
        sa.Column("insult_id", sa.Integer(), sa.ForeignKey("insults.id"), primary_key=True),
        sa.Column("user_id", sa.String(255), sa.ForeignKey("users.id"), primary_key=True),
    )
