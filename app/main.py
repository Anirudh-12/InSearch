"""FastAPI application factory and startup."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.internships import router as internships_router
from app.api.meta import router as meta_router
from app.config import settings
from app.database import Base, SessionLocal, create_fts_table, engine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Seed helper
# ---------------------------------------------------------------------------


def _seed_database(db):
    """Insert seed internships on first startup."""
    from app.models.internship import Internship
    from app.scrapers.seed_source import SeedSource
    from app.services.deduplication import compute_fingerprint, find_by_fingerprint
    from app.services.search import search_service

    source = SeedSource()
    records = source.fetch()

    inserted = 0
    for record in records:
        fp = compute_fingerprint(record.company_name, record.title, record.location)
        if find_by_fingerprint(db, fp):
            continue
        internship = Internship(
            **{k: v for k, v in record.model_dump().items() if k not in ("skills", "tags")},
            fingerprint=fp,
        )
        internship.skills = record.skills
        internship.tags = record.tags
        db.add(internship)
        db.flush()
        search_service.index_internship(db, internship)
        inserted += 1

    db.commit()
    logger.info(f"Seeded {inserted} internships.")


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown lifecycle."""
    logger.info("Starting InSearch…")
    try:
        Base.metadata.create_all(bind=engine)
        create_fts_table(engine)

        db = SessionLocal()
        try:
            from app.models.internship import Internship

            count = db.query(Internship).count()
            if count == 0:
                logger.info("Database is empty — loading seed data…")
                _seed_database(db)
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Startup error (non-fatal in tests): {e}")

    yield

    logger.info("InSearch shutdown.")


# ---------------------------------------------------------------------------
# App creation
# ---------------------------------------------------------------------------

app = FastAPI(
    title="InSearch",
    description="Remote Software Engineering Internship Search Engine for Indian Students",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static files & templates
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(internships_router)
app.include_router(meta_router)

# ---------------------------------------------------------------------------
# Frontend routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Serve the main search page."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/internship/{internship_id}", response_class=HTMLResponse)
def internship_detail(request: Request, internship_id: int):
    """Serve the internship detail page."""
    return templates.TemplateResponse(request, "internship.html")
