"""add insult_tags, tag_id on insults, comment_stars, insult_likes

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tables = insp.get_table_names()

    if "insult_tags" not in tables:
        op.create_table(
            "insult_tags",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(80), nullable=False),
        )
        op.create_index("ix_insult_tags_name", "insult_tags", ["name"], unique=True)

    if "insults" in tables:
        cols = [c["name"] for c in insp.get_columns("insults")]
        if "tag_id" not in cols:
            op.add_column("insults", sa.Column("tag_id", sa.Integer(), nullable=True))
        fks = [fk["name"] for fk in insp.get_foreign_keys("insults")]
        if "fk_insults_tag_id_insult_tags" not in fks:
            op.create_foreign_key(
                "fk_insults_tag_id_insult_tags",
                "insults",
                "insult_tags",
                ["tag_id"],
                ["id"],
            )

    if "comment_stars" not in tables:
        op.create_table(
            "comment_stars",
            sa.Column("comment_id", sa.Integer(), sa.ForeignKey("insult_comments.id"), primary_key=True),
            sa.Column("user_id", sa.String(255), sa.ForeignKey("users.id"), primary_key=True),
        )

    if "insult_likes" not in tables:
        op.create_table(
            "insult_likes",
            sa.Column("insult_id", sa.Integer(), sa.ForeignKey("insults.id"), primary_key=True),
            sa.Column("user_id", sa.String(255), sa.ForeignKey("users.id"), primary_key=True),
        )


def downgrade() -> None:
    op.drop_table("insult_likes")
    op.drop_table("comment_stars")
    op.drop_constraint("fk_insults_tag_id_insult_tags", "insults", type_="foreignkey")
    op.drop_column("insults", "tag_id")
    op.drop_index("ix_insult_tags_name", "insult_tags")
    op.drop_table("insult_tags")
