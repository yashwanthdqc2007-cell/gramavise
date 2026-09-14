"""immutable_analysis_snapshots

Revision ID: 0002_immutable_analysis_snapshots
Revises: 0001_initial_schema
Create Date: 2026-09-12 23:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_immutable_analysis_snapshots"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create financial_input_snapshots table
    op.create_table(
        "financial_input_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("own_capital", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("desired_loan", sa.Float(), nullable=True),
        sa.Column("startup_cost", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("equipment_cost", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("inventory_cost", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("monthly_fixed_cost", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("customers_per_day", sa.Integer(), server_default="0", nullable=False),
        sa.Column("avg_ticket_price", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("working_days_per_month", sa.Integer(), server_default="26", nullable=False),
        sa.Column("variable_cost_pct", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("interest_rate_pct", sa.Float(), server_default="10.0", nullable=False),
        sa.Column("loan_tenure_months", sa.Integer(), server_default="36", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("analysis_id"),
    )
    op.create_index("ix_financial_input_snapshots_analysis_id", "financial_input_snapshots", ["analysis_id"], unique=True)

    # 2. Create financial_result_snapshots table
    op.create_table(
        "financial_result_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("total_capex", sa.Float(), nullable=False),
        sa.Column("required_loan_amount", sa.Float(), nullable=False),
        sa.Column("monthly_revenue", sa.Float(), nullable=False),
        sa.Column("monthly_variable_cost", sa.Float(), nullable=False),
        sa.Column("monthly_gross_profit", sa.Float(), nullable=False),
        sa.Column("monthly_fixed_cost", sa.Float(), nullable=False),
        sa.Column("monthly_emi", sa.Float(), nullable=False),
        sa.Column("monthly_net_profit", sa.Float(), nullable=False),
        sa.Column("net_profit_margin_pct", sa.Float(), nullable=False),
        sa.Column("break_even_revenue_monthly", sa.Float(), nullable=False),
        sa.Column("break_even_units_daily", sa.Integer(), nullable=False),
        sa.Column("dscr", sa.Float(), nullable=False),
        sa.Column("is_financially_viable", sa.Boolean(), nullable=False),
        sa.Column("explanations", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("analysis_id"),
    )
    op.create_index("ix_financial_result_snapshots_analysis_id", "financial_result_snapshots", ["analysis_id"], unique=True)

    # 3. Alter analyses table to add snapshot columns & metadata
    with op.batch_alter_table("analyses") as batch_op:
        batch_op.add_column(sa.Column("schema_version", sa.String(length=20), server_default="1.0.0", nullable=False))
        batch_op.add_column(sa.Column("rules_version", sa.String(length=20), server_default="1.0.0", nullable=False))
        batch_op.add_column(sa.Column("overall_verdict", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("business_input_snapshot", sa.JSON(), server_default="{}", nullable=False))
        batch_op.add_column(sa.Column("market_result_snapshot", sa.JSON(), server_default="{}", nullable=False))
        batch_op.add_column(sa.Column("scheme_result_snapshot", sa.JSON(), server_default="{}", nullable=False))
        batch_op.add_column(sa.Column("evidence_ledger_snapshot", sa.JSON(), server_default="[]", nullable=False))
        batch_op.add_column(sa.Column("decision_trace_snapshot", sa.JSON(), server_default="{}", nullable=False))
        batch_op.add_column(sa.Column("action_plan_snapshot", sa.JSON(), server_default="{}", nullable=False))
        batch_op.add_column(sa.Column("bank_readiness_snapshot", sa.JSON(), server_default="{}", nullable=False))
        batch_op.alter_column("business_id", existing_type=sa.String(length=36), nullable=True)
        batch_op.drop_column("financial_result")
        batch_op.drop_column("market_result")
        batch_op.drop_column("scheme_result")


def downgrade() -> None:
    # 1. Revert analyses table changes
    with op.batch_alter_table("analyses") as batch_op:
        batch_op.add_column(sa.Column("scheme_result", sa.JSON(), server_default="{}", nullable=False))
        batch_op.add_column(sa.Column("market_result", sa.JSON(), server_default="{}", nullable=False))
        batch_op.add_column(sa.Column("financial_result", sa.JSON(), server_default="{}", nullable=False))
        batch_op.alter_column("business_id", existing_type=sa.String(length=36), nullable=False)
        batch_op.drop_column("bank_readiness_snapshot")
        batch_op.drop_column("action_plan_snapshot")
        batch_op.drop_column("decision_trace_snapshot")
        batch_op.drop_column("evidence_ledger_snapshot")
        batch_op.drop_column("scheme_result_snapshot")
        batch_op.drop_column("market_result_snapshot")
        batch_op.drop_column("business_input_snapshot")
        batch_op.drop_column("overall_verdict")
        batch_op.drop_column("rules_version")
        batch_op.drop_column("schema_version")

    # 2. Drop financial snapshot tables
    op.drop_index("ix_financial_result_snapshots_analysis_id", table_name="financial_result_snapshots")
    op.drop_table("financial_result_snapshots")
    op.drop_index("ix_financial_input_snapshots_analysis_id", table_name="financial_input_snapshots")
    op.drop_table("financial_input_snapshots")
