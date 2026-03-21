"""World Bank source adapter metadata and normalization."""

from __future__ import annotations

from pathlib import Path

from civlab.data.io import default_raw_path, write_canonical_csv, write_json, read_json
from civlab.data.models import (
    AssetFormat,
    CanonicalTable,
    DataRole,
    DatasetAsset,
    DownloadResult,
    Granularity,
    NormalizationResult,
    SourceSummary,
)
from civlab.data.normalize import coalesce, parse_numeric_text, parse_year
from civlab.data.schema import get_schema
from civlab.data.sources.base import DataSourceAdapter
from civlab.data.world_bank_api import fetch_indicator_series

WORLD_BANK_DEFAULT_INDICATORS = (
    "SP.POP.TOTL",
    "NY.GDP.PCAP.KD",
    "NE.TRD.GNFS.ZS",
    "SI.POV.GINI",
)


class WorldBankSource(DataSourceAdapter):
    key = "world_bank"

    def describe(self) -> SourceSummary:
        assets = (
            DatasetAsset(
                slug="world-bank-indicators-api",
                title="World Bank Indicators API",
                url="https://data.worldbank.org/indicator/",
                description="Country-year indicators for development, macroeconomics, public services, and aid.",
                roles=frozenset({DataRole.MACRO, DataRole.DEMOGRAPHY, DataRole.DEVELOPMENT_FINANCE}),
                granularities=frozenset({Granularity.COUNTRY_YEAR}),
                download_url="https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json",
                asset_format=AssetFormat.API_JSON,
                default_filename="world_bank_indicators.json",
                canonical_table=CanonicalTable.COUNTRY_YEAR,
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

    def download_asset(self, asset_slug: str, root: Path, **kwargs: object) -> DownloadResult:
        asset = self.get_asset(asset_slug)
        series_codes = tuple(kwargs.get("series_codes") or WORLD_BANK_DEFAULT_INDICATORS)
        payload = {
            "asset_slug": asset.slug,
            "series_codes": list(series_codes),
            "series": {code: fetch_indicator_series(code) for code in series_codes},
        }
        path = default_raw_path(root, self.key, asset)
        write_json(path, payload)
        return DownloadResult(asset=asset, path=path)

    def normalize_asset(
        self,
        asset_slug: str,
        raw_path: Path,
        output_path: Path,
        **_: object,
    ) -> NormalizationResult:
        asset = self.get_asset(asset_slug)
        payload = read_json(raw_path)
        series_payload = payload["series"]
        normalized_rows: list[dict[str, str]] = []
        for indicator_code, rows in series_payload.items():
            for row in rows:
                value, value_text = parse_numeric_text(row.get("value"))
                if not value and not value_text:
                    continue
                normalized_rows.append(
                    {
                        "source": self.key,
                        "dataset": asset.slug,
                        "country_name": coalesce(row["country"]["value"]),
                        "country_iso3": coalesce(row.get("countryiso3code")),
                        "country_iso_numeric": "",
                        "year": parse_year(row.get("date")),
                        "series_code": indicator_code,
                        "series_name": coalesce(row["indicator"]["value"]),
                        "value": value,
                        "value_text": value_text,
                        "unit": coalesce(row.get("unit")),
                        "note": "",
                    }
                )
        row_count = write_canonical_csv(output_path, get_schema(CanonicalTable.COUNTRY_YEAR), normalized_rows)
        return NormalizationResult(asset=asset, table=CanonicalTable.COUNTRY_YEAR, path=output_path, row_count=row_count)

