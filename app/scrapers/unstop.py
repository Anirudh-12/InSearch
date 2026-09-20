"""Unstop internship source adapter.

Fetches work-from-home software engineering internships from Unstop's
public API (https://unstop.com/api/public/opportunity/search-result).

The /api/public/* path is explicitly allowed in Unstop's robots.txt.
No authentication is required. We identify WFH listings, apply a SWE
keyword filter to exclude non-technical roles, and map all available
fields to InternshipCreate.

Rate limit: 1 request/second (configurable). Max 50 pages per run
(500 listings) by default, sorted by most recent.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from html import unescape
from typing import Any

import httpx

from app.models.internship import (
    CompensationType,
    EmploymentType,
    IndiaEligibility,
    InternshipType,
)
from app.schemas.internship import InternshipCreate
from app.scrapers.base import InternshipSource
from app.services.eligibility import classify as classify_eligibility

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://unstop.com/api/public/opportunity/search-result"
SOURCE_NAME = "Unstop"
SOURCE_BASE = "https://unstop.com"

# SWE / CS keyword allowlist — a listing is included if its title or
# workfunction tags contain at least one of these terms.
#
# IMPORTANT: Use longer, unambiguous phrases here to avoid substring false
# positives. Short/ambiguous tokens go into SWE_WORD_PATTERNS below.
SWE_KEYWORDS: frozenset[str] = frozenset(
    [
        "software",
        "developer",
        "development engineer",
        "software development",
        "web development",
        "backend",
        "back-end",
        "back end",
        "frontend",
        "front-end",
        "front end",
        "full stack",
        "fullstack",
        "full-stack",
        "python",
        "javascript",
        "typescript",
        "golang",
        "c++",
        "devops",
        "devsecops",
        "flutter",
        "react native",
        "data engineer",
        "data engineering",
        "machine learning",
        "ml engineer",
        "ai engineer",
        "deep learning",
        "computer science",
        "site reliability",
        "embedded",
        "firmware",
        "blockchain",
        "cybersecurity",
        "security engineer",
        "game developer",
        "game development",
        "networking engineer",
        "web developer",
        "platform engineer",
        "infrastructure engineer",
        "cloud engineer",
        "cloud developer",
        "test engineer",
        "qa engineer",
        "mobile developer",
        "android developer",
    ]
)

# Short / ambiguous keywords that need word-boundary matching (\b) to avoid
# false positives like 'unity' in 'community', 'rust' in 'trust', etc.
_SWE_WORD_PATTERN_STRINGS: list[str] = [
    r"\bengineer\b",
    r"\bengineering\b",
    r"\bjava\b",           # not 'javascript' (already in KEYWORDS)
    r"\brust\b",
    r"\bios\b",
    r"\bapi\b",
    r"\bandroid\b",
    r"\bmobile\b",
    r"\bcloud\b",
    r"\bsystems\b",
    r"\bunity\b",
    r"\bunreal\b",
    r"\bsre\b",
    r"\bdatabase\b",
    r"\binfrastructure\b",
    r"\bdevsecops\b",
]
_SWE_WORD_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE) for p in _SWE_WORD_PATTERN_STRINGS
]

# Non-SWE title exclusion patterns — checked BEFORE the SWE match.
# If a title matches any of these, it is excluded even if it contains
# SWE keywords like 'mobile' or 'engineer' (e.g. 'mobile marketing engineer')
_SWE_EXCLUSION_STRINGS: list[str] = [
    r"\bcampus ambassador\b",
    r"\bbrand ambassador\b",
    r"\bsocial media\b",
    r"\bdigital marketing\b",
    r"\bcontent (creator|writer|marketing|manager|creation)\b",
    r"\bmarketing (intern|manager|coordinator|specialist|executive)\b",
    r"\b(sales|business development|bd)\s+(intern|associate|executive|consultant|manager)\b",
    r"\bhr\s+(intern|executive|manager|operations)\b",
    r"\bhuman resource\b",
    r"\brecruiter\b",
    r"\bpublic relations\b",
    r"\bgraphic design(er|ing)?\b",
    r"\bui[\s/]?ux design(er|ing)?\b",
    r"\bproduct design(er|ing)?\b",
    r"\bvisual design(er|ing)?\b",
    r"\bseo\s+specialist\b",
    r"\bcopywriter\b",
    r"\bfinance\s+(intern|analyst|manager)\b",
    r"\baccounting\s+(intern|executive)\b",
    r"\boperations (intern|executive|manager|coordinator)\b",
    r"\bprogram (coordinator|manager|intern|management)\b",
    r"\boutreach\s+(and|&)?\s+(partner|coordinator)\b",
    r"\bpsychology\b",
    r"\bevent\s+(management|coordinator|planner)\b",
]
_SWE_EXCLUSION_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE) for p in _SWE_EXCLUSION_STRINGS
]

# Currency icon → ISO code mapping from Unstop
_CURRENCY_MAP: dict[str, str] = {
    "fa-rupee": "INR",
    "fa-rupee-sign": "INR",
    "fa-dollar-sign": "USD",
    "fa-euro-sign": "EUR",
    "fa-pound-sign": "GBP",
    "fa-yen-sign": "JPY",
    "inr": "INR",
    "usd": "USD",
    "eur": "EUR",
    "gbp": "GBP",
}

# Timing → EmploymentType
_TIMING_MAP: dict[str, EmploymentType] = {
    "full_time": EmploymentType.FULL_TIME,
    "fulltime": EmploymentType.FULL_TIME,
    "part_time": EmploymentType.PART_TIME,
    "parttime": EmploymentType.PART_TIME,
}

# pay_in → salary period labels
_PAY_IN_MAP: dict[str, str] = {
    "monthly": "monthly",
    "hourly": "hourly",
    "lumpsum": "lumpsum",
    "stipend": "monthly",
}

# Default request headers to appear as a normal browser client
_HEADERS: dict[str, str] = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://unstop.com/internships",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_html(html_text: str | None) -> str | None:
    """Remove HTML tags and decode entities from a string."""
    if not html_text:
        return None
    try:
        from bs4 import BeautifulSoup  # type: ignore[import-untyped]
        text = BeautifulSoup(html_text, "html.parser").get_text(separator="\n")
    except Exception:
        # Fallback: crude regex strip
        text = re.sub(r"<[^>]+>", " ", html_text)
    return unescape(text).strip() or None


def _parse_date(value: Any) -> datetime | None:
    """Parse a date value that may be an ISO string, UNIX timestamp, or None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc).replace(tzinfo=None)
        except (OSError, OverflowError, ValueError):
            return None
    if isinstance(value, str):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def _map_currency(raw: str | None) -> str | None:
    """Map Unstop's icon-class currency codes to ISO codes."""
    if not raw:
        return None
    return _CURRENCY_MAP.get(raw.lower().strip(), raw.upper().strip())


