"""Search service.

Provides a clean abstraction over the underlying search engine (SQLite FTS5).
The SearchService interface can be replaced with Elasticsearch/OpenSearch later.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.models.internship import (
    CompensationType,
    EmploymentType,
    IndiaEligibility,
    Internship,
    InternshipType,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class SearchService(ABC):
    """Abstract search interface — swap implementations without changing the API."""

    @abstractmethod
    def search(
        self,
        db: Session,
        query: Optional[str] = None,
        skills: Optional[list[str]] = None,
        india_eligibility: Optional[list[IndiaEligibility]] = None,
        employment_type: Optional[list[EmploymentType]] = None,
        internship_type: Optional[list[InternshipType]] = None,
        compensation_type: Optional[list[CompensationType]] = None,
        remote_only: bool = True,
        posted_after: Optional[datetime] = None,
        experience: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        sort: str = "relevance",
    ) -> tuple[list[Internship], int]:
        """Return (results, total_count)."""
        ...

    @abstractmethod
    def rebuild_index(self, db: Session) -> None:
        """Sync the search index from the main table."""
        ...


# ---------------------------------------------------------------------------
# SQLite FTS5 implementation
# ---------------------------------------------------------------------------


class FTS5SearchService(SearchService):
    """Full-text search using SQLite FTS5 virtual table."""

    def search(
        self,
        db: Session,
        query: Optional[str] = None,
        skills: Optional[list[str]] = None,
        india_eligibility: Optional[list[IndiaEligibility]] = None,
        employment_type: Optional[list[EmploymentType]] = None,
        internship_type: Optional[list[InternshipType]] = None,
        compensation_type: Optional[list[CompensationType]] = None,
        remote_only: bool = True,
        posted_after: Optional[datetime] = None,
        experience: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        sort: str = "relevance",
    ) -> tuple[list[Internship], int]:
        offset = (page - 1) * limit

        if query and query.strip():
            results, total = self._fts_search(
                db,
                query.strip(),
                skills,
                india_eligibility,
                employment_type,
                internship_type,
                compensation_type,
                remote_only,
                posted_after,
                experience,
                page,
                limit,
                sort,
            )
        else:
            results, total = self._filter_search(
                db,
                skills,
                india_eligibility,
                employment_type,
                internship_type,
                compensation_type,
                remote_only,
                posted_after,
                experience,
                page,
                limit,
                sort,
            )

        return results, total

    def _fts_search(
        self,
        db: Session,
        query: str,
        skills,
        india_eligibility,
        employment_type,
        internship_type,
        compensation_type,
        remote_only,
        posted_after,
        experience,
        page,
        limit,
        sort,
    ) -> tuple[list[Internship], int]:
        """Use FTS5 match for full-text search then apply filters."""
        offset = (page - 1) * limit

        # Escape FTS5 special chars and build query string
        fts_query = self._build_fts_query(query)

        # Base: join FTS results to main table
        base_sql = """
            SELECT i.id, bm25(internships_fts) as rank
            FROM internships_fts
            JOIN internships i ON internships_fts.rowid = i.id
            WHERE internships_fts MATCH :fts_query
              AND i.is_active = 1
        """
        params: dict = {"fts_query": fts_query}

        base_sql, params = self._apply_filters(
            base_sql,
            params,
            skills,
            india_eligibility,
            employment_type,
            internship_type,
            compensation_type,
            remote_only,
            posted_after,
            experience,
        )

        # Count
        count_sql = f"SELECT COUNT(*) FROM ({base_sql})"
        total = db.execute(text(count_sql), params).scalar() or 0

        # Sort
        if sort == "newest":
            order = "i.posted_at DESC NULLS LAST, i.created_at DESC"
        elif sort == "oldest":
            order = "i.posted_at ASC NULLS LAST, i.created_at ASC"
        else:  # relevance (default for queries)
            order = "rank ASC, i.posted_at DESC NULLS LAST"

        data_sql = f"{base_sql} ORDER BY {order} LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        rows = db.execute(text(data_sql), params).fetchall()
        ids = [r[0] for r in rows]

        if not ids:
            return [], total

        # Fetch full ORM objects, preserving order
        objs = db.query(Internship).filter(Internship.id.in_(ids)).all()
        id_map = {o.id: o for o in objs}
        ordered = [id_map[i] for i in ids if i in id_map]
        return ordered, total

    def _filter_search(
        self,
        db: Session,
        skills,
        india_eligibility,
        employment_type,
        internship_type,
        compensation_type,
        remote_only,
        posted_after,
        experience,
        page,
        limit,
        sort,
    ) -> tuple[list[Internship], int]:
        """No query — pure ORM filter + sort."""
        q = db.query(Internship).filter(Internship.is_active == True)

        if remote_only:
            q = q.filter(Internship.remote == True)

        if india_eligibility:
            q = q.filter(Internship.india_eligibility.in_(india_eligibility))

        if employment_type:
            q = q.filter(Internship.employment_type.in_(employment_type))

        if internship_type:
            q = q.filter(Internship.internship_type.in_(internship_type))

        if compensation_type:
            q = q.filter(Internship.compensation_type.in_(compensation_type))

        if posted_after:
            q = q.filter(Internship.posted_at >= posted_after)

        if experience == "none":
            q = q.filter(
                (Internship.experience_min == None) | (Internship.experience_min == 0)
            )
        elif experience == "0_1":
            q = q.filter(
                (Internship.experience_min == None) | (Internship.experience_min <= 1)
            )

        if skills:
            # Filter rows whose skills JSON contains any of the requested skills
            for skill in skills:
                q = q.filter(Internship._skills.ilike(f'%"{skill}"%'))

        total = q.count()

        if sort == "oldest":
            q = q.order_by(
                Internship.posted_at.asc().nulls_last(), Internship.created_at.asc()
            )
        elif sort == "deadline":
            q = q.order_by(Internship.deadline.asc().nulls_last())
        else:  # newest (default for browse)
            q = q.order_by(
                Internship.posted_at.desc().nulls_last(), Internship.created_at.desc()
            )

        results = q.offset((page - 1) * limit).limit(limit).all()
        return results, total

    def _apply_filters(
        self,
        sql: str,
        params: dict,
        skills,
        india_eligibility,
        employment_type,
        internship_type,
        compensation_type,
        remote_only,
        posted_after,
        experience,
    ) -> tuple[str, dict]:
        """Append SQL filter clauses."""
        if remote_only:
            sql += " AND i.remote = 1"

        if india_eligibility:
            placeholders = ", ".join(f":eli_{i}" for i in range(len(india_eligibility)))
            sql += f" AND i.india_eligibility IN ({placeholders})"
            for i, v in enumerate(india_eligibility):
                params[f"eli_{i}"] = v.value if hasattr(v, "value") else v

        if employment_type:
            placeholders = ", ".join(f":et_{i}" for i in range(len(employment_type)))
            sql += f" AND i.employment_type IN ({placeholders})"
            for i, v in enumerate(employment_type):
                params[f"et_{i}"] = v.value if hasattr(v, "value") else v

        if internship_type:
            placeholders = ", ".join(f":it_{i}" for i in range(len(internship_type)))
            sql += f" AND i.internship_type IN ({placeholders})"
            for i, v in enumerate(internship_type):
                params[f"it_{i}"] = v.value if hasattr(v, "value") else v

        if compensation_type:
            placeholders = ", ".join(f":ct_{i}" for i in range(len(compensation_type)))
            sql += f" AND i.compensation_type IN ({placeholders})"
            for i, v in enumerate(compensation_type):
                params[f"ct_{i}"] = v.value if hasattr(v, "value") else v

        if posted_after:
            sql += " AND i.posted_at >= :posted_after"
            params["posted_after"] = posted_after.isoformat()

        if skills:
            for idx, skill in enumerate(skills):
                sql += f" AND i.skills LIKE :skill_{idx}"
                params[f"skill_{idx}"] = f'%"{skill}"%'

        return sql, params

    def _build_fts_query(self, query: str) -> str:
        """Convert a natural-language query into an FTS5 query string.

        Uses simple prefix matching: each token becomes token* so partial
        matches work (e.g. "python" matches "python" and "pythonic").
        Double-quotes around each token to prevent FTS special-char issues.
        """
        import re

        # Strip special FTS chars
        clean = re.sub(r"[^\w\s]", " ", query)
        tokens = clean.split()
        if not tokens:
            return '""'
        # Use quoted tokens with prefix for relevance
        parts = [f'"{t}"*' for t in tokens if t]
        return " OR ".join(parts)

    def rebuild_index(self, db: Session) -> None:
        """Rebuild FTS5 index from all active internships."""
        db.execute(text("DELETE FROM internships_fts"))
        db.execute(text("""
            INSERT INTO internships_fts(rowid, title, company_name, description, skills, tags, location)
            SELECT id, title, company_name,
                   COALESCE(description, ''),
                   COALESCE(skills, ''),
                   COALESCE(tags, ''),
                   COALESCE(location, '')
            FROM internships
        """))
        db.commit()


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------

search_service: SearchService = FTS5SearchService()
