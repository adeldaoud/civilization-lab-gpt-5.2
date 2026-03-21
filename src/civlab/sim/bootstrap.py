"""Empirical bootstrap utilities that map normalized data into simulator state."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from civlab.sim.models import (
    BiologyProfile,
    CohortState,
    CountryState,
    GeographyState,
    GovernmentState,
    LeaderState,
    PsychologyProfile,
    ResourceStock,
    SociologyProfile,
    clamp,
)

csv.field_size_limit(1024 * 1024 * 64)


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def _to_float(value: object) -> float | None:
    text = _clean(value)
    if not text:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def _mean(values: list[float], default: float) -> float:
    if not values:
        return default
    return sum(values) / len(values)


def _scale_linear(value: float | None, lower: float, upper: float, default: float = 0.5) -> float:
    if value is None:
        return default
    if upper <= lower:
        return default
    return clamp((value - lower) / (upper - lower))


def _scale_log(value: float | None, max_value: float, default: float = 0.0) -> float:
    if value is None or value <= 0:
        return default
    return clamp(math.log1p(value) / math.log1p(max_value))


@dataclass(frozen=True)
class EmpiricalBootstrapSpec:
    country_iso3: str
    year: int
    country_year_files: tuple[Path, ...]
    project_exposure_files: tuple[Path, ...] = ()
    country_name: str = ""
    country_iso_numeric: str = ""


class EmpiricalRepository:
    def __init__(self) -> None:
        self._cache: dict[Path, list[dict[str, str]]] = {}

    def rows(self, path: Path) -> list[dict[str, str]]:
        path = path.resolve()
        if path not in self._cache:
            self._cache[path] = _read_csv_rows(path)
        return self._cache[path]

    def country_year_series(self, spec: EmpiricalBootstrapSpec) -> dict[str, list[float]]:
        series: dict[str, list[float]] = {}
        for path in spec.country_year_files:
            for row in self.rows(path):
                if _clean(row.get("year")) != str(spec.year):
                    continue
                if not self._matches_country(row, spec):
                    continue
                value = _to_float(row.get("value"))
                if value is None:
                    continue
                series.setdefault(_clean(row.get("series_code")), []).append(value)
        return series

    def project_metrics(self, spec: EmpiricalBootstrapSpec) -> dict[str, float]:
        total_commitment = 0.0
        total_disbursement = 0.0
        total_performance = 0.0
        performance_count = 0
        project_ids: set[str] = set()

        for path in spec.project_exposure_files:
            for row in self.rows(path):
                if not self._matches_project_country(row, spec):
                    continue
                project_id = _clean(row.get("project_id"))
                if project_id:
                    project_ids.add(project_id)
                commitment_year = _clean(row.get("commitment_year"))
                if commitment_year and commitment_year.isdigit() and int(commitment_year) > spec.year:
                    continue
                total_commitment += _to_float(row.get("usd_commitment")) or 0.0
                total_disbursement += _to_float(row.get("usd_disbursement")) or 0.0
                performance = _to_float(row.get("performance_score"))
                if performance is not None:
                    total_performance += performance
                    performance_count += 1

        return {
            "project_count": float(len(project_ids)),
            "total_commitment": total_commitment,
            "total_disbursement": total_disbursement,
            "avg_performance": (total_performance / performance_count) if performance_count else 0.0,
        }

    def _matches_country(self, row: dict[str, str], spec: EmpiricalBootstrapSpec) -> bool:
        iso3 = _clean(row.get("country_iso3"))
        numeric = _clean(row.get("country_iso_numeric"))
        name = _clean(row.get("country_name")).lower()
        return (
            (spec.country_iso3 and iso3 == spec.country_iso3)
            or (spec.country_iso_numeric and numeric == spec.country_iso_numeric)
            or (spec.country_name and name == spec.country_name.lower())
        )

    def _matches_project_country(self, row: dict[str, str], spec: EmpiricalBootstrapSpec) -> bool:
        iso3 = _clean(row.get("recipient_iso3"))
        numeric = _clean(row.get("recipient_iso_numeric"))
        name = _clean(row.get("recipient_name")).lower()
        return (
            (spec.country_iso3 and iso3 == spec.country_iso3)
            or (spec.country_iso_numeric and numeric == spec.country_iso_numeric)
            or (spec.country_name and name == spec.country_name.lower())
        )


class EmpiricalLatentMapper:
    def __init__(self, repository: EmpiricalRepository | None = None) -> None:
        self.repository = repository or EmpiricalRepository()

    def bootstrap_country(
        self,
        *,
        name: str,
        iso3: str,
        region: str,
        spec: EmpiricalBootstrapSpec,
        base: CountryState | None = None,
    ) -> CountryState:
        series = self.repository.country_year_series(spec)
        projects = self.repository.project_metrics(spec)

        governance_values = self._values(series, "wbgi_cce", "wbgi_rle", "icrg_qog", "vdem_corr", "vdem_polyarchy")
        bureaucracy_values = self._values(series, "proff_pca", "impar1", "wbgi_gee", "icrg_qog")
        inequality_values = self._values(series, "wdi_gini", "lis_gini")
        tax_values = self._values(series, "wdi_taxrev")
        pop_values = self._values(series, "wdi_pop", "SP.POP.TOTL")
        gdp_pc_values = self._values(series, "wdi_gdpcapcon2015", "NY.GDP.PCAP.KD")
        trade_values = self._values(series, "wdi_trade", "NE.TRD.GNFS.ZS")
        conflict_values = self._values(
            series,
            "sb_total_deaths_best_cy",
            "ns_total_deaths_best_cy",
            "os_total_deaths_best_cy",
            "cumulative_total_deaths_in_orgvio_best_cy",
        )

        institutional_quality = _mean(
            [
                _scale_linear(_mean(governance_values, 0.0), -2.5, 2.5, 0.5),
                _scale_linear(_mean(self._values(series, "vdem_corr", "vdem_polyarchy"), 0.5), 0.0, 1.0, 0.5),
            ],
            0.5,
        )
        bureaucratic_quality = _mean(
            [
                _scale_linear(_mean(bureaucracy_values, 0.0), -2.5, 2.5, 0.5),
                _scale_linear(_mean(self._values(series, "proff_pca", "impar1"), 0.0), -2.5, 2.5, 0.5),
            ],
            0.5,
        )
        inequality = _scale_linear(_mean(inequality_values, 35.0), 20.0, 65.0, 0.35)
        tax_capacity = _scale_linear(_mean(tax_values, 18.0), 5.0, 40.0, 0.35)
        population = max(_mean(pop_values, 15_000_000.0), 500_000.0)
        gdp_pc = max(_mean(gdp_pc_values, 4_500.0), 500.0)
        trade_dependence = _scale_linear(_mean(trade_values, 45.0), 10.0, 180.0, 0.4)
        conflict_burden = _scale_log(sum(conflict_values), 50_000.0, 0.0)
        external_finance_exposure = _scale_log(projects["total_commitment"], 10_000_000_000.0, 0.0)
        avg_project_performance = _scale_linear(projects["avg_performance"], 1.0, 6.0, 0.5)

        geography = base.geography if base else GeographyState()
        resources = base.resources if base else ResourceStock()
        biology = base.biology if base else BiologyProfile()
        psychology = base.psychology if base else PsychologyProfile()
        sociology = base.sociology if base else SociologyProfile()
        leader = base.leader if base else LeaderState(name=f"{name} Leadership")
        government = base.government if base else GovernmentState()
        cohorts = base.cohorts if base and base.cohorts else self._default_cohorts()

        resources.treasury = 20.0 + 80.0 * _scale_linear(gdp_pc, 500.0, 80_000.0, 0.2)
        resources.industry = 15.0 + 80.0 * _scale_linear(gdp_pc, 500.0, 80_000.0, 0.2)
        resources.knowledge = 15.0 + 70.0 * institutional_quality
        resources.food = 25.0 + 60.0 * (1.0 - geography.climate_risk) * geography.arable_land
        resources.energy = 20.0 + 60.0 * geography.energy
        resources.minerals = 20.0 + 60.0 * geography.minerals

        psychology.trust = _mean([institutional_quality, bureaucratic_quality, avg_project_performance], 0.5)
        psychology.fear = clamp(0.2 + 0.5 * conflict_burden + 0.2 * geography.climate_risk)
        psychology.self_control = clamp(0.45 + 0.35 * bureaucratic_quality)
        psychology.status_drive = clamp(0.35 + 0.30 * inequality)
        psychology.trauma = clamp(0.15 + 0.6 * conflict_burden)

        sociology.institutional_quality = institutional_quality
        sociology.bureaucratic_quality = bureaucratic_quality
        sociology.inequality = inequality
        sociology.polarization = clamp(0.2 + 0.3 * inequality + 0.3 * conflict_burden)
        sociology.legitimacy = clamp(0.25 + 0.45 * institutional_quality + 0.15 * bureaucratic_quality - 0.2 * conflict_burden)
        sociology.information_integrity = clamp(0.35 + 0.35 * bureaucratic_quality)
        sociology.collective_efficacy = clamp(0.3 + 0.3 * institutional_quality + 0.2 * avg_project_performance)

        biology.aggression = clamp(0.35 + 0.15 * conflict_burden)
        biology.stress_reactivity = clamp(0.35 + 0.25 * inequality + 0.25 * conflict_burden)
        biology.self_preservation = clamp(0.55 + 0.2 * psychology.self_control)
        biology.health_burden = clamp(0.2 + 0.2 * geography.climate_risk)

        leader.competence = clamp(0.4 + 0.35 * institutional_quality)
        leader.hawkishness = clamp(0.25 + 0.35 * conflict_burden + 0.15 * biology.aggression)
        leader.charisma = clamp(0.45 + 0.15 * sociology.legitimacy)
        leader.strategic_horizon = clamp(0.45 + 0.25 * sociology.bureaucratic_quality)

        government.tax_rate = clamp(0.12 + 0.25 * tax_capacity, 0.08, 0.5)
        government.welfare_share = clamp(0.22 + 0.25 * inequality)
        government.military_share = clamp(0.12 + 0.35 * conflict_burden)
        government.infrastructure_share = clamp(0.20 + 0.20 * external_finance_exposure)
        government.institution_share = clamp(0.22 + 0.25 * bureaucratic_quality)
        government.repression = clamp(0.08 + 0.25 * conflict_burden + 0.15 * sociology.polarization)
        government.diplomacy_posture = clamp(0.55 + 0.20 * sociology.legitimacy - 0.25 * conflict_burden)
        government.normalize()

        country = base or CountryState(
            name=name,
            iso3=iso3,
            region=region,
            population=population,
            geography=geography,
            resources=resources,
            biology=biology,
            psychology=psychology,
            sociology=sociology,
            leader=leader,
            government=government,
            cohorts=cohorts,
        )
        country.name = name
        country.iso3 = iso3
        country.region = region
        country.population = population
        country.trade_dependence = trade_dependence
        country.external_finance_exposure = external_finance_exposure
        country.conflict_burden = conflict_burden
        country.external_threat = clamp(0.2 + 0.5 * conflict_burden)
        country.normalize()
        return country

    def _default_cohorts(self) -> list[CohortState]:
        return [
            CohortState(name="elite", social_class="elite", population_share=0.08, productivity=1.3, political_power=0.75),
            CohortState(name="middle", social_class="middle", population_share=0.37, productivity=1.0, political_power=0.45),
            CohortState(name="working", social_class="working", population_share=0.40, productivity=0.9, political_power=0.25),
            CohortState(name="rural_poor", social_class="poor", population_share=0.15, productivity=0.75, political_power=0.12),
        ]

    def _values(self, series: dict[str, list[float]], *keys: str) -> list[float]:
        output: list[float] = []
        for key in keys:
            output.extend(series.get(key, []))
        return output