def _is_swe_relevant(title: str, workfunctions: list[str]) -> bool:
    """Return True if the listing is SWE-relevant based on title + workfunction.

    Three-step check:
    0. Exclusion blocklist on title — if matched, return False immediately.
       Catches non-SWE roles (campus ambassador, marketing, sales, etc.) that
       might otherwise trigger SWE keyword matches.
    1. Plain substring on title + workfunctions for long, unambiguous phrases.
    2. Word-boundary regex on TITLE ONLY for short/ambiguous tokens.
    """
    title_lower = title.lower()

    # Step 0: fast exclusion — reject known non-SWE patterns
    if any(p.search(title_lower) for p in _SWE_EXCLUSION_PATTERNS):
        return False

    haystack_full = (title + " " + " ".join(workfunctions)).lower()

    # Step 1: plain substring on full haystack (title + workfunctions)
    if any(kw in haystack_full for kw in SWE_KEYWORDS):
        return True

    # Step 2: word-boundary regex on TITLE ONLY
    return any(p.search(title_lower) for p in _SWE_WORD_PATTERNS)


def _build_source_url(raw_url: str | None, opp_id: int | None) -> str:
    """Build a valid Unstop listing URL."""
    if raw_url:
        url = raw_url.strip()
        if url.startswith("http"):
            return url
        return SOURCE_BASE + "/" + url.lstrip("/")
    if opp_id:
        return f"{SOURCE_BASE}/internship/{opp_id}"
    return SOURCE_BASE


