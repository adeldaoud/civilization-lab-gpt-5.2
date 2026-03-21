"""Simple CLI for inspecting the empirical data layer."""

from __future__ import annotations

import argparse
from typing import Iterable

from civlab.data.catalog import build_default_pipeline, default_targets


def _format_list(values: Iterable[str]) -> str:
    return ", ".join(values) if values else "-"


def main() -> None:
    parser = argparse.ArgumentParser(prog="civlab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-sources", help="List registered empirical data sources")
    subparsers.add_parser("list-targets", help="List supported empirical target families")

    describe_source = subparsers.add_parser(
        "describe-source",
        help="Show metadata for a specific empirical data source",
    )
    describe_source.add_argument("source_key")

    plan_target = subparsers.add_parser(
        "plan-target",
        help="Show the recommended multi-source validation plan for a target family",
    )
    plan_target.add_argument("target_key")

    args = parser.parse_args()
    pipeline = build_default_pipeline()

    if args.command == "list-sources":
        for source in pipeline.registry.list_sources():
            summary = source.describe()
            print(f"{summary.key}: {summary.name}")
            print(f"  roles: {_format_list(sorted(role.value for role in summary.roles))}")
            print(
                "  granularities: "
                f"{_format_list(sorted(granularity.value for granularity in summary.granularities))}"
            )
        return

    if args.command == "describe-source":
        summary = pipeline.registry.get(args.source_key).describe()
        print(f"{summary.name} ({summary.key})")
        print(f"homepage: {summary.homepage}")
        print(f"roles: {_format_list(sorted(role.value for role in summary.roles))}")
        print(
            "granularities: "
            f"{_format_list(sorted(granularity.value for granularity in summary.granularities))}"
        )
        print("assets:")
        for asset in summary.assets:
            print(f"  - {asset.slug}: {asset.title}")
            print(f"    url: {asset.url}")
        return

    if args.command == "list-targets":
        for target in default_targets():
            print(f"{target.key}: {target.label}")
            print(f"  roles: {_format_list(sorted(role.value for role in target.required_roles))}")
            print(f"  granularity: {target.preferred_granularity.value}")
        return

    if args.command == "plan-target":
        plan = pipeline.plan_for_target(args.target_key)
        print(f"{plan.target.label} ({plan.target.key})")
        print(f"target granularity: {plan.target.preferred_granularity.value}")
        print(f"source stack: {_format_list(plan.source_keys)}")
        if plan.missing_roles:
            print(f"missing roles: {_format_list(role.value for role in plan.missing_roles)}")
        else:
            print("missing roles: -")
        print("notes:")
        for note in plan.notes:
            print(f"  - {note}")
        return


if __name__ == "__main__":
    main()

