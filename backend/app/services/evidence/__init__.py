"""Evidence Collection and Classification Services."""
from app.services.evidence.collector import EvidenceServiceInterface, EvidenceCollector
from app.services.evidence.validator import validate_evidence_integrity
from app.services.evidence.confidence import compute_weighted_confidence

__all__ = [
    "EvidenceServiceInterface",
    "EvidenceCollector",
    "validate_evidence_integrity",
    "compute_weighted_confidence",
]
