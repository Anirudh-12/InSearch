"""Tests for India eligibility classifier."""

import pytest
from app.models.internship import IndiaEligibility
from app.services.eligibility import classify

# ─── Likely ──────────────────────────────────────────────────────────────────


def test_explicit_india_location():
    result = classify(location="Remote – India")
    assert result == IndiaEligibility.LIKELY


def test_india_in_description():
    result = classify(description="Candidates can work remotely from India.")
    assert result == IndiaEligibility.LIKELY


def test_apac_location():
    result = classify(location="Remote – APAC")
    assert result == IndiaEligibility.LIKELY


def test_south_asia_location():
    result = classify(location="Remote – South Asia")
    assert result == IndiaEligibility.LIKELY


# ─── Unclear ─────────────────────────────────────────────────────────────────


def test_worldwide_location():
    result = classify(location="Remote – Worldwide")
    assert result == IndiaEligibility.UNCLEAR


def test_global_description():
    result = classify(description="We are a global team. Work from anywhere.")
    assert result == IndiaEligibility.UNCLEAR


def test_fully_remote():
    result = classify(location="Fully Remote")
    assert result == IndiaEligibility.UNCLEAR


def test_no_location_info():
    result = classify(location=None, description=None, title=None)
    assert result == IndiaEligibility.UNCLEAR


def test_empty_strings():
    result = classify(location="", description="", title="")
    assert result == IndiaEligibility.UNCLEAR


# ─── Unlikely ────────────────────────────────────────────────────────────────


def test_us_only_location():
    result = classify(location="Remote – US Only")
    assert result == IndiaEligibility.UNLIKELY


def test_us_work_authorization_required():
    result = classify(description="US work authorization required.")
    assert result == IndiaEligibility.UNLIKELY


def test_must_be_located_in_us():
    result = classify(description="Candidates must be located in the United States.")
    assert result == IndiaEligibility.UNLIKELY


def test_remote_within_us():
    result = classify(location="Remote within the United States")
    assert result == IndiaEligibility.UNLIKELY


def test_north_america_only():
    result = classify(location="Remote – North America")
    assert result == IndiaEligibility.UNLIKELY


def test_security_clearance():
    result = classify(description="Applicants must hold a security clearance.")
    assert result == IndiaEligibility.UNLIKELY


def test_us_citizen():
    result = classify(description="Must be a US citizen or permanent resident.")
    assert result == IndiaEligibility.UNLIKELY


# ─── Priority: negative > positive ───────────────────────────────────────────


def test_negative_overrides_positive():
    """Even if 'India' appears in description, explicit US-only should dominate."""
    result = classify(
        location="Remote – US Only",
        description="Our product is used by teams in India and the US. Must be a US citizen.",
    )
    assert result == IndiaEligibility.UNLIKELY
