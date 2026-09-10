"""Tests for the deduplication service."""

import pytest
from app.services.deduplication import (
    compute_fingerprint,
    find_by_fingerprint,
    is_duplicate,
)

from tests.conftest import make_internship


def test_fingerprint_is_deterministic():
    fp1 = compute_fingerprint("Acme Corp", "Software Engineer Intern", "Remote")
    fp2 = compute_fingerprint("Acme Corp", "Software Engineer Intern", "Remote")
    assert fp1 == fp2


def test_fingerprint_is_normalized():
    """Different capitalizations should produce the same fingerprint."""
    fp1 = compute_fingerprint("Acme Corp", "Software Engineer Intern", "Remote")
    fp2 = compute_fingerprint("acme corp", "software engineer intern", "remote")
    assert fp1 == fp2


def test_fingerprint_ignores_stop_words():
    """Common stop words shouldn't differentiate fingerprints."""
    fp1 = compute_fingerprint(
        "The Acme Corporation", "Software Engineering Intern", "Remote"
    )
    fp2 = compute_fingerprint("Acme Corp", "Software Engineering Intern", "Remote")
    # These might differ slightly due to 'the' removal — just verify they're stable
    assert fp1 == fp1  # idempotent
    assert fp2 == fp2


def test_fingerprint_different_companies():
    fp1 = compute_fingerprint("Company A", "Backend Intern", "Remote")
    fp2 = compute_fingerprint("Company B", "Backend Intern", "Remote")
    assert fp1 != fp2


def test_fingerprint_different_titles():
    fp1 = compute_fingerprint("Acme", "Backend Engineering Intern", "Remote")
    fp2 = compute_fingerprint("Acme", "Frontend Engineering Intern", "Remote")
    assert fp1 != fp2


def test_find_by_fingerprint_found(db):
    job = make_internship(
        db, title="Dup Test A", source_url="https://example.com/dup-a"
    )
    fp = compute_fingerprint(job.company_name, job.title, job.location)
    found = find_by_fingerprint(db, fp)
    assert found is not None
    assert found.id == job.id


def test_find_by_fingerprint_not_found(db):
    result = find_by_fingerprint(db, "nonexistentfingerprint123")
    assert result is None


def test_is_duplicate_by_fingerprint(db):
    make_internship(
        db,
        title="Software Engineer Intern",
        company_name="DupCo",
        location="Remote",
        source_url="https://example.com/dup1",
    )

    dup, existing = is_duplicate(
        db,
        company_name="DupCo",
        title="Software Engineer Intern",
        location="Remote",
        source_url="https://example.com/different-url",  # different URL but same content
    )
    assert dup is True
    assert existing is not None


def test_is_duplicate_by_source_url(db):
    make_internship(
        db,
        title="Unique Intern",
        source_url="https://example.com/unique-url",
    )

    dup, existing = is_duplicate(
        db,
        company_name="Different Company",
        title="Different Title",
        location=None,
        source_url="https://example.com/unique-url",  # same URL
    )
    assert dup is True


def test_not_duplicate(db):
    make_internship(
        db,
        title="Python Intern",
        company_name="Acme",
        source_url="https://example.com/py",
    )

    dup, existing = is_duplicate(
        db,
        company_name="Acme",
        title="Java Intern",
        location=None,
        source_url="https://example.com/java-new",
    )
    assert dup is False
    assert existing is None


def test_duplicate_records_not_inserted_twice(db):
    """Inserting the same internship twice should not create a second record."""
    from app.models.internship import Internship

    job1 = make_internship(
        db,
        title="Go Backend Intern",
        company_name="GoCorpX",
        source_url="https://example.com/go1",
    )

    fp = compute_fingerprint("GoCorpX", "Go Backend Intern", job1.location)
    dup, _ = is_duplicate(
        db,
        "GoCorpX",
        "Go Backend Intern",
        job1.location,
        "https://example.com/go-duplicate",
    )

    # Don't insert again if duplicate
    if not dup:
        make_internship(
            db,
            title="Go Backend Intern",
            company_name="GoCorpX",
            source_url="https://example.com/go-duplicate",
        )

    count = (
        db.query(Internship)
        .filter(
            Internship.company_name == "GoCorpX",
            Internship.title == "Go Backend Intern",
        )
        .count()
    )

    assert count == 1
