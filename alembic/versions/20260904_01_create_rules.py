"""create rules table"""
from alembic import op
import sqlalchemy as sa

revision = "20260904_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword", sa.String(255), nullable=False),
        sa.Column("match_type", sa.String(20), nullable=False),
        sa.Column("action_type", sa.String(20), nullable=False),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("label", sa.String(100), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("case_sensitive", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("match_type IN ('contains','startsWith','exact')", name="ck_rules_match_type"),
        sa.CheckConstraint("action_type IN ('highlight','tooltip')", name="ck_rules_action_type"),
        sa.CheckConstraint("priority >= 0 AND priority <= 100", name="ck_rules_priority"),
    )
    op.create_index("ix_rules_enabled_priority", "rules", ["enabled", "priority"])


def downgrade() -> None:
    op.drop_index("ix_rules_enabled_priority", table_name="rules")
    op.drop_table("rules")

