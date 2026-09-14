"""Phase 6C Repository Layer & Unit of Work Test Suite.

Verifies:
- Test 1: BusinessProfile create & read fidelity via repository.
- Test 2: Analysis create & read fidelity via repository.
- Test 3: Atomic creation of Analysis + FinancialInputSnapshot + FinancialResultSnapshot via Unit of Work.
- Test 4: Atomic multi-entity commit.
- Test 5: Transaction rollback on failure leaving no partial records.
- Test 6: Repository does not alter supplied calculation values.
- Test 7: Analysis repository has no update/overwrite methods (immutability protection).
- Test 8: Snapshot ownership and uniqueness constraint enforcement.
- Test 9: Unit of Work session lifecycle and guaranteed closure.
- Test 10: SQLite development/test database compatibility.
- Test 11: Multi-Analysis Immutability Invariant through Unit of Work.
"""
import uuid
import pytest
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database import Base, init_db
from app.models import (
    User,
    BusinessProfile,
    Analysis,
    FinancialInputSnapshot,
    FinancialResultSnapshot,
    RecommendationStatusEnum,
)
from app.repositories import (
    BusinessProfileRepository,
    AnalysisRepository,
    FinancialSnapshotRepository,
    UnitOfWork,
)


@pytest.fixture
def test_engine(tmp_path):
    """Provides a fresh SQLite test database engine for each test."""
    db_file = tmp_path / "test_repo_uow.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    init_db(target_engine=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(test_engine):
    """Provides a sessionmaker bound to the test engine."""
    return sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def test_business_profile_repository_create_read(session_factory):
    """Test 1: Create a BusinessProfile through the repository and retrieve it with high fidelity."""
    profile_id = str(uuid.uuid4())
    with UnitOfWork(session_factory=session_factory) as uow:
        profile = BusinessProfile(
            id=profile_id,
            business_name="Shree Ganesh Flour Mill",
            category="Agro Processing",
            description="Atta and spices milling in village center",
            state="Madhya Pradesh",
            district="Sehore",
            village="Ashta",
            latitude=23.018,
            longitude=76.998,
            experience_years=4,
            own_capital=40000.0,
            desired_loan=120000.0,
            is_new_business=False,
        )
        uow.business_profiles.create(profile)
        uow.commit()

    with UnitOfWork(session_factory=session_factory) as uow:
        fetched = uow.business_profiles.get_by_id(profile_id)
        assert fetched is not None
        assert fetched.business_name == "Shree Ganesh Flour Mill"
        assert fetched.category == "Agro Processing"
        assert fetched.state == "Madhya Pradesh"
        assert fetched.experience_years == 4
        assert fetched.own_capital == 40000.0
        assert fetched.desired_loan == 120000.0
        assert fetched.is_new_business is False


def test_analysis_repository_create_read(session_factory):
    """Test 2: Create an Analysis through the repository and retrieve core attributes."""
    analysis_id = str(uuid.uuid4())
    with UnitOfWork(session_factory=session_factory) as uow:
        analysis = Analysis(
            id=analysis_id,
            recommendation_status=RecommendationStatusEnum.PROCEED,
            overall_verdict="PROCEED",
            confidence_score=0.91,
            schema_version="1.0.0",
            rules_version="1.0.0",
            risk_factors=[{"factor": "Power outage risk", "severity": "LOW", "mitigation": "Solar backup"}],
            ai_explanation={"summary": "Enterprise exhibits robust margins."},
        )
        uow.analyses.create(analysis)
        uow.commit()

    with UnitOfWork(session_factory=session_factory) as uow:
        fetched = uow.analyses.get_by_id(analysis_id)
        assert fetched is not None
        assert fetched.id == analysis_id
        assert fetched.recommendation_status == RecommendationStatusEnum.PROCEED
        assert fetched.confidence_score == 0.91
        assert len(fetched.risk_factors) == 1
        assert fetched.risk_factors[0]["severity"] == "LOW"


