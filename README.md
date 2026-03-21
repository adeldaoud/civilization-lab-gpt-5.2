# Civilization Lab

Working plan for a world civilization simulator focused on collective intelligence, conflict, peace, and human flourishing.

## Mission

Build a research-grade simulator that can represent civilizations as interacting political, economic, cultural, and psychological systems. The simulator should support:

- rule-based agents
- reinforcement-learning agents
- LLM-based agents
- hybrid agents that combine scripted constraints with learned policies

The system is intended to explain observed macro-social dynamics, test counterfactuals, and eventually support cautious forecasting about nations and humanity as a whole.
It should also support retrospective backtesting on real country-year and project-level data, especially through QoG, AidData, and related comparative datasets, so that forecasting and explanation are grounded in observed history.

## Core Research Questions

1. What mechanisms make civilizations cooperative, intelligent, resilient, or fragile?
2. Why do nations choose war, deterrence, bargaining, or peace under different institutional and material conditions?
3. How do biological tendencies, psychology, and social structure interact across micro, meso, and macro scales?
4. Which combinations of institutions, norms, geography, and incentives support flourishing?
5. Can simulation traces become training data for a civilization foundation model?
6. Can the simulator reproduce and explain observed trajectories in real country data before it is trusted for forecasts?

## Initial Product Decision

Do not build the first version directly inside a heavyweight game engine.

The recommended architecture is:

1. a headless simulation core in Python
2. a separate visualization client
3. pluggable agent policies that share one action interface

This keeps the science, training loops, calibration, and reproducibility independent from the rendering stack.

## Recommended Stack

- `Python` for the simulation core, experimentation, RL, and data work
- `Pydantic` or typed config objects for scenario definitions
- `Polars` or `DuckDB` for event logs and analysis
- `PyTorch` for learned policies and representation learning
- `Ray` only when distributed rollouts become necessary
- `Unity` as the first serious 3D visualization client
- optional `Cesium for Unreal` later if full-globe cinematic geospatial presentation becomes important

## Why This Stack

- `Minecraft` is strong for open-ended agent experiments and was useful for Project Sid, but it is a poor fit for an Earth-like civilization simulator with controlled institutions and geospatial realism.
- `Unity` is a better balance for research iteration, tooling, ML integration, and custom visualization.
- `Unreal` is attractive for visual fidelity and globe-scale rendering, especially with `Cesium`, but it adds engineering weight too early.

## Planned System Layers

1. `World Layer`: Earth-like geography, climate, resources, biomes, transport, and borders
2. `Society Layer`: states, governments, institutions, laws, religions, cultures, and class structure
3. `Agent Layer`: leaders, ministries, elites, firms, military actors, households, and population cohorts
4. `Decision Layer`: rule-based, RL, LLM, and hybrid policy engines
5. `Empirical Layer`: multi-source data ingestion, harmonization, calibration, backtesting, and hindcasting
6. `Research Layer`: metrics, experiments, forecasting, and interpretability
7. `Visual Layer`: map, timeline, diplomacy view, class tension view, and event replay

## First Deliverables

- a formal ontology for civilizations, institutions, agents, and events
- an Earth-based world model using real geography and resources
- a vertical slice with a small number of countries and population cohorts
- a conflict-and-flourishing metrics framework
- a simulator loop that can run the same scenario with different agent backends
- a country-year validation pipeline that can compare simulated trajectories to observed historical panels
- a visual analytics client for inspection and replay

## Documents

- `docs/system-architecture.md`
- `docs/research-framework.md`
- `docs/empirical-validation.md`
- `docs/technology-decision.md`
- `docs/roadmap.md`

## Empirical Data Principle

Do not let the simulator inherit the ontology of any single dataset.

- `QoG` is a strong governance anchor for country-year backtesting.
- `AidData` adds project-level, geospatial, and development-finance structure.
- `UCDP` adds conflict events and country-year violence outcomes.
- `World Bank` adds macroeconomic and demographic country-year indicators.
- the empirical layer should fuse multiple sources into simulator-native latent variables rather than mirror one source schema.

## Early Code Scaffold

The repository now includes a minimal Python package for the empirical layer:

- `pyproject.toml`
- `src/civlab/data/models.py`
- `src/civlab/data/registry.py`
- `src/civlab/data/pipeline.py`
- `src/civlab/data/sources/qog.py`
- `src/civlab/data/sources/aiddata.py`
- `src/civlab/data/sources/ucdp.py`
- `src/civlab/data/sources/world_bank.py`
- `src/civlab/cli.py`

Example commands:

- `python -m pip install -e .`
- `civlab list-sources`
- `civlab describe-source qog`
- `civlab plan-target conflict_risk`

## Source Inspirations

- Project Sid paper: `https://arxiv.org/abs/2411.00114`
- Project Sid repository: `https://github.com/altera-al/project-sid`
- AI Economist: `https://github.com/salesforce/ai-economist`
- Cesium for Unreal: `https://cesium.com/learn/cesium-unreal/ref-doc/`
