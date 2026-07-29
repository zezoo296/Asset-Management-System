"""add import jobs

Revision ID: c9d4e1f7a2b3
Revises: 27271cad6594
Create Date: 2026-07-29 17:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "c9d4e1f7a2b3"
down_revision: Union[str, Sequence[str], None] = "27271cad6594"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    importjobstatus = postgresql.ENUM(
        "PENDING",
        "RUNNING",
        "SUCCESS",
        "FAILED",
        name="importjobstatus",
        create_type=False,
    )
    importjobstatus.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "import_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("celery_task_id", sa.String(length=255), nullable=True),
        sa.Column("status", importjobstatus, nullable=False),
        sa.Column("processed_rows", sa.Integer(), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("created_count", sa.Integer(), nullable=False),
        sa.Column("updated_count", sa.Integer(), nullable=False),
        sa.Column("relationships_created_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("import_jobs")
    sa.Enum(name="importjobstatus").drop(op.get_bind(), checkfirst=True)
