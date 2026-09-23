"""Shared ingestion pipeline.

Provides a single reusable function that takes any InternshipSource,
fetches records, deduplicates against the database, classifies India
eligibility, and inserts/updates records.

Used by:
  - scripts/run_scrapers.py  (CLI)
  - scripts/seed.py          (seed data)
  - scripts/import_jobs.py   (JSON import)
  - app/main.py              (startup seed)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.internship import IndiaEligibility, Internship, utcnow
from app.scrapers.base import InternshipSource
from app.schemas.internship import InternshipCreate
from app.services.deduplication import (
    compute_fingerprint,
    find_by_fingerprint,
    find_by_source_url,
)
from app.services.eligibility import classify as classify_eligibility

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class IngestionResult:
    """Summary of a single ingestion run."""

    source_name: str
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    fetch_errors: int = 0

    @property
    def total_processed(self) -> int:
        return self.inserted + self.updated + self.skipped + self.errors

    def __str__(self) -> str:
        return (
            f"[{self.source_name}] "
            f"inserted={self.inserted}, "
            f"updated={self.updated}, "
            f"skipped={self.skipped}, "
            f"errors={self.errors}"
        )


# ---------------------------------------------------------------------------
# Core ingestion function
# ---------------------------------------------------------------------------


def ingest_source(
    source: InternshipSource,
    db: Session,
    *,
    auto_classify: bool = True,
    update_existing: bool = True,
) -> IngestionResult:
    """Fetch from a source, deduplicate, and insert/update into the database.

    Args:
        source:          Any InternshipSource adapter.
        db:              Active SQLAlchemy session.
        auto_classify:   If True, run the India eligibility classifier on
                         records that have india_eligibility == UNCLEAR.
        update_existing: If True, update last_verified_at on duplicate records.

    Returns:
        IngestionResult with counts for inserted / updated / skipped / errors.
    """
    result = IngestionResult(source_name=source.source_name)

    # --- Fetch -----------------------------------------------------------------
    try:
        records: list[InternshipCreate] = source.fetch()
    except Exception as exc:
        logger.error(f"[Ingestion] Failed to fetch from {source.source_name!r}: {exc}")
        result.fetch_errors += 1
        return result

    logger.info(f"[Ingestion] {source.source_name}: fetched {len(records)} records.")

    # --- Process ---------------------------------------------------------------
    for record in records:
        try:
            _process_record(
                record=record,
                db=db,
                result=result,
                auto_classify=auto_classify,
                update_existing=update_existing,
            )
        except Exception as exc:
            logger.warning(
                f"[Ingestion] Unexpected error processing "
                f"{record.title!r} / {record.company_name!r}: {exc}"
            )
            result.errors += 1
            # Rollback the failed record without losing previous inserts
            try:
                db.rollback()
            except Exception:
                pass

    # --- Commit ----------------------------------------------------------------
    try:
        db.commit()
        logger.info(
            f"[Ingestion] {source.source_name}: "
            f"committed. {result}"
        )
    except Exception as exc:
        logger.error(f"[Ingestion] Commit failed: {exc}")
        db.rollback()
        result.errors += 1

    return result


# ---------------------------------------------------------------------------
# Per-record logic
# ---------------------------------------------------------------------------


def _process_record(
    record: InternshipCreate,
    db: Session,
    result: IngestionResult,
    auto_classify: bool,
    update_existing: bool,
) -> None:
    """Handle a single record: deduplicate, classify, insert or update."""
    fp = compute_fingerprint(record.company_name, record.title, record.location)

    # Check for exact URL match first, then fingerprint
    existing = find_by_source_url(db, record.source_url) or find_by_fingerprint(db, fp)

    if existing:
        if update_existing:
            existing.is_active = record.is_active
            existing.last_verified_at = utcnow()
            db.flush()
            result.updated += 1
        else:
            result.skipped += 1
        return

    # --- Auto-classify India eligibility for UNCLEAR records ---
    if auto_classify and record.india_eligibility == IndiaEligibility.UNCLEAR:
        inferred = classify_eligibility(
            location=record.location,
            description=record.description,
            title=record.title,
        )
        # Build a mutable dict so we can override the field
        record_dict = record.model_dump()
        record_dict["india_eligibility"] = inferred
    else:
        record_dict = record.model_dump()

    # --- Insert ----------------------------------------------------------------
    internship = Internship(
        **{k: v for k, v in record_dict.items() if k not in ("skills", "tags")},
        fingerprint=fp,
    )
    internship.skills = record.skills
    internship.tags = record.tags

    db.add(internship)
    db.flush()  # Assigns the id before FTS indexing

    result.inserted += 1