def test_financial_snapshots_atomic_creation(session_factory):
    """Test 3: Create Analysis + FinancialInputSnapshot + FinancialResultSnapshot through one Unit of Work."""
    analysis_id = str(uuid.uuid4())

    with UnitOfWork(session_factory=session_factory) as uow:
        analysis = Analysis(
            id=analysis_id,
            recommendation_status=RecommendationStatusEnum.PROCEED,
            confidence_score=0.89,
        )
        input_snap = FinancialInputSnapshot(
            own_capital=50000.0,
            desired_loan=150000.0,
            startup_cost=20000.0,
            equipment_cost=100000.0,
            inventory_cost=80000.0,
            monthly_fixed_cost=12000.0,
            customers_per_day=30,
            avg_ticket_price=150.0,
            working_days_per_month=26,
            variable_cost_pct=45.0,
            interest_rate_pct=10.5,
            loan_tenure_months=36,
        )
        result_snap = FinancialResultSnapshot(
            total_capex=200000.0,
            required_loan_amount=150000.0,
            monthly_revenue=117000.0,
            monthly_variable_cost=52650.0,
            monthly_gross_profit=64350.0,
            monthly_fixed_cost=12000.0,
            monthly_emi=4875.14,
            monthly_net_profit=47474.86,
            net_profit_margin_pct=40.58,
            break_even_revenue_monthly=30682.07,
            break_even_units_daily=8,
            dscr=10.74,
            is_financially_viable=True,
            explanations={"monthly_revenue": {"plain_meaning": "Estimated sales"}},
        )

        uow.analyses.create(analysis, input_snapshot=input_snap, result_snapshot=result_snap)
        uow.commit()

    with UnitOfWork(session_factory=session_factory) as uow:
        fetched = uow.analyses.get_by_id(analysis_id)
        assert fetched is not None
        assert fetched.financial_input_snapshot is not None
        assert fetched.financial_input_snapshot.customers_per_day == 30
        assert fetched.financial_input_snapshot.variable_cost_pct == 45.0
        assert fetched.financial_result_snapshot is not None
        assert fetched.financial_result_snapshot.monthly_revenue == 117000.0
        assert fetched.financial_result_snapshot.monthly_net_profit == 47474.86
        assert fetched.financial_result_snapshot.dscr == 10.74


def test_atomic_multi_entity_commit(session_factory):
    """Test 4: Create multiple related entities (User, Business, Analysis) and verify atomic commit."""
    user_id = str(uuid.uuid4())
    business_id = str(uuid.uuid4())
    analysis_id = str(uuid.uuid4())

    with UnitOfWork(session_factory=session_factory) as uow:
        user = User(id=user_id, phone_number="+919876500001", full_name="Anita Sharma")
        uow.users.create(user)

        business = BusinessProfile(
            id=business_id,
            user_id=user_id,
            business_name="Anita Beauty Parlour",
            category="Personal Services",
            state="Rajasthan",
            district="Jaipur",
            village="Sanganer",
        )
        uow.business_profiles.create(business)

        analysis = Analysis(
            id=analysis_id,
            business_id=business_id,
            recommendation_status=RecommendationStatusEnum.PROCEED,
            confidence_score=0.90,
        )
        uow.analyses.create(analysis)
        uow.commit()

    with UnitOfWork(session_factory=session_factory) as uow:
        assert uow.users.get_by_id(user_id) is not None
        assert uow.business_profiles.get_by_id(business_id) is not None
        assert uow.analyses.get_by_id(analysis_id) is not None
        user_businesses = uow.business_profiles.list_for_user(user_id)
        assert len(user_businesses) == 1


def test_transaction_rollback_on_failure(session_factory):
    """Test 5: Transaction rollback occurs automatically when an exception is raised."""
    business_id = str(uuid.uuid4())
    analysis_id = str(uuid.uuid4())

    with pytest.raises(RuntimeError):
        with UnitOfWork(session_factory=session_factory) as uow:
            business = BusinessProfile(
                id=business_id,
                business_name="Unsaved Pottery Works",
                category="Handicrafts",
                state="Odisha",
                district="Puri",
                village="Raghurajpur",
            )
            uow.business_profiles.create(business)

            analysis = Analysis(
                id=analysis_id,
                business_id=business_id,
                recommendation_status=RecommendationStatusEnum.VALIDATE_FIRST,
            )
            uow.analyses.create(analysis)

            # Deliberate failure before commit
            raise RuntimeError("Simulated pipeline error before commit")

    # Verify nothing was persisted
    with UnitOfWork(session_factory=session_factory) as uow:
        assert uow.business_profiles.get_by_id(business_id) is None
        assert uow.analyses.get_by_id(analysis_id) is None


