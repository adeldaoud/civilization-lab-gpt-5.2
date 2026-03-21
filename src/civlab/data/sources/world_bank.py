"""World Bank source adapter metadata."""

from __future__ import annotations

from civlab.data.models import DataRole, DatasetAsset, Granularity, SourceSummary
from civlab.data.sources.base import DataSourceAdapter


class WorldBankSource(DataSourceAdapter):
    key = "world_bank"

    def describe(self) -> SourceSummary:
        assets = (
            DatasetAsset(
                slug="world-bank-indicators",
                title="World Bank Indicators",
                url="https://data.worldbank.org/indicator/",
                description="Country-year indicators for development, macroeconomics, public services, and aid.",
                roles=frozenset({DataRole.MACRO, DataRole.DEMOGRAPHY, DataRole.DEVELOPMENT_FINANCE}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
            ),
        )

        return SourceSummary(
            key=self.key,
            name="World Bank Data",
            homepage="https://data.worldbank.org/indicator/",
            description="Broad country-year indicators for macroeconomic, demographic, and development outcomes.",
            roles=frozenset({DataRole.MACRO, DataRole.DEMOGRAPHY, DataRole.DEVELOPMENT_FINANCE}),
            granularities=frozenset({Granularity.COUNTRY_YEAR}),
            assets=assets,
        )

