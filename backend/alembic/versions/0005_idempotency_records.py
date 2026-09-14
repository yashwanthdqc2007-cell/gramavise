"""idempotency_records

Revision ID: 0005_idempotency_records
Revises: 0004_versioned_scheme_catalog
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005_idempotency_records"
down_revision: Union[str, None] = "0004_versioned_scheme_catalog"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("scope", sa.String(length=50), nullable=False),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="COMPLETED", nullable=False),
        sa.Column("response_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "scope", name="uq_idempotency_key_scope"),
    )
    op.create_index("ix_idempotency_records_key", "idempotency_records", ["key"], unique=False)
    op.create_index("ix_idempotency_records_scope", "idempotency_records", ["scope"], unique=False)
    op.create_index("ix_idempotency_records_resource_id", "idempotency_records", ["resource_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_idempotency_records_resource_id", table_name="idempotency_records")
    op.drop_index("ix_idempotency_records_scope", table_name="idempotency_records")
    op.drop_index("ix_idempotency_records_key", table_name="idempotency_records")
    op.drop_table("idempotency_records")
