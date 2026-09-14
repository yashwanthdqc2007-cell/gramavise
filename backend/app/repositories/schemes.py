"""Scheme & Versioned Scheme Catalog persistence repository."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from app.models.scheme import Scheme, SchemeVersion, SchemeStatusEnum
from app.repositories.base import AbstractRepository


class SchemeRepository(AbstractRepository[Scheme]):
    """Encapsulates database access and queries for government Scheme masters and SchemeVersions."""

    def get_by_id(self, scheme_id: str) -> Optional[Scheme]:
        """Fetch master Scheme by primary key ID."""
        stmt = select(Scheme).where(Scheme.id == scheme_id)
        return self.session.scalar(stmt)

    def get_by_code(self, scheme_code: str) -> Optional[Scheme]:
        """Fetch master Scheme by unique scheme code."""
        stmt = select(Scheme).where(Scheme.scheme_code == scheme_code)
        return self.session.scalar(stmt)

    def get_active_version(self, scheme_code: str) -> Optional[SchemeVersion]:
        """Fetch the current ACTIVE version of a scheme."""
        stmt = select(SchemeVersion).where(
            and_(
                SchemeVersion.scheme_code == scheme_code,
                SchemeVersion.status == SchemeStatusEnum.ACTIVE,
            )
        ).order_by(SchemeVersion.created_at.desc())
        return self.session.scalar(stmt)

    def get_version(self, scheme_code: str, version: str) -> Optional[SchemeVersion]:
        """Fetch a specific historical or active version of a scheme."""
        stmt = select(SchemeVersion).where(
            and_(
                SchemeVersion.scheme_code == scheme_code,
                SchemeVersion.version == version,
            )
        )
        return self.session.scalar(stmt)

    def list_active(self) -> List[SchemeVersion]:
        """List all currently ACTIVE scheme versions in the catalog."""
        stmt = select(SchemeVersion).where(
            SchemeVersion.status == SchemeStatusEnum.ACTIVE
        ).order_by(SchemeVersion.scheme_code.asc())
        return list(self.session.scalars(stmt).all())

    def list_schemes(self) -> List[Scheme]:
        """List all master schemes registered in the catalog."""
        stmt = select(Scheme).order_by(Scheme.scheme_name.asc())
        return list(self.session.scalars(stmt).all())

    def list_all(self) -> List[Scheme]:
        """Alias for list_schemes for backward compatibility."""
        return self.list_schemes()

    def list_versions(self, scheme_code: str) -> List[SchemeVersion]:
        """List all versions (ACTIVE, SUPERSEDED, RETIRED, DRAFT) for a specific scheme code."""
        stmt = select(SchemeVersion).where(
            SchemeVersion.scheme_code == scheme_code
        ).order_by(SchemeVersion.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def add(self, scheme: Scheme) -> Scheme:
        """Register a new Scheme master entity."""
        self.session.add(scheme)
        return scheme

    def create(self, scheme: Scheme) -> Scheme:
        """Alias for add."""
        return self.add(scheme)

    def add_scheme(self, scheme: Scheme) -> Scheme:
        """Register a new Scheme master entity."""
        return self.add(scheme)

    def add_version(self, version: SchemeVersion) -> SchemeVersion:
        """Register an immutable SchemeVersion entity."""
        self.session.add(version)
        return version
