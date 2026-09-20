"""CLI entry point for running one or more internship scrapers.

Usage:
    python scripts/run_scrapers.py
    python scripts/run_scrapers.py --sources unstop
    python scripts/run_scrapers.py --sources unstop --max-pages 5
    python scripts/run_scrapers.py --max-pages 50 --delay 1.5

Options:
    --sources   Comma-separated list of source names to run.
                Default: all available sources.
                Available: unstop
    --max-pages Number of pages to fetch per source (default: 50 = 500 records).
    --delay     Seconds to wait between page requests (default: 1.0).
    --dry-run   Fetch and print stats but do NOT write to the database.

Examples:
    # Quick test: fetch only 3 pages from Unstop
    python scripts/run_scrapers.py --sources unstop --max-pages 3

    # Full production run
    python scripts/run_scrapers.py --max-pages 50

    # Dry run to see what would be fetched
    python scripts/run_scrapers.py --max-pages 5 --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Make 'app' importable from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_scrapers")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def _build_registry(max_pages: int, delay: float) -> dict:
    """Return a mapping of source_name → InternshipSource instance."""
    from app.scrapers.unstop import UnstopSource

    return {
        "unstop": UnstopSource(max_pages=max_pages, per_page=25, request_delay=delay),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(
    sources: list[str],
    max_pages: int,
    delay: float,
    dry_run: bool,
) -> int:
    """Execute the scraping pipeline. Returns exit code (0 = success)."""
    from app.database import Base, SessionLocal, create_fts_table, engine
    from app.services.ingestion import IngestionResult, ingest_source

    # Ensure DB schema is up to date
    Base.metadata.create_all(bind=engine)
    create_fts_table(engine)

    registry = _build_registry(max_pages=max_pages, delay=delay)

    # Validate requested sources
    unknown = [s for s in sources if s not in registry]
    if unknown:
        logger.error(f"Unknown source(s): {', '.join(unknown)}")
        logger.error(f"Available: {', '.join(registry)}")
        return 1

    active_sources = {name: src for name, src in registry.items() if name in sources}
    logger.info(f"Running {len(active_sources)} source(s): {', '.join(active_sources)}")

    overall_inserted = 0
    overall_updated = 0
    overall_skipped = 0
    overall_errors = 0
    all_results: list[IngestionResult] = []

    for name, source in active_sources.items():
        print(f"\n{'=' * 60}")
        print(f"  Source: {name.upper()}")
        print(f"{'=' * 60}")

        start = time.time()

        if dry_run:
            print("  [DRY RUN] Fetching records (no DB writes)…")
            try:
                records = source.fetch()
                elapsed = time.time() - start
                print(f"  Fetched:  {len(records)} SWE-relevant records")
                print(f"  Elapsed:  {elapsed:.1f}s")
                # Show a few sample titles
                for r in records[:5]:
                    print(f"    • {r.title} @ {r.company_name}")
                if len(records) > 5:
                    print(f"    … and {len(records) - 5} more")
            except Exception as exc:
                logger.error(f"Dry-run fetch failed: {exc}")
            continue

        db = SessionLocal()
        try:
            result = ingest_source(source, db)
            elapsed = time.time() - start
            all_results.append(result)

            overall_inserted += result.inserted
            overall_updated += result.updated
            overall_skipped += result.skipped
            overall_errors += result.errors

            print(f"  Inserted : {result.inserted}")
            print(f"  Updated  : {result.updated}")
            print(f"  Skipped  : {result.skipped}")
            print(f"  Errors   : {result.errors}")
            print(f"  Elapsed  : {elapsed:.1f}s")

            # Print scraper-specific stats if available
            if hasattr(source, "stats"):
                stats = source.stats
                print(f"\n  Scraper stats:")
                print(f"    Raw fetched    : {stats.get('fetched', '?')}")
                print(f"    SWE filter in  : {stats.get('swe_filtered_in', '?')}")
                print(f"    Non-remote out : {stats.get('non_remote_skipped', '?')}")
                print(f"    Parse errors   : {stats.get('parse_errors', '?')}")
        finally:
            db.close()

    if not dry_run and all_results:
        print(f"\n{'=' * 60}")
        print("  TOTAL SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Inserted : {overall_inserted}")
        print(f"  Updated  : {overall_updated}")
        print(f"  Skipped  : {overall_skipped}")
        print(f"  Errors   : {overall_errors}")
        print()

    return 0 if overall_errors == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run InSearch scraping pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--sources",
        default="unstop",
        help="Comma-separated source names to run (default: unstop)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Max pages to fetch per source (default: 100 = ~2500 raw listings)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds between page requests (default: 1.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch but do not write to the database",
    )

    args = parser.parse_args()
    source_list = [s.strip().lower() for s in args.sources.split(",") if s.strip()]

    sys.exit(
        run(
            sources=source_list,
            max_pages=args.max_pages,
            delay=args.delay,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