def _extract_skills(opportunity: dict) -> list[str]:
    """Extract skill names from the Unstop opportunity object."""
    skills: list[str] = []
    # From required_skills array
    for skill_item in opportunity.get("required_skills") or []:
        if isinstance(skill_item, dict):
            name = skill_item.get("skill_name") or skill_item.get("name")
            if name and isinstance(name, str):
                skills.append(name.strip())
    # Also from skillsets arrays
    for skill_item in opportunity.get("skillsets") or []:
        if isinstance(skill_item, dict):
            name = skill_item.get("skill_name") or skill_item.get("name")
            if name and isinstance(name, str) and name not in skills:
                skills.append(name.strip())
    return skills


def _extract_workfunctions(opportunity: dict) -> list[str]:
    """Extract workfunction / domain tag names."""
    tags: list[str] = []
    for wf in opportunity.get("workfunction") or []:
        if isinstance(wf, dict):
            name = wf.get("name")
            if name and isinstance(name, str):
                tags.append(name.strip())
    return tags


def _extract_location(opportunity: dict) -> str | None:
    """Build a human-readable location string."""
    # Check city / country in address_with_country_logo
    address_info = opportunity.get("address_with_country_logo") or {}
    city = address_info.get("city") or ""
    country = address_info.get("country") or ""
    region = (opportunity.get("region") or "").strip()

    if region.lower() in ("online", "work from home", "wfh", "remote"):
        if city and country:
            return f"Remote ({city}, {country})"
        return "Remote"

    parts = [p.strip() for p in [city, country] if p.strip()]
    if parts:
        return ", ".join(parts)
    return region or None


def _map_internship_type(opportunity: dict) -> InternshipType:
    """Detect summer/winter internship from title or dates."""
    title = (opportunity.get("title") or "").lower()
    if "summer" in title:
        return InternshipType.SUMMER
    if "winter" in title:
        return InternshipType.WINTER
    return InternshipType.GENERAL