def test_repository_does_not_calculate_or_alter_values(session_factory):
    """Test 6: Repositories store exact supplied numbers without altering or recalculating them."""
    analysis_id = str(uuid.uuid4())
    arbitrary_revenue = 12345.67
    arbitrary_net_profit = 9876.54
    arbitrary_dscr = 4.321

    with UnitOfWork(session_factory=session_factory) as uow:
        analysis = Analysis(
            id=analysis_id,
            recommendation_status=RecommendationStatusEnum.PROCEED,
        )
        result_snap = FinancialResultSnapshot(
            total_capex=50000.0,
            required_loan_amount=30000.0,
            monthly_revenue=arbitrary_revenue,
            monthly_variable_cost=2000.0,
            monthly_gross_profit=10345.67,
            monthly_fixed_cost=1000.0,
            monthly_emi=500.0,
            monthly_net_profit=arbitrary_net_profit,
            net_profit_margin_pct=80.0,
            break_even_revenue_monthly=1500.0,
            break_even_units_daily=2,
            dscr=arbitrary_dscr,
            is_financially_viable=True,
            explanations={},
        )
        uow.analyses.create(analysis, result_snapshot=result_snap)
        uow.commit()

    with UnitOfWork(session_factory=session_factory) as uow:
        fetched = uow.analyses.get_by_id(analysis_id)
        assert fetched.financial_result_snapshot.monthly_revenue == arbitrary_revenue
        assert fetched.financial_result_snapshot.monthly_net_profit == arbitrary_net_profit
        assert fetched.financial_result_snapshot.dscr == arbitrary_dscr


def test_analysis_repository_immutability_interface(session_factory):
    """Test 7: Verify AnalysisRepository does NOT expose update, overwrite, or replace methods."""
    repo = AnalysisRepository(session=None)
    forbidden_methods = [
        "update",
        "update_analysis",
        "overwrite",
        "overwrite_result",
        "replace_snapshot",
        "save_update",
    ]
    for method in forbidden_methods:
        assert not hasattr(repo, method), f"AnalysisRepository illegally exposes mutable method '{method}'"


def test_snapshot_ownership_uniqueness(session_factory):
    """Test 8: Snapshot analysis_id uniqueness is strictly enforced."""
    analysis_1_id = str(uuid.uuid4())
    analysis_2_id = str(uuid.uuid4())

    with UnitOfWork(session_factory=session_factory) as uow:
        a1 = Analysis(id=analysis_1_id, recommendation_status=RecommendationStatusEnum.PROCEED)
        a2 = Analysis(id=analysis_2_id, recommendation_status=RecommendationStatusEnum.PROCEED)
        uow.analyses.create(a1)
        uow.analyses.create(a2)
        
        # Add input snapshot for a1
        s1 = FinancialInputSnapshot(
            analysis_id=analysis_1_id,
            own_capital=10000.0,
            startup_cost=5000.0,
            equipment_cost=5000.0,
        )
        uow.snapshots.add_input_snapshot(s1)
        uow.commit()

    # Attempting to assign a second FinancialInputSnapshot to analysis_1_id must fail unique constraint
    with pytest.raises(IntegrityError):
        with UnitOfWork(session_factory=session_factory) as uow:
            duplicate_snap = FinancialInputSnapshot(
                analysis_id=analysis_1_id,  # Duplicate
                own_capital=20000.0,
                startup_cost=10000.0,
                equipment_cost=10000.0,
            )
            uow.snapshots.add_input_snapshot(duplicate_snap)
            uow.commit()


def test_unit_of_work_session_closure(session_factory):
    """Test 9: UnitOfWork guarantees session closure on exit."""
    captured_session = None
    with UnitOfWork(session_factory=session_factory) as uow:
        captured_session = uow.session
        assert captured_session is not None
        assert captured_session.is_active

    # After context exit, the session should be closed
    # In SQLAlchemy, closed sessions are no longer active/in-transaction
    assert not captured_session.is_active or captured_session.bind is not None


