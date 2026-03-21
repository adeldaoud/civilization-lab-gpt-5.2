"""Core world and agent state models for the simulator."""

from __future__ import annotations

from dataclasses import dataclass, field


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


@dataclass
class GeographyState:
    arable_land: float = 0.5
    minerals: float = 0.5
    energy: float = 0.5
    ruggedness: float = 0.5
    coastal_access: float = 0.5
    climate_risk: float = 0.3
    trade_access: float = 0.5

    def normalize(self) -> None:
        self.arable_land = clamp(self.arable_land)
        self.minerals = clamp(self.minerals)
        self.energy = clamp(self.energy)
        self.ruggedness = clamp(self.ruggedness)
        self.coastal_access = clamp(self.coastal_access)
        self.climate_risk = clamp(self.climate_risk)
        self.trade_access = clamp(self.trade_access)


@dataclass
class ResourceStock:
    food: float = 50.0
    energy: float = 50.0
    minerals: float = 50.0
    industry: float = 50.0
    knowledge: float = 50.0
    treasury: float = 50.0

    def normalize(self) -> None:
        self.food = max(0.0, self.food)
        self.energy = max(0.0, self.energy)
        self.minerals = max(0.0, self.minerals)
        self.industry = max(0.0, self.industry)
        self.knowledge = max(0.0, self.knowledge)
        self.treasury = max(0.0, self.treasury)


@dataclass
class BiologyProfile:
    aggression: float = 0.45
    stress_reactivity: float = 0.5
    self_preservation: float = 0.6
    health_burden: float = 0.2

    def normalize(self) -> None:
        self.aggression = clamp(self.aggression)
        self.stress_reactivity = clamp(self.stress_reactivity)
        self.self_preservation = clamp(self.self_preservation)
        self.health_burden = clamp(self.health_burden)


@dataclass
class PsychologyProfile:
    trust: float = 0.5
    fear: float = 0.3
    self_control: float = 0.55
    status_drive: float = 0.45
    trauma: float = 0.1

    def normalize(self) -> None:
        self.trust = clamp(self.trust)
        self.fear = clamp(self.fear)
        self.self_control = clamp(self.self_control)
        self.status_drive = clamp(self.status_drive)
        self.trauma = clamp(self.trauma)


@dataclass
class SociologyProfile:
    legitimacy: float = 0.5
    inequality: float = 0.35
    polarization: float = 0.3
    institutional_quality: float = 0.5
    bureaucratic_quality: float = 0.5
    information_integrity: float = 0.5
    collective_efficacy: float = 0.5

    def normalize(self) -> None:
        self.legitimacy = clamp(self.legitimacy)
        self.inequality = clamp(self.inequality)
        self.polarization = clamp(self.polarization)
        self.institutional_quality = clamp(self.institutional_quality)
        self.bureaucratic_quality = clamp(self.bureaucratic_quality)
        self.information_integrity = clamp(self.information_integrity)
        self.collective_efficacy = clamp(self.collective_efficacy)


@dataclass
class CohortState:
    name: str
    social_class: str
    population_share: float
    productivity: float = 1.0
    income: float = 50.0
    grievances: float = 0.3
    trust_in_state: float = 0.5
    mobilization: float = 0.15
    political_power: float = 0.25
    cultural_cohesion: float = 0.5

    def normalize(self) -> None:
        self.population_share = clamp(self.population_share, 0.0, 1.0)
        self.productivity = max(0.1, self.productivity)
        self.income = max(0.0, self.income)
        self.grievances = clamp(self.grievances)
        self.trust_in_state = clamp(self.trust_in_state)
        self.mobilization = clamp(self.mobilization)
        self.political_power = clamp(self.political_power)
        self.cultural_cohesion = clamp(self.cultural_cohesion)


@dataclass
class LeaderState:
    name: str
    ideology: str = "centrist"
    competence: float = 0.55
    hawkishness: float = 0.45
    charisma: float = 0.5
    strategic_horizon: float = 0.55

    def normalize(self) -> None:
        self.competence = clamp(self.competence)
        self.hawkishness = clamp(self.hawkishness)
        self.charisma = clamp(self.charisma)
        self.strategic_horizon = clamp(self.strategic_horizon)


