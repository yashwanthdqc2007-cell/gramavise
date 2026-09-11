from typing import List
from app.schemas.analysis import EvidenceItem, EvidenceType

TYPE_WEIGHTS = {
    EvidenceType.OBSERVED: 1.0,
    EvidenceType.CALCULATED: 0.95,
    EvidenceType.MODELLED: 0.8,
    EvidenceType.ASSUMED: 0.6,
    EvidenceType.NEEDS_VERIFICATION: 0.4
}


def compute_weighted_confidence(evidence_items: List[EvidenceItem]) -> float:
    """Calculate aggregate confidence metric based on evidence source reliability.
    
    TODO [Evidence Lead]: Implement Bayesian confidence updating model.
    """
    if not evidence_items:
        return 0.5
    
    weighted_sum = sum(item.confidence * TYPE_WEIGHTS.get(item.evidence_type, 0.7) for item in evidence_items)
    total_weights = sum(TYPE_WEIGHTS.get(item.evidence_type, 0.7) for item in evidence_items)

    return round(weighted_sum / total_weights, 2) if total_weights > 0 else 0.5
