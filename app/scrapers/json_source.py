"""JSON file source adapter.

Reads a JSON file containing a list of internship records and returns
normalized InternshipCreate objects. Used by the import script.
"""

import json
from pathlib import Path

from app.schemas.internship import InternshipCreate
from app.scrapers.base import InternshipSource
from pydantic import ValidationError


class JSONFileSource(InternshipSource):
    """Load internships from a JSON file.

    Expected format: a JSON array of internship objects whose keys match
    the InternshipCreate schema fields.
    """

    source_name = "JSON Import"

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def fetch(self) -> list[InternshipCreate]:
        """Load and validate records from the JSON file.

        Returns only records that pass Pydantic validation.
        Invalid records are logged but skipped (the caller tracks counts).
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {self.file_path}")

        with open(self.file_path, encoding="utf-8") as f:
            raw = json.load(f)

        if not isinstance(raw, list):
            raise ValueError(
                "JSON file must contain a top-level array of internship objects."
            )

        results: list[InternshipCreate] = []
        self._errors: list[tuple[int, str]] = []

        for idx, record in enumerate(raw):
            try:
                results.append(InternshipCreate(**record))
            except (ValidationError, TypeError) as e:
                self._errors.append((idx, str(e)))

        return results

    @property
    def errors(self) -> list[tuple[int, str]]:
        """Return validation errors from the last fetch() call."""
        return getattr(self, "_errors", [])
