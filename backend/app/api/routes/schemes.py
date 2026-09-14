"""Read-Only Government Scheme Catalog & Version History API."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from app.schemas.scheme import (
    SchemeCatalogItem,
    SchemeVersionResponse,
)
from app.repositories import UnitOfWork, get_uow
from app.services.schemes.matcher import SchemeService
from app.models.scheme import SchemeStatusEnum

router = APIRouter()
scheme_service = SchemeService()


def _map_version_model_to_response(v) -> SchemeVersionResponse:
    """Helper to convert a SchemeVersion ORM model to SchemeVersionResponse schema."""
    return SchemeVersionResponse(
        id=v.id,
        scheme_code=v.scheme_code,
        version=v.version,
        status=v.status.value if hasattr(v.status, "value") else str(v.status),
        description=v.description,
        official_source_name=v.official_source_name,
        official_portal_url=v.official_portal_url,
        source_publication_date=v.source_publication_date,
        effective_from=v.effective_from,
        effective_to=v.effective_to,
        retrieved_at=v.retrieved_at,
        max_loan_amount=v.max_loan_amount,
        subsidy_percentage_general=v.subsidy_percentage_general,
        subsidy_percentage_special=v.subsidy_percentage_special,
        beneficiary_contribution_general_pct=v.beneficiary_contribution_general_pct,
        beneficiary_contribution_special_pct=v.beneficiary_contribution_special_pct,
        interest_subvention_pct=v.interest_subvention_pct,
        eligibility_criteria=v.eligibility_criteria or {},
        required_documents=v.required_documents or [],
        verification_notes=v.verification_notes or [],
        metadata_payload=v.metadata_payload or {},
        created_at=v.created_at,
    )


@router.get("/schemes", response_model=List[SchemeCatalogItem], summary="List Active Government Credit & Subsidy Schemes")
async def list_schemes(
    category: Optional[str] = Query(None, description="Filter by business sector"),
    uow: UnitOfWork = Depends(get_uow),
):
    """Fetch active government schemes from the persistent versioned catalog."""
    master_schemes = uow.schemes.list_schemes()
    if not master_schemes:
        # Fallback to static data if catalog is not yet seeded
        raw_list = scheme_service.get_schemes(category=category)
        return [
            SchemeCatalogItem(
                id=s.get("scheme_id", "UNKNOWN"),
                scheme_code=s.get("scheme_id", "UNKNOWN"),
                scheme_name=s.get("scheme_name", ""),
                ministry=s.get("ministry"),
                department=s.get("department"),
                description=s.get("description"),
                active_version=None,
                total_versions=1,
                created_at=uow.schemes.session.bind and None or None, # handled safely
            )
            for s in raw_list
        ]

    items = []
    for s in master_schemes:
        active_ver = uow.schemes.get_active_version(s.scheme_code)
        all_versions = uow.schemes.list_versions(s.scheme_code)
        
        # Optional category filtering
        if category and active_ver:
            types = active_ver.eligibility_criteria.get("eligible_business_types", [])
            cat_upper = category.upper()
            if cat_upper not in [t.upper() for t in types] and "ALL" not in types:
                continue

        ver_resp = _map_version_model_to_response(active_ver) if active_ver else None
        items.append(SchemeCatalogItem(
            id=s.id,
            scheme_code=s.scheme_code,
            scheme_name=s.scheme_name,
            ministry=s.ministry or s.ministry_or_dept,
            department=s.department,
            description=s.description,
            active_version=ver_resp,
            total_versions=len(all_versions) if all_versions else 1,
            created_at=s.created_at,
        ))

    return items


@router.get("/schemes/{scheme_code}", response_model=SchemeCatalogItem, summary="Get Active Scheme Catalog Details")
async def get_scheme_by_code(
    scheme_code: str,
    uow: UnitOfWork = Depends(get_uow),
):
    """Fetch master scheme and its active version metadata by scheme code."""
    scheme = uow.schemes.get_by_code(scheme_code.upper())
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme '{scheme_code}' not found in persistent catalog."
        )

    active_ver = uow.schemes.get_active_version(scheme.scheme_code)
    all_versions = uow.schemes.list_versions(scheme.scheme_code)
    ver_resp = _map_version_model_to_response(active_ver) if active_ver else None

    return SchemeCatalogItem(
        id=scheme.id,
        scheme_code=scheme.scheme_code,
        scheme_name=scheme.scheme_name,
        ministry=scheme.ministry or scheme.ministry_or_dept,
        department=scheme.department,
        description=scheme.description,
        active_version=ver_resp,
        total_versions=len(all_versions) if all_versions else 1,
        created_at=scheme.created_at,
    )


@router.get("/schemes/{scheme_code}/versions", response_model=List[SchemeVersionResponse], summary="List Scheme Version History")
async def list_scheme_versions(
    scheme_code: str,
    uow: UnitOfWork = Depends(get_uow),
):
    """Fetch complete immutable version history for an authoritative scheme."""
    scheme = uow.schemes.get_by_code(scheme_code.upper())
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme '{scheme_code}' not found in catalog."
        )

    versions = uow.schemes.list_versions(scheme.scheme_code)
    return [_map_version_model_to_response(v) for v in versions]
