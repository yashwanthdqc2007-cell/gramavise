"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-12 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=True),
        sa.Column("preferred_language", sa.String(length=10), server_default="en", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_phone_number", "users", ["phone_number"], unique=True)

    # 2. business_profiles table
    op.create_table(
        "business_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("business_name", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("village", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("experience_years", sa.Integer(), server_default="0", nullable=False),
        sa.Column("own_capital", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("desired_loan", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("is_new_business", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_business_profiles_user_id", "business_profiles", ["user_id"], unique=False)

    # 3. financial_assumptions table
    op.create_table(
        "financial_assumptions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("business_id", sa.String(length=36), nullable=False),
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
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["business_id"], ["business_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_financial_assumptions_business_id", "financial_assumptions", ["business_id"], unique=False)

    # 4. local_evidence table
    op.create_table(
        "local_evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("business_id", sa.String(length=36), nullable=False),
        sa.Column("indicator", sa.String(length=150), nullable=False),
        sa.Column("value", sa.String(length=150), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column(
            "evidence_type",
            sa.Enum("OBSERVED", "CALCULATED", "MODELLED", "ASSUMED", "NEEDS_VERIFICATION", name="evidencetypeenum"),
            nullable=False,
        ),
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("source", sa.String(length=150), nullable=True),
        sa.Column("source_url", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_local_evidence_business_id", "local_evidence", ["business_id"], unique=False)

    # 5. schemes table
    op.create_table(
        "schemes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scheme_code", sa.String(length=50), nullable=False),
        sa.Column("scheme_name", sa.String(length=255), nullable=False),
        sa.Column("ministry_or_dept", sa.String(length=255), nullable=True),
        sa.Column("max_loan_amount", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("subsidy_percentage_general", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("subsidy_percentage_special", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("interest_subvention_pct", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("eligibility_criteria", sa.JSON(), nullable=False),
        sa.Column("required_documents", sa.JSON(), nullable=False),
        sa.Column("official_portal_url", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_schemes_scheme_code", "schemes", ["scheme_code"], unique=True)

    # 6. analyses table
    op.create_table(
        "analyses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("business_id", sa.String(length=36), nullable=False),
        sa.Column(
            "recommendation_status",
            sa.Enum("PROCEED", "VALIDATE_FIRST", "RECONSIDER", name="recommendationstatusenum"),
            nullable=False,
        ),
        sa.Column("confidence_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("financial_result", sa.JSON(), nullable=False),
        sa.Column("market_result", sa.JSON(), nullable=False),
        sa.Column("scheme_result", sa.JSON(), nullable=False),
        sa.Column("risk_factors", sa.JSON(), nullable=False),
        sa.Column("ai_explanation", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["business_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analyses_business_id", "analyses", ["business_id"], unique=False)


def downgrade() -> None:
    op.drop_table("analyses")
    op.drop_table("schemes")
    op.drop_table("local_evidence")
    op.drop_table("financial_assumptions")
    op.drop_table("business_profiles")
    op.drop_table("users")
    
    # Drop enum types in PostgreSQL if present
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="evidencetypeenum").drop(bind, checkfirst=True)
        sa.Enum(name="recommendationstatusenum").drop(bind, checkfirst=True)
