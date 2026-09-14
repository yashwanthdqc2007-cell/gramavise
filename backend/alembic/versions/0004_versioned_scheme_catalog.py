"""versioned_scheme_catalog

Revision ID: 0004_versioned_scheme_catalog
Revises: 0003_scenario_records
Create Date: 2026-09-12 23:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_versioned_scheme_catalog"
down_revision: Union[str, None] = "0003_scenario_records"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns to schemes table if not present
    with op.batch_alter_table("schemes") as batch_op:
        batch_op.add_column(sa.Column("ministry", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("department", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))

    # 2. Create scheme_versions table
    op.create_table(
        "scheme_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scheme_id", sa.String(length=36), nullable=False),
        sa.Column("scheme_code", sa.String(length=50), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "ACTIVE", "SUPERSEDED", "RETIRED", name="schemestatusenum"),
            server_default="ACTIVE",
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("official_source_name", sa.String(length=255), nullable=True),
        sa.Column("official_portal_url", sa.String(length=255), nullable=True),
        sa.Column("source_publication_date", sa.String(length=50), nullable=True),
        sa.Column("effective_from", sa.DateTime(), nullable=True),
        sa.Column("effective_to", sa.DateTime(), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(), nullable=False),
        sa.Column("max_loan_amount", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("subsidy_percentage_general", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("subsidy_percentage_special", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("beneficiary_contribution_general_pct", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("beneficiary_contribution_special_pct", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("interest_subvention_pct", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("eligibility_criteria", sa.JSON(), nullable=False),
        sa.Column("required_documents", sa.JSON(), nullable=False),
        sa.Column("verification_notes", sa.JSON(), nullable=False),
        sa.Column("metadata_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["scheme_id"], ["schemes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scheme_code", "version", name="uq_scheme_version"),
    )
    op.create_index("ix_scheme_versions_scheme_id", "scheme_versions", ["scheme_id"], unique=False)
    op.create_index("ix_scheme_versions_scheme_code", "scheme_versions", ["scheme_code"], unique=False)
    op.create_index("ix_scheme_versions_status", "scheme_versions", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scheme_versions_status", table_name="scheme_versions")
    op.drop_index("ix_scheme_versions_scheme_code", table_name="scheme_versions")
    op.drop_index("ix_scheme_versions_scheme_id", table_name="scheme_versions")
    op.drop_table("scheme_versions")

    with op.batch_alter_table("schemes") as batch_op:
        batch_op.drop_column("description")
        batch_op.drop_column("department")
        batch_op.drop_column("ministry")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="schemestatusenum").drop(bind, checkfirst=True)
