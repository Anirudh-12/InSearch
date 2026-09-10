"""Seed the database with demo internship records.

Usage:
    python scripts/seed.py

This inserts all records from SeedSource that don't already exist.
It is safe to run multiple times (idempotent).
"""
import sys
from pathlib import Path

# Make sure 'app' is importable from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, SessionLocal, create_fts_table, engine
from app.models.internship import Internship
from app.scrapers.seed_source import SeedSource
from app.services.deduplication import compute_fingerprint, find_by_fingerprint
from app.services.search import search_service


def run():
    # Create tables + FTS
    Base.metadata.create_all(bind=engine)
    create_fts_table(engine)

    db = SessionLocal()
    try:
        source = SeedSource()
        records = source.fetch()

        inserted = 0
        skipped  = 0
        errors   = 0

        for record in records:
            try:
                fp = compute_fingerprint(record.company_name, record.title, record.location)
                if find_by_fingerprint(db, fp):
                    skipped += 1
                    continue

                internship = Internship(
                    **{k: v for k, v in record.model_dump().items() if k not in ("skills", "tags")},
                    fingerprint=fp,
                )
                internship.skills = record.skills
                internship.tags   = record.tags
                db.add(internship)
                db.flush()  # get the ID
                search_service.index_internship(db, internship)
                inserted += 1
            except Exception as e:
                db.rollback()
                print(f"  ERROR: {e} — record: {record.title!r}")
                errors += 1

        db.commit()
        print(f"\nSeed complete.")
        print(f"  Inserted : {inserted}")
        print(f"  Skipped  : {skipped} (already exist)")
        print(f"  Errors   : {errors}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
