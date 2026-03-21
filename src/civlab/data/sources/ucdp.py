"""UCDP source adapter metadata."""

from __future__ import annotations

from civlab.data.models import DataRole, DatasetAsset, Granularity, SourceSummary
from civlab.data.sources.base import DataSourceAdapter


class UcdpSource(DataSourceAdapter):
    key = "ucdp"

    def describe(self) -> SourceSummary:
        assets = (
            DatasetAsset(
                slug="ucdp-country-year",
                title="UCDP Country-Year Dataset on Organized Violence",
                url="https://ucdp.uu.se/downloads/",
                description="Country-year aggregates for organized violence within country borders.",
                roles=frozenset({DataRole.CONFLICT}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
            ),
            DatasetAsset(
                slug="ucdp-ged",
                title="UCDP Georeferenced Event Dataset",
                url="https://ucdp.uu.se/downloads/",
                description="Event-level organized violence data with village-level geocoding and day resolution.",
                roles=frozenset({DataRole.CONFLICT, DataRole.GEOSPATIAL}),
                granularities=frozenset({Granularity.GEOCODED_PROJECT}),
            ),
            DatasetAsset(
                slug="ucdp-battle-deaths",
                title="UCDP Battle-Related Deaths Dataset",
                url="https://ucdp.uu.se/downloads/",
                description="Dyad-year and conflict-level battle-death counts for armed conflicts.",
                roles=frozenset({DataRole.CONFLICT}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
            ),
        )

        return SourceSummary(
            key=self.key,
            name="Uppsala Conflict Data Program",
            homepage="https://ucdp.uu.se/downloads/",
            description="Conflict event, country-year, and battle-death datasets for organized violence validation.",
            roles=frozenset({DataRole.CONFLICT, DataRole.GEOSPATIAL}),
            granularities=frozenset({Granularity.COUNTRY_YEAR, Granularity.GEOCODED_PROJECT}),
            assets=assets,
        )

