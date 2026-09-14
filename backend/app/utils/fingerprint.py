"""Deterministic request fingerprinting utility."""
import hashlib
import json
from typing import Any, Union
from pydantic import BaseModel


def _normalize(data: Any) -> Any:
    """Recursively normalize data structures for deterministic hashing."""
    if isinstance(data, BaseModel):
        return _normalize(data.model_dump())
    elif isinstance(data, dict):
        return {k: _normalize(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        return [_normalize(item) for item in data]
    elif isinstance(data, float):
        # Round float to 6 decimal places to prevent float precision drift
        return round(data, 6)
    return data


def compute_request_fingerprint(payload: Union[BaseModel, dict]) -> str:
    """Generate a deterministic SHA-256 hex digest for a JSON-serializable payload."""
    normalized = _normalize(payload)
    canonical_json = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