def _map_to_internship_create(opportunity: dict) -> InternshipCreate | None:
    """Map a raw Unstop API opportunity dict to an InternshipCreate schema.

    Returns None if the record is missing required fields, is not remote,
    or is not SWE-relevant.
    """
    title = (opportunity.get("title") or "").strip()
    if not title:
        return None

    # Organisation
    org = opportunity.get("organisation") or opportunity.get("organization") or {}
    company_name = (org.get("name") or "").strip()
    if not company_name:
        company_name = (opportunity.get("company_name") or "").strip()
    if not company_name:
        return None

    org_public_url = org.get("public_url") or org.get("slug") or ""
    if org_public_url:
        company_url = SOURCE_BASE + "/" + org_public_url.lstrip("/")
    else:
        company_url = SOURCE_BASE

    # Source URL
    opp_id = opportunity.get("id")
    seo_url = opportunity.get("seo_url") or opportunity.get("slug") or ""
    source_url = _build_source_url(seo_url, opp_id)

    # Description
    raw_desc = (
        opportunity.get("details")
        or opportunity.get("description")
        or opportunity.get("detail")
    )
    description = _strip_html(raw_desc)

    # Location
    location = _extract_location(opportunity)

    # Remote detection
    region = (opportunity.get("region") or "").lower().strip()
    job_detail = opportunity.get("jobDetail") or opportunity.get("job_detail") or {}
    job_type = (job_detail.get("type") or job_detail.get("job_type") or "").lower()
    remote = region in ("online", "wfh", "remote", "work from home") or job_type in (
        "wfh",
        "remote",
        "online",
    )

    # Only include remote listings
    if not remote:
        return None

    # Skills and workfunction tags
    skills = _extract_skills(opportunity)
    workfunctions = _extract_workfunctions(opportunity)

    # SWE filter
    if not _is_swe_relevant(title, workfunctions + skills):
        return None

    # Salary / compensation
    paid_unpaid = (job_detail.get("paid_unpaid") or "").lower()
    if paid_unpaid == "paid":
        compensation_type = CompensationType.PAID
    elif paid_unpaid == "unpaid":
        compensation_type = CompensationType.UNPAID
    else:
        compensation_type = CompensationType.UNKNOWN

    salary_min_raw = job_detail.get("min_salary") or job_detail.get("salary_min")
    salary_max_raw = job_detail.get("max_salary") or job_detail.get("salary_max")
    try:
        salary_min = float(salary_min_raw) if salary_min_raw not in (None, "", 0, "0") else None
    except (TypeError, ValueError):
        salary_min = None
    try:
        salary_max = float(salary_max_raw) if salary_max_raw not in (None, "", 0, "0") else None
    except (TypeError, ValueError):
        salary_max = None

    raw_currency = job_detail.get("currency") or job_detail.get("salary_currency")
    salary_currency = _map_currency(raw_currency)

    raw_pay_in = (job_detail.get("pay_in") or "").lower()
    salary_period = _PAY_IN_MAP.get(raw_pay_in, raw_pay_in or None)

    # Employment type
    raw_timing = (job_detail.get("timing") or job_detail.get("employment_type") or "").lower()
    employment_type = _TIMING_MAP.get(raw_timing, EmploymentType.UNKNOWN)

    # Experience
    try:
        experience_min = float(job_detail.get("min_experience") or 0) or None
    except (TypeError, ValueError):
        experience_min = None
    try:
        experience_max = float(job_detail.get("max_experience") or 0) or None
    except (TypeError, ValueError):
        experience_max = None

    # Dates
    posted_at = _parse_date(
        opportunity.get("approved_date")
        or opportunity.get("published_at")
        or opportunity.get("created_at")
    )

    regn = opportunity.get("regnRequirements") or opportunity.get("regn_requirements") or {}
    deadline = _parse_date(
        regn.get("end_regn_dt")
        or opportunity.get("end_date")
        or opportunity.get("deadline")
    )

    # Active status
    status = (opportunity.get("status") or "").upper()
    reg_status = (regn.get("reg_status") or "").upper()
    is_active = status == "LIVE" and reg_status != "FINISHED"

    # India eligibility — run the classifier on location + description
    india_eligibility = classify_eligibility(
        location=location,
        description=description,
        title=title,
    )

    # Internship type
    internship_type = _map_internship_type(opportunity)

    return InternshipCreate(
        title=title,
        company_name=company_name,
        company_url=company_url,
        description=description,
        source=SOURCE_NAME,
        source_url=source_url,
        location=location,
        remote=remote,
        india_eligibility=india_eligibility,
        employment_type=employment_type,
        internship_type=internship_type,
        compensation_type=compensation_type,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        salary_period=salary_period,
        experience_min=experience_min,
        experience_max=experience_max,
        skills=skills,
        tags=workfunctions,
        posted_at=posted_at,
        deadline=deadline,
        is_active=is_active,
        is_seed=False,
    )


# ---------------------------------------------------------------------------
# Source adapter
# ---------------------------------------------------------------------------