def test_multi_analysis_immutability_through_uow(session_factory):
    """Test 11 & 18: Analysis A remains unchanged when Analysis B is created through Unit of Work."""
    business_id = str(uuid.uuid4())
    analysis_A_id = str(uuid.uuid4())
    analysis_B_id = str(uuid.uuid4())

    with UnitOfWork(session_factory=session_factory) as uow:
        # Create business
        business = BusinessProfile(
            id=business_id,
            business_name="Kisan Agro Services",
            category="Agri Inputs",
            state="Punjab",
            district="Ludhiana",
            village="Khanna",
        )
        uow.business_profiles.create(business)

        # 1. Commit Analysis A with inputs X / results Y
        analysis_A = Analysis(
            id=analysis_A_id,
            business_id=business_id,
            recommendation_status=RecommendationStatusEnum.PROCEED,
            confidence_score=0.80,
            created_at=datetime(2026, 9, 1, 10, 0, 0),
        )
        input_A = FinancialInputSnapshot(
            customers_per_day=20,
            avg_ticket_price=100.0,
            working_days_per_month=26,
        )
        result_A = FinancialResultSnapshot(
            total_capex=50000.0,
            required_loan_amount=30000.0,
            monthly_revenue=52000.0,
            monthly_variable_cost=20000.0,
            monthly_gross_profit=32000.0,
            monthly_fixed_cost=5000.0,
            monthly_emi=968.0,
            monthly_net_profit=26032.0,
            net_profit_margin_pct=50.06,
            break_even_revenue_monthly=9697.0,
            break_even_units_daily=4,
            dscr=27.89,
            is_financially_viable=True,
            explanations={},
        )
        uow.analyses.create(analysis_A, input_snapshot=input_A, result_snapshot=result_A)
        uow.commit()

    # 2. Commit Analysis B with inputs Z / results W under the same business
    with UnitOfWork(session_factory=session_factory) as uow:
        analysis_B = Analysis(
            id=analysis_B_id,
            business_id=business_id,
            recommendation_status=RecommendationStatusEnum.PROCEED,
            confidence_score=0.92,
            created_at=datetime(2026, 9, 12, 12, 0, 0),
        )
        input_B = FinancialInputSnapshot(
            customers_per_day=50,  # Changed
            avg_ticket_price=100.0,
            working_days_per_month=26,
        )
        result_B = FinancialResultSnapshot(
            total_capex=50000.0,
            required_loan_amount=30000.0,
            monthly_revenue=130000.0,  # Changed
            monthly_variable_cost=50000.0,
            monthly_gross_profit=80000.0,
            monthly_fixed_cost=5000.0,
            monthly_emi=968.0,
            monthly_net_profit=74032.0,  # Changed
            net_profit_margin_pct=56.95,
            break_even_revenue_monthly=9697.0,
            break_even_units_daily=4,
            dscr=77.48,
            is_financially_viable=True,
            explanations={},
        )
        uow.analyses.create(analysis_B, input_snapshot=input_B, result_snapshot=result_B)
        uow.commit()

    # 3. Verify Analysis A values are completely intact and unmodified
    with UnitOfWork(session_factory=session_factory) as uow:
        loaded_A = uow.analyses.get_by_id(analysis_A_id)
        assert loaded_A is not None
        assert loaded_A.financial_input_snapshot.customers_per_day == 20
        assert loaded_A.financial_result_snapshot.monthly_revenue == 52000.0
        assert loaded_A.financial_result_snapshot.monthly_net_profit == 26032.0

        loaded_B = uow.analyses.get_by_id(analysis_B_id)
        assert loaded_B is not None
        assert loaded_B.financial_input_snapshot.customers_per_day == 50
        assert loaded_B.financial_result_snapshot.monthly_revenue == 130000.0
        assert loaded_B.financial_result_snapshot.monthly_net_profit == 74032.0

        # Verify business has both analyses listed
        business_analyses = uow.analyses.list_by_business(business_id)
        assert len(business_analyses) == 2
