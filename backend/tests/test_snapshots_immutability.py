"""Phase 6B Snapshot Architecture & Immutability Test Suite.

Verifies:
- Test 1: Financial input snapshot (all 12 assumptions persisted & retrieved exactly).
- Test 2: Financial result snapshot (completed financial result stored without recalculation).
- Test 3: Immutable analysis data representation.
- Test 4: Evidence ledger snapshot round-trip & provenance retention.
- Test 5: Decision trace snapshot round-trip & rule evaluation fidelity.
- Test 6: Action plan snapshot round-trip.
- Test 7: Scheme and market result snapshots round-trip.
- Test 8: PostgreSQL DDL compilation for all models and JSON/JSONB fields.
- Test 9: SQLite compatibility.
- Test 10: Immutability Invariant: Analysis A (inputs X, result Y) remains unchanged
          when a new Analysis B (inputs Z, result new_Y) is created for the same business.
"""
import uuid
from datetime import datetime
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.database import Base, init_db
from app.models import (
    User,
    BusinessProfile,
    Analysis,
    FinancialInputSnapshot,
    FinancialResultSnapshot,
    RecommendationStatusEnum,
)
from app.services.financial.calculator import FinancialService
from app.schemas.financial import FinancialAssumptionsInput, FinancialCalculationRequest


@pytest.fixture
def db_session(tmp_path):
    """Provides an isolated SQLite database session for each test."""
    db_file = tmp_path / "test_snapshots.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    init_db(target_engine=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_financial_input_snapshot_persistence(db_session):
    """Test 1: All 12 financial input assumptions can be persisted and retrieved exactly."""
    analysis = Analysis(
        id=str(uuid.uuid4()),
        recommendation_status=RecommendationStatusEnum.PROCEED,
        confidence_score=0.92,
        schema_version="1.0.0",
        rules_version="1.0.0",
    )
    db_session.add(analysis)
    db_session.flush()

    # Create 12 financial input assumptions snapshot
    input_snap = FinancialInputSnapshot(
        analysis_id=analysis.id,
        own_capital=50000.0,
        desired_loan=150000.0,
        startup_cost=20000.0,
        equipment_cost=100000.0,
        inventory_cost=80000.0,
        monthly_fixed_cost=15000.0,
        customers_per_day=35,
        avg_ticket_price=120.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=10.5,
        loan_tenure_months=36,
    )
    db_session.add(input_snap)
    db_session.commit()

    # Query back
    fetched = db_session.scalar(
        select(FinancialInputSnapshot).where(FinancialInputSnapshot.analysis_id == analysis.id)
    )
    assert fetched is not None
    assert fetched.own_capital == 50000.0
    assert fetched.desired_loan == 150000.0
    assert fetched.startup_cost == 20000.0
    assert fetched.equipment_cost == 100000.0
    assert fetched.inventory_cost == 80000.0
    assert fetched.monthly_fixed_cost == 15000.0
    assert fetched.customers_per_day == 35
    assert fetched.avg_ticket_price == 120.0
    assert fetched.working_days_per_month == 26
    assert fetched.variable_cost_pct == 40.0
    assert fetched.interest_rate_pct == 10.5
    assert fetched.loan_tenure_months == 36


def test_financial_result_snapshot_persistence(db_session):
    """Test 2: A completed deterministic financial result is stored directly without recalculation."""
    analysis = Analysis(
        id=str(uuid.uuid4()),
        recommendation_status=RecommendationStatusEnum.PROCEED,
        confidence_score=0.88,
    )
    db_session.add(analysis)
    db_session.flush()

    result_snap = FinancialResultSnapshot(
        analysis_id=analysis.id,
        total_capex=200000.0,
        required_loan_amount=150000.0,
        monthly_revenue=109200.0,
        monthly_variable_cost=43680.0,
        monthly_gross_profit=65520.0,
        monthly_fixed_cost=15000.0,
        monthly_emi=4875.14,
        monthly_net_profit=45644.86,
        net_profit_margin_pct=41.8,
        break_even_revenue_monthly=33125.23,
        break_even_units_daily=11,
        dscr=10.36,
        is_financially_viable=True,
        explanations={"monthly_revenue": {"plain_meaning": "Total monthly sales estimate"}},
    )
    db_session.add(result_snap)
    db_session.commit()

    fetched = db_session.scalar(
        select(FinancialResultSnapshot).where(FinancialResultSnapshot.analysis_id == analysis.id)
    )
    assert fetched is not None
    assert fetched.total_capex == 200000.0
    assert fetched.required_loan_amount == 150000.0
    assert fetched.monthly_net_profit == 45644.86
    assert fetched.dscr == 10.36
    assert fetched.is_financially_viable is True
    assert "monthly_revenue" in fetched.explanations