class UnstopSource(InternshipSource):
    """Fetch SWE-relevant WFH internships from Unstop's public API.

    Usage:
        source = UnstopSource(max_pages=50)
        records = source.fetch()   # list[InternshipCreate]

    The API path /api/public/* is explicitly Allowed in Unstop's robots.txt.
    We add a 1-second delay between page requests to be polite.
    """

    source_name = SOURCE_NAME

    def __init__(
        self,
        max_pages: int = 100,
        per_page: int = 25,
        request_delay: float = 1.0,
        timeout: float = 15.0,
        empty_batch_stop: int = 8,
    ) -> None:
        self.max_pages = max_pages
        self.per_page = per_page
        self.request_delay = request_delay
        self.timeout = timeout
        # Stop early if N consecutive pages yield 0 SWE results
        self.empty_batch_stop = empty_batch_stop
        self._stats: dict[str, int] = {
            "fetched": 0,
            "swe_filtered_in": 0,
            "non_remote_skipped": 0,
            "parse_errors": 0,
        }

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fetch(self) -> list[InternshipCreate]:
        """Fetch and return SWE WFH internships from Unstop, newest first.

        Stops early if `empty_batch_stop` consecutive pages all yield 0
        SWE-relevant listings (avoids scanning deep barren sections).
        """
        results: list[InternshipCreate] = []
        consecutive_empty = 0

        with httpx.Client(headers=_HEADERS, timeout=self.timeout, follow_redirects=True) as client:
            for page in range(1, self.max_pages + 1):
                batch = self._fetch_page(client, page)
                if batch is None:
                    # Hard error — stop
                    break
                if not batch:
                    # Empty page — we've exhausted results
                    logger.info(f"[Unstop] No results on page {page}. Stopping.")
                    break

                self._stats["fetched"] += len(batch)
                converted = self._convert_batch(batch)
                results.extend(converted)

                if converted:
                    consecutive_empty = 0
                else:
                    consecutive_empty += 1
                    if consecutive_empty >= self.empty_batch_stop:
                        logger.info(
                            f"[Unstop] {consecutive_empty} consecutive pages with 0 SWE "
                            f"results on page {page}. Stopping early."
                        )
                        break

                logger.info(
                    f"[Unstop] Page {page}: {len(batch)} raw, "
                    f"{len(converted)} SWE-relevant. Total so far: {len(results)}"
                )

                if page < self.max_pages:
                    time.sleep(self.request_delay)

        logger.info(
            f"[Unstop] Fetch complete. "
            f"Raw fetched={self._stats['fetched']}, "
            f"SWE in={self._stats['swe_filtered_in']}, "
            f"non-remote skipped={self._stats['non_remote_skipped']}, "
            f"parse errors={self._stats['parse_errors']}"
        )
        return results

    @property
    def stats(self) -> dict[str, int]:
        """Return fetch statistics from the last fetch() call."""
        return dict(self._stats)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_page(self, client: httpx.Client, page: int) -> list[dict] | None:
        """Fetch a single page from the Unstop API. Returns None on hard error."""
        params = {
            "opportunity": "internships",
            "per_page": self.per_page,
            "page": page,
            "job_type": "wfh",  # work-from-home filter
            "sort_by": "published_at",  # most recent first
        }

        for attempt in range(1, 4):  # up to 3 retries
            try:
                response = client.get(BASE_URL, params=params)
                response.raise_for_status()
                payload = response.json()
                return self._extract_opportunities(payload)
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    f"[Unstop] HTTP {exc.response.status_code} on page {page} "
                    f"(attempt {attempt}/3)"
                )
                if exc.response.status_code in (429, 503):
                    time.sleep(attempt * 5)  # back-off on rate limit
                else:
                    break
            except httpx.RequestError as exc:
                logger.warning(
                    f"[Unstop] Request error on page {page} (attempt {attempt}/3): {exc}"
                )
                time.sleep(attempt * 2)
            except Exception as exc:
                logger.error(f"[Unstop] Unexpected error on page {page}: {exc}")
                return None

        return None

    def _extract_opportunities(self, payload: Any) -> list[dict]:
        """Extract the list of opportunity dicts from the API response payload."""
        if not isinstance(payload, dict):
            return []
        data = payload.get("data") or {}
        if isinstance(data, dict):
            items = (
                data.get("data")
                or data.get("items")
                or data.get("opportunities")
                or data.get("results")
                or []
            )
        elif isinstance(data, list):
            items = data
        else:
            items = []
        return [item for item in items if isinstance(item, dict)]

    def _convert_batch(self, batch: list[dict]) -> list[InternshipCreate]:
        """Convert a batch of raw API dicts to InternshipCreate objects."""
        results: list[InternshipCreate] = []
        for raw in batch:
            try:
                record = _map_to_internship_create(raw)
                if record is None:
                    region = (raw.get("region") or "").lower()
                    if region not in ("online", "wfh", "remote"):
                        self._stats["non_remote_skipped"] += 1
                    continue
                self._stats["swe_filtered_in"] += 1
                results.append(record)
            except Exception as exc:
                logger.warning(
                    f"[Unstop] Parse error for record id={raw.get('id')}: {exc}"
                )
                self._stats["parse_errors"] += 1
        return results
