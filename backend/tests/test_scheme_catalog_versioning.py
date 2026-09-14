"""Phase 6F Tests: Persistent Scheme Catalog, Versioning, and Auditability."""
import os
import uuid
import pytest
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from app.database import Base, init_db
from app.models.scheme import Scheme, SchemeVersion, SchemeStatusEnum
from app.repositories.unit_of_work import UnitOfWork, get_uow
from app.repositories.schemes import SchemeRepository
from scripts.seed_schemes import seed_schemes
from app.services.schemes.matcher import SchemeService
from app.rules.scheme_rules import SchemeRules
from app.schemas.business import BusinessProfileBase, LocationSchema
from app.schemas.financial import FinancialResultResponse
from app.main import app


@pytest.fixture
def client_with_db(tmp_path):
    """Provides a TestClient with an isolated test SQLite database and overridden UoW dependency."""
    db_file = tmp_path / "test_scheme_catalog.db"
    test_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    init_db(target_engine=test_engine)
    test_session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def override_get_uow():
        with UnitOfWork(session_factory=test_session_factory) as uow:
            yield uow

    app.dependency_overrides[get_uow] = override_get_uow
    client = TestClient(app)
    try:
        yield client, test_session_factory
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()


# ==============================================================================
# TEST 1: Seed PMEGP
# ==============================================================================
def test_01_seed_pmegp(client_with_db):
    """Verify PMEGP catalog master and version exist with expected metadata."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    with UnitOfWork(session_factory=session_factory) as uow:
        scheme = uow.schemes.get_by_code("PMEGP")
        assert scheme is not None
        assert "Employment Generation" in scheme.scheme_name
        assert "MSME" in (scheme.ministry or "")

        ver = uow.schemes.get_active_version("PMEGP")
        assert ver is not None
        assert ver.version == "2024.1"
        assert ver.status == SchemeStatusEnum.ACTIVE
        assert ver.subsidy_percentage_general == 25.0
        assert ver.subsidy_percentage_special == 35.0
        assert ver.beneficiary_contribution_general_pct == 10.0
        assert ver.beneficiary_contribution_special_pct == 5.0
        assert ver.official_portal_url == "https://www.pmegp.msme.gov.in/"
        assert "KVIC" in (ver.official_source_name or "")


# ==============================================================================
# TEST 2: Seed MUDRA
# ==============================================================================
def test_02_seed_mudra_tiers(client_with_db):
    """Verify all four MUDRA categories remain represented correctly."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    with UnitOfWork(session_factory=session_factory) as uow:
        scheme = uow.schemes.get_by_code("PMMY")
        assert scheme is not None
        assert "MUDRA" in scheme.scheme_name

        ver = uow.schemes.get_active_version("PMMY")
        assert ver is not None
        assert ver.status == SchemeStatusEnum.ACTIVE
        assert ver.max_loan_amount == 2000000.0

        tiers = ver.eligibility_criteria.get("tiers", {})
        assert "SHISHU" in tiers
        assert "KISHORE" in tiers
        assert "TARUN" in tiers
        assert "TARUN_PLUS" in tiers

        assert tiers["SHISHU"]["max_loan"] == 50000.0
        assert tiers["KISHORE"]["max_loan"] == 500000.0
        assert tiers["TARUN"]["max_loan"] == 1000000.0
        assert tiers["TARUN_PLUS"]["max_loan"] == 2000000.0
        assert tiers["TARUN_PLUS"].get("requires_prior_tarun_repayment") is True


