"""Shared models for empirical sources and validation targets."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


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


@dataclass(frozen=True)
class DatasetAsset:
    slug: str
    title: str
    url: str
    description: str
    roles: frozenset[DataRole]
    granularities: frozenset[Granularity]


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

