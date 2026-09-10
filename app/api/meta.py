"""Meta / utility API routes: filters, stats, health."""

from app.config import settings
from app.database import get_db
from app.models.internship import (
    CompensationType,
    EmploymentType,
    IndiaEligibility,
    Internship,
    InternshipType,
)
from app.schemas.internship import FilterOptions, HealthResponse, StatsResponse
from fastapi import APIRouter, Depends
from sqlalchemy import func, text
from sqlalchemy.orm import Session

router = APIRouter(tags=["meta"])

# All skills available for filtering
ALL_SKILLS = [
    "Python",
    "Java",
    "C++",
    "C",
    "Rust",
    "Go",
    "JavaScript",
    "TypeScript",
    "React",
    "FastAPI",
    "Django",
    "Flask",
    "Node.js",
    "SQL",
    "PostgreSQL",
    "AWS",
    "Azure",
    "GCP",
    "Docker",
    "Kubernetes",
    "Git",
    "Machine Learning",
    "Data Engineering",
    "Spring Boot",
    "Vue.js",
    "GraphQL",
    "React Native",
    "Android",
    "iOS",
    "Swift",
    "Kotlin",
    "Flutter",
    "Dart",
    "Haskell",
    "OCaml",
    "LLVM",
    "Compilers",
    "Security",
    "Embedded",
    "RTOS",
    "CUDA",
    "PyTorch",
    "Open Source",
]


@router.get("/api/filters", response_model=FilterOptions)
def get_filters(db: Session = Depends(get_db)):
    """Return available filter options for the frontend."""
    sources = [
        row[0]
        for row in db.query(Internship.source)
        .filter(Internship.is_active == True)
        .distinct()
        .order_by(Internship.source)
        .all()
    ]

    return FilterOptions(
        skills=sorted(ALL_SKILLS),
        india_eligibility=[e.value for e in IndiaEligibility],
        employment_types=[e.value for e in EmploymentType],
        internship_types=[e.value for e in InternshipType],
        compensation_types=[e.value for e in CompensationType],
        sources=sources,
    )


@router.get("/api/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Return summary statistics about the internship database."""
    total = db.query(func.count(Internship.id)).scalar() or 0
    active = (
        db.query(func.count(Internship.id))
        .filter(Internship.is_active == True)
        .scalar()
        or 0
    )
    seed = (
        db.query(func.count(Internship.id)).filter(Internship.is_seed == True).scalar()
        or 0
    )

    source_rows = (
        db.query(Internship.source, func.count(Internship.id))
        .filter(Internship.is_active == True)
        .group_by(Internship.source)
        .all()
    )
    sources_dict = {row[0]: row[1] for row in source_rows}

    elig_rows = (
        db.query(Internship.india_eligibility, func.count(Internship.id))
        .filter(Internship.is_active == True)
        .group_by(Internship.india_eligibility)
        .all()
    )
    elig_dict = {
        row[0].value if hasattr(row[0], "value") else row[0]: row[1]
        for row in elig_rows
    }

    return StatsResponse(
        total_internships=total,
        active_internships=active,
        seed_internships=seed,
        sources=sources_dict,
        eligibility_breakdown=elig_dict,
    )


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Liveness / health check endpoint."""
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        environment=settings.ENVIRONMENT,
        db_ok=db_ok,
    )
