"""Tests for the FastAPI API endpoints."""
import math

import pytest
from fastapi.testclient import TestClient

from app.models.internship import CompensationType, EmploymentType, IndiaEligibility, InternshipType
from tests.conftest import make_internship


# ─── GET /health ─────────────────────────────────────────────────────────────

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["db_ok"] is True


# ─── GET /api/filters ────────────────────────────────────────────────────────

def test_get_filters(client):
    res = client.get("/api/filters")
    assert res.status_code == 200
    data = res.json()
    assert "skills" in data
    assert "Python" in data["skills"]
    assert "india_eligibility" in data
    assert "likely" in data["india_eligibility"]


# ─── GET /api/stats ──────────────────────────────────────────────────────────

def test_get_stats(client, db):
    make_internship(db, title="Stats Test", source_url="https://example.com/stats")
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_internships"] >= 1
    assert "sources" in data
    assert "eligibility_breakdown" in data


# ─── GET /api/internships ─────────────────────────────────────────────────────

def test_list_internships_empty(client, db):
    res = client.get("/api/internships")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["results"] == []


def test_list_internships_basic(client, db):
    make_internship(db, title="Python Backend Intern", source_url="https://example.com/pbi",
                    skills=["Python"])
    res = client.get("/api/internships")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["results"][0]["title"] == "Python Backend Intern"


def test_search_query_param(client, db):
    make_internship(db, title="Rust Systems Intern",  source_url="https://example.com/r1")
    make_internship(db, title="Python Backend Intern",source_url="https://example.com/p1")

    res = client.get("/api/internships?q=rust")
    assert res.status_code == 200
    data = res.json()
    titles = [r["title"] for r in data["results"]]
    assert any("Rust" in t for t in titles)


def test_filter_india_eligibility_likely(client, db):
    make_internship(db, title="Likely",   source_url="https://example.com/l",
                    india_eligibility=IndiaEligibility.LIKELY)
    make_internship(db, title="Unlikely", source_url="https://example.com/u",
                    india_eligibility=IndiaEligibility.UNLIKELY)

    res = client.get("/api/internships?india_eligibility=likely")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["results"][0]["india_eligibility"] == "likely"


def test_filter_compensation_paid(client, db):
    make_internship(db, title="Paid",   source_url="https://example.com/paid",
                    compensation_type=CompensationType.PAID)
    make_internship(db, title="Unpaid", source_url="https://example.com/unpaid",
                    compensation_type=CompensationType.UNPAID)

    res = client.get("/api/internships?compensation_type=paid")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["results"][0]["compensation_type"] == "paid"


def test_filter_internship_type(client, db):
    make_internship(db, title="Summer", source_url="https://example.com/sum",
                    internship_type=InternshipType.SUMMER)
    make_internship(db, title="Winter", source_url="https://example.com/win",
                    internship_type=InternshipType.WINTER)

    res = client.get("/api/internships?internship_type=summer")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["results"][0]["internship_type"] == "summer"


def test_filter_skills(client, db):
    make_internship(db, title="Python Role", source_url="https://example.com/py",
                    skills=["Python", "FastAPI"])
    make_internship(db, title="Java Role",   source_url="https://example.com/jv",
                    skills=["Java"])

    res = client.get("/api/internships?skills=Python")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert all("Python" in r["skills"] for r in data["results"])


def test_pagination_page1_page2(client, db):
    for i in range(25):
        make_internship(
            db,
            title=f"Intern Pagination {i:02d}",
            company_name=f"PageCo {i}",
            source_url=f"https://example.com/pg-{i}",
        )

    r1 = client.get("/api/internships?page=1&limit=10").json()
    r2 = client.get("/api/internships?page=2&limit=10").json()

    assert r1["total"] == 25
    assert r1["pages"] == 3
    assert len(r1["results"]) == 10
    assert len(r2["results"]) == 10

    ids1 = {r["id"] for r in r1["results"]}
    ids2 = {r["id"] for r in r2["results"]}
    assert ids1.isdisjoint(ids2)


def test_pagination_metadata(client, db):
    for i in range(5):
        make_internship(db, title=f"Meta Intern {i}", source_url=f"https://example.com/meta-{i}")

    res = client.get("/api/internships?page=1&limit=3").json()
    assert res["page"] == 1
    assert res["limit"] == 3
    assert res["total"] == 5
    assert res["pages"] == 2


def test_sort_newest(client, db):
    from datetime import datetime, timedelta, timezone
    old = (datetime.now(timezone.utc) - timedelta(days=30)).replace(tzinfo=None)
    new = (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None)

    make_internship(db, title="Old Post",    source_url="https://example.com/old", posted_at=old)
    make_internship(db, title="Recent Post", source_url="https://example.com/new", posted_at=new)

    res = client.get("/api/internships?sort=newest").json()
    assert res["results"][0]["title"] == "Recent Post"


def test_sort_oldest(client, db):
    from datetime import datetime, timedelta, timezone
    old = (datetime.now(timezone.utc) - timedelta(days=30)).replace(tzinfo=None)
    new = (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None)

    make_internship(db, title="Old Post",    source_url="https://example.com/oldst", posted_at=old)
    make_internship(db, title="Recent Post", source_url="https://example.com/newest", posted_at=new)

    res = client.get("/api/internships?sort=oldest").json()
    assert res["results"][0]["title"] == "Old Post"


def test_inactive_excluded(client, db):
    make_internship(db, title="Active",   source_url="https://example.com/act", is_active=True)
    make_internship(db, title="Inactive", source_url="https://example.com/ina", is_active=False)

    res = client.get("/api/internships").json()
    titles = [r["title"] for r in res["results"]]
    assert "Active" in titles
    assert "Inactive" not in titles


# ─── GET /api/internships/{id} ────────────────────────────────────────────────

def test_get_internship_found(client, db):
    job = make_internship(db, title="Detail Test", source_url="https://example.com/detail")

    res = client.get(f"/api/internships/{job.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == job.id
    assert data["title"] == "Detail Test"
    assert "description" in data  # Detail schema includes description


def test_get_internship_not_found(client):
    res = client.get("/api/internships/999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# ─── Frontend routes ──────────────────────────────────────────────────────────

def test_homepage_serves_html(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "InSearch" in res.text


def test_detail_page_serves_html(client, db):
    job = make_internship(db, title="HTML Page Test", source_url="https://example.com/htmltest")
    res = client.get(f"/internship/{job.id}")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
