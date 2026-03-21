"""Shared models for empirical sources, downloads, and canonical tables."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class DataRole(StrEnum):
    GOVERNANCE = "governance"
    BUREAUCRACY = "bureaucracy"
    DEVELOPMENT_FINANCE = "development_finance"
    GEOSPATIAL = "geospatial"
    ELITE_PERCEPTIONS = "elite_perceptions"
    PROJECT_PERFORMANCE = "project_performance"
    CONFLICT = "conflict"
    MACRO = "macro"
    DEMOGRAPHY = "demography"


class Granularity(StrEnum):
    COUNTRY_YEAR = "country_year"
    COUNTRY_CROSS_SECTION = "country_cross_section"
    PROJECT = "project"
    GEOCODED_PROJECT = "geocoded_project"
    SURVEY_AGGREGATE = "survey_aggregate"


class AssetFormat(StrEnum):
    CSV = "csv"
    ZIP = "zip"
    JSON = "json"
    API_JSON = "api_json"
    HTML = "html"


class CanonicalTable(StrEnum):
    COUNTRY_YEAR = "country_year"
    PROJECT_EXPOSURE = "project_exposure"


@dataclass(frozen=True)
class DatasetAsset:
    slug: str
    title: str
    url: str
    description: str
    roles: frozenset[DataRole]
    granularities: frozenset[Granularity]
    download_url: str | None = None
    asset_format: AssetFormat = AssetFormat.CSV
    default_filename: str | None = None
    canonical_table: CanonicalTable | None = None


@dataclass(frozen=True)
class SourceSummary:
    key: str
    name: str
    homepage: str
    description: str
    roles: frozenset[DataRole]
    granularities: frozenset[Granularity]
    assets: tuple[DatasetAsset, ...]


@dataclass(frozen=True)
class EmpiricalTarget:
    key: str
    label: str
    description: str
    required_roles: frozenset[DataRole]
    preferred_granularity: Granularity
    recommended_sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationPlan:
    target: EmpiricalTarget
    source_keys: tuple[str, ...]
    missing_roles: tuple[DataRole, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CanonicalColumn:
    name: str
    dtype: str
    description: str


@dataclass(frozen=True)
class CanonicalSchema:
    table: CanonicalTable
    description: str
    columns: tuple[CanonicalColumn, ...]


@dataclass(frozen=True)
class DownloadResult:
    asset: DatasetAsset
    path: Path


@dataclass(frozen=True)
class NormalizationResult:
    asset: DatasetAsset
    table: CanonicalTable
    path: Path
    row_count: int

