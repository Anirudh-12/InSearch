"""Pytest configuration and shared fixtures."""

import pytest
from app.database import Base, create_fts_table, get_db
from app.main import app
from app.models.internship import (
    CompensationType,
    EmploymentType,
    IndiaEligibility,
    Internship,
    InternshipType,
)
from app.services.deduplication import compute_fingerprint
from app.services.search import search_service
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ─── In-memory SQLite test database ──────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # StaticPool ensures all connections share the same in-memory SQLite
    # instance, which is critical for FTS virtual tables to be visible
    # across the different connections that SQLAlchemy uses internally.
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def set_sqlite_pragmas(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Create fresh tables and FTS for each test, yield a session, then drop."""
    # Drop FTS virtual table first (it's not managed by SQLAlchemy metadata)
    with test_engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS internships_fts"))
        conn.commit()

    Base.metadata.create_all(bind=test_engine)
    create_fts_table(test_engine)

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop FTS before SQLAlchemy tables to avoid constraint errors
        with test_engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS internships_fts"))
            conn.commit()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI test client with DB overridden to use the test session."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Internship factory ───────────────────────────────────────────────────────


def make_internship(
    db,
    title="Software Engineering Intern",
    company_name="Test Corp",
    source="Test",
    source_url=None,
    location="Remote – India",
    remote=True,
    india_eligibility=IndiaEligibility.LIKELY,
    employment_type=EmploymentType.FULL_TIME,
    internship_type=InternshipType.GENERAL,
    compensation_type=CompensationType.PAID,
    skills=None,
    tags=None,
    is_active=True,
    is_seed=False,
    posted_at=None,
    **kwargs,
) -> Internship:
    """Create and insert a test internship. Auto-generates fingerprint."""
    from datetime import datetime, timezone

    if source_url is None:
        import uuid

        source_url = f"https://example.com/jobs/{uuid.uuid4()}"

    fp = compute_fingerprint(company_name, title, location)

    internship = Internship(
        title=title,
        company_name=company_name,
        source=source,
        source_url=source_url,
        location=location,
        remote=remote,
        india_eligibility=india_eligibility,
        employment_type=employment_type,
        internship_type=internship_type,
        compensation_type=compensation_type,
        is_active=is_active,
        is_seed=is_seed,
        fingerprint=fp,
        posted_at=posted_at or datetime.now(timezone.utc).replace(tzinfo=None),
        **kwargs,
    )
    internship.skills = skills or []
    internship.tags = tags or []

    db.add(internship)
    db.flush()
    search_service.index_internship(db, internship)
    db.commit()
    return internship