def test_immutable_analysis_data(db_session):
    """Test 3: Analysis parent record encapsulates all modular point-in-time snapshots."""
    analysis = Analysis(
        id=str(uuid.uuid4()),
        recommendation_status=RecommendationStatusEnum.VALIDATE_FIRST,
        overall_verdict="VALIDATE_FIRST",
        confidence_score=0.78,
        schema_version="1.0.0",
        rules_version="1.0.0",
        business_input_snapshot={
            "business_name": "Gram Vikas Tailoring",
            "category": "Tailoring",
            "state": "Maharashtra",
            "district": "Pune",
            "village": "Khed",
            "experience_years": 3,
            "own_capital": 25000.0,
            "desired_loan": 75000.0,
            "is_new_business": True,
        },
        risk_factors=[
            {"factor": "Single supplier dependency", "severity": "MEDIUM", "mitigation": "Identify alternative suppliers"}
        ],
        ai_explanation={"summary": "Feasible subject to initial verification of footfall."},
    )
    db_session.add(analysis)
    db_session.commit()

    fetched = db_session.scalar(select(Analysis).where(Analysis.id == analysis.id))
    assert fetched is not None
    assert fetched.recommendation_status == RecommendationStatusEnum.VALIDATE_FIRST
    assert fetched.business_input_snapshot["business_name"] == "Gram Vikas Tailoring"
    assert len(fetched.risk_factors) == 1
    assert fetched.risk_factors[0]["severity"] == "MEDIUM"


def test_evidence_snapshot_roundtrip(db_session):
    """Test 4: Representative Evidence Ledger data with provenance survives persistence round-trip."""
    evidence_payload = [
        {
            "id": "EV-DEM-001",
            "indicator": "village_population",
            "value": 4850,
            "unit": "persons",
            "evidence_type": "OBSERVED",
            "confidence": 0.95,
            "source": "Census Data Provider",
            "source_url": "https://censusindia.gov.in",
            "observed_at": "2026-01-15T00:00:00Z",
            "methodology": "Aggregated 2011 Census with state growth projections",
            "limitations": ["Projection may deviate in rapidly urbanizing corridors"],
        },
        {
            "id": "EV-MKT-002",
            "indicator": "competitor_density",
            "value": "2 competitors within 1.5km",
            "unit": "count",
            "evidence_type": "MODELLED",
            "confidence": 0.80,
            "source": "Overpass OSM Geo Provider",
            "source_url": "https://overpass-api.de",
            "observed_at": "2026-09-10T12:00:00Z",
            "methodology": "Overpass POI density query within 2km catchment",
            "limitations": ["Unmapped informal micro-units not indexed in OSM"],
        },
    ]

    analysis = Analysis(
        id=str(uuid.uuid4()),
        recommendation_status=RecommendationStatusEnum.PROCEED,
        confidence_score=0.85,
        evidence_ledger_snapshot=evidence_payload,
    )
    db_session.add(analysis)
    db_session.commit()

    fetched = db_session.scalar(select(Analysis).where(Analysis.id == analysis.id))
    assert fetched is not None
    assert len(fetched.evidence_ledger_snapshot) == 2
    assert fetched.evidence_ledger_snapshot[0]["id"] == "EV-DEM-001"
    assert fetched.evidence_ledger_snapshot[0]["evidence_type"] == "OBSERVED"
    assert fetched.evidence_ledger_snapshot[1]["source"] == "Overpass OSM Geo Provider"


