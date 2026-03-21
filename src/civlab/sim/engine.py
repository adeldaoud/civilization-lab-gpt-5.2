"""Simulation engine and result writers."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from civlab.sim.models import (
    BilateralRelationState,
    CountrySnapshot,
    CountryState,
    PolicyDecision,
    SimulationEvent,
    SimulationResult,
    SimulationSetup,
    clamp,
)
from civlab.sim.policies import build_policy


def run_simulation(setup: SimulationSetup) -> SimulationResult:
    snapshots: list[CountrySnapshot] = []
    events: list[SimulationEvent] = []

    for step in range(setup.duration_years):
        year = setup.start_year + step
        policy_decisions = {
            iso3: build_policy(country.policy_kind, country.policy_params).decide(country, setup)
            for iso3, country in setup.countries.items()
        }

        for iso3, decision in policy_decisions.items():
            _apply_policy(setup.countries[iso3], decision)
            events.append(
                SimulationEvent(
                    year=year,
                    event_type="policy",
                    actors=[iso3],
                    severity=0.2,
                    detail=decision.rationale,
                )
            )

        for iso3, country in setup.countries.items():
            _update_country(country)
            if _domestic_unrest(country):
                events.append(
                    SimulationEvent(
                        year=year,
                        event_type="domestic_unrest",
                        actors=[iso3],
                        severity=country.sociology.polarization,
                        detail=f"{country.name} experiences heightened domestic unrest",
                    )
                )

        for relation in setup.relations.values():
            events.extend(_resolve_relation(year, relation, setup.countries))

        for country in setup.countries.values():
            _finalize_country_metrics(country)
            snapshots.append(
                CountrySnapshot(
                    year=year,
                    country=country.name,
                    iso3=country.iso3,
                    economic_output=country.economic_output,
                    flourishing=country.flourishing,
                    legitimacy=country.sociology.legitimacy,
                    trust=country.psychology.trust,
                    inequality=country.sociology.inequality,
                    polarization=country.sociology.polarization,
                    conflict_risk=country.conflict_risk,
                    external_threat=country.external_threat,
                    treasury=country.resources.treasury,
                    population=country.population,
                )
            )

    return SimulationResult(
        scenario_name=setup.scenario_name,
        start_year=setup.start_year,
        steps=setup.duration_years,
        snapshots=snapshots,
        events=events,
    )


def write_simulation_outputs(result: SimulationResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.json"
    country_year_path = output_dir / "country_year.csv"
    events_path = output_dir / "events.jsonl"

    final_year = result.start_year + result.steps - 1
    final_snapshots = [snapshot for snapshot in result.snapshots if snapshot.year == final_year]
    summary = {
        "scenario_name": result.scenario_name,
        "start_year": result.start_year,
        "steps": result.steps,
        "final_year": final_year,
        "countries": [asdict(snapshot) for snapshot in final_snapshots],
        "event_count": len(result.events),
    }
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    with country_year_path.open("w", encoding="utf-8", newline="") as handle:
        if result.snapshots:
            writer = csv.DictWriter(handle, fieldnames=list(asdict(result.snapshots[0]).keys()))
            writer.writeheader()
            for snapshot in result.snapshots:
                writer.writerow(asdict(snapshot))

    with events_path.open("w", encoding="utf-8") as handle:
        for event in result.events:
            handle.write(json.dumps(asdict(event)) + "\n")


def _apply_policy(country: CountryState, decision: PolicyDecision) -> None:
    country.government.tax_rate = decision.tax_rate
    country.government.welfare_share = decision.welfare_share
    country.government.military_share = decision.military_share
    country.government.infrastructure_share = decision.infrastructure_share
    country.government.institution_share = decision.institution_share
    country.government.repression = decision.repression
    country.government.diplomacy_posture = decision.diplomacy_posture
    country.government.normalize()


def _update_country(country: CountryState) -> None:
    geo = country.geography
    soc = country.sociology
    psy = country.psychology
    bio = country.biology
    gov = country.government
    resources = country.resources

    resource_productivity = (
        0.18 * geo.arable_land
        + 0.14 * geo.minerals
        + 0.14 * geo.energy
        + 0.20 * geo.trade_access
        + 0.08 * geo.coastal_access
        + 0.12 * (resources.industry / 100.0)
        + 0.14 * soc.institutional_quality
    )
    labor_productivity = sum(cohort.population_share * cohort.productivity for cohort in country.cohorts)
    output = country.population_millions * 6.0 * resource_productivity * labor_productivity * (1.1 - bio.health_burden)
    country.economic_output = max(0.0, output)

    tax_revenue = country.economic_output * gov.tax_rate
    non_tax_revenue = country.economic_output * (0.03 + 0.02 * soc.institutional_quality)
    allocatable_budget = tax_revenue * 0.92
    welfare_budget = allocatable_budget * gov.welfare_share
    military_budget = allocatable_budget * gov.military_share
    infrastructure_budget = allocatable_budget * gov.infrastructure_share
    institution_budget = allocatable_budget * gov.institution_share
    corruption_leakage = tax_revenue * 0.08 * soc.inequality

    resources.treasury += tax_revenue + non_tax_revenue - (
        welfare_budget + military_budget + infrastructure_budget + institution_budget + corruption_leakage
    )
    resources.treasury = max(resources.treasury, 0.0)
    resources.industry += infrastructure_budget * 0.4 - geo.climate_risk * 0.6
    resources.knowledge += institution_budget * 0.5 + infrastructure_budget * 0.15 - gov.repression * 1.5
    resources.food += geo.arable_land * 4.0 - country.population_millions * 0.15 - geo.climate_risk * 1.2
    resources.energy += geo.energy * 2.5 - military_budget * 0.2
    resources.minerals += geo.minerals * 2.0 - infrastructure_budget * 0.15
    resources.normalize()

    welfare_per_capita = welfare_budget / max(country.population_millions, 0.1)
    avg_grievance = 0.0
    avg_trust = 0.0

    for cohort in country.cohorts:
        class_bias = 0.1 if cohort.social_class == "elite" else -0.02
        cohort.income = max(0.0, cohort.income + welfare_per_capita * cohort.population_share + output * 0.04 * cohort.productivity + class_bias)
        cohort.grievances = clamp(
            cohort.grievances
            + 0.08 * soc.inequality
            + 0.10 * gov.repression
            + 0.08 * psy.fear
            - 0.12 * welfare_per_capita / 10.0
            - 0.08 * soc.legitimacy
        )
        cohort.trust_in_state = clamp(
            cohort.trust_in_state
            + 0.10 * soc.legitimacy
            + 0.05 * welfare_per_capita / 10.0
            - 0.12 * gov.repression
            - 0.08 * cohort.grievances
        )
        cohort.mobilization = clamp(
            cohort.mobilization + 0.12 * cohort.grievances + 0.08 * soc.polarization - 0.10 * cohort.trust_in_state
        )
        cohort.cultural_cohesion = clamp(cohort.cultural_cohesion + 0.05 * psy.trust - 0.08 * soc.polarization)
        avg_grievance += cohort.grievances * cohort.population_share
        avg_trust += cohort.trust_in_state * cohort.population_share

    psy.trust = clamp(0.55 * psy.trust + 0.25 * avg_trust + 0.15 * soc.legitimacy - 0.10 * gov.repression)
    psy.fear = clamp(0.60 * psy.fear + 0.20 * country.external_threat + 0.10 * country.conflict_burden + 0.10 * geo.climate_risk)
    psy.trauma = clamp(0.70 * psy.trauma + 0.25 * country.conflict_burden)

    soc.institutional_quality = clamp(
        soc.institutional_quality + 0.05 * institution_budget / max(country.economic_output, 1.0) - 0.03 * gov.repression
    )
    soc.bureaucratic_quality = clamp(
        soc.bureaucratic_quality + 0.04 * institution_budget / max(country.economic_output, 1.0) - 0.02 * gov.repression
    )
    soc.polarization = clamp(0.70 * soc.polarization + 0.18 * avg_grievance + 0.08 * gov.repression - 0.08 * psy.trust)
    soc.legitimacy = clamp(
        0.65 * soc.legitimacy
        + 0.16 * soc.institutional_quality
        + 0.10 * avg_trust
        - 0.12 * gov.repression
        - 0.12 * soc.inequality
        - 0.10 * country.conflict_burden
    )
    soc.collective_efficacy = clamp(
        0.60 * soc.collective_efficacy + 0.18 * soc.legitimacy + 0.10 * psy.trust - 0.08 * soc.polarization
    )
    soc.inequality = clamp(
        0.85 * soc.inequality + 0.08 * max(0.0, 1.0 - gov.welfare_share) + 0.03 * max(0.0, 0.3 - gov.tax_rate)
    )

    country.external_threat = clamp(0.75 * country.external_threat + 0.10 * country.conflict_burden + 0.10 * psy.fear)
    country.war_exhaustion = clamp(0.80 * country.war_exhaustion + 0.15 * country.conflict_burden)


def _resolve_relation(
    year: int,
    relation: BilateralRelationState,
    countries: dict[str, CountryState],
) -> list[SimulationEvent]:
    relation.normalize()
    country_a = countries[relation.country_a]
    country_b = countries[relation.country_b]
    events: list[SimulationEvent] = []

    scarcity_a = 1.0 - clamp((country_a.resources.food + country_a.resources.energy) / 200.0)
    scarcity_b = 1.0 - clamp((country_b.resources.food + country_b.resources.energy) / 200.0)
    diplomacy_buffer = (country_a.government.diplomacy_posture + country_b.government.diplomacy_posture) / 2.0
    tension = clamp(
        0.20 * relation.border_tension
        + 0.15 * country_a.leader.hawkishness
        + 0.15 * country_b.leader.hawkishness
        + 0.10 * country_a.biology.aggression
        + 0.10 * country_b.biology.aggression
        + 0.10 * scarcity_a
        + 0.10 * scarcity_b
        + 0.10 * country_a.psychology.fear
        + 0.10 * country_b.psychology.fear
        - 0.10 * relation.trade_intensity
        - 0.10 * relation.alliance_score
        - 0.18 * diplomacy_buffer
    )
    relation.border_tension = clamp(0.65 * relation.border_tension + 0.35 * tension)

    if relation.active_conflict:
        if tension < 0.45:
            relation.active_conflict = False
            relation.border_tension = clamp(relation.border_tension - 0.20)
            events.append(
                SimulationEvent(
                    year=year,
                    event_type="peace_agreement",
                    actors=[country_a.iso3, country_b.iso3],
                    severity=0.45,
                    detail=f"{country_a.name} and {country_b.name} de-escalate into an uneasy peace",
                )
            )
        else:
            severity = clamp(0.45 + 0.45 * tension)
            _apply_conflict_losses(country_a, country_b, severity)
            events.append(
                SimulationEvent(
                    year=year,
                    event_type="ongoing_conflict",
                    actors=[country_a.iso3, country_b.iso3],
                    severity=severity,
                    detail=f"{country_a.name} and {country_b.name} remain in armed confrontation",
                )
            )
        return events

    if tension > 0.82:
        relation.active_conflict = True
        severity = clamp(0.50 + 0.35 * tension)
        _apply_conflict_losses(country_a, country_b, severity)
        events.append(
            SimulationEvent(
                year=year,
                event_type="war_onset",
                actors=[country_a.iso3, country_b.iso3],
                severity=severity,
                detail=f"{country_a.name} and {country_b.name} enter open conflict",
            )
        )
    elif tension > 0.62:
        events.append(
            SimulationEvent(
                year=year,
                event_type="border_crisis",
                actors=[country_a.iso3, country_b.iso3],
                severity=tension,
                detail=f"{country_a.name} and {country_b.name} escalate a border crisis",
            )
        )
        country_a.external_threat = clamp(country_a.external_threat + 0.12 * tension)
        country_b.external_threat = clamp(country_b.external_threat + 0.12 * tension)

    return events


def _apply_conflict_losses(country_a: CountryState, country_b: CountryState, severity: float) -> None:
    casualties_a = country_a.population * 0.0002 * severity
    casualties_b = country_b.population * 0.0002 * severity
    for country, casualties in ((country_a, casualties_a), (country_b, casualties_b)):
        country.population = max(1000.0, country.population - casualties)
        country.resources.treasury = max(0.0, country.resources.treasury - 2.5 * severity)
        country.resources.industry = max(0.0, country.resources.industry - 1.6 * severity)
        country.conflict_burden = clamp(country.conflict_burden + 0.20 * severity)
        country.war_exhaustion = clamp(country.war_exhaustion + 0.25 * severity)
        country.external_threat = clamp(country.external_threat + 0.18 * severity)


def _domestic_unrest(country: CountryState) -> bool:
    mean_mobilization = sum(cohort.mobilization * cohort.population_share for cohort in country.cohorts)
    return mean_mobilization + country.sociology.polarization > 0.95


def _finalize_country_metrics(country: CountryState) -> None:
    social_trust = country.psychology.trust
    peace = 1.0 - clamp(country.conflict_burden + country.war_exhaustion * 0.5)
    prosperity = clamp(country.economic_output / (country.population_millions * 12.0))
    capacity = (country.sociology.institutional_quality + country.sociology.bureaucratic_quality) / 2.0
    equality = 1.0 - country.sociology.inequality
    resilience = 1.0 - country.geography.climate_risk

    country.conflict_risk = clamp(
        0.25 * country.external_threat
        + 0.20 * country.sociology.polarization
        + 0.15 * country.biology.aggression
        + 0.15 * country.psychology.fear
        + 0.15 * country.conflict_burden
        - 0.15 * country.government.diplomacy_posture
        - 0.10 * social_trust
    )
    country.flourishing = clamp(
        0.18 * prosperity
        + 0.16 * social_trust
        + 0.18 * country.sociology.legitimacy
        + 0.16 * equality
        + 0.16 * peace
        + 0.10 * capacity
        + 0.06 * resilience
    )