@dataclass
class GovernmentState:
    tax_rate: float = 0.22
    welfare_share: float = 0.22
    military_share: float = 0.18
    infrastructure_share: float = 0.22
    institution_share: float = 0.18
    repression: float = 0.12
    diplomacy_posture: float = 0.55

    def normalize(self) -> None:
        self.tax_rate = clamp(self.tax_rate, 0.05, 0.7)
        self.welfare_share = clamp(self.welfare_share)
        self.military_share = clamp(self.military_share)
        self.infrastructure_share = clamp(self.infrastructure_share)
        self.institution_share = clamp(self.institution_share)
        total = self.welfare_share + self.military_share + self.infrastructure_share + self.institution_share
        if total <= 0:
            self.welfare_share = 0.25
            self.military_share = 0.25
            self.infrastructure_share = 0.25
            self.institution_share = 0.25
        else:
            self.welfare_share /= total
            self.military_share /= total
            self.infrastructure_share /= total
            self.institution_share /= total
        self.repression = clamp(self.repression)
        self.diplomacy_posture = clamp(self.diplomacy_posture)


@dataclass
class CountryState:
    name: str
    iso3: str
    region: str
    population: float
    geography: GeographyState = field(default_factory=GeographyState)
    resources: ResourceStock = field(default_factory=ResourceStock)
    biology: BiologyProfile = field(default_factory=BiologyProfile)
    psychology: PsychologyProfile = field(default_factory=PsychologyProfile)
    sociology: SociologyProfile = field(default_factory=SociologyProfile)
    leader: LeaderState = field(default_factory=lambda: LeaderState(name="Unnamed Leader"))
    government: GovernmentState = field(default_factory=GovernmentState)
    cohorts: list[CohortState] = field(default_factory=list)
    trade_dependence: float = 0.4
    urbanization: float = 0.5
    external_finance_exposure: float = 0.0
    conflict_burden: float = 0.0
    war_exhaustion: float = 0.0
    external_threat: float = 0.2
    economic_output: float = 0.0
    flourishing: float = 0.0
    conflict_risk: float = 0.0
    policy_kind: str = "rule"
    policy_params: dict[str, float] = field(default_factory=dict)

    def normalize(self) -> None:
        self.population = max(1000.0, self.population)
        self.geography.normalize()
        self.resources.normalize()
        self.biology.normalize()
        self.psychology.normalize()
        self.sociology.normalize()
        self.leader.normalize()
        self.government.normalize()
        self.trade_dependence = clamp(self.trade_dependence)
        self.urbanization = clamp(self.urbanization)
        self.external_finance_exposure = clamp(self.external_finance_exposure)
        self.conflict_burden = clamp(self.conflict_burden)
        self.war_exhaustion = clamp(self.war_exhaustion)
        self.external_threat = clamp(self.external_threat)
        for cohort in self.cohorts:
            cohort.normalize()
        total_share = sum(cohort.population_share for cohort in self.cohorts)
        if total_share > 0:
            for cohort in self.cohorts:
                cohort.population_share /= total_share

    @property
    def population_millions(self) -> float:
        return max(self.population / 1_000_000.0, 0.05)


@dataclass
class BilateralRelationState:
    country_a: str
    country_b: str
    trade_intensity: float = 0.35
    alliance_score: float = 0.0
    border_tension: float = 0.2
    active_conflict: bool = False

    def normalize(self) -> None:
        self.trade_intensity = clamp(self.trade_intensity)
        self.alliance_score = clamp(self.alliance_score)
        self.border_tension = clamp(self.border_tension)


@dataclass
class PolicyDecision:
    tax_rate: float
    welfare_share: float
    military_share: float
    infrastructure_share: float
    institution_share: float
    repression: float
    diplomacy_posture: float
    rationale: str = ""


@dataclass
class SimulationEvent:
    year: int
    event_type: str
    actors: list[str]
    severity: float
    detail: str


@dataclass
class CountrySnapshot:
    year: int
    country: str
    iso3: str
    economic_output: float
    flourishing: float
    legitimacy: float
    trust: float
    inequality: float
    polarization: float
    conflict_risk: float
    external_threat: float
    treasury: float
    population: float


@dataclass
class SimulationResult:
    scenario_name: str
    start_year: int
    steps: int
    snapshots: list[CountrySnapshot]
    events: list[SimulationEvent]


@dataclass
class SimulationSetup:
    scenario_name: str
    start_year: int
    duration_years: int
    countries: dict[str, CountryState]
    relations: dict[tuple[str, str], BilateralRelationState]
