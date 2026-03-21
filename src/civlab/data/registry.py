"""Registry for empirical data source adapters."""

from __future__ import annotations

from civlab.data.models import DataRole
from civlab.data.sources.base import DataSourceAdapter


class SourceRegistry:
    """Tracks empirical source adapters by stable key."""

    def __init__(self) -> None:
        self._sources: dict[str, DataSourceAdapter] = {}

    def register(self, source: DataSourceAdapter) -> None:
        if source.key in self._sources:
            raise ValueError(f"Source '{source.key}' is already registered.")
        self._sources[source.key] = source

    def get(self, key: str) -> DataSourceAdapter:
        try:
            return self._sources[key]
        except KeyError as exc:
            raise KeyError(f"Unknown source '{key}'.") from exc

    def list_sources(self) -> tuple[DataSourceAdapter, ...]:
        return tuple(self._sources[key] for key in sorted(self._sources))

    def find_sources_for_roles(self, required_roles: frozenset[DataRole]) -> tuple[DataSourceAdapter, ...]:
        return tuple(
            source
            for source in self.list_sources()
            if required_roles.intersection(source.describe().roles)
        )

