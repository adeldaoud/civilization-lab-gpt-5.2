"""Base class for empirical source adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from civlab.data.models import SourceSummary


class DataSourceAdapter(ABC):
    """Abstract interface for empirical source adapters."""

    key: str

    @abstractmethod
    def describe(self) -> SourceSummary:
        """Return static metadata about the source and its assets."""

