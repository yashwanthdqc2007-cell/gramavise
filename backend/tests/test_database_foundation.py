"""Phase 6A Database Foundation & Alembic Migration Test Suite.

Verifies:
- Test A: SQLite database initialization, session lifecycle, and query execution.
- Test B: Alembic metadata discovery and table registration.
- Test C: Alembic migration execution consistency (upgrade -> downgrade -> upgrade).
- Test D: Model import completeness in Base.metadata.
- Test E: PostgreSQL dialect compatibility of schemas and types.
"""
import os
import uuid
import pytest
from sqlalchemy import create_engine, inspect, text, select
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from app.database import Base, init_db, get_db
import app.models as models
from app.models import (
    User,
    BusinessProfile,
    FinancialAssumption,
    LocalEvidence,
    Scheme,
    Analysis,
    EvidenceTypeEnum,
    RecommendationStatusEnum,
)


EXPECTED_TABLES = {
    "users",
    "business_profiles",
    "financial_assumptions",
    "local_evidence",
    "schemes",
    "scheme_versions",
    "analyses",
    "financial_input_snapshots",
    "financial_result_snapshots",
    "scenario_records",
    "idempotency_records",
}



def test_sqlite_connection_and_session(tmp_path):
    """Test A: SQLite database can initialize via init_db, open a session, query, and close cleanly."""
    db_file = tmp_path / "test_foundation.db"
    test_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    
    # 1. Initialize schema
    init_db(target_engine=test_engine)
    
    # 2. Verify tables exist
    inspector = inspect(test_engine)
    created_tables = set(inspector.get_table_names())
    for expected in EXPECTED_TABLES:
        assert expected in created_tables, f"Table {expected} missing from initialized SQLite schema"
        
    # 3. Open session and perform basic operations
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        # Create a test user
        user = User(
            id=str(uuid.uuid4()),
            phone_number="+919876543210",
            full_name="Ramesh Patel",
            preferred_language="hi"
        )
        session.add(user)
        session.commit()
        
        # Query back
        stmt = select(User).where(User.phone_number == "+919876543210")
        fetched_user = session.scalar(stmt)
        assert fetched_user is not None
        assert fetched_user.full_name == "Ramesh Patel"
        assert fetched_user.preferred_language == "hi"
    finally:
        session.close()
        test_engine.dispose()


def test_alembic_metadata_discovery():
    """Test B: Alembic metadata discovers all application models."""
    assert len(Base.metadata.tables) >= len(EXPECTED_TABLES)
    for table_name in EXPECTED_TABLES:
        assert table_name in Base.metadata.tables, f"Table {table_name} not found in Base.metadata"


def test_alembic_migration_upgrade_downgrade_cycle(tmp_path):
    """Test C: Alembic migration 0001_initial_schema supports upgrade -> downgrade -> upgrade cleanly."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
    
    db_file = tmp_path / "test_alembic_migration.db"
    db_url = f"sqlite:///{db_file}"
    
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
    
    test_engine = create_engine(db_url)
    
    try:
        # 1. First Upgrade
        command.upgrade(alembic_cfg, "head")
        inspector = inspect(test_engine)
        tables_after_upgrade = set(inspector.get_table_names())
        for expected in EXPECTED_TABLES:
            assert expected in tables_after_upgrade, f"Table {expected} missing after migration upgrade"
        assert "alembic_version" in tables_after_upgrade
        
        # 2. Downgrade to base
        command.downgrade(alembic_cfg, "base")
        inspector = inspect(test_engine)
        tables_after_downgrade = set(inspector.get_table_names())
        for expected in EXPECTED_TABLES:
            assert expected not in tables_after_downgrade, f"Table {expected} still present after downgrade"
            
        # 3. Second Upgrade (Re-apply)
        command.upgrade(alembic_cfg, "head")
        inspector = inspect(test_engine)
        tables_after_reupgrade = set(inspector.get_table_names())
        for expected in EXPECTED_TABLES:
            assert expected in tables_after_reupgrade, f"Table {expected} missing after migration re-upgrade"
    finally:
        test_engine.dispose()


def test_model_import_completeness():
    """Test D: All intended models are registered in Base.metadata with proper foreign keys."""
    # Check all model classes exist in app.models
    assert hasattr(models, "User")
    assert hasattr(models, "BusinessProfile")
    assert hasattr(models, "FinancialAssumption")
    assert hasattr(models, "LocalEvidence")
    assert hasattr(models, "Scheme")
    assert hasattr(models, "Analysis")
    
    # Check foreign keys in metadata
    bp_table = Base.metadata.tables["business_profiles"]
    bp_fks = {fk.target_fullname for fk in bp_table.foreign_keys}
    assert "users.id" in bp_fks
    
    fa_table = Base.metadata.tables["financial_assumptions"]
    fa_fks = {fk.target_fullname for fk in fa_table.foreign_keys}
    assert "business_profiles.id" in fa_fks
    
    ev_table = Base.metadata.tables["local_evidence"]
    ev_fks = {fk.target_fullname for fk in ev_table.foreign_keys}
    assert "business_profiles.id" in ev_fks
    
    an_table = Base.metadata.tables["analyses"]
    an_fks = {fk.target_fullname for fk in an_table.foreign_keys}
    assert "business_profiles.id" in an_fks

    fis_table = Base.metadata.tables["financial_input_snapshots"]
    fis_fks = {fk.target_fullname for fk in fis_table.foreign_keys}
    assert "analyses.id" in fis_fks

    frs_table = Base.metadata.tables["financial_result_snapshots"]
    frs_fks = {fk.target_fullname for fk in frs_table.foreign_keys}
    assert "analyses.id" in frs_fks


def test_postgresql_compatibility_compilation():
    """Test E: Model definitions and JSON column types compile cleanly against PostgreSQL dialect."""
    from sqlalchemy.dialects import postgresql
    from sqlalchemy.schema import CreateTable
    
    # Verify create table statements compile for all registered tables under postgresql dialect
    for table_name, table in Base.metadata.tables.items():
        ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        assert f"CREATE TABLE {table_name}" in ddl or f'CREATE TABLE "{table_name}"' in ddl, (
            f"Table {table_name} failed PostgreSQL DDL compilation: {ddl}"
        )
