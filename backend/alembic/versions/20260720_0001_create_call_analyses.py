"""create call analyses

Revision ID: 20260720_0001
Revises:
Create Date: 2026-07-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "call_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("crm_activity_id", sa.String(), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("lead_score", sa.Integer(), nullable=True),
        sa.Column("agent_performance", sa.String(), nullable=True),
        sa.Column("strengths", sa.JSON(), nullable=True),
        sa.Column("weaknesses", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_call_analyses_crm_activity_id"),
        "call_analyses",
        ["crm_activity_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_call_analyses_id"),
        "call_analyses",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_call_analyses_id"), table_name="call_analyses")
    op.drop_index(
        op.f("ix_call_analyses_crm_activity_id"), table_name="call_analyses"
    )
    op.drop_table("call_analyses")
