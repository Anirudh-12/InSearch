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
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


import asyncio
from starlette.concurrency import run_in_threadpool

def _run_all_scrapers():
    """Sync function to run scrapers in a background thread."""
    from app.database import SessionLocal
    from app.scrapers.unstop import UnstopSource
    from app.services.ingestion import ingest_source
    
    # Use max_pages=10 for periodic fresh fetches
    source = UnstopSource(max_pages=10)
    db = SessionLocal()
    try:
        logger.info("[Background] Running Unstop scraper...")
        result = ingest_source(source, db)
        logger.info(f"[Background] Finished Unstop: Inserted {result.inserted}, Updated {result.updated}")
    except Exception as e:
        logger.error(f"[Background] Scraper failed: {e}")
    finally:
        db.close()


async def periodic_scraper():
    """Background task that runs scrapers periodically."""
    # Wait a few seconds after startup before the first run
    await asyncio.sleep(10)
    while True:
        try:
            await run_in_threadpool(_run_all_scrapers)
        except asyncio.CancelledError:
            logger.info("Periodic scraper task cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in periodic scraper: {e}")
            
        # Wait 4 hours before the next run
        await asyncio.sleep(4 * 3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown lifecycle."""
    logger.info("Starting InSearch…")
    scraper_task = None
    try:
        Base.metadata.create_all(bind=engine)
        create_fts_table(engine)
            
        # Start the periodic background scraper
        scraper_task = asyncio.create_task(periodic_scraper())
    except Exception as e:
        logger.warning(f"Startup error (non-fatal in tests): {e}")

    yield

    if scraper_task:
        scraper_task.cancel()
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
