# Restart Checkpoint — 2026-03-27

This file records the current saved state of the project so work can resume cleanly after a PC restart.

## Saved State

- branch: `main`
- commit: `63f49dcdf83e84a60fbe38c4e42e6f01783aa2b3`
- remote: `https://github.com/adeldaoud/civilization-lab-gpt-5.2`
- working tree: clean at checkpoint creation

## Current Artifacts

- `artifacts/two-country/`
- `artifacts/kenya-ethiopia/`

Each run currently contains:

- `summary.json`
- `country_year.csv`
- `events.jsonl`

The browser dashboard manifest is regenerated locally from `artifacts/` and does not need to be committed.

## Resume After Reboot

From the project root:

- `python -m civlab.cli refresh-dashboard --root .`
- `python -m civlab.cli serve-dashboard --root . --port 8000`

Or use:

- `powershell -ExecutionPolicy Bypass -File .\scripts\resume-dashboard.ps1`

Then open:

- `http://127.0.0.1:8000/web/index.html`

## Restarting the Simulator From Another Time Point

The simulator already supports alternate time points through scenario configuration.

- edit the `start_year` field in a scenario file such as `scenarios/two_country_rivalry.json`
- or create a new scenario JSON with a different `start_year`
- optionally override duration with `--steps`

Example:

- `python -m civlab.cli run-scenario scenarios/two_country_rivalry.json --steps 25 --output artifacts/two-country-alt --root .`

If a new historical start period is needed, the next implementation step is to add explicit checkpoint/resume support from saved simulation state, rather than only from scenario definitions.
