import pytest
from app.providers.price import PriceDataProvider
from app.services.geo.market import MockMarketService
from app.services.evidence.collector import EvidenceCollector
from app.schemas.market import MarketEvidenceQuery, GeographyLevel
from app.schemas.evidence import EvidenceType
from app.schemas.financial import FinancialAssumptionsInput
from app.services.financial.calculator import FinancialService
from app.services.recommendation.feasibility import evaluate_feasibility_status


@pytest.fixture
def price_provider():
    return PriceDataProvider()


@pytest.fixture
def market_service(price_provider):
    return MockMarketService(price_provider=price_provider)


@pytest.fixture
def evidence_collector(price_provider):
    return EvidenceCollector(price_provider=price_provider)


def test_known_official_commodity_market_record(price_provider):
    """Test retrieving known official Agmarknet mandi records for Tomato in Baramati/Pune."""
    res = price_provider.fetch_evidence({
        "commodity": "Tomato",
        "state": "Maharashtra",
        "district": "Pune",
        "market": "Baramati"
    })
    assert res.success is True
    assert len(res.evidence_items) == 1
    item = res.evidence_items[0]
    assert item.evidence_type == EvidenceType.OBSERVED
    assert item.confidence == 1.0
    assert item.verification_status == "VERIFIED_SOURCE"
    assert "₹3,200.00/quintal" in item.value
    assert "₹32.00/kg" in item.value

    payload = res.raw_payload
    assert payload["commodity"] == "Tomato"
    assert payload["market_name"] == "Baramati"
    assert payload["district_name"] == "Pune"
    assert payload["state_name"] == "Maharashtra"
    assert payload["modal_price"] == 3200.0
    assert payload["min_price"] == 2800.0
    assert payload["max_price"] == 3600.0
    assert payload["price_unit"] == "INR/quintal"
    assert payload["price_per_kg"] == 32.0
    assert payload["arrival_date"] == "2024-09-10"


def test_official_source_metadata(price_provider):
    """Test that official GoI DMI / OGD metadata is preserved."""
    res = price_provider.fetch_evidence({
        "commodity": "Garlic",
        "state": "Madhya Pradesh",
        "district": "Ujjain"
    })
    assert res.success is True
    payload = res.raw_payload
    assert payload["source"] == "Directorate of Marketing & Inspection (DMI) / OGD"
    assert "data.gov.in" in payload["source_url"]
    assert "Current Daily Price of Various Commodities" in payload["source_title"]
    assert payload["source_department"] == "Directorate of Marketing & Inspection (DMI)"
    assert payload["source_last_verified"] == "2024-09"


def test_modal_min_max_and_original_unit_preserved(price_provider):
    """Test preservation of modal, minimum, and maximum prices in original source unit."""
    res = price_provider.fetch_evidence({
        "commodity": "Onion",
        "state": "Maharashtra",
        "district": "Nashik",
        "market": "Lasalgaon"
    })
    payload = res.raw_payload
    assert payload["modal_price"] == 2650.0
    assert payload["min_price"] == 1800.0
    assert payload["max_price"] == 3200.0
    assert payload["price_unit"] == "INR/quintal"
    assert payload["currency"] == "INR"


def test_quintal_to_kg_conversion_explicit(price_provider):
    """Test explicit conversion: 1 quintal = 100 kg."""
    res = price_provider.fetch_evidence({
        "commodity": "Wheat",
        "state": "Madhya Pradesh",
        "district": "Ujjain"
    })
    payload = res.raw_payload
    modal_price = payload["modal_price"]
    price_per_kg = payload["price_per_kg"]
    assert price_per_kg == round(modal_price / 100.0, 2)


