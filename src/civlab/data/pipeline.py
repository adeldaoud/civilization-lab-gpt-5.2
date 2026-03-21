"""Planning logic for empirical validation across multiple data sources."""

from __future__ import annotations

from civlab.data.models import DataRole, EmpiricalTarget, ValidationPlan
from civlab.data.registry import SourceRegistry


class EmpiricalPipeline:
    """Builds multi-source validation plans for the simulator."""

    def __init__(self, registry: SourceRegistry, targets: tuple[EmpiricalTarget, ...]) -> None:
        self.registry = registry
        self._targets = {target.key: target for target in targets}

    def targets(self) -> tuple[EmpiricalTarget, ...]:
        return tuple(self._targets[key] for key in sorted(self._targets))

    def plan_for_target(self, target_key: str) -> ValidationPlan:
        if target_key not in self._targets:
            raise KeyError(f"Unknown target '{target_key}'.")

        target = self._targets[target_key]
        available_sources = self.registry.list_sources()
        chosen_keys: list[str] = []
        covered_roles: set[DataRole] = set()
        notes: list[str] = []

        for source_key in target.recommended_sources:
            source = self.registry.get(source_key)
            chosen_keys.append(source.key)
            covered_roles.update(source.describe().roles)

        for role in target.required_roles:
            if role in covered_roles:
                continue
            for source in available_sources:
                if source.key in chosen_keys:
                    continue
                if role in source.describe().roles:
                    chosen_keys.append(source.key)
                    covered_roles.update(source.describe().roles)
                    break

        missing_roles = tuple(
            role for role in sorted(target.required_roles, key=lambda value: value.value) if role not in covered_roles
        )

        if "qog" in chosen_keys and "aiddata" in chosen_keys:
            notes.append(
                "QoG anchors institutions and governance, while AidData adds project-level and geospatial exposure."
            )
        elif "qog" in chosen_keys:
            notes.append("QoG is used here as a governance anchor, not as the sole empirical schema.")
        elif "aiddata" in chosen_keys:
            notes.append("AidData contributes finance and geospatial structure, not full governance coverage.")

        if "ucdp" in chosen_keys:
            notes.append("UCDP supplies the conflict outcomes needed to evaluate violence pathways and onset.")

        if "world_bank" in chosen_keys:
            notes.append("World Bank indicators supply macro and demographic outcomes for country-year validation.")

        if missing_roles:
            notes.append(
                "This target still needs additional adapters before full historical backtesting is possible."
            )
        else:
            notes.append(
                "This target can be backtested with a multi-source stack and compared to statistical baselines."
            )

        return ValidationPlan(
            target=target,
            source_keys=tuple(chosen_keys),
            missing_roles=missing_roles,
            notes=tuple(notes),
        )