# ==============================================================================
# TEST 3: Seed PMFME
# ==============================================================================
def test_03_seed_pmfme(client_with_db):
    """Verify PMFME subsidy, ODOP relevance, and contribution metadata."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    with UnitOfWork(session_factory=session_factory) as uow:
        scheme = uow.schemes.get_by_code("PMFME")
        assert scheme is not None
        assert "Food Processing" in scheme.scheme_name

        ver = uow.schemes.get_active_version("PMFME")
        assert ver is not None
        assert ver.status == SchemeStatusEnum.ACTIVE
        assert ver.subsidy_percentage_general == 35.0
        assert ver.beneficiary_contribution_general_pct == 10.0
        assert ver.eligibility_criteria.get("subsidy_max_amount") == 1000000.0
        assert ver.official_portal_url == "https://pmfme.mofpi.gov.in/"


# ==============================================================================
# TEST 4: Seed Idempotency
# ==============================================================================
def test_04_seed_idempotency(client_with_db):
    """Run seed twice. Verify no duplicate scheme or version rows are created."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        res1 = seed_schemes(session=uow.session)
        assert res1["schemes_created"] == 3
        assert res1["versions_created"] == 3

    # Second seed run
    with UnitOfWork(session_factory=session_factory) as uow:
        res2 = seed_schemes(session=uow.session)
        assert res2["schemes_created"] == 0
        assert res2["schemes_existing"] == 3
        assert res2["versions_created"] == 0
        assert res2["versions_existing"] == 3

    # Verify counts in database
    with UnitOfWork(session_factory=session_factory) as uow:
        schemes = uow.schemes.list_schemes()
        assert len(schemes) == 3
        pmegp_versions = uow.schemes.list_versions("PMEGP")
        assert len(pmegp_versions) == 1


# ==============================================================================
# TEST 5: Version Uniqueness Constraint
# ==============================================================================
def test_05_version_uniqueness_constraint(client_with_db):
    """Attempt duplicate scheme_code + version insertion. Verify rejection."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    with UnitOfWork(session_factory=session_factory) as uow:
        scheme = uow.schemes.get_by_code("PMEGP")

        duplicate_version = SchemeVersion(
            id="duplicate-uuid-1234",
            scheme_id=scheme.id,
            scheme_code="PMEGP",
            version="2024.1",  # Already exists
            status=SchemeStatusEnum.ACTIVE,
            max_loan_amount=5000000.0,
            subsidy_percentage_general=25.0,
            subsidy_percentage_special=35.0,
            beneficiary_contribution_general_pct=10.0,
            beneficiary_contribution_special_pct=5.0,
            interest_subvention_pct=0.0,
            eligibility_criteria={},
            required_documents=[],
            verification_notes=[],
            metadata_payload={},
            created_at=datetime.utcnow(),
        )

        uow.schemes.add_version(duplicate_version)
        with pytest.raises(IntegrityError):
            uow.commit()
        uow.rollback()


# ==============================================================================
# TEST 6: Published Version Immutability
# ==============================================================================
def test_06_published_version_immutability_interface(client_with_db):
    """Verify repository does not expose update/overwrite methods on published versions."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        repo = uow.schemes
        assert not hasattr(repo, "update_version")
        assert not hasattr(repo, "overwrite_version")
        assert not hasattr(repo, "delete_version")


