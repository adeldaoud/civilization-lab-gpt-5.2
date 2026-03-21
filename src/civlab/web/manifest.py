"""Manifest builder for browser dashboard runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def build_dashboard_manifest(root: Path) -> Path:
    root = root.resolve()
    artifacts_dir = root / "artifacts"
    runs_dir = root / "web" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = runs_dir / "index.json"

    runs: list[dict[str, object]] = []
    if artifacts_dir.exists():
        for run_dir in sorted((path for path in artifacts_dir.iterdir() if path.is_dir()), key=lambda item: item.name):
            summary_path = run_dir / "summary.json"
            country_year_path = run_dir / "country_year.csv"
            events_path = run_dir / "events.jsonl"
            if not summary_path.exists() or not country_year_path.exists() or not events_path.exists():
                continue
            with summary_path.open("r", encoding="utf-8") as handle:
                summary = json.load(handle)
            runs.append(
                {
                    "slug": run_dir.name,
                    "scenario_name": summary.get("scenario_name", run_dir.name),
                    "start_year": summary.get("start_year"),
                    "final_year": summary.get("final_year"),
                    "steps": summary.get("steps"),
                    "event_count": summary.get("event_count"),
                    "summary_path": f"/artifacts/{run_dir.name}/summary.json",
                    "country_year_path": f"/artifacts/{run_dir.name}/country_year.csv",
                    "events_path": f"/artifacts/{run_dir.name}/events.jsonl",
                }
            )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runs": runs,
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return manifest_path

