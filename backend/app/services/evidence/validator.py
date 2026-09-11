from app.schemas.analysis import EvidenceItem


def validate_evidence_integrity(item: EvidenceItem) -> bool:
    """Verify validity of evidence item structure and metadata.
    
    TODO [Evidence Lead]: Implement integrity checks against external source hashes.
    """
    return bool(item.indicator and item.value and 0.0 <= item.confidence <= 1.0)