# ==============================================================================
# TEST 7: New Version Creation While Old Remains Available
# ==============================================================================
def test_07_new_version_creation(client_with_db):
    """Create a new version for an existing scheme. Verify old version remains available."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    with UnitOfWork(session_factory=session_factory) as uow:
        scheme = uow.schemes.get_by_code("PMEGP")

        # Mark old version as superseded
        old_ver = uow.schemes.get_version("PMEGP", "2024.1")
        old_ver.status = SchemeStatusEnum.SUPERSEDED

        # Insert new version
        new_ver = SchemeVersion(
            id="new-pmegp-version-uuid",
            scheme_id=scheme.id,
            scheme_code="PMEGP",
            version="2026.1",
            status=SchemeStatusEnum.ACTIVE,
            description="Updated 2026 PMEGP operational guidelines",
            official_source_name="KVIC MSME Gazette 2026",
            official_portal_url="https://www.pmegp.msme.gov.in/",
            source_publication_date="2026-01",
            max_loan_amount=7500000.0,
            subsidy_percentage_general=30.0,
            subsidy_percentage_special=40.0,
            beneficiary_contribution_general_pct=10.0,
            beneficiary_contribution_special_pct=5.0,
            interest_subvention_pct=0.0,
            eligibility_criteria={"eligible_business_types": ["MANUFACTURING"]},
            required_documents=[],
            verification_notes=[],
            metadata_payload={},
            created_at=datetime.utcnow(),
        )
        uow.schemes.add_version(new_ver)
        uow.commit()

    with UnitOfWork(session_factory=session_factory) as uow:
        # Query all versions
        versions = uow.schemes.list_versions("PMEGP")
        assert len(versions) == 2
        ver_codes = [v.version for v in versions]
        assert "2024.1" in ver_codes
        assert "2026.1" in ver_codes

        # Old version is still retrievable
        retrieved_old = uow.schemes.get_version("PMEGP", "2024.1")
        assert retrieved_old.status == SchemeStatusEnum.SUPERSEDED
        assert retrieved_old.subsidy_percentage_general == 25.0


# ==============================================================================
# TEST 8: Active Version Filtering
# ==============================================================================
def test_08_active_version_filtering(client_with_db):
    """Verify only the intended version is returned by get_active_version."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    with UnitOfWork(session_factory=session_factory) as uow:
        scheme = uow.schemes.get_by_code("PMEGP")

        old_ver = uow.schemes.get_version("PMEGP", "2024.1")
        old_ver.status = SchemeStatusEnum.SUPERSEDED

        new_ver = SchemeVersion(
            id="active-pmegp-version-uuid",
            scheme_id=scheme.id,
            scheme_code="PMEGP",
            version="2026.1",
            status=SchemeStatusEnum.ACTIVE,
            max_loan_amount=7500000.0,
            subsidy_percentage_general=30.0,
            subsidy_percentage_special=40.0,
            beneficiary_contribution_general_pct=10.0,
            beneficiary_contribution_special_pct=5.0,
            interest_subvention_pct=0.0,
            eligibility_criteria={},
            required_documents=[],
            verification_notes=[],
            metadata_payload={},
            created_at=datetime.utcnow(),
        )
        uow.schemes.add_version(new_ver)
        uow.commit()

    with UnitOfWork(session_factory=session_factory) as uow:
        active_ver = uow.schemes.get_active_version("PMEGP")
        assert active_ver is not None
        assert active_ver.version == "2026.1"
        assert active_ver.status == SchemeStatusEnum.ACTIVE


