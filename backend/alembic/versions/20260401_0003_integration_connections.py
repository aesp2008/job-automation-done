"""integration_connections for RSS and future OAuth metadata

Revision ID: 20260401_0003
Revises: 20260331_0002
Create Date: 2026-04-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260401_0003"
down_revision: Union[str, None] = "20260331_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "integration_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "provider", name="uq_integration_user_provider"),
    )
    op.create_index(op.f("ix_integration_connections_id"), "integration_connections", ["id"], unique=False)
    op.create_index(
        op.f("ix_integration_connections_user_id"),
        "integration_connections",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_integration_connections_user_id"), table_name="integration_connections")
    op.drop_index(op.f("ix_integration_connections_id"), table_name="integration_connections")
    op.drop_table("integration_connections")
