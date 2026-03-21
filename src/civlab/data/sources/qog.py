"""QoG source adapter metadata and normalization."""

from __future__ import annotations

from pathlib import Path

from civlab.data.io import read_csv_rows, write_canonical_csv
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

QOG_DEFAULT_SERIES = (
    "icrg_qog",
    "ti_cpi",
    "vdem_corr",
    "vdem_polyarchy",
    "wbgi_cce",
    "wbgi_gee",
    "wbgi_rle",
    "wdi_gdpcapcon2015",
    "wdi_gini",
    "wdi_pop",
    "wdi_taxrev",
)


class QogSource(DataSourceAdapter):
    key = "qog"

    def describe(self) -> SourceSummary:
        assets = (
            DatasetAsset(
                slug="qog-basic-ts",
                title="QoG Basic Dataset Time-Series",
                url="https://www.gu.se/en/quality-government/qog-data/data-downloads/basic-dataset",
                description="QoG Basic time-series country-year panel.",
                roles=frozenset({DataRole.GOVERNANCE, DataRole.BUREAUCRACY}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
                download_url="https://www.qogdata.pol.gu.se/data/qog_bas_ts_jan26.csv",
                asset_format=AssetFormat.CSV,
                default_filename="qog_bas_ts_jan26.csv",
                canonical_table=CanonicalTable.COUNTRY_YEAR,
            ),
            DatasetAsset(
                slug="qog-basic-cs",
                title="QoG Basic Dataset Cross-Section",
                url="https://www.gu.se/en/quality-government/qog-data/data-downloads/basic-dataset",
                description="QoG Basic cross-section country panel.",
                roles=frozenset({DataRole.GOVERNANCE, DataRole.BUREAUCRACY}),
                granularities=frozenset({Granularity.COUNTRY_CROSS_SECTION}),
                download_url="https://www.qogdata.pol.gu.se/data/qog_bas_cs_jan26.csv",
                asset_format=AssetFormat.CSV,
                default_filename="qog_bas_cs_jan26.csv",
                canonical_table=None,
            ),
            DatasetAsset(
                slug="qog-expert-survey-2020",
                title="QoG Expert Survey 2020 Aggregate Dataset",
                url="https://datafinder.qog.gu.se/download/expert",
                description="Expert-coded bureaucracy design and behavior indicators.",
                roles=frozenset({DataRole.BUREAUCRACY, DataRole.GOVERNANCE}),
                granularities=frozenset({Granularity.COUNTRY_CROSS_SECTION, Granularity.SURVEY_AGGREGATE}),
                download_url="https://www.qogdata.pol.gu.se/data/qog_exp_agg_20.csv",
                asset_format=AssetFormat.CSV,
                default_filename="qog_exp_agg_20.csv",
                canonical_table=CanonicalTable.COUNTRY_YEAR,
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

    def normalize_asset(
        self,
        asset_slug: str,
        raw_path: Path,
        output_path: Path,
        **kwargs: object,
    ) -> NormalizationResult:
        asset = self.get_asset(asset_slug)
        if asset_slug == "qog-basic-cs":
            raise ValueError(
                "qog-basic-cs is a cross-section snapshot without an explicit year column. "
                "It is intentionally not normalized into the canonical country_year table."
            )
        rows = read_csv_rows(raw_path)
        series_codes = kwargs.get("series_codes")
        normalized_rows = self._normalize_rows(asset.slug, rows, series_codes=series_codes)
        row_count = write_canonical_csv(output_path, get_schema(CanonicalTable.COUNTRY_YEAR), normalized_rows)
        return NormalizationResult(asset=asset, table=CanonicalTable.COUNTRY_YEAR, path=output_path, row_count=row_count)

    def _normalize_rows(
        self,
        asset_slug: str,
        rows: list[dict[str, str]],
        *,
        series_codes: object = None,
    ) -> list[dict[str, str]]:
        if not rows:
            return []

        if asset_slug == "qog-expert-survey-2020":
            id_columns = ("year", "cname", "ccode", "ccodecow", "ccodewb", "ccodealp", "oecd", "eu27", "region")
            default_series = tuple(column for column in rows[0] if column not in id_columns)
        else:
            id_columns = ("ccode", "ccode_qog", "ccodealp", "ccodealp_year", "ccodecow", "cname", "cname_qog", "cname_year", "year")
            default_series = tuple(column for column in QOG_DEFAULT_SERIES if column in rows[0])

        preferred = tuple(series_codes) if series_codes else default_series
        selected_series = select_series(rows[0].keys(), preferred, id_columns)
        normalized_rows: list[dict[str, str]] = []

        for row in rows:
            country_name = coalesce(row.get("cname"), row.get("cname_year"), row.get("cname_qog"))
            iso3 = coalesce(row.get("ccodealp"), row.get("ccodealp_year"))
            iso_numeric = coalesce(row.get("ccode"), row.get("ccodewb"), row.get("ccode_qog"))
            year = parse_year(row.get("year"))

            for series_code in selected_series:
                raw_value = row.get(series_code)
                value, value_text = parse_numeric_text(raw_value)
                if not value and not value_text:
                    continue
                normalized_rows.append(
                    {
                        "source": self.key,
                        "dataset": asset_slug,
                        "country_name": country_name,
                        "country_iso3": iso3,
                        "country_iso_numeric": iso_numeric,
                        "year": year,
                        "series_code": series_code,
                        "series_name": series_code,
                        "value": value,
                        "value_text": value_text,
                        "unit": "",
                        "note": "",
                    }
                )

        return normalized_rows
