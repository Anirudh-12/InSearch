from app.services.deduplication import (
    compute_fingerprint,
    find_by_fingerprint,
    is_duplicate,
)
from app.services.eligibility import classify as classify_eligibility
from app.services.ingestion import IngestionResult, ingest_source
from app.services.search import FTS5SearchService, SearchService, search_service

__all__ = [
    "FTS5SearchService",
    "IngestionResult",
    "SearchService",
    "classify_eligibility",
    "compute_fingerprint",
    "find_by_fingerprint",
    "ingest_source",
    "is_duplicate",
    "search_service",
]
