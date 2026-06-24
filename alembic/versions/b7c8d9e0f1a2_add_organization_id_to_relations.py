"""add organization_id to relations

Revision ID: b7c8d9e0f1a2
Revises: e44c87f4db91
Create Date: 2026-06-24 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "e44c87f4db91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "relations",
        sa.Column("organization_id", postgresql.UUID(), nullable=True),
    )
    op.execute(
        """
        UPDATE relations r
        SET organization_id = a.organization_id
        FROM assets a
        WHERE r.from_id = a.id
        """
    )
    op.alter_column("relations", "organization_id", nullable=False)
    op.create_foreign_key(
        "fk_relations_organization_id",
        "relations",
        "organizations",
        ["organization_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_relations_organization_id", "relations", type_="foreignkey")
    op.drop_column("relations", "organization_id")
