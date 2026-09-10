"""Import internships from a JSON file.

Usage:
    python scripts/import_jobs.py path/to/jobs.json

The JSON file must be a top-level array of internship objects whose keys
match the InternshipCreate schema fields.

Example minimal record:
    {
        "title": "Backend Engineering Intern",
        "company_name": "Acme Corp",
        "source": "Wellfound",
        "source_url": "https://wellfound.com/jobs/acme-backend-intern"
    }

Output:
    Imported : 143
    Updated  : 21
    Duplicates skipped: 37
    Invalid  : 4
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, SessionLocal, create_fts_table, engine
from app.models.internship import Internship
from app.scrapers.json_source import JSONFileSource
from app.services.deduplication import compute_fingerprint, find_by_fingerprint, find_by_source_url
from app.services.eligibility import classify as classify_eligibility
from app.services.search import search_service


def run(file_path: str):
    if not Path(file_path).exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    create_fts_table(engine)

    db = SessionLocal()
    try:
        source = JSONFileSource(file_path)
        print(f"Reading {file_path}…")
        records = source.fetch()
        invalid_count = len(source.errors)

        if source.errors:
            print(f"\n{invalid_count} records failed validation:")
            for idx, err in source.errors[:10]:
                print(f"  Record #{idx}: {err}")
            if len(source.errors) > 10:
                print(f"  … and {len(source.errors) - 10} more.")

        print(f"\nProcessing {len(records)} valid records…")

        imported  = 0
        updated   = 0
        skipped   = 0
        errors    = 0

        for record in records:
            try:
                fp = compute_fingerprint(record.company_name, record.title, record.location)

                # Check for exact source URL match first
                existing_by_url = find_by_source_url(db, record.source_url)
                existing_by_fp  = find_by_fingerprint(db, fp)
                existing        = existing_by_url or existing_by_fp

                if existing:
                    # Update last_verified_at and is_active
                    existing.is_active = record.is_active
                    from app.models.internship import utcnow
                    existing.last_verified_at = utcnow()
                    db.flush()
                    search_service.index_internship(db, existing)
                    updated += 1
                    continue

                # Auto-classify eligibility if not explicitly set
                from app.models.internship import IndiaEligibility
                if record.india_eligibility == IndiaEligibility.UNCLEAR:
                    inferred = classify_eligibility(
                        location=record.location,
                        description=record.description,
                        title=record.title,
                    )
                    # Only override UNCLEAR — don't override explicit values
                    record_dict = record.model_dump()
                    record_dict['india_eligibility'] = inferred
                else:
                    record_dict = record.model_dump()

                internship = Internship(
                    **{k: v for k, v in record_dict.items() if k not in ("skills", "tags")},
                    fingerprint=fp,
                )
                internship.skills = record.skills
                internship.tags   = record.tags
                db.add(internship)
                db.flush()
                search_service.index_internship(db, internship)
                imported += 1

            except Exception as e:
                db.rollback()
                print(f"  ERROR processing record {record.title!r}: {e}")
                errors += 1

        db.commit()

        print(f"\nImport complete.")
        print(f"  Imported           : {imported}")
        print(f"  Updated            : {updated}")
        print(f"  Duplicates skipped : {skipped}")
        print(f"  Invalid (schema)   : {invalid_count}")
        print(f"  Errors             : {errors}")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_jobs.py <path/to/jobs.json>", file=sys.stderr)
        sys.exit(1)
    run(sys.argv[1])
