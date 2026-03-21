"""Default source registry and target catalog."""

from __future__ import annotations

from civlab.data.models import DataRole, EmpiricalTarget, Granularity
from civlab.data.pipeline import EmpiricalPipeline
from civlab.data.registry import SourceRegistry
from civlab.data.sources.aiddata import AidDataSource
from civlab.data.sources.qog import QogSource
from civlab.data.sources.ucdp import UcdpSource
from civlab.data.sources.world_bank import WorldBankSource


def default_targets() -> tuple[EmpiricalTarget, ...]:
    return (
        EmpiricalTarget(
            key="governance_capacity",
            label="Governance Capacity",
            description="Track legitimacy, bureaucratic quality, and state capacity over time.",
            required_roles=frozenset({DataRole.GOVERNANCE, DataRole.BUREAUCRACY}),
            preferred_granularity=Granularity.COUNTRY_YEAR,
            recommended_sources=("qog",),
        ),
        EmpiricalTarget(
            key="development_exposure",
            label="Development Exposure",
            description="Link external finance, infrastructure exposure, and social response.",
            required_roles=frozenset({DataRole.DEVELOPMENT_FINANCE, DataRole.GEOSPATIAL}),
            preferred_granularity=Granularity.GEOCODED_PROJECT,
            recommended_sources=("aiddata",),
        ),
        EmpiricalTarget(
            key="conflict_risk",
            label="Conflict Risk",
            description="Backtest conflict pathways using governance, project exposure, and later conflict adapters.",
            required_roles=frozenset(
                {DataRole.GOVERNANCE, DataRole.BUREAUCRACY, DataRole.DEVELOPMENT_FINANCE, DataRole.CONFLICT}
            ),
            preferred_granularity=Granularity.COUNTRY_YEAR,
            recommended_sources=("qog", "aiddata"),
        ),
        EmpiricalTarget(
            key="flourishing",
            label="Flourishing",
            description="Evaluate multi-dimensional flourishing across institutions, material conditions, and safety.",
            required_roles=frozenset(
                {DataRole.GOVERNANCE, DataRole.BUREAUCRACY, DataRole.DEVELOPMENT_FINANCE, DataRole.MACRO}
            ),
            preferred_granularity=Granularity.COUNTRY_YEAR,
            recommended_sources=("qog", "aiddata"),
        ),
    )


def build_default_registry() -> SourceRegistry:
    registry = SourceRegistry()
    registry.register(QogSource())
    registry.register(AidDataSource())
    registry.register(UcdpSource())
    registry.register(WorldBankSource())
    return registry


def build_default_pipeline() -> EmpiricalPipeline:
    return EmpiricalPipeline(build_default_registry(), default_targets())
