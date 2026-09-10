"""SQLAlchemy ORM model for the internship table."""
import json
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Session

from app.database import Base


class IndiaEligibility(str, PyEnum):
    LIKELY = "likely"
    UNCLEAR = "unclear"
    UNLIKELY = "unlikely"


class EmploymentType(str, PyEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    UNKNOWN = "unknown"


class InternshipType(str, PyEnum):
    SUMMER = "summer"
    WINTER = "winter"
    GENERAL = "general"
    UNKNOWN = "unknown"


class CompensationType(str, PyEnum):
    PAID = "paid"
    UNPAID = "unpaid"
    UNKNOWN = "unknown"


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)

    # Core fields
    title = Column(String(512), nullable=False, index=True)
    company_name = Column(String(256), nullable=False, index=True)
    company_url = Column(String(1024), nullable=True)
    description = Column(Text, nullable=True)

    # Source tracking
    source = Column(String(128), nullable=False)
    source_url = Column(String(2048), nullable=False)

    # Location / remote
    location = Column(String(256), nullable=True)
    remote = Column(Boolean, nullable=False, default=True, index=True)

    # India eligibility
    india_eligibility = Column(
        Enum(IndiaEligibility),
        nullable=False,
        default=IndiaEligibility.UNCLEAR,
        index=True,
    )

    # Job type
    employment_type = Column(
        Enum(EmploymentType),
        nullable=False,
        default=EmploymentType.UNKNOWN,
        index=True,
    )
    internship_type = Column(
        Enum(InternshipType),
        nullable=False,
        default=InternshipType.GENERAL,
        index=True,
    )

    # Compensation
    compensation_type = Column(
        Enum(CompensationType),
        nullable=False,
        default=CompensationType.UNKNOWN,
        index=True,
    )
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(8), nullable=True)
    salary_period = Column(String(32), nullable=True)  # e.g. "monthly", "yearly", "stipend"

    # Experience
    experience_min = Column(Float, nullable=True)  # years
    experience_max = Column(Float, nullable=True)  # years

    # Skills and tags stored as JSON strings
    # e.g. '["Python", "FastAPI", "PostgreSQL"]'
    _skills = Column("skills", Text, nullable=True, default="[]")
    _tags = Column("tags", Text, nullable=True, default="[]")

    # Dates
    posted_at = Column(DateTime, nullable=True, index=True)
    deadline = Column(DateTime, nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Ingestion metadata
    discovered_at = Column(DateTime, nullable=False, default=utcnow)
    last_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    # Deduplication fingerprint (normalized company+title+location hash)
    fingerprint = Column(String(128), nullable=False, unique=True, index=True)

    # Mark seed/demo records so they can be replaced with real data later
    is_seed = Column(Boolean, nullable=False, default=False, index=True)

    __table_args__ = (
        UniqueConstraint("fingerprint", name="uq_internship_fingerprint"),
        Index("ix_internships_posted_at_active", "posted_at", "is_active"),
        Index("ix_internships_eligibility_active", "india_eligibility", "is_active"),
    )

    # ---------------------------------------------------------------------------
    # Skills / Tags property helpers
    # ---------------------------------------------------------------------------

    @property
    def skills(self) -> list[str]:
        try:
            return json.loads(self._skills or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @skills.setter
    def skills(self, value: list[str]):
        self._skills = json.dumps(value or [])

    @property
    def tags(self) -> list[str]:
        try:
            return json.loads(self._tags or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @tags.setter
    def tags(self, value: list[str]):
        self._tags = json.dumps(value or [])

    def skills_text(self) -> str:
        """Space-joined skills for FTS indexing."""
        return " ".join(self.skills)

    def tags_text(self) -> str:
        """Space-joined tags for FTS indexing."""
        return " ".join(self.tags)

    def __repr__(self) -> str:
        return f"<Internship id={self.id} title={self.title!r} company={self.company_name!r}>"
