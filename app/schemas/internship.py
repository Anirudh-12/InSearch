"""Pydantic schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.models.internship import (
    CompensationType,
    EmploymentType,
    IndiaEligibility,
    InternshipType,
)
from pydantic import BaseModel, ConfigDict, field_validator

# ---------------------------------------------------------------------------
# Base / shared schema
# ---------------------------------------------------------------------------


class InternshipBase(BaseModel):
    title: str
    company_name: str
    company_url: Optional[str] = None
    description: Optional[str] = None
    source: str
    source_url: str
    location: Optional[str] = None
    remote: bool = True
    india_eligibility: IndiaEligibility = IndiaEligibility.UNCLEAR
    employment_type: EmploymentType = EmploymentType.UNKNOWN
    internship_type: InternshipType = InternshipType.GENERAL
    compensation_type: CompensationType = CompensationType.UNKNOWN
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    skills: list[str] = []
    tags: list[str] = []
    posted_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    is_active: bool = True
    is_seed: bool = False


# ---------------------------------------------------------------------------
# Create schema (used for ingestion)
# ---------------------------------------------------------------------------


class InternshipCreate(InternshipBase):
    """Schema used when creating a new internship record."""

    pass


# ---------------------------------------------------------------------------
# Response schemas (used for API output)
# ---------------------------------------------------------------------------


class InternshipResponse(BaseModel):
    """Compact listing card — used in search results."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str
    company_url: Optional[str] = None
    source: str
    source_url: str
    location: Optional[str] = None
    remote: bool
    india_eligibility: IndiaEligibility
    employment_type: EmploymentType
    internship_type: InternshipType
    compensation_type: CompensationType
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    skills: list[str] = []
    tags: list[str] = []
    posted_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    @field_validator("skills", "tags", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        import json

        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []


class InternshipDetail(InternshipResponse):
    """Full detail view — includes description."""

    description: Optional[str] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    discovered_at: datetime
    last_verified_at: Optional[datetime] = None
    updated_at: datetime
    is_seed: bool = False


# ---------------------------------------------------------------------------
# Search / filter response schemas
# ---------------------------------------------------------------------------


class SearchResponse(BaseModel):
    """Paginated list of internship results."""

    results: list[InternshipResponse]
    page: int
    limit: int
    total: int
    pages: int
    query: Optional[str] = None


class FilterOptions(BaseModel):
    """Available filter options returned by /api/filters."""

    skills: list[str]
    india_eligibility: list[str]
    employment_types: list[str]
    internship_types: list[str]
    compensation_types: list[str]
    sources: list[str]


class StatsResponse(BaseModel):
    """Summary statistics returned by /api/stats."""

    total_internships: int
    active_internships: int
    seed_internships: int
    sources: dict[str, int]
    eligibility_breakdown: dict[str, int]


class HealthResponse(BaseModel):
    status: str
    environment: str
    db_ok: bool