def test_observation_date_preserved_not_labelled_current(price_provider):
    """Test that arrival date is preserved and not labelled as 'current' without date provenance."""
    res = price_provider.fetch_evidence({
        "commodity": "Soybean",
        "state": "Madhya Pradesh",
        "district": "Indore"
    })
    payload = res.raw_payload
    assert payload["arrival_date"] == "2024-09-11"
    item = res.evidence_items[0]
    assert "11 Sep 2024" in item.notes


def test_conservative_commodity_matching(price_provider):
    """Test case-insensitivity, trim, and explicit synonyms vs rejection of aggressive fuzzy matches."""
    # Synonyms match
    assert price_provider.resolve_commodity("tomato") == "Tomato"
    assert price_provider.resolve_commodity("tamatar") == "Tomato"
    assert price_provider.resolve_commodity("GARLIC") == "Garlic"
    assert price_provider.resolve_commodity("lahsun") == "Garlic"
    assert price_provider.resolve_commodity("kela") == "Banana"
    assert price_provider.resolve_commodity("green chilli") == "Chilli Green"

    # Aggressive partials / unrelated words do NOT match
    assert price_provider.resolve_commodity("tomato ketchup") is None
    assert price_provider.resolve_commodity("tomato sauce") is None
    assert price_provider.resolve_commodity("garlic bread") is None
    assert price_provider.resolve_commodity("banana shake") is None


def test_unknown_commodity_returns_needs_verification(price_provider):
    """Test that an unmapped commodity returns NEEDS_VERIFICATION."""
    res = price_provider.fetch_evidence({
        "commodity": "Silk Sarees",
        "state": "Karnataka",
        "district": "Mandya"
    })
    assert res.success is True
    assert len(res.evidence_items) == 1
    item = res.evidence_items[0]
    assert item.evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert item.confidence == 0.0
    assert item.verification_status == "NEEDS_VERIFICATION"


def test_market_selection_hierarchy(price_provider):
    """Test exact market match -> district match -> state match -> unmapped."""
    # 1. Exact market match
    res_market = price_provider.query_mandi_prices("Tomato", state="Maharashtra", district="Pune", market="Baramati")
    assert len(res_market) == 1
    assert res_market[0]["market_name"] == "Baramati"

    # 2. District-level match (when market not specified)
    res_dist = price_provider.query_mandi_prices("Tomato", state="Maharashtra", district="Pune")
    assert len(res_dist) >= 1
    assert any(r["district_name"] == "Pune" for r in res_dist)

    # 3. State-level match (when district outside snapshot but state matches)
    res_state = price_provider.query_mandi_prices("Tomato", state="Maharashtra", district="Solapur")
    assert len(res_state) >= 1
    assert all(r["state_name"] == "Maharashtra" for r in res_state)

    # 4. Out of snapshot
    res_out = price_provider.query_mandi_prices("Tomato", state="Assam", district="Kamrup")
    assert len(res_out) == 0


def test_market_service_populates_price_benchmark_and_observations(market_service):
    """Test MockMarketService populates PriceBenchmark and price_observations."""
    query = MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Tomato"
    )
    res = market_service.get_market_indicators(query)
    assert res.price_benchmark is not None
    assert res.price_benchmark.evidence_type == EvidenceType.OBSERVED
    assert res.price_benchmark.median_price == 3200.0
    assert res.price_benchmark.price_per_kg == 32.0
    assert res.price_benchmark.market_name == "Baramati"
    assert res.price_benchmark.verification_status == "VERIFIED_SOURCE"

    assert len(res.price_observations) >= 1
    obs = res.price_observations[0]
    assert obs.commodity == "Tomato"
    assert obs.market_name == "Baramati"
    assert obs.modal_price == 3200.0


def test_market_service_unmapped_category_needs_verification(market_service):
    """Test MockMarketService returns NEEDS_VERIFICATION for non-agricultural category."""
    query = MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Tailoring Services"
    )
    res = market_service.get_market_indicators(query)
    assert res.price_benchmark is not None
    assert res.price_benchmark.evidence_type == EvidenceType.NEEDS_VERIFICATION
    assert res.price_benchmark.median_price is None
    assert len(res.price_observations) == 0


