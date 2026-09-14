"""Deterministic Scheme Catalog & Versioning Seeder.

Reads verified statutory scheme data files from `backend/app/data/schemes/`
and populates the persistent `schemes` and `scheme_versions` database tables.

Idempotent: safe to run multiple times without duplicating or overwriting active definitions.
Never run automatically on application startup.
"""
import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

# Add backend directory to path if executed as script
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.database import SessionLocal
from app.models.scheme import Scheme, SchemeVersion, SchemeStatusEnum
from app.repositories.unit_of_work import UnitOfWork
from app.utils.logging import logger


DEFAULT_VERSION = "2024.1"


def load_json(filepath: Path) -> dict:
    """Load JSON definition file from disk."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_schemes(session=None) -> dict:
    """Deterministic, idempotent seeder for master schemes and version catalog."""
    data_dir = backend_root / "app" / "data" / "schemes"
    
    # Files to seed
    scheme_files = {
        "PMEGP": data_dir / "pmegp.json",
        "PMMY": data_dir / "mudra.json",
        "PMFME": data_dir / "pmfme.json",
    }

    results = {
        "schemes_created": 0,
        "schemes_existing": 0,
        "versions_created": 0,
        "versions_existing": 0,
    }

    with UnitOfWork(existing_session=session) as uow:
        for code, filepath in scheme_files.items():
            if not filepath.exists():
                logger.warning(f"Scheme definition file missing: {filepath}")
                continue

            raw = load_json(filepath)
            scheme_code = raw.get("scheme_id", code)
            scheme_name = raw.get("scheme_name", scheme_code)
            ministry = raw.get("ministry")
            description = raw.get("description")

            # 1. Master Scheme entity
            existing_scheme = uow.schemes.get_by_code(scheme_code)
            if not existing_scheme:
                scheme = Scheme(
                    id=str(uuid.uuid4()),
                    scheme_code=scheme_code,
                    scheme_name=scheme_name,
                    ministry=ministry,
                    department=raw.get("department", ministry),
                    description=description,
                    ministry_or_dept=ministry,
                    max_loan_amount=raw.get("maximum_loan_amount") or 0.0,
                    subsidy_percentage_general=(
                        raw.get("subsidy_rate", {}).get("general_rural", 0.0)
                        if isinstance(raw.get("subsidy_rate"), dict)
                        else (raw.get("subsidy_rate") or 0.0)
                    ),
                    subsidy_percentage_special=(
                        raw.get("subsidy_rate", {}).get("special_rural", 0.0)
                        if isinstance(raw.get("subsidy_rate"), dict)
                        else (raw.get("subsidy_rate") or 0.0)
                    ),
                    interest_subvention_pct=0.0,
                    eligibility_criteria=raw.get("eligible_business_types", []),
                    required_documents=raw.get("verification_required", []),
                    official_portal_url=raw.get("source_url"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                uow.schemes.add(scheme)
                uow.commit()
                existing_scheme = scheme
                results["schemes_created"] += 1
                logger.info(f"Created Master Scheme: {scheme_code}")
            else:
                results["schemes_existing"] += 1
                logger.info(f"Master Scheme already exists: {scheme_code}")

            # 2. SchemeVersion entity
            version_str = DEFAULT_VERSION
            existing_version = uow.schemes.get_version(scheme_code, version_str)
            if not existing_version:
                # Calculate subsidy & contribution defaults based on scheme facts
                sub_gen = 0.0
                sub_spec = 0.0
                if isinstance(raw.get("subsidy_rate"), dict):
                    sub_gen = raw["subsidy_rate"].get("general_rural", 0.0)
                    sub_spec = raw["subsidy_rate"].get("special_rural", 0.0)
                elif isinstance(raw.get("subsidy_rate"), (int, float)):
                    sub_gen = float(raw["subsidy_rate"])
                    sub_spec = float(raw["subsidy_rate"])

                contrib_gen = 0.0
                contrib_spec = 0.0
                if isinstance(raw.get("beneficiary_contribution"), dict):
                    contrib_gen = raw["beneficiary_contribution"].get("general", 0.0)
                    contrib_spec = raw["beneficiary_contribution"].get("special", contrib_gen)
                elif isinstance(raw.get("beneficiary_contribution"), (int, float)):
                    contrib_gen = float(raw["beneficiary_contribution"])
                    contrib_spec = float(raw["beneficiary_contribution"])

                scheme_ver = SchemeVersion(
                    id=str(uuid.uuid4()),
                    scheme_id=existing_scheme.id,
                    scheme_code=scheme_code,
                    version=version_str,
                    status=SchemeStatusEnum.ACTIVE,
                    description=description,
                    official_source_name=raw.get("source_title"),
                    official_portal_url=raw.get("source_url"),
                    source_publication_date=raw.get("source_last_verified"),
                    effective_from=datetime(2024, 9, 1),
                    effective_to=None,
                    retrieved_at=datetime.utcnow(),
                    max_loan_amount=raw.get("maximum_loan_amount") or 0.0,
                    subsidy_percentage_general=sub_gen,
                    subsidy_percentage_special=sub_spec,
                    beneficiary_contribution_general_pct=contrib_gen,
                    beneficiary_contribution_special_pct=contrib_spec,
                    interest_subvention_pct=0.0,
                    eligibility_criteria={
                        "applicable_states": raw.get("applicable_states", ["ALL_INDIA"]),
                        "eligible_business_types": raw.get("eligible_business_types", []),
                        "eligible_enterprise_types": raw.get("eligible_enterprise_types", []),
                        "new_or_existing": raw.get("new_or_existing", "BOTH"),
                        "minimum_age": raw.get("minimum_age", 18),
                        "maximum_project_cost": raw.get("maximum_project_cost"),
                        "subsidy_max_amount": raw.get("subsidy_max_amount"),
                        "tiers": raw.get("tiers", {}),
                    },
                    required_documents=raw.get("verification_required", []),
                    verification_notes=raw.get("special_conditions", []),
                    metadata_payload=raw,
                    created_at=datetime.utcnow(),
                )
                uow.schemes.add_version(scheme_ver)
                uow.commit()
                results["versions_created"] += 1
                logger.info(f"Created SchemeVersion: {scheme_code} v{version_str}")
            else:
                results["versions_existing"] += 1
                logger.info(f"SchemeVersion already exists: {scheme_code} v{version_str}")

    return results


if __name__ == "__main__":
    print("Seeding Scheme Catalog & Version History...")
    res = seed_schemes()
    print("Seed Complete:")
    print(f"  Master Schemes Created:  {res['schemes_created']}")
    print(f"  Master Schemes Existing: {res['schemes_existing']}")
    print(f"  Versions Created:        {res['versions_created']}")
    print(f"  Versions Existing:       {res['versions_existing']}")
