"""UCDP source adapter metadata and normalization."""

from __future__ import annotations

from pathlib import Path

from civlab.data.io import read_zip_csv_rows, write_canonical_csv
from civlab.data.models import (
    AssetFormat,
    CanonicalTable,
    DataRole,
    DatasetAsset,
    Granularity,
    NormalizationResult,
    SourceSummary,
)
from civlab.data.normalize import coalesce, parse_numeric_text, parse_year, select_series
from civlab.data.schema import get_schema
from civlab.data.sources.base import DataSourceAdapter

UCDP_COUNTRY_YEAR_SERIES = (
    "sb_exist_cy",
    "sb_total_deaths_best_cy",
    "ns_exist_cy",
    "ns_total_deaths_best_cy",
    "os_exist_cy",
    "os_total_deaths_best_cy",
    "cumulative_total_deaths_in_orgvio_best_cy",
)

UCDP_BATTLE_DEATHS_SERIES = ("bd_best", "bd_high", "bd_low")


class UcdpSource(DataSourceAdapter):
    key = "ucdp"

    def describe(self) -> SourceSummary:
        assets = (
            DatasetAsset(
                slug="ucdp-organized-violence-country-year",
                title="UCDP Country-Year Dataset on Organized Violence",
                url="https://ucdp.uu.se/downloads/",
                description="Country-year aggregates for organized violence within country borders.",
                roles=frozenset({DataRole.CONFLICT}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
                download_url="https://ucdp.uu.se/downloads/organizedviolencecy/organizedviolencecy-251-csv.zip",
                asset_format=AssetFormat.ZIP,
                default_filename="organizedviolencecy-251-csv.zip",
                canonical_table=CanonicalTable.COUNTRY_YEAR,
            ),
            DatasetAsset(
                slug="ucdp-battle-deaths-conflict",
                title="UCDP Battle-Related Deaths Conflict-Level Dataset",
                url="https://ucdp.uu.se/downloads/",
                description="Conflict-level battle-death counts for armed conflicts.",
                roles=frozenset({DataRole.CONFLICT}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
                download_url="https://ucdp.uu.se/downloads/brd/ucdp-brd-conf-251-csv.zip",
                asset_format=AssetFormat.ZIP,
                default_filename="ucdp-brd-conf-251-csv.zip",
                canonical_table=CanonicalTable.COUNTRY_YEAR,
            ),
            DatasetAsset(
                slug="ucdp-battle-deaths-dyadic",
                title="UCDP Battle-Related Deaths Dyadic Dataset",
                url="https://ucdp.uu.se/downloads/",
                description="Dyad-year battle-death counts for armed conflicts.",
                roles=frozenset({DataRole.CONFLICT}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
                download_url="https://ucdp.uu.se/downloads/brd/ucdp-brd-dyadic-251-csv.zip",
                asset_format=AssetFormat.ZIP,
                default_filename="ucdp-brd-dyadic-251-csv.zip",
                canonical_table=CanonicalTable.COUNTRY_YEAR,
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

    def normalize_asset(
        self,
        asset_slug: str,
        raw_path: Path,
        output_path: Path,
        **kwargs: object,
    ) -> NormalizationResult:
        asset = self.get_asset(asset_slug)
        if asset_slug == "ucdp-organized-violence-country-year":
            rows = self._normalize_country_year(raw_path, asset.slug, kwargs.get("series_codes"))
        else:
            rows = self._normalize_battle_deaths(raw_path, asset.slug, kwargs.get("series_codes"))

        row_count = write_canonical_csv(output_path, get_schema(CanonicalTable.COUNTRY_YEAR), rows)
        return NormalizationResult(asset=asset, table=CanonicalTable.COUNTRY_YEAR, path=output_path, row_count=row_count)

    def _normalize_country_year(
        self,
        raw_path: Path,
        asset_slug: str,
        series_codes: object,
    ) -> list[dict[str, str]]:
        _, rows = read_zip_csv_rows(raw_path, lambda name: "organizedviolencecy" in name.lower())
        selected_series = select_series(
            rows[0].keys(),
            tuple(series_codes) if series_codes else UCDP_COUNTRY_YEAR_SERIES,
            ("country_id_cy", "country_cy", "year_cy", "region_cy", "main_govt_name_cy", "version"),
        )
        normalized_rows: list[dict[str, str]] = []
        for row in rows:
            for series_code in selected_series:
                value, value_text = parse_numeric_text(row.get(series_code))
                if not value and not value_text:
                    continue
                normalized_rows.append(
                    {
                        "source": self.key,
                        "dataset": asset_slug,
                        "country_name": coalesce(row.get("country_cy")),
                        "country_iso3": "",
                        "country_iso_numeric": coalesce(row.get("country_id_cy")),
                        "year": parse_year(row.get("year_cy")),
                        "series_code": series_code,
                        "series_name": series_code,
                        "value": value,
                        "value_text": value_text,
                        "unit": "count" if "deaths" in series_code else "",
                        "note": "",
                    }
                )
        return normalized_rows

    def _normalize_battle_deaths(
        self,
        raw_path: Path,
        asset_slug: str,
        series_codes: object,
    ) -> list[dict[str, str]]:
        _, rows = read_zip_csv_rows(raw_path, lambda name: "ucdp-brd" in name.lower())
        selected_series = select_series(
            rows[0].keys(),
            tuple(series_codes) if series_codes else UCDP_BATTLE_DEATHS_SERIES,
            ("conflict_id", "dyad_id", "year", "location_inc", "side_a", "side_b", "territory_name", "version"),
        )
        normalized_rows: list[dict[str, str]] = []
        for row in rows:
            note = f"conflict_id={coalesce(row.get('conflict_id'))}; dyad_id={coalesce(row.get('dyad_id'))}"
            for series_code in selected_series:
                value, value_text = parse_numeric_text(row.get(series_code))
                if not value and not value_text:
                    continue
                normalized_rows.append(
                    {
                        "source": self.key,
                        "dataset": asset_slug,
                        "country_name": coalesce(row.get("territory_name"), row.get("location_inc")),
                        "country_iso3": "",
                        "country_iso_numeric": "",
                        "year": parse_year(row.get("year")),
                        "series_code": series_code,
                        "series_name": series_code,
                        "value": value,
                        "value_text": value_text,
                        "unit": "deaths",
                        "note": note,
                    }
                )
        return normalized_rows