def test_decision_trace_snapshot_roundtrip(db_session):
    """Test 5: Decision trace rules and outcomes survive persistence round-trip."""
    trace_payload = {
        "recommendation_status": "PROCEED",
        "summary": "High profitability and DSCR >= 1.5x with manageable local competition.",
        "rule_evaluations": [
            {
                "rule_id": "NET_PROFIT_POSITIVE",
                "rule_name": "Net Profit Positive",
                "condition": "net_profit > 0",
                "result": "PASS",
                "severity": "CRITICAL",
                "explanation": "Estimated net monthly profit of ₹45,645 is positive.",
                "source": "FeasibilityRules",
            },
            {
                "rule_id": "SOLVENCY_DSCR",
                "rule_name": "Debt Service Coverage Ratio",
                "condition": "dscr >= 1.5",
                "result": "PASS",
                "severity": "CRITICAL",
                "explanation": "DSCR of 10.36 exceeds the 1.5x safety threshold.",
                "source": "FeasibilityRules",
            },
        ],
        "key_positive_factors": ["High operating margin", "Comfortable debt coverage"],
        "key_caution_factors": [],
        "authority": "FeasibilityRules",
    }

    analysis = Analysis(
        id=str(uuid.uuid4()),
        recommendation_status=RecommendationStatusEnum.PROCEED,
        confidence_score=0.90,
        decision_trace_snapshot=trace_payload,
    )
    db_session.add(analysis)
    db_session.commit()

    fetched = db_session.scalar(select(Analysis).where(Analysis.id == analysis.id))
    assert fetched is not None
    assert fetched.decision_trace_snapshot["authority"] == "FeasibilityRules"
    assert len(fetched.decision_trace_snapshot["rule_evaluations"]) == 2
    assert fetched.decision_trace_snapshot["rule_evaluations"][0]["result"] == "PASS"


def test_action_plan_snapshot_roundtrip(db_session):
    """Test 6: Pre-loan action plan items survive persistence round-trip."""
    action_plan_payload = {
        "actions": [
            {
                "action": "Verify daily footfall in target weekly market",
                "category": "MARKET_VERIFICATION",
                "priority": "HIGH",
                "status": "PENDING",
                "source": "FeasibilityRules",
                "rationale": "High revenue assumption relies on 35 daily customers",
            },
            {
                "action": "Obtain quotation from certified machinery supplier",
                "category": "EQUIPMENT_CAPEX",
                "priority": "MEDIUM",
                "status": "PENDING",
                "source": "FeasibilityRules",
                "rationale": "Ensure ₹1,00,000 equipment budget matches vendor prices",
            },
        ]
    }

    analysis = Analysis(
        id=str(uuid.uuid4()),
        recommendation_status=RecommendationStatusEnum.PROCEED,
        action_plan_snapshot=action_plan_payload,
    )
    db_session.add(analysis)
    db_session.commit()

    fetched = db_session.scalar(select(Analysis).where(Analysis.id == analysis.id))
    assert fetched is not None
    assert len(fetched.action_plan_snapshot["actions"]) == 2
    assert fetched.action_plan_snapshot["actions"][0]["priority"] == "HIGH"


def test_scheme_and_market_snapshots_roundtrip(db_session):
    """Test 7: Scheme matching and market results survive persistence round-trip."""
    scheme_payload = {
        "matched_schemes": [
            {
                "scheme_code": "PMEGP",
                "scheme_name": "Prime Minister Employment Generation Programme",
                "is_eligible": True,
                "max_loan_amount": 5000000.0,
                "subsidy_amount_estimated": 52500.0,
                "subsidy_percentage": 35.0,
                "match_reasons": ["Rural manufacturing/service micro-enterprise"],
            }
        ]
    }
    market_payload = {
        "competitor_count": 2,
        "market_demand_level": "MODERATE",
        "price_benchmark": {"avg_ticket_benchmark": 110.0, "spread": 20.0},
    }

    analysis = Analysis(
        id=str(uuid.uuid4()),
        recommendation_status=RecommendationStatusEnum.PROCEED,
        scheme_result_snapshot=scheme_payload,
        market_result_snapshot=market_payload,
    )
    db_session.add(analysis)
    db_session.commit()

    fetched = db_session.scalar(select(Analysis).where(Analysis.id == analysis.id))
    assert fetched is not None
    assert fetched.scheme_result_snapshot["matched_schemes"][0]["scheme_code"] == "PMEGP"
    assert fetched.market_result_snapshot["competitor_count"] == 2


def test_postgresql_compatibility_compilation():
    """Test 8: Model definitions and snapshot tables compile cleanly against PostgreSQL dialect."""
    for table_name, table in Base.metadata.tables.items():
        ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        assert f"CREATE TABLE {table_name}" in ddl or f'CREATE TABLE "{table_name}"' in ddl, (
            f"Table {table_name} failed PostgreSQL DDL compilation: {ddl}"
        )


