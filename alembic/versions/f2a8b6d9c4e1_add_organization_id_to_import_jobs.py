"""add organization id to import jobs

Revision ID: f2a8b6d9c4e1
Revises: c9d4e1f7a2b3
Create Date: 2026-07-29 18:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "f2a8b6d9c4e1"
down_revision: Union[str, Sequence[str], None] = "c9d4e1f7a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "import_jobs",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_foreign_key(
        "fk_import_jobs_organization_id",
        "import_jobs",
        "organizations",
        ["organization_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_import_jobs_organization_id"),
        "import_jobs",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_import_jobs_organization_id"), table_name="import_jobs")
    op.drop_constraint("fk_import_jobs_organization_id", "import_jobs", type_="foreignkey")
    op.drop_column("import_jobs", "organization_id")
