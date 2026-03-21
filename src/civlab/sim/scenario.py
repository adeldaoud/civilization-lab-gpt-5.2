"""Scenario loading and setup building."""

from __future__ import annotations

import json
from pathlib import Path

from civlab.sim.bootstrap import EmpiricalBootstrapSpec, EmpiricalLatentMapper
from civlab.sim.models import (
    BilateralRelationState,
    BiologyProfile,
    CohortState,
    CountryState,
    GeographyState,
    GovernmentState,
    LeaderState,
    PsychologyProfile,
    ResourceStock,
    SimulationSetup,
    SociologyProfile,
)


def _load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _profile_from_dict(profile_cls, payload: dict[str, object] | None):
    return profile_cls(**(payload or {}))


def _cohorts_from_payload(payload: list[dict[str, object]] | None) -> list[CohortState]:
    if not payload:
        return [
            CohortState(name="elite", social_class="elite", population_share=0.08, productivity=1.3, political_power=0.75),
            CohortState(name="middle", social_class="middle", population_share=0.37, productivity=1.0, political_power=0.45),
            CohortState(name="working", social_class="working", population_share=0.40, productivity=0.9, political_power=0.25),
            CohortState(name="rural_poor", social_class="poor", population_share=0.15, productivity=0.75, political_power=0.12),
        ]
    return [CohortState(**item) for item in payload]


def load_scenario(path: Path, *, steps_override: int | None = None) -> SimulationSetup:
    path = path.resolve()
    payload = _load_json(path)
    base_dir = path.parent
    mapper = EmpiricalLatentMapper()

    countries: dict[str, CountryState] = {}
    for item in payload["countries"]:
        item = dict(item)
        leader_payload = item.get("leader")
        base_country = CountryState(
            name=item["name"],
            iso3=item["iso3"],
            region=item.get("region", "unknown"),
            population=float(item.get("population", 10_000_000)),
            geography=_profile_from_dict(GeographyState, item.get("geography")),
            resources=_profile_from_dict(ResourceStock, item.get("resources")),
            biology=_profile_from_dict(BiologyProfile, item.get("biology")),
            psychology=_profile_from_dict(PsychologyProfile, item.get("psychology")),
            sociology=_profile_from_dict(SociologyProfile, item.get("sociology")),
            leader=_profile_from_dict(LeaderState, leader_payload) if leader_payload else LeaderState(name=f"{item['name']} Leader"),
            government=_profile_from_dict(GovernmentState, item.get("government")),
            cohorts=_cohorts_from_payload(item.get("cohorts")),
            trade_dependence=float(item.get("trade_dependence", 0.4)),
            urbanization=float(item.get("urbanization", 0.5)),
            policy_kind=item.get("policy", {}).get("kind", "rule"),
            policy_params=item.get("policy", {}).get("params", {}),
        )

        bootstrap = item.get("bootstrap")
        if bootstrap:
            spec = EmpiricalBootstrapSpec(
                country_iso3=bootstrap.get("country_iso3", item["iso3"]),
                country_iso_numeric=bootstrap.get("country_iso_numeric", ""),
                country_name=bootstrap.get("country_name", item["name"]),
                year=int(bootstrap["year"]),
                country_year_files=tuple((base_dir / relative_path).resolve() for relative_path in bootstrap.get("country_year_files", [])),
                project_exposure_files=tuple((base_dir / relative_path).resolve() for relative_path in bootstrap.get("project_exposure_files", [])),
            )
            base_country = mapper.bootstrap_country(
                name=item["name"],
                iso3=item["iso3"],
                region=item.get("region", "unknown"),
                spec=spec,
                base=base_country,
            )
            base_country.policy_kind = item.get("policy", {}).get("kind", base_country.policy_kind)
            base_country.policy_params = item.get("policy", {}).get("params", base_country.policy_params)

        base_country.normalize()
        countries[base_country.iso3] = base_country

    relations: dict[tuple[str, str], BilateralRelationState] = {}
    for relation_payload in payload.get("relations", []):
        relation = BilateralRelationState(**relation_payload)
        relation.normalize()
        relations[_relation_key(relation.country_a, relation.country_b)] = relation

    if not relations:
        iso_codes = list(countries)
        for index, iso_a in enumerate(iso_codes):
            for iso_b in iso_codes[index + 1 :]:
                relations[_relation_key(iso_a, iso_b)] = BilateralRelationState(country_a=iso_a, country_b=iso_b)

    return SimulationSetup(
        scenario_name=payload["scenario_name"],
        start_year=int(payload["start_year"]),
        duration_years=int(steps_override or payload.get("duration_years", 10)),
        countries=countries,
        relations=relations,
    )


def _relation_key(country_a: str, country_b: str) -> tuple[str, str]:
    return tuple(sorted((country_a, country_b)))