def test_sqlite_compatibility(tmp_path):
    """Test 9: SQLite test/dev environment functions smoothly with all snapshot models."""
    db_file = tmp_path / "test_sqlite_comp.db"
    engine = create_engine(f"sqlite:///{db_file}")
    init_db(target_engine=engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user = User(id=str(uuid.uuid4()), phone_number="+919123456780", full_name="Savitri Devi")
        profile = BusinessProfile(
            id=str(uuid.uuid4()),
            user_id=user.id,
            business_name="Devi Dairy",
            category="Dairy",
            state="UP",
            district="Varanasi",
            village="Ramnagar",
        )
        analysis = Analysis(
            id=str(uuid.uuid4()),
            business_id=profile.id,
            recommendation_status=RecommendationStatusEnum.PROCEED,
            confidence_score=0.91,
        )
        session.add_all([user, profile, analysis])
        session.commit()

        loaded = session.scalar(select(Analysis).where(Analysis.id == analysis.id))
        assert loaded is not None
        assert loaded.business.business_name == "Devi Dairy"
    finally:
        session.close()
        engine.dispose()


def test_immutability_invariant(db_session):
    """Test 10 & 21: Analysis A (inputs X, result Y) remains unchanged when a new
    Analysis B (inputs Z, result new_Y) is created for the same business."""
    # 1. Create Business Profile
    business = BusinessProfile(
        id=str(uuid.uuid4()),
        business_name="Maa Laxmi Kirana",
        category="Retail Grocery",
        state="Bihar",
        district="Patna",
        village="Danapur",
        own_capital=30000.0,
        desired_loan=70000.0,
    )
    db_session.add(business)
    db_session.flush()

    # 2. Run deterministic calculation for Scenario X
    calc_req_X = FinancialCalculationRequest(
        own_capital=30000.0,
        desired_loan=70000.0,
        financials=FinancialAssumptionsInput(
            startup_cost=10000.0,
            equipment_cost=40000.0,
            inventory_cost=50000.0,
            monthly_fixed_cost=8000.0,
            customers_per_day=20,
            avg_ticket_price=100.0,
            working_days_per_month=26,
            variable_cost_pct=60.0,
            interest_rate_pct=10.0,
            loan_tenure_months=36,
        ),
    )
    financial_service = FinancialService()
    result_X = financial_service.calculate(
        own_capital=calc_req_X.own_capital,
        desired_loan=calc_req_X.desired_loan,
        financials=calc_req_X.financials,
    )

    # 3. Store Analysis A (Snapshot X)
    analysis_A = Analysis(
        id=str(uuid.uuid4()),
        business_id=business.id,
        recommendation_status=RecommendationStatusEnum.PROCEED,
        confidence_score=0.85,
        created_at=datetime(2026, 9, 1, 10, 0, 0),
    )
    db_session.add(analysis_A)
    db_session.flush()

    snap_input_A = FinancialInputSnapshot(
        analysis_id=analysis_A.id,
        own_capital=calc_req_X.own_capital,
        desired_loan=calc_req_X.desired_loan,
        startup_cost=calc_req_X.financials.startup_cost,
        equipment_cost=calc_req_X.financials.equipment_cost,
        inventory_cost=calc_req_X.financials.inventory_cost,
        monthly_fixed_cost=calc_req_X.financials.monthly_fixed_cost,
        customers_per_day=calc_req_X.financials.customers_per_day,
        avg_ticket_price=calc_req_X.financials.avg_ticket_price,
        working_days_per_month=calc_req_X.financials.working_days_per_month,
        variable_cost_pct=calc_req_X.financials.variable_cost_pct,
        interest_rate_pct=calc_req_X.financials.interest_rate_pct,
        loan_tenure_months=calc_req_X.financials.loan_tenure_months,
    )
    snap_result_A = FinancialResultSnapshot(
        analysis_id=analysis_A.id,
        total_capex=result_X.total_capex,
        required_loan_amount=result_X.required_loan_amount,
        monthly_revenue=result_X.monthly_revenue,
        monthly_variable_cost=result_X.monthly_variable_cost,
        monthly_gross_profit=result_X.monthly_gross_profit,
        monthly_fixed_cost=result_X.monthly_fixed_cost,
        monthly_emi=result_X.monthly_emi,
        monthly_net_profit=result_X.monthly_net_profit,
        net_profit_margin_pct=result_X.net_profit_margin_pct,
        break_even_revenue_monthly=result_X.break_even_revenue_monthly,
        break_even_units_daily=result_X.break_even_units_daily,
        dscr=result_X.dscr,
        is_financially_viable=result_X.is_financially_viable,
        explanations={},
    )
    db_session.add_all([snap_input_A, snap_result_A])
    db_session.commit()

    # Capture original values of Analysis A
    orig_A_revenue = result_X.monthly_revenue
    orig_A_profit = result_X.monthly_net_profit
    orig_A_customers = calc_req_X.financials.customers_per_day

    # 4. User modifies assumptions later -> Scenario Z (50 customers/day, lower costs)
    calc_req_Z = FinancialCalculationRequest(
        own_capital=30000.0,
        desired_loan=70000.0,
        financials=FinancialAssumptionsInput(
            startup_cost=10000.0,
            equipment_cost=40000.0,
            inventory_cost=50000.0,
            monthly_fixed_cost=8000.0,
            customers_per_day=50,  # Changed from 20 to 50
            avg_ticket_price=100.0,
            working_days_per_month=26,
            variable_cost_pct=60.0,
            interest_rate_pct=10.0,
            loan_tenure_months=36,
        ),
    )
    result_Z = financial_service.calculate(
        own_capital=calc_req_Z.own_capital,
        desired_loan=calc_req_Z.desired_loan,
        financials=calc_req_Z.financials,
    )

    # 5. Store Analysis B as a NEW separate immutable record
    analysis_B = Analysis(
        id=str(uuid.uuid4()),
        business_id=business.id,
        recommendation_status=RecommendationStatusEnum.PROCEED,
        confidence_score=0.92,
        created_at=datetime(2026, 9, 12, 12, 0, 0),
    )
    db_session.add(analysis_B)
    db_session.flush()

    snap_input_B = FinancialInputSnapshot(
        analysis_id=analysis_B.id,
        own_capital=calc_req_Z.own_capital,
        desired_loan=calc_req_Z.desired_loan,
        startup_cost=calc_req_Z.financials.startup_cost,
        equipment_cost=calc_req_Z.financials.equipment_cost,
        inventory_cost=calc_req_Z.financials.inventory_cost,
        monthly_fixed_cost=calc_req_Z.financials.monthly_fixed_cost,
        customers_per_day=calc_req_Z.financials.customers_per_day,
        avg_ticket_price=calc_req_Z.financials.avg_ticket_price,
        working_days_per_month=calc_req_Z.financials.working_days_per_month,
        variable_cost_pct=calc_req_Z.financials.variable_cost_pct,
        interest_rate_pct=calc_req_Z.financials.interest_rate_pct,
        loan_tenure_months=calc_req_Z.financials.loan_tenure_months,
    )
    snap_result_B = FinancialResultSnapshot(
        analysis_id=analysis_B.id,
        total_capex=result_Z.total_capex,
        required_loan_amount=result_Z.required_loan_amount,
        monthly_revenue=result_Z.monthly_revenue,
        monthly_variable_cost=result_Z.monthly_variable_cost,
        monthly_gross_profit=result_Z.monthly_gross_profit,
        monthly_fixed_cost=result_Z.monthly_fixed_cost,
        monthly_emi=result_Z.monthly_emi,
        monthly_net_profit=result_Z.monthly_net_profit,
        net_profit_margin_pct=result_Z.net_profit_margin_pct,
        break_even_revenue_monthly=result_Z.break_even_revenue_monthly,
        break_even_units_daily=result_Z.break_even_units_daily,
        dscr=result_Z.dscr,
        is_financially_viable=result_Z.is_financially_viable,
        explanations={},
    )
    db_session.add_all([snap_input_B, snap_result_B])
    db_session.commit()

    # 6. Verify IMMUTABILITY: Query Analysis A and verify it was NEVER modified
    queried_A = db_session.scalar(select(Analysis).where(Analysis.id == analysis_A.id))
    assert queried_A is not None
    assert queried_A.financial_input_snapshot.customers_per_day == orig_A_customers == 20
    assert queried_A.financial_result_snapshot.monthly_revenue == orig_A_revenue == result_X.monthly_revenue
    assert queried_A.financial_result_snapshot.monthly_net_profit == orig_A_profit == result_X.monthly_net_profit

    # 7. Verify Analysis B contains the new calculations
    queried_B = db_session.scalar(select(Analysis).where(Analysis.id == analysis_B.id))
    assert queried_B is not None
    assert queried_B.financial_input_snapshot.customers_per_day == 50
    assert queried_B.financial_result_snapshot.monthly_revenue == result_Z.monthly_revenue
    assert queried_B.financial_result_snapshot.monthly_net_profit == result_Z.monthly_net_profit

    # Ensure both analyses exist independently under the same business
    all_analyses = db_session.scalars(
        select(Analysis).where(Analysis.business_id == business.id).order_by(Analysis.created_at)
    ).all()
    assert len(all_analyses) == 2
    assert all_analyses[0].id == analysis_A.id
    assert all_analyses[1].id == analysis_B.id
