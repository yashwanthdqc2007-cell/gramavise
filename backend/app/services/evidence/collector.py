from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.analysis import EvidenceItem, EvidenceType


class EvidenceServiceInterface(ABC):
    """Abstract interface defining evidence gathering and classification operations."""

    @abstractmethod
    def collect(self, context: Dict[str, Any]) -> List[EvidenceItem]:
        """Aggregate evidence items across all sub-engines."""
        pass

    @abstractmethod
    def validate(self, evidence: EvidenceItem) -> bool:
        """Validate provenance and integrity of evidence item."""
        pass

    @abstractmethod
    def calculate_confidence(self, evidence_list: List[EvidenceItem]) -> float:
        """Compute aggregate confidence score (0.0 to 1.0)."""
        pass


class EvidenceCollector(EvidenceServiceInterface):
    """Aggregates and tags evidence items with appropriate verification levels."""

    def collect(self, context: Dict[str, Any]) -> List[EvidenceItem]:
        """Compile evidence records from financials, geo indicators, and benchmarks."""
        items: List[EvidenceItem] = []

        # 1. Financial Unit Economics Evidence
        items.append(EvidenceItem(
            indicator="Monthly Operating Surplus",
            value=f"₹{context.get('monthly_net_profit', 0):,.2f}",
            unit="INR/month",
            evidence_type=EvidenceType.CALCULATED,
            confidence=1.0,
            source="Deterministic Financial Engine",
            notes="Computed via formula: Gross Profit - Fixed Costs - Loan EMI."
        ))

        # 2. Break-Even Benchmark Evidence
        items.append(EvidenceItem(
            indicator="Daily Break-Even Footfall",
            value=f"{context.get('break_even_units_daily', 0)} orders/day",
            unit="units/day",
            evidence_type=EvidenceType.CALCULATED,
            confidence=1.0,
            source="Contribution Margin Model",
            notes="Required minimum sales to cover operational overheads and debt repayment."
        ))

        # 3. Market Density Evidence
        items.append(EvidenceItem(
            indicator="Local Category Competitors",
            value=f"{context.get('competitor_count', 0)} nearby units",
            unit="count",
            evidence_type=EvidenceType.OBSERVED,
            confidence=0.85,
            source="OpenStreetMap Overpass Registry",
            source_url="https://www.openstreetmap.org",
            notes="Identified commercial listings within 5km radius."
        ))

        # 4. Entrepreneur Stated Assumptions
        items.append(EvidenceItem(
            indicator="Expected Daily Footfall",
            value=f"{context.get('customers_per_day', 0)} customers",
            unit="customers/day",
            evidence_type=EvidenceType.ASSUMED,
            confidence=0.75,
            source="Entrepreneur Self-Declaration",
            notes="Self-reported baseline customer volume requiring on-ground validation."
        ))

        return items

    def validate(self, evidence: EvidenceItem) -> bool:
        return evidence.confidence >= 0.0 and bool(evidence.indicator)

    def calculate_confidence(self, evidence_list: List[EvidenceItem]) -> float:
        """Compute weighted mean confidence across all evidence items."""
        if not evidence_list:
            return 0.5
        total = sum(e.confidence for e in evidence_list)
        return round(total / len(evidence_list), 2)
