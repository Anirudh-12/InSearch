"""Internship API routes."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.internship import (
    CompensationType,
    EmploymentType,
    IndiaEligibility,
    Internship,
    InternshipType,
)
from app.schemas.internship import InternshipDetail, InternshipResponse, SearchResponse
from app.services.search import search_service
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/internships", tags=["internships"])


@router.get("", response_model=SearchResponse)
def list_internships(
    q: Optional[str] = Query(None, description="Full-text search query"),
    skills: Optional[str] = Query(None, description="Comma-separated skill names"),
    india_eligibility: Optional[str] = Query(
        None, description="Comma-separated: likely,unclear,unlikely"
    ),
    employment_type: Optional[str] = Query(
        None, description="Comma-separated: full_time,part_time,contract,unknown"
    ),
    internship_type: Optional[str] = Query(
        None, description="Comma-separated: summer,winter,general,unknown"
    ),
    compensation_type: Optional[str] = Query(
        None, description="Comma-separated: paid,unpaid,unknown"
    ),
    remote_only: bool = Query(True, description="Only show remote internships"),
    posted_after: Optional[str] = Query(
        None, description="ISO date string — only show postings after this date"
    ),
    experience: Optional[str] = Query(
        None, description="Experience level: none, 0_1, 1_plus"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    sort: str = Query(
        "relevance",
        description="Sort order: relevance, newest, oldest, deadline",
        pattern="^(relevance|newest|oldest|deadline)$",
    ),
    db: Session = Depends(get_db),
):
    """Search and filter internships with pagination."""
    # Parse comma-separated filter params
    skills_list = _parse_list(skills)

    india_eli_list = None
    if india_eligibility:
        india_eli_list = []
        for v in india_eligibility.split(","):
            v = v.strip()
            try:
                india_eli_list.append(IndiaEligibility(v))
            except ValueError:
                pass

    emp_type_list = None
    if employment_type:
        emp_type_list = []
        for v in employment_type.split(","):
            v = v.strip()
            try:
                emp_type_list.append(EmploymentType(v))
            except ValueError:
                pass

    int_type_list = None
    if internship_type:
        int_type_list = []
        for v in internship_type.split(","):
            v = v.strip()
            try:
                int_type_list.append(InternshipType(v))
            except ValueError:
                pass

    comp_type_list = None
    if compensation_type:
        comp_type_list = []
        for v in compensation_type.split(","):
            v = v.strip()
            try:
                comp_type_list.append(CompensationType(v))
            except ValueError:
                pass

    posted_after_dt = None
    if posted_after:
        try:
            posted_after_dt = datetime.fromisoformat(posted_after)
        except ValueError:
            raise HTTPException(
                status_code=422, detail="posted_after must be a valid ISO date"
            )

    results, total = search_service.search(
        db=db,
        query=q,
        skills=skills_list or None,
        india_eligibility=india_eli_list,
        employment_type=emp_type_list,
        internship_type=int_type_list,
        compensation_type=comp_type_list,
        remote_only=remote_only,
        posted_after=posted_after_dt,
        experience=experience,
        page=page,
        limit=limit,
        sort=sort,
    )

    import math

    return SearchResponse(
        results=[InternshipResponse.model_validate(r) for r in results],
        page=page,
        limit=limit,
        total=total,
        pages=max(1, math.ceil(total / limit)),
        query=q,
    )


@router.get("/{internship_id}", response_model=InternshipDetail)
def get_internship(internship_id: int, db: Session = Depends(get_db)):
    """Get full details for a single internship."""
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    return InternshipDetail.model_validate(internship)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_list(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]
