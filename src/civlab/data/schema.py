"""Canonical table schemas for normalized empirical data."""

from __future__ import annotations

from civlab.data.models import CanonicalColumn, CanonicalSchema, CanonicalTable


COUNTRY_YEAR_SCHEMA = CanonicalSchema(
    table=CanonicalTable.COUNTRY_YEAR,
    description="Long-form country-year observations across governance, conflict, macro, and survey data.",
    columns=(
        CanonicalColumn("source", "string", "Stable source key, for example qog or ucdp."),
        CanonicalColumn("dataset", "string", "Dataset asset slug within the source."),
        CanonicalColumn("country_name", "string", "Country or political unit name from the source."),
        CanonicalColumn("country_iso3", "string", "ISO-3166-1 alpha-3 code when available."),
        CanonicalColumn("country_iso_numeric", "string", "ISO-3166-1 numeric code or source numeric code."),
        CanonicalColumn("year", "int", "Observation year."),
        CanonicalColumn("series_code", "string", "Source-native indicator or measure code."),
        CanonicalColumn("series_name", "string", "Human-readable label for the indicator when available."),
        CanonicalColumn("value", "string", "Normalized scalar value as text for CSV portability."),
        CanonicalColumn("value_text", "string", "Original non-numeric value when the source is categorical."),
        CanonicalColumn("unit", "string", "Measurement unit when known."),
        CanonicalColumn("note", "string", "Optional normalization note or provenance detail."),
    ),
)


PROJECT_EXPOSURE_SCHEMA = CanonicalSchema(
    table=CanonicalTable.PROJECT_EXPOSURE,
    description="Project-level and geospatial exposure records across development-finance sources.",
    columns=(
        CanonicalColumn("source", "string", "Stable source key, for example aiddata."),
        CanonicalColumn("dataset", "string", "Dataset asset slug within the source."),
        CanonicalColumn("project_id", "string", "Stable project identifier from the source."),
        CanonicalColumn("project_name", "string", "Project title or best available label."),
        CanonicalColumn("recipient_name", "string", "Recipient country or location name."),
        CanonicalColumn("recipient_iso3", "string", "Recipient ISO alpha-3 code when available."),
        CanonicalColumn("recipient_iso_numeric", "string", "Recipient ISO numeric code or source numeric code."),
        CanonicalColumn("commitment_year", "int", "Commitment or approval year when known."),
        CanonicalColumn("start_year", "int", "Project start year when known."),
        CanonicalColumn("end_year", "int", "Project end or completion year when known."),
        CanonicalColumn("flow_type", "string", "Aid, loan, grant, or other flow classification."),
        CanonicalColumn("usd_commitment", "string", "Commitment value in USD when available."),
        CanonicalColumn("usd_disbursement", "string", "Disbursement value in USD when available."),
        CanonicalColumn("latitude", "string", "Latitude when available."),
        CanonicalColumn("longitude", "string", "Longitude when available."),
        CanonicalColumn("location_name", "string", "Subnational or project location label."),
        CanonicalColumn("location_precision", "string", "Spatial precision such as adm1, adm2, exact, or approximate."),
        CanonicalColumn("sector_code", "string", "Source-native sector code when available."),
        CanonicalColumn("sector_name", "string", "Human-readable sector label when available."),
        CanonicalColumn("status", "string", "Project or implementation status when available."),
        CanonicalColumn("performance_score", "string", "Normalized performance or evaluation score when available."),
        CanonicalColumn("raw_rating", "string", "Original categorical or ordinal rating when available."),
        CanonicalColumn("note", "string", "Optional normalization note or provenance detail."),
    ),
)


SCHEMAS = {
    COUNTRY_YEAR_SCHEMA.table: COUNTRY_YEAR_SCHEMA,
    PROJECT_EXPOSURE_SCHEMA.table: PROJECT_EXPOSURE_SCHEMA,
}


def get_schema(table: CanonicalTable) -> CanonicalSchema:
    return SCHEMAS[table]

