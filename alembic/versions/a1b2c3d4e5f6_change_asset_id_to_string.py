"""change asset id to string

Revision ID: a1b2c3d4e5f6
Revises: e6d7ed38c059
Create Date: 2026-06-24 14:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e6d7ed38c059"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("relations")

    op.alter_column(
        "assets",
        "id",
        existing_type=postgresql.UUID(),
        type_=sa.String(length=255),
        existing_nullable=False,
        postgresql_using="id::text",
    )

    relation_type = postgresql.ENUM(
        "PARENT",
        "COVERS",
        "DETECTED_ON",
        "RESOLVES_TO",
        "RESOLVED_FROM",
        "RUNS_ON",
        name="relationtype",
        create_type=False,
    )
    relation_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "relations",
        sa.Column("from_id", sa.String(length=255), nullable=False),
        sa.Column("to_id", sa.String(length=255), nullable=False),
        sa.Column("type", relation_type, nullable=False),
        sa.ForeignKeyConstraint(["from_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_id"], ["assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("from_id", "to_id", "type"),
    )


def downgrade() -> None:
    op.drop_table("relations")

    op.alter_column(
        "assets",
        "id",
        existing_type=sa.String(length=255),
        type_=postgresql.UUID(),
        existing_nullable=False,
        postgresql_using="id::uuid",
    )

    relation_type = postgresql.ENUM(
        "PARENT",
        "COVERS",
        "DETECTED_ON",
        "RESOLVES_TO",
        "RESOLVED_FROM",
        "RUNS_ON",
        name="relationtype",
        create_type=False,
    )

    op.create_table(
        "relations",
        sa.Column("from_id", postgresql.UUID(), nullable=False),
        sa.Column("to_id", postgresql.UUID(), nullable=False),
        sa.Column("type", relation_type, nullable=False),
        sa.ForeignKeyConstraint(["from_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["to_id"], ["assets.id"]),
        sa.PrimaryKeyConstraint("from_id", "to_id", "type"),
    )