def test_evidence_collector_includes_mandi_price_evidence(evidence_collector):
    """Test EvidenceCollector includes OBSERVED mandi modal price item."""
    context = {
        "category": "Garlic",
        "state": "Madhya Pradesh",
        "district": "Ujjain",
        "village": "Nagda",
        "monthly_net_profit": 15000.0,
        "break_even_units_daily": 10,
        "customers_per_day": 20,
        "competitor_count": 2
    }
    items = evidence_collector.collect(context)
    mandi_items = [i for i in items if "Mandi" in i.indicator]
    assert len(mandi_items) >= 1
    mandi_item = mandi_items[0]
    assert mandi_item.evidence_type == EvidenceType.OBSERVED
    assert mandi_item.confidence == 1.0
    assert "₹12,500.00/quintal" in mandi_item.value or "₹12,000.00/quintal" in mandi_item.value
    assert "Agmarknet" in mandi_item.notes or "Directorate of Marketing & Inspection" in mandi_item.source


def test_price_evidence_does_not_alter_financial_engine():
    """Test strict separation: Mandi price does not alter financial calculations or retail price."""
    calc = FinancialService()
    fin_inputs = FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=30000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=10000.0,
        customers_per_day=25,
        avg_ticket_price=40.0,  # User retail price
        working_days_per_month=26,
        variable_cost_pct=50.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    res = calc.calculate(own_capital=30000.0, desired_loan=70000.0, financials=fin_inputs)

    # Revenue is computed purely from customers_per_day * avg_ticket_price * working_days
    expected_rev = 25 * 40.0 * 26  # 26,000.0
    assert res.monthly_revenue == expected_rev
    # Agmarknet wholesale price (e.g. ₹32/kg for tomato) has ZERO effect on user retail calculations
    assert res.monthly_revenue != 25 * 32.0 * 26


def test_price_evidence_does_not_alter_recommendation_status(market_service):
    """Test that feasibility recommendation rules are NOT altered by mandi prices."""
    calc = FinancialService()
    fin_inputs = FinancialAssumptionsInput(
        startup_cost=50000.0,
        equipment_cost=30000.0,
        inventory_cost=20000.0,
        monthly_fixed_cost=5000.0,
        customers_per_day=30,
        avg_ticket_price=100.0,
        working_days_per_month=26,
        variable_cost_pct=40.0,
        interest_rate_pct=10.0,
        loan_tenure_months=36
    )
    fin_res = calc.calculate(own_capital=50000.0, desired_loan=50000.0, financials=fin_inputs)
    
    # Query with Tomato (has verified mandi price)
    mkt_query_tomato = MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Tomato"
    )
    mkt_res_tomato = market_service.get_market_indicators(mkt_query_tomato)
    rec_tomato = evaluate_feasibility_status(fin_res, mkt_res_tomato)

    # Query with non-mandi category (unverified price)
    mkt_query_tailor = MarketEvidenceQuery(
        state="Maharashtra",
        district="Pune",
        village="Baramati",
        category="Tailoring Services"
    )
    mkt_res_tailor = market_service.get_market_indicators(mkt_query_tailor)
    rec_tailor = evaluate_feasibility_status(fin_res, mkt_res_tailor)

    # Both recommendations must match identically because mandi price is purely contextual evidence
    assert rec_tomato == rec_tailor


def test_deterministic_repeated_lookup(price_provider):
    """Test deterministic output on repeated lookups."""
    q = {"commodity": "Tomato", "state": "Maharashtra", "district": "Pune", "market": "Baramati"}
    res1 = price_provider.fetch_evidence(q)
    res2 = price_provider.fetch_evidence(q)
    assert res1.raw_payload == res2.raw_payload
    assert res1.evidence_items[0].value == res2.evidence_items[0].value

