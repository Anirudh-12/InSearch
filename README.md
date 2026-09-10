# InSearch

**Remote Software Engineering & CS Internship Search Engine for Indian Students**

InSearch is a minimal, focused search engine that helps CS/SWE students in India find remote internships they can actually apply to. Unlike broad job boards, InSearch classifies each listing for India eligibility and optimizes for utility of results, not volume.

---

## Features

- **Full-text search** over title, company, description, and skills using SQLite FTS5 with BM25 ranking
- **India eligibility classifier** — each listing is automatically classified as `likely`, `unclear`, or `unlikely` for applicants in India
- **Deduplication** — SHA-256 fingerprinting prevents duplicate listings
- **Filters** — eligibility, compensation type (paid/unpaid), internship type (summer/winter/general), employment type, and skills
- **Sort** — by relevance, newest, oldest, or deadline
- **Pagination** — page-based navigation with URL-synced state
- **Detail pages** — full listing view with skills, metadata, and link to original listing
- **Import scripts** — seed from built-in demo data or import JSON files

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Database | SQLite with FTS5 (WAL mode) |
| Migrations | Alembic |
| Frontend | Vanilla HTML/CSS/JS, Jinja2 templates |
| Testing | pytest, FastAPI TestClient |

---

## Quickstart

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (default settings work out of the box)
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Seed the database

```bash
python scripts/seed.py
```

### 6. Start the server

```bash
python run.py
# or directly:
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Importing Custom Data

To import internships from a JSON file:

```bash
python scripts/import_jobs.py path/to/jobs.json
```

Each record in the JSON array should match the `InternshipCreate` schema. Minimum required fields:

```json
{
  "title": "Software Engineering Intern",
  "company_name": "Acme Corp",
  "source": "Wellfound",
  "source_url": "https://wellfound.com/jobs/acme-swe-intern"
}
```

Optional fields include `description`, `skills`, `location`, `compensation_type`, `salary_min`, `salary_max`, `salary_currency`, `india_eligibility`, `posted_at`, `deadline`, etc.

---

## API Reference

| Endpoint | Description |
|----------|-------------|
| `GET /api/internships` | Search and filter internships |
| `GET /api/internships/{id}` | Full details for one internship |
| `GET /api/filters` | Available filter options |
| `GET /api/stats` | Database summary statistics |
| `GET /health` | Health / liveness check |

### Query Parameters for `/api/internships`

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Full-text search query |
| `india_eligibility` | comma-separated | `likely`, `unclear`, `unlikely` |
| `compensation_type` | comma-separated | `paid`, `unpaid`, `unknown` |
| `employment_type` | comma-separated | `full_time`, `part_time` |
| `internship_type` | comma-separated | `summer`, `winter`, `general` |
| `skills` | comma-separated | Skill names to filter by |
| `sort` | string | `relevance`, `newest`, `oldest`, `deadline` |
| `page` | int | Page number (default: 1) |
| `limit` | int | Results per page (default: 20, max: 100) |

Interactive API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs) when running in development mode.

---

## Running Tests

```bash
pytest tests/ -v
```

The test suite covers:
- API endpoint correctness (search, filtering, pagination, sorting)
- FTS5 search ranking behavior
- India eligibility classifier patterns
- Deduplication fingerprinting

---

## Project Structure

```
internship-search/
├── app/
│   ├── api/
│   │   ├── internships.py   # Search/detail endpoints
│   │   └── meta.py          # Filters, stats, health
│   ├── models/
│   │   └── internship.py    # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── internship.py    # Pydantic request/response schemas
│   ├── services/
│   │   ├── eligibility.py   # India eligibility classifier
│   │   ├── deduplication.py # Fingerprint-based dedup
│   │   └── search.py        # FTS5 search service
│   ├── scrapers/
│   │   ├── base.py          # Abstract source interface
│   │   ├── seed_source.py   # Built-in demo data (~38 records)
│   │   └── json_source.py   # JSON file importer
│   ├── templates/
│   │   ├── index.html       # Search page
│   │   └── internship.html  # Detail page
│   ├── config.py            # Settings (dotenv)
│   ├── database.py          # Engine, FTS table setup
│   └── main.py              # FastAPI app + routing
├── static/
│   ├── css/style.css        # Design system
│   └── js/
│       ├── app.js           # Search page JS
│       └── internship.js    # Detail page JS
├── scripts/
│   ├── seed.py              # Seed from demo data
│   └── import_jobs.py       # Bulk import from JSON
├── alembic/                 # DB migrations
├── tests/                   # pytest test suite
├── .env.example
├── requirements.txt
└── run.py                   # Entry point
```

---

## India Eligibility Classification

InSearch uses a rule-based classifier to tag each listing:

| Label | Meaning |
|-------|---------|
| **✓ Likely from India** | Listing explicitly mentions India, APAC, South Asia, or is open worldwide |
| **? India eligibility unclear** | No geo-restrictions mentioned — could be anywhere |
| **✕ Likely not from India** | Contains US-only, clearance required, or other India-excluding signals |

The classifier checks location, description, and title fields for keyword patterns. Negative signals (e.g., "US citizens only") take priority over positive ones.

---

## Design Principles

1. **Utility over volume** — A curated set of genuinely applicable listings beats a sea of irrelevant ones.
2. **No AI-generated content** — All classification is deterministic and auditable.
3. **Fast and simple** — SQLite + FTS5 is sufficient for the MVP; the search layer is decoupled so PostgreSQL/Elasticsearch can be swapped in later.
4. **Searchable, not scrapeable** — The frontend is minimal and search-engine-inspired; the API is the primary interface.
