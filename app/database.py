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

    This uses triggers to automatically keep the FTS index in sync with the
    internships table, preventing rowid mismatch corruption.
    """
    target = db_engine or engine
    with target.connect() as conn:
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS internships_fts
            USING fts5(
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
        
        # Triggers to keep FTS index up to date
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS internships_ai AFTER INSERT ON internships BEGIN
              INSERT INTO internships_fts(rowid, title, company_name, description, skills, tags, location)
              VALUES (new.id, new.title, new.company_name, coalesce(new.description,''), coalesce(new.skills,''), coalesce(new.tags,''), coalesce(new.location,''));
            END;
        """))
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS internships_ad AFTER DELETE ON internships BEGIN
              INSERT INTO internships_fts(internships_fts, rowid, title, company_name, description, skills, tags, location)
              VALUES('delete', old.id, old.title, old.company_name, coalesce(old.description,''), coalesce(old.skills,''), coalesce(old.tags,''), coalesce(old.location,''));
            END;
        """))
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS internships_au AFTER UPDATE ON internships BEGIN
              INSERT INTO internships_fts(internships_fts, rowid, title, company_name, description, skills, tags, location)
              VALUES('delete', old.id, old.title, old.company_name, coalesce(old.description,''), coalesce(old.skills,''), coalesce(old.tags,''), coalesce(old.location,''));
              INSERT INTO internships_fts(rowid, title, company_name, description, skills, tags, location)
              VALUES (new.id, new.title, new.company_name, coalesce(new.description,''), coalesce(new.skills,''), coalesce(new.tags,''), coalesce(new.location,''));
            END;
        """))
        conn.commit()