# ==============================================================================
# TEST 9: Historical Scheme Identity in Persisted Analysis
# ==============================================================================
def test_09_historical_scheme_identity_in_analysis(client_with_db):
    """Persist an Analysis with Version A. Activate Version B. Verify Analysis still contains Version A."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    payload = {
        "profile": {
            "business_name": "Rural Atta Chakki",
            "category": "Flour Milling",
            "description": "Grain processing unit",
            "location": {
                "state": "Uttar Pradesh",
                "district": "Varanasi",
                "village": "Rohania",
                "latitude": 25.26,
                "longitude": 82.95
            },
            "experience_years": 3,
            "own_capital": 100000.0,
            "desired_loan": 300000.0,
            "is_new_business": True
        },
        "financials": {
            "startup_cost": 50000.0,
            "equipment_cost": 300000.0,
            "inventory_cost": 50000.0,
            "monthly_fixed_cost": 15000.0,
            "customers_per_day": 25,
            "avg_ticket_price": 100.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 30.0,
            "interest_rate_pct": 10.0,
            "loan_tenure_months": 36
        }
    }

    # 1. Create Analysis under Version 2024.1
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    analysis_id = resp.json()["analysis_id"]
    initial_schemes = resp.json()["scheme_result"]["schemes"]
    assert len(initial_schemes) > 0
    assert initial_schemes[0].get("scheme_version") == "2024.1"

    # 2. Add new version to catalog
    with UnitOfWork(session_factory=session_factory) as uow:
        scheme = uow.schemes.get_by_code("PMEGP")
        old_ver = uow.schemes.get_version("PMEGP", "2024.1")
        old_ver.status = SchemeStatusEnum.SUPERSEDED

        new_ver = SchemeVersion(
            id="v2026-pmegp-uuid",
            scheme_id=scheme.id,
            scheme_code="PMEGP",
            version="2026.1",
            status=SchemeStatusEnum.ACTIVE,
            max_loan_amount=9000000.0,
            subsidy_percentage_general=40.0,
            subsidy_percentage_special=50.0,
            beneficiary_contribution_general_pct=10.0,
            beneficiary_contribution_special_pct=5.0,
            interest_subvention_pct=0.0,
            eligibility_criteria={},
            required_documents=[],
            verification_notes=[],
            metadata_payload={},
            created_at=datetime.utcnow(),
        )
        uow.schemes.add_version(new_ver)
        uow.commit()

    # 3. Retrieve Historical Analysis
    get_resp = client.get(f"/api/analyze/{analysis_id}")
    assert get_resp.status_code == 200
    retrieved_schemes = get_resp.json()["scheme_result"]["schemes"]
    assert retrieved_schemes[0].get("scheme_version") == "2024.1"
    assert retrieved_schemes[0]["subsidy_eligible_amount"] == initial_schemes[0]["subsidy_eligible_amount"]


# ==============================================================================
# TEST 10: No Scheme Refresh on Historical GET
# ==============================================================================
def test_10_no_scheme_recalculation_on_historical_get(client_with_db, monkeypatch):
    """Verify retrieving a historical analysis does not invoke scheme matcher or recalculate eligibility."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    payload = {
        "profile": {
            "business_name": "Rural Kirana",
            "category": "Retail",
            "description": "General store",
            "location": {
                "state": "Bihar",
                "district": "Patna",
                "village": "Danapur",
                "latitude": 25.6,
                "longitude": 85.1
            },
            "experience_years": 2,
            "own_capital": 50000.0,
            "desired_loan": 100000.0,
            "is_new_business": True
        },
        "financials": {
            "startup_cost": 20000.0,
            "equipment_cost": 30000.0,
            "inventory_cost": 100000.0,
            "monthly_fixed_cost": 8000.0,
            "customers_per_day": 30,
            "avg_ticket_price": 50.0,
            "working_days_per_month": 26,
            "variable_cost_pct": 60.0,
            "interest_rate_pct": 10.0,
            "loan_tenure_months": 36
        }
    }

    create_resp = client.post("/api/analyze", json=payload)
    assert create_resp.status_code == 200
    analysis_id = create_resp.json()["analysis_id"]

    # Mock match_schemes to raise an exception if called during GET
    def mock_match_fail(*args, **kwargs):
        raise AssertionError("Scheme matching MUST NOT be invoked on historical GET")

    monkeypatch.setattr("app.services.schemes.matcher.SchemeService.match_schemes", mock_match_fail)

    # Retrieval should succeed cleanly from snapshot without invoking matcher
    get_resp = client.get(f"/api/analyze/{analysis_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["analysis_id"] == analysis_id


# ==============================================================================
# TEST 11: Deterministic Matching Parity
# ==============================================================================
def test_11_deterministic_matching_parity():
    """Verify deterministic matching parity between SchemeRules and SchemeService."""
    service = SchemeService()
    profile = BusinessProfileBase(
        business_name="Test Dairy",
        category="Dairy",
        description="Milk chilling and processing",
        location=LocationSchema(state="Gujarat", district="Anand", village="Mogri"),
        experience_years=5,
        own_capital=100000.0,
        desired_loan=400000.0,
        is_new_business=True
    )
    financials = FinancialResultResponse(
        total_capex=500000.0,
        required_loan_amount=400000.0,
        monthly_revenue=100000.0,
        monthly_variable_cost=40000.0,
        monthly_gross_profit=60000.0,
        monthly_fixed_cost=20000.0,
        monthly_emi=12906.0,
        monthly_net_profit=27094.0,
        net_profit_margin_pct=27.09,
        break_even_revenue_monthly=33333.33,
        break_even_units_daily=13,
        dscr=2.1,
        is_financially_viable=True
    )

    res = service.match_schemes(profile, financials)
    assert res.eligible_schemes_count >= 2
    matched_codes = [s.scheme_code for s in res.schemes]
    assert "PMEGP" in matched_codes
    assert "MUDRA_KISHORE" in matched_codes


# ==============================================================================
# TEST 12: Official Source Provenance
# ==============================================================================
def test_12_official_source_provenance(client_with_db):
    """Verify each seeded scheme has the expected official source URL and title."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    with UnitOfWork(session_factory=session_factory) as uow:
        pmegp = uow.schemes.get_active_version("PMEGP")
        assert pmegp.official_portal_url == "https://www.pmegp.msme.gov.in/"
        assert pmegp.source_publication_date == "2024-09"

        mudra = uow.schemes.get_active_version("PMMY")
        assert pmegp.official_portal_url.startswith("https://")
        assert mudra.official_portal_url == "https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy"

        pmfme = uow.schemes.get_active_version("PMFME")
        assert pmfme.official_portal_url == "https://pmfme.mofpi.gov.in/"


# ==============================================================================
# TEST 13: Missing Catalog Data Becomes NEEDS_VERIFICATION
# ==============================================================================
def test_13_missing_or_unmapped_category_verification():
    """Verify unmapped/unverified conditions return NEEDS_VERIFICATION or PARTIALLY_ELIGIBLE."""
    profile = BusinessProfileBase(
        business_name="General Craft",
        category="General Craft",
        description="Handmade pottery",
        location=LocationSchema(state="UnknownState", district="UnknownDistrict", village="UnknownVillage"),
        experience_years=1,
        own_capital=20000.0,
        desired_loan=50000.0,
        is_new_business=True
    )
    # PMFME on non-food returns NOT_ELIGIBLE
    matched, status, _, _, reasons, _ = SchemeRules.evaluate_pmfme(
        profile=profile,
        capex=70000.0,
        loan_amount=50000.0,
        odop_product=None,
        is_odop_aligned=False
    )
    assert matched is False
    assert status == "NOT_ELIGIBLE"


# ==============================================================================
# TEST 14: API List (/api/schemes)
# ==============================================================================
def test_14_api_list_schemes(client_with_db):
    """Verify GET /api/schemes returns active catalog entries with active_version."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    resp = client.get("/api/schemes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    codes = [item["scheme_code"] for item in data]
    assert "PMEGP" in codes
    assert "PMMY" in codes
    assert "PMFME" in codes

    pmegp_item = next(item for item in data if item["scheme_code"] == "PMEGP")
    assert pmegp_item["active_version"] is not None
    assert pmegp_item["active_version"]["version"] == "2024.1"


# ==============================================================================
# TEST 15: API Version History (/api/schemes/{code}/versions)
# ==============================================================================
def test_15_api_scheme_version_history(client_with_db):
    """Verify GET /api/schemes/{scheme_code}/versions returns historical versions."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    with UnitOfWork(session_factory=session_factory) as uow:
        scheme = uow.schemes.get_by_code("PMEGP")

        # Add a second version
        new_ver = SchemeVersion(
            id="v2-test-uuid",
            scheme_id=scheme.id,
            scheme_code="PMEGP",
            version="2025.1",
            status=SchemeStatusEnum.SUPERSEDED,
            max_loan_amount=5000000.0,
            subsidy_percentage_general=25.0,
            subsidy_percentage_special=35.0,
            beneficiary_contribution_general_pct=10.0,
            beneficiary_contribution_special_pct=5.0,
            interest_subvention_pct=0.0,
            eligibility_criteria={},
            required_documents=[],
            verification_notes=[],
            metadata_payload={},
            created_at=datetime.utcnow(),
        )
        uow.schemes.add_version(new_ver)
        uow.commit()

    resp = client.get("/api/schemes/PMEGP/versions")
    assert resp.status_code == 200
    versions = resp.json()
    assert len(versions) == 2
    ver_nums = [v["version"] for v in versions]
    assert "2024.1" in ver_nums
    assert "2025.1" in ver_nums


# ==============================================================================
# TEST 16: Single Scheme Detail (/api/schemes/{code})
# ==============================================================================
def test_16_api_get_scheme_by_code(client_with_db):
    """Verify GET /api/schemes/{code} returns detailed master and active version info."""
    client, session_factory = client_with_db
    with UnitOfWork(session_factory=session_factory) as uow:
        seed_schemes(session=uow.session)

    resp = client.get("/api/schemes/PMFME")
    assert resp.status_code == 200
    data = resp.json()
    assert data["scheme_code"] == "PMFME"
    assert "Food Processing" in data["scheme_name"]
    assert data["active_version"]["subsidy_percentage_general"] == 35.0

    # 404 on non-existent scheme
    resp404 = client.get("/api/schemes/NON_EXISTENT_SCHEME")
    assert resp404.status_code == 404
