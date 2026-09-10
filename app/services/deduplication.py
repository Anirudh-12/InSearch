"""Deduplication service.

Generates a normalized fingerprint from an internship record and checks
for existing duplicates in the database.
"""

import hashlib
import re
import unicodedata

from app.models.internship import Internship
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

_PUNCTUATION_RE = re.compile(r"[^\w\s]")
_WHITESPACE_RE = re.compile(r"\s+")

_STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "in",
    "at",
    "for",
    "to",
    "on",
    "is",
    "are",
    "was",
    "be",
    "inc",
    "llc",
    "ltd",
    "corp",
    "pvt",
    "co",
    "company",
    "technologies",
    "solutions",
    "services",
}


def _normalize_token(text: str) -> str:
    """Lowercase, strip accents, remove punctuation, collapse whitespace."""
    text = text.lower().strip()
    # Strip unicode accents
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    # Remove punctuation
    text = _PUNCTUATION_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def _tokenize(text: str) -> list[str]:
    tokens = _normalize_token(text).split()
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 0]


def compute_fingerprint(
    company_name: str,
    title: str,
    location: str | None = None,
) -> str:
    """Compute a deterministic deduplication fingerprint.

    The fingerprint is a SHA-256 hex digest of the sorted, normalized token
    set from company_name + title + location. Using sorted tokens means minor
    word-order differences don't create false duplicates.
    """
    company_tokens = sorted(_tokenize(company_name or ""))
    title_tokens = sorted(_tokenize(title or ""))
    location_tokens = sorted(_tokenize(location or ""))

    # Build a canonical string: company||title||location
    canonical = "|".join(
        [
            " ".join(company_tokens),
            " ".join(title_tokens),
            " ".join(location_tokens),
        ]
    )

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


def find_by_fingerprint(db: Session, fingerprint: str) -> Internship | None:
    """Return an existing internship with the given fingerprint, or None."""
    return db.query(Internship).filter(Internship.fingerprint == fingerprint).first()


def find_by_source_url(db: Session, source_url: str) -> Internship | None:
    """Return an existing internship with the exact same source URL, or None."""
    return db.query(Internship).filter(Internship.source_url == source_url).first()


def is_duplicate(
    db: Session,
    company_name: str,
    title: str,
    location: str | None,
    source_url: str,
) -> tuple[bool, Internship | None]:
    """Check whether a potential new internship is a duplicate.

    Returns (is_dup, existing_record). Checks source URL first (exact match),
    then falls back to fingerprint comparison.
    """
    existing = find_by_source_url(db, source_url)
    if existing:
        return True, existing

    fp = compute_fingerprint(company_name, title, location)
    existing = find_by_fingerprint(db, fp)
    if existing:
        return True, existing

    return False, None
