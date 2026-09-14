"""scenario_records

Revision ID: 0003_scenario_records
Revises: 0002_immutable_analysis_snapshots
Create Date: 2026-09-12 23:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003_scenario_records"
down_revision: Union[str, None] = "0002_immutable_analysis_snapshots"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scenario_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=150), server_default="Custom Scenario", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("scenario_inputs", sa.JSON(), nullable=False),
        sa.Column("scenario_financial_result", sa.JSON(), nullable=False),
        sa.Column("scenario_recommendation", sa.JSON(), nullable=False),
        sa.Column("comparison_result", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scenario_records_analysis_id", "scenario_records", ["analysis_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scenario_records_analysis_id", table_name="scenario_records")
    op.drop_table("scenario_records")
