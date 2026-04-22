"""Waitlist table — collects emails from landing page before launch.

Revision ID: 002
Revises: 001
Create Date: 2026-04-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "waitlist",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),  # Nth to join
        sa.Column("source", sa.String(length=64), nullable=True),  # utm_source
        sa.Column("referrer", sa.String(length=512), nullable=True),  # document.referrer
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "converted_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "welcome_email_sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_waitlist_email", "waitlist", ["email"], unique=True)
    op.create_index("ix_waitlist_position", "waitlist", ["position"])
    op.create_index("ix_waitlist_created_at", "waitlist", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_waitlist_created_at", table_name="waitlist")
    op.drop_index("ix_waitlist_position", table_name="waitlist")
    op.drop_index("ix_waitlist_email", table_name="waitlist")
    op.drop_table("waitlist")
