"""QoG source adapter metadata."""

from __future__ import annotations

from civlab.data.models import DataRole, DatasetAsset, Granularity, SourceSummary
from civlab.data.sources.base import DataSourceAdapter


class QogSource(DataSourceAdapter):
    key = "qog"

    def describe(self) -> SourceSummary:
        assets = (
            DatasetAsset(
                slug="qog-basic",
                title="QoG Basic Dataset",
                url="https://www.gu.se/en/quality-government/qog-data",
                description="Compact country-year panel for governance-oriented backtesting.",
                roles=frozenset({DataRole.GOVERNANCE, DataRole.BUREAUCRACY}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
            ),
            DatasetAsset(
                slug="qog-standard",
                title="QoG Standard Dataset",
                url="https://www.gu.se/en/quality-government/qog-data",
                description="Broader country-year panel for governance, regime, and institutional variables.",
                roles=frozenset({DataRole.GOVERNANCE, DataRole.BUREAUCRACY}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
            ),
            DatasetAsset(
                slug="qog-expert-survey",
                title="QoG Expert Survey",
                url="https://datafinder.qog.gu.se/download/expert",
                description="Cross-country expert indicators on bureaucratic structure and behavior.",
                roles=frozenset({DataRole.BUREAUCRACY, DataRole.GOVERNANCE}),
                granularities=frozenset({Granularity.COUNTRY_CROSS_SECTION, Granularity.SURVEY_AGGREGATE}),
            ),
        )

        return SourceSummary(
            key=self.key,
            name="Quality of Government Institute",
            homepage="https://www.gu.se/en/quality-government/qog-data",
            description="Governance-focused country-year and expert-survey datasets for institutional validation.",
            roles=frozenset({DataRole.GOVERNANCE, DataRole.BUREAUCRACY}),
            granularities=frozenset(
                {Granularity.COUNTRY_YEAR, Granularity.COUNTRY_CROSS_SECTION, Granularity.SURVEY_AGGREGATE}
            ),
            assets=assets,
        )

