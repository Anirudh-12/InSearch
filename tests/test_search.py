"""Tests for search service (FTS5)."""

import pytest
from app.models.internship import IndiaEligibility, InternshipType
from app.services.search import search_service
from tests.conftest import make_internship


def test_search_returns_results(db):
    make_internship(
        db, title="Python Backend Engineering Intern", skills=["Python", "FastAPI"]
    )
    make_internship(
        db, title="Java Full Stack Developer Intern", skills=["Java", "Spring Boot"]
    )

    results, total = search_service.search(db, query="python")
    assert total >= 1
    titles = [r.title for r in results]
    assert any("Python" in t for t in titles)


def test_search_title_ranks_higher_than_description(db):
    """A result with query in the title should rank above one where it's only in description."""
    make_internship(
        db,
        title="Python Backend Engineering Intern",
        company_name="Acme A",
        source_url="https://example.com/a",
        skills=["Python"],
    )
    make_internship(
        db,
        title="Frontend Developer Intern",
        company_name="Acme B",
        source_url="https://example.com/b",
        description="This role requires some python scripting occasionally.",
        skills=["JavaScript"],
    )

    results, total = search_service.search(db, query="python backend")
    assert total >= 1
    # First result should be the Python Backend title
    assert "Python" in results[0].title


def test_search_backend(db):
    make_internship(
        db, title="Backend Engineering Intern", source_url="https://example.com/be"
    )
    make_internship(db, title="Frontend UI Intern", source_url="https://example.com/fe")

    results, total = search_service.search(db, query="backend")
    titles = [r.title for r in results]
    assert any("Backend" in t for t in titles)


def test_search_rust(db):
    make_internship(
        db,
        title="Rust Systems Intern",
        source_url="https://example.com/rust",
        skills=["Rust"],
    )
    make_internship(
        db,
        title="Python Developer",
        source_url="https://example.com/py",
        skills=["Python"],
    )

    results, total = search_service.search(db, query="rust")
    assert total >= 1
    assert any("Rust" in r.title for r in results)


def test_search_software_engineering(db):
    make_internship(
        db, title="Software Engineering Intern", source_url="https://example.com/se1"
    )
    make_internship(
        db,
        title="Software Development Internship",
        source_url="https://example.com/se2",
    )
    make_internship(
        db, title="Marketing Coordinator", source_url="https://example.com/mkt"
    )

    results, total = search_service.search(db, query="software engineering")
    assert total >= 1
    titles = [r.title for r in results]
    assert any("Software" in t for t in titles)


def test_empty_query_returns_all_active(db):
    make_internship(db, title="Python Intern", source_url="https://example.com/p")
    make_internship(db, title="Rust Intern", source_url="https://example.com/r")
    make_internship(
        db, title="Inactive", source_url="https://example.com/i", is_active=False
    )

    results, total = search_service.search(db, query=None)
    assert total == 2  # excludes inactive


def test_search_inactive_excluded(db):
    make_internship(
        db,
        title="Active Python Intern",
        source_url="https://example.com/act",
        is_active=True,
    )
    make_internship(
        db,
        title="Inactive Python Intern",
        source_url="https://example.com/ina",
        is_active=False,
    )

    results, total = search_service.search(db, query="python")
    active_titles = [r.title for r in results]
    assert not any("Inactive" in t for t in active_titles)


def test_filter_by_eligibility(db):
    from app.models.internship import IndiaEligibility

    make_internship(
        db,
        title="Likely India",
        source_url="https://example.com/l",
        india_eligibility=IndiaEligibility.LIKELY,
    )
    make_internship(
        db,
        title="Unlikely India",
        source_url="https://example.com/u",
        india_eligibility=IndiaEligibility.UNLIKELY,
    )

    results, total = search_service.search(
        db, india_eligibility=[IndiaEligibility.LIKELY]
    )
    assert total == 1
    assert results[0].india_eligibility == IndiaEligibility.LIKELY


def test_filter_by_internship_type(db):
    from app.models.internship import InternshipType

    make_internship(
        db,
        title="Summer Intern",
        source_url="https://example.com/s",
        internship_type=InternshipType.SUMMER,
    )
    make_internship(
        db,
        title="General Intern",
        source_url="https://example.com/g",
        internship_type=InternshipType.GENERAL,
    )

    results, total = search_service.search(db, internship_type=[InternshipType.SUMMER])
    assert total == 1
    assert results[0].internship_type == InternshipType.SUMMER


def test_filter_by_compensation(db):
    from app.models.internship import CompensationType

    make_internship(
        db,
        title="Paid Intern",
        source_url="https://example.com/paid",
        compensation_type=CompensationType.PAID,
    )
    make_internship(
        db,
        title="Unpaid Intern",
        source_url="https://example.com/unpaid",
        compensation_type=CompensationType.UNPAID,
    )

    results, total = search_service.search(
        db, compensation_type=[CompensationType.PAID]
    )
    assert total == 1
    assert results[0].compensation_type == CompensationType.PAID


def test_pagination(db):
    for i in range(25):
        make_internship(
            db,
            title=f"Intern {i:02d}",
            company_name=f"Company {i}",
            source_url=f"https://example.com/job-{i}",
        )

    results_p1, total = search_service.search(db, page=1, limit=10)
    results_p2, _ = search_service.search(db, page=2, limit=10)

    assert total == 25
    assert len(results_p1) == 10
    assert len(results_p2) == 10

    ids_p1 = {r.id for r in results_p1}
    ids_p2 = {r.id for r in results_p2}
    assert ids_p1.isdisjoint(ids_p2)  # No overlap between pages


def test_sort_newest(db):
    from datetime import datetime, timedelta, timezone

    old_date = (datetime.now(timezone.utc) - timedelta(days=30)).replace(tzinfo=None)
    new_date = (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None)

    make_internship(
        db, title="Old Intern", source_url="https://example.com/old", posted_at=old_date
    )
    make_internship(
        db,
        title="Recent Intern",
        source_url="https://example.com/new",
        posted_at=new_date,
    )

    results, _ = search_service.search(db, sort="newest")
    assert results[0].title == "Recent Intern"


def test_filter_by_skill(db):
    make_internship(
        db,
        title="Python Role",
        source_url="https://example.com/pyskill",
        skills=["Python", "FastAPI"],
    )
    make_internship(
        db,
        title="Java Role",
        source_url="https://example.com/javaskill",
        skills=["Java", "Spring Boot"],
    )

    results, total = search_service.search(db, skills=["Python"])
    assert total >= 1
    assert all("Python" in r.skills for r in results)
