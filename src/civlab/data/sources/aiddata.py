"""AidData source adapter metadata."""

from __future__ import annotations

from civlab.data.models import DataRole, DatasetAsset, Granularity, SourceSummary
from civlab.data.sources.base import DataSourceAdapter


class AidDataSource(DataSourceAdapter):
    key = "aiddata"

    def describe(self) -> SourceSummary:
        assets = (
            DatasetAsset(
                slug="aiddata-versioned-datasets",
                title="AidData Versioned Datasets",
                url="https://www.aiddata.org/datasets",
                description="Catalog of project-level, dashboard, survey, and geospatial data products.",
                roles=frozenset({DataRole.DEVELOPMENT_FINANCE, DataRole.GEOSPATIAL}),
                granularities=frozenset(
                    {Granularity.PROJECT, Granularity.GEOCODED_PROJECT, Granularity.SURVEY_AGGREGATE}
                ),
            ),
            DatasetAsset(
                slug="aiddata-global-chinese-development-finance",
                title="AidData Global Chinese Development Finance Dataset",
                url="https://www.aiddata.org/data/aiddatas-global-chinese-development-finance-dataset-version-2-0",
                description="Project-level finance flows across 165 countries with strong external exposure value.",
                roles=frozenset({DataRole.DEVELOPMENT_FINANCE}),
                granularities=frozenset({Granularity.PROJECT}),
            ),
            DatasetAsset(
                slug="aiddata-geocoded-finance",
                title="AidData Geocoded Global Chinese Official Finance Dataset",
                url="https://www.aiddata.org/publications/aiddatas-geospatial-global-chinese-development-finance-dataset",
                description="Geocoded project locations for spatial exposure and infrastructure analyses.",
                roles=frozenset({DataRole.DEVELOPMENT_FINANCE, DataRole.GEOSPATIAL}),
                granularities=frozenset({Granularity.GEOCODED_PROJECT}),
            ),
            DatasetAsset(
                slug="aiddata-project-performance",
                title="AidData Project Performance Database",
                url="https://www.aiddata.org/data/project-performance-database-ppd-version-2-0",
                description="Project evaluation ratings for donor-financed interventions across recipient countries.",
                roles=frozenset({DataRole.PROJECT_PERFORMANCE, DataRole.DEVELOPMENT_FINANCE}),
                granularities=frozenset({Granularity.PROJECT}),
            ),
            DatasetAsset(
                slug="aiddata-listening-to-leaders",
                title="AidData Listening to Leaders",
                url="https://www.aiddata.org/data/the-2020-listening-to-leaders-survey-aggregate-dataset",
                description="Survey aggregate data on development priorities, progress, and donor performance.",
                roles=frozenset({DataRole.ELITE_PERCEPTIONS}),
                granularities=frozenset({Granularity.SURVEY_AGGREGATE}),
            ),
        )

        return SourceSummary(
            key=self.key,
            name="AidData",
            homepage="https://www.aiddata.org/datasets",
            description="Project-level, geospatial, and survey datasets on development finance and external exposure.",
            roles=frozenset(
                {
                    DataRole.DEVELOPMENT_FINANCE,
                    DataRole.GEOSPATIAL,
                    DataRole.PROJECT_PERFORMANCE,
                    DataRole.ELITE_PERCEPTIONS,
                }
            ),
            granularities=frozenset(
                {Granularity.PROJECT, Granularity.GEOCODED_PROJECT, Granularity.SURVEY_AGGREGATE}
            ),
            assets=assets,
        )

