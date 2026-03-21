"""Policy interfaces and baseline policy implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from civlab.sim.models import CountryState, PolicyDecision, SimulationSetup, clamp


class PolicyAdapter(ABC):
    kind: str

    @abstractmethod
    def decide(self, country: CountryState, setup: SimulationSetup) -> PolicyDecision:
        """Return a policy decision for the current simulation step."""


class RulePolicy(PolicyAdapter):
    kind = "rule"

    def __init__(self, **weights: float) -> None:
        self.weights = weights

    def decide(self, country: CountryState, setup: SimulationSetup) -> PolicyDecision:
        scarcity = clamp(1.0 - ((country.resources.food + country.resources.energy + country.resources.treasury) / 300.0))
        unrest = clamp(
            sum(cohort.grievances * cohort.population_share for cohort in country.cohorts) + country.sociology.polarization * 0.25
        )
        threat = clamp(country.external_threat * 0.5 + country.conflict_burden * 0.3 + country.leader.hawkishness * 0.2)
        competence = country.leader.competence

        tax_rate = clamp(0.16 + 0.18 * scarcity + 0.08 * threat + 0.04 * country.sociology.inequality, 0.08, 0.55)
        welfare_share = clamp(0.25 + 0.35 * unrest + 0.10 * competence - 0.15 * threat)
        military_share = clamp(0.15 + 0.45 * threat + 0.10 * country.biology.aggression)
        infrastructure_share = clamp(0.22 + 0.15 * competence + 0.10 * country.geography.trade_access - 0.10 * threat)
        institution_share = clamp(0.22 + 0.20 * competence + 0.15 * country.sociology.polarization - 0.05 * threat)
        repression = clamp(0.08 + 0.35 * unrest + 0.10 * threat - 0.18 * country.psychology.self_control)
        diplomacy_posture = clamp(0.62 + 0.15 * competence - 0.35 * threat - 0.10 * country.leader.hawkishness)

        return PolicyDecision(
            tax_rate=tax_rate,
            welfare_share=welfare_share,
            military_share=military_share,
            infrastructure_share=infrastructure_share,
            institution_share=institution_share,
            repression=repression,
            diplomacy_posture=diplomacy_posture,
            rationale="baseline rule policy",
        )


class HybridPolicy(RulePolicy):
    kind = "hybrid"

    def decide(self, country: CountryState, setup: SimulationSetup) -> PolicyDecision:
        decision = super().decide(country, setup)
        decision.infrastructure_share = clamp(decision.infrastructure_share + 0.05 * country.external_finance_exposure)
        decision.institution_share = clamp(decision.institution_share + 0.04 * country.sociology.bureaucratic_quality)
        decision.repression = clamp(decision.repression - 0.05 * country.psychology.self_control)
        decision.rationale = "hybrid policy using rule backbone with latent-state adjustments"
        return decision


class RLStylePolicy(RulePolicy):
    kind = "rl"

    def decide(self, country: CountryState, setup: SimulationSetup) -> PolicyDecision:
        decision = super().decide(country, setup)
        exploration = country.policy_params.get("exploration", 0.08)
        decision.welfare_share = clamp(decision.welfare_share + exploration * (0.5 - country.sociology.inequality))
        decision.military_share = clamp(decision.military_share + exploration * (country.external_threat - 0.3))
        decision.rationale = "rl-style placeholder policy using rule baseline plus exploration bias"
        return decision


class LLMStylePolicy(RulePolicy):
    kind = "llm"

    def decide(self, country: CountryState, setup: SimulationSetup) -> PolicyDecision:
        decision = super().decide(country, setup)
        decision.diplomacy_posture = clamp(
            decision.diplomacy_posture + 0.06 * country.leader.strategic_horizon + 0.04 * country.psychology.trust
        )
        decision.institution_share = clamp(decision.institution_share + 0.04 * country.sociology.information_integrity)
        decision.rationale = "llm-style placeholder policy using rule baseline plus deliberative bias"
        return decision


def build_policy(kind: str, params: dict[str, float] | None = None) -> PolicyAdapter:
    params = params or {}
    if kind == "rule":
        return RulePolicy(**params)
    if kind == "hybrid":
        return HybridPolicy(**params)
    if kind == "rl":
        return RLStylePolicy(**params)
    if kind == "llm":
        return LLMStylePolicy(**params)
    raise ValueError(f"Unsupported policy kind '{kind}'.")
