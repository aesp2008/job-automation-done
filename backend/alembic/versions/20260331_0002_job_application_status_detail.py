"""job application status_detail for manual apply fallback

Revision ID: 20260331_0002
Revises: 20260324_0001
Create Date: 2026-03-31
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260331_0002"
down_revision: Union[str, None] = "20260324_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "job_applications",
        sa.Column("status_detail", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("job_applications", "status_detail")
