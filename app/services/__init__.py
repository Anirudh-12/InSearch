from app.services.deduplication import (
    compute_fingerprint,
    find_by_fingerprint,
    is_duplicate,
)
from app.services.eligibility import classify as classify_eligibility
from app.services.search import FTS5SearchService, SearchService, search_service

__all__ = [
    "FTS5SearchService",
    "SearchService",
    "classify_eligibility",
    "compute_fingerprint",
    "find_by_fingerprint",
    "is_duplicate",
    "search_service",
]
