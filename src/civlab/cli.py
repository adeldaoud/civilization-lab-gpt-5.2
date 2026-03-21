"""Simple CLI for inspecting the empirical data layer."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from civlab.data.catalog import build_default_pipeline, default_targets
from civlab.data.io import default_processed_path, default_raw_path
from civlab.data.models import CanonicalTable
from civlab.data.schema import SCHEMAS
from civlab.sim.engine import run_simulation, write_simulation_outputs
from civlab.sim.scenario import load_scenario


def _format_list(values: Iterable[str]) -> str:
    return ", ".join(values) if values else "-"


def main() -> None:
    parser = argparse.ArgumentParser(prog="civlab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-sources", help="List registered empirical data sources")
    subparsers.add_parser("list-targets", help="List supported empirical target families")

    list_assets = subparsers.add_parser("list-assets", help="List downloadable assets for a source")
    list_assets.add_argument("source_key")

    show_schema = subparsers.add_parser("show-schema", help="Show the canonical schema for a table")
    show_schema.add_argument("table", choices=[table.value for table in SCHEMAS])

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

    download_asset = subparsers.add_parser(
        "download-asset",
        help="Download a raw asset from an official source endpoint",
    )
    download_asset.add_argument("source_key")
    download_asset.add_argument("asset_slug")
    download_asset.add_argument("--root", default=".", help="Project root containing data/raw and data/processed")
    download_asset.add_argument("--series", action="append", default=[], help="Series codes for API-backed assets")

    normalize_asset = subparsers.add_parser(
        "normalize-asset",
        help="Normalize a raw asset into a canonical flat table",
    )
    normalize_asset.add_argument("source_key")
    normalize_asset.add_argument("asset_slug")
    normalize_asset.add_argument("--root", default=".", help="Project root containing data/raw and data/processed")
    normalize_asset.add_argument("--input", help="Raw file path. Defaults to data/raw/<source>/...")
    normalize_asset.add_argument("--output", help="Processed file path. Defaults to data/processed/<source>/...")
    normalize_asset.add_argument("--series", action="append", default=[], help="Series subset for long-form output")

    ingest_asset = subparsers.add_parser(
        "ingest-asset",
        help="Download and normalize an asset in one step",
    )
    ingest_asset.add_argument("source_key")
    ingest_asset.add_argument("asset_slug")
    ingest_asset.add_argument("--root", default=".", help="Project root containing data/raw and data/processed")
    ingest_asset.add_argument("--series", action="append", default=[], help="Series subset for long-form output")

    run_scenario = subparsers.add_parser(
        "run-scenario",
        help="Run a simulator scenario and write outputs",
    )
    run_scenario.add_argument("scenario_path")
    run_scenario.add_argument("--steps", type=int, help="Override scenario duration in years")
    run_scenario.add_argument("--output", default="artifacts/latest-run", help="Output directory for summary and logs")

    describe_scenario = subparsers.add_parser(
        "describe-scenario",
        help="Print a compact summary of a scenario definition",
    )
    describe_scenario.add_argument("scenario_path")

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

    if args.command == "list-assets":
        source = pipeline.registry.get(args.source_key)
        summary = source.describe()
        for asset in summary.assets:
            table = asset.canonical_table.value if asset.canonical_table else "-"
            print(f"{asset.slug}: {asset.title}")
            print(f"  format: {asset.asset_format.value}")
            print(f"  canonical: {table}")
            print(f"  download: {asset.download_url or '-'}")
        return

    if args.command == "show-schema":
        schema = SCHEMAS[CanonicalTable(args.table)]
        print(f"{schema.table.value}: {schema.description}")
        for column in schema.columns:
            print(f"  - {column.name} [{column.dtype}]")
            print(f"    {column.description}")
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

    if args.command == "describe-scenario":
        setup = load_scenario(Path(args.scenario_path), steps_override=args.steps if hasattr(args, "steps") else None)
        print(f"{setup.scenario_name}")
        print(f"  start_year: {setup.start_year}")
        print(f"  duration_years: {setup.duration_years}")
        print(f"  countries: {_format_list(sorted(setup.countries))}")
        print(f"  relations: {len(setup.relations)}")
        return

    if args.command in {"download-asset", "normalize-asset", "ingest-asset"}:
        root = Path(args.root).resolve()
        source = pipeline.registry.get(args.source_key)
        asset = source.get_asset(args.asset_slug)
        series = args.series or None

        if args.command == "download-asset":
            result = source.download_asset(args.asset_slug, root, series_codes=series)
            print(result.path)
            return

        raw_path = Path(args.input).resolve() if getattr(args, "input", None) else default_raw_path(root, source.key, asset)
        output_path = (
            Path(args.output).resolve()
            if getattr(args, "output", None)
            else default_processed_path(root, source.key, asset)
        )

        if args.command == "normalize-asset":
            result = source.normalize_asset(args.asset_slug, raw_path, output_path, series_codes=series)
            print(f"{result.path} ({result.row_count} rows)")
            return

        download_result = source.download_asset(args.asset_slug, root, series_codes=series)
        normalization = source.normalize_asset(
            args.asset_slug,
            download_result.path,
            default_processed_path(root, source.key, asset),
            series_codes=series,
        )
        print(f"raw: {download_result.path}")
        print(f"normalized: {normalization.path} ({normalization.row_count} rows)")
        return

    if args.command == "run-scenario":
        scenario_path = Path(args.scenario_path).resolve()
        setup = load_scenario(scenario_path, steps_override=args.steps)
        result = run_simulation(setup)
        output_dir = Path(args.output).resolve()
        write_simulation_outputs(result, output_dir)
        final_year = setup.start_year + setup.duration_years - 1
        print(f"scenario: {setup.scenario_name}")
        print(f"final_year: {final_year}")
        print(f"output: {output_dir}")
        print(f"events: {len(result.events)}")
        return


if __name__ == "__main__":
    main()
