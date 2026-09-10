"""Abstract base class for all internship data sources."""
from abc import ABC, abstractmethod

from app.schemas.internship import InternshipCreate


class InternshipSource(ABC):
    """Base class for all internship sources.

    Each source adapter must implement `fetch()` and return a list of
    normalized InternshipCreate objects. The ingestion pipeline handles
    deduplication, eligibility classification, and database insertion.
    """

    #: Human-readable name for this source (e.g. "Wellfound", "Internshala")
    source_name: str = "Unknown"

    @abstractmethod
    def fetch(self) -> list[InternshipCreate]:
        """Fetch and return normalized internship records from this source."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} source={self.source_name!r}>"
