"""Database engine, session factory, and Base declaration."""

from app.config import settings
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite-specific: enable WAL mode and foreign keys on every connection
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_fts_table(db_engine=None):
    """Create the SQLite FTS5 virtual table for full-text search.

    This is idempotent — safe to call multiple times.
    FTS5 content= tables mirror the content table columns by actual name.
    """
    target = db_engine or engine
    with target.connect() as conn:
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS internships_fts
            USING fts5(
                id UNINDEXED,
                title,
                company_name,
                description,
                skills,
                tags,
                location,
                content='internships',
                content_rowid='id'
            )
        """))
        conn.commit()
