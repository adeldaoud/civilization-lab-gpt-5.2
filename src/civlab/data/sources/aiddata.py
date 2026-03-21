"""AidData source adapter metadata and normalization."""

from __future__ import annotations

from pathlib import Path

from civlab.data.io import read_zip_csv_rows, write_canonical_csv, zip_members
from civlab.data.models import (
    AssetFormat,
    CanonicalTable,
    DataRole,
    DatasetAsset,
    Granularity,
    NormalizationResult,
    SourceSummary,
)
from civlab.data.normalize import coalesce, parse_numeric_text, parse_year
from civlab.data.schema import get_schema
from civlab.data.sources.base import DataSourceAdapter


class AidDataSource(DataSourceAdapter):
    key = "aiddata"

    def describe(self) -> SourceSummary:
        assets = (
            DatasetAsset(
                slug="aiddata-ppd-v2",
                title="AidData Project Performance Database v2.0",
                url="https://www.aiddata.org/data/project-performance-database-ppd-version-2-0",
                description="Project evaluation ratings for donor-financed interventions across recipient countries.",
                roles=frozenset({DataRole.PROJECT_PERFORMANCE, DataRole.DEVELOPMENT_FINANCE}),
                granularities=frozenset({Granularity.PROJECT}),
                download_url="https://docs.aiddata.org/ad4/datasets/PPD2_archive_Jan21_2022.zip",
                asset_format=AssetFormat.ZIP,
                default_filename="PPD2_archive_Jan21_2022.zip",
                canonical_table=CanonicalTable.PROJECT_EXPOSURE,
            ),
            DatasetAsset(
                slug="aiddata-gcdf-v3-adm",
                title="AidData Global Chinese Development Finance v3.0 ADM Locations",
                url="https://www.aiddata.org/data/aiddatas-global-chinese-development-finance-dataset-version-3-0",
                description="Administrative-area location tables for Chinese development finance exposure.",
                roles=frozenset({DataRole.DEVELOPMENT_FINANCE, DataRole.GEOSPATIAL}),
                granularities=frozenset({Granularity.GEOCODED_PROJECT}),
                download_url="https://docs.aiddata.org/ad4/datasets/AidDatas_Global_Chinese_Development_Finance_Dataset_Version_3_0.zip",
                asset_format=AssetFormat.ZIP,
                default_filename="AidDatas_Global_Chinese_Development_Finance_Dataset_Version_3_0.zip",
                canonical_table=CanonicalTable.PROJECT_EXPOSURE,
            ),
            DatasetAsset(
                slug="aiddata-ltl-2020",
                title="AidData Listening to Leaders 2020 Public Release",
                url="https://www.aiddata.org/data/the-2020-listening-to-leaders-survey-aggregate-dataset",
                description="Survey aggregate data on development priorities, progress, and donor performance.",
                roles=frozenset({DataRole.ELITE_PERCEPTIONS}),
                granularities=frozenset({Granularity.SURVEY_AGGREGATE}),
                download_url="https://docs.aiddata.org/ad4/datasets/LtL_2020_public_release_data.zip",
                asset_format=AssetFormat.ZIP,
                default_filename="LtL_2020_public_release_data.zip",
                canonical_table=None,
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

    def normalize_asset(
        self,
        asset_slug: str,
        raw_path: Path,
        output_path: Path,
        **_: object,
    ) -> NormalizationResult:
        asset = self.get_asset(asset_slug)
        if asset_slug == "aiddata-ppd-v2":
            rows = self._normalize_ppd(raw_path, asset.slug)
        elif asset_slug == "aiddata-gcdf-v3-adm":
            rows = self._normalize_gcdf_locations(raw_path, asset.slug)
        else:
            raise ValueError(
                "This AidData asset is not yet mapped to a canonical table. "
                "Current executable normalizers cover aiddata-ppd-v2 and aiddata-gcdf-v3-adm."
            )

        row_count = write_canonical_csv(output_path, get_schema(CanonicalTable.PROJECT_EXPOSURE), rows)
        return NormalizationResult(
            asset=asset,
            table=CanonicalTable.PROJECT_EXPOSURE,
            path=output_path,
            row_count=row_count,
        )

    def _normalize_ppd(self, raw_path: Path, asset_slug: str) -> list[dict[str, str]]:
        _, rows = read_zip_csv_rows(raw_path, lambda name: "ppd2_" in name.lower())
        normalized_rows: list[dict[str, str]] = []
        for row in rows:
            score, _ = parse_numeric_text(row.get("six_overall_rating"))
            disbursement, _ = parse_numeric_text(row.get("aiddata_disbursement_amount"))
            normalized_rows.append(
                {
                    "source": self.key,
                    "dataset": asset_slug,
                    "project_id": coalesce(row.get("project_id"), row.get("aiddata_id"), row.get("wb_project_id")),
                    "project_name": coalesce(row.get("projectname"), row.get("aiddata_title")),
                    "recipient_name": coalesce(row.get("countryname_WB"), row.get("countryname_COW")),
                    "recipient_iso3": "",
                    "recipient_iso_numeric": coalesce(row.get("country_code_WB"), row.get("country_code_COW"), row.get("ccode")),
                    "commitment_year": parse_year(row.get("startyear")),
                    "start_year": parse_year(row.get("start_date")),
                    "end_year": parse_year(row.get("completion_date") or row.get("completionyear") or row.get("completion_year")),
                    "flow_type": coalesce(row.get("aid_type")),
                    "usd_commitment": "",
                    "usd_disbursement": disbursement,
                    "latitude": "",
                    "longitude": "",
                    "location_name": "",
                    "location_precision": "country",
                    "sector_code": coalesce(row.get("sector_code"), row.get("aiddata_sectorcode"), row.get("crs_purpose_code")),
                    "sector_name": coalesce(
                        row.get("sector_description"),
                        row.get("aiddata_sectorname"),
                        row.get("crs_sector_description"),
                    ),
                    "status": coalesce(row.get("gfatm_newstatus")),
                    "performance_score": score,
                    "raw_rating": coalesce(row.get("original_overall_rating")),
                    "note": "",
                }
            )
        return normalized_rows

    def _normalize_gcdf_locations(self, raw_path: Path, asset_slug: str) -> list[dict[str, str]]:
        normalized_rows: list[dict[str, str]] = []
        for member_name in zip_members(raw_path):
            member_lower = member_name.lower()
            if "__macosx" in member_lower or not member_lower.endswith(".csv") or "locations" not in member_lower:
                continue
            location_precision = "adm2" if "adm2" in member_lower else "adm1"
            _, rows = read_zip_csv_rows(raw_path, lambda name, target=member_name: name == target)
            for row in rows:
                commitment, _ = parse_numeric_text(
                    row.get("intersection_ratio_commitment_value") or row.get("even_split_ratio_commitment_value")
                )
                latitude, _ = parse_numeric_text(row.get("centroid_latitude"))
                longitude, _ = parse_numeric_text(row.get("centroid_longitude"))
                normalized_rows.append(
                    {
                        "source": self.key,
                        "dataset": asset_slug,
                        "project_id": coalesce(row.get("id")),
                        "project_name": "",
                        "recipient_name": coalesce(row.get("shapeName")),
                        "recipient_iso3": coalesce(row.get("shapeGroup")),
                        "recipient_iso_numeric": "",
                        "commitment_year": "",
                        "start_year": "",
                        "end_year": "",
                        "flow_type": "development_finance",
                        "usd_commitment": commitment,
                        "usd_disbursement": "",
                        "latitude": latitude,
                        "longitude": longitude,
                        "location_name": coalesce(row.get("shapeName")),
                        "location_precision": location_precision,
                        "sector_code": "",
                        "sector_name": "",
                        "status": "",
                        "performance_score": "",
                        "raw_rating": "",
                        "note": (
                            f"intersection_ratio={coalesce(row.get('intersection_ratio'))}; "
                            f"even_split_ratio={coalesce(row.get('even_split_ratio'))}"
                        ),
                    }
                )
        return normalized_rows

