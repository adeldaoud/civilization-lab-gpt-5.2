# Empirical Validation

## Purpose

This project is not only a sandbox simulator.
It should be an empirical research system that can:

- backtest against observed country trajectories
- generate cautious forecasts
- explain why outcomes emerged

## Evidence Stack

The simulator should not be designed around the schema of one dataset.

Use an evidence stack:

- governance and institutions from sources such as QoG
- development-finance and project exposure from sources such as AidData
- conflict, macroeconomic, demographic, and survey layers from additional adapters

The simulator's latent state should sit above the data sources, so new datasets refine or challenge the model rather than redefine its ontology.

## Primary Data Anchor: QoG

The first validation anchor should be the Quality of Government data ecosystem.

Recommended initial sources:

- QoG Basic time-series dataset for a compact country-year panel
- QoG Standard time-series dataset for broader variable coverage
- QoG Expert Survey for bureaucratic design and behavior

Why this matters:

- the unit of analysis matches the first macro validation target: country-year
- governance quality is central to legitimacy, capacity, taxation, compliance, and peace
- QoG already harmonizes many source datasets that would otherwise need manual reconciliation

## Variable Mapping

The simulator should distinguish between latent state and observed indicators.

Example latent state:

- state capacity
- bureaucratic quality
- legitimacy
- elite cohesion
- social trust
- class conflict
- external threat

Example observed proxies:

- QoG bureaucracy and impartiality measures
- tax revenue indicators
- regime and democracy indicators
- public goods outcomes
- conflict event labels

The model should never assume that an observed variable is the same thing as the latent construct.

AidData is especially important here because it contributes project-level and geospatial evidence that does not fit neatly into a pure country-year panel. That makes it useful both for validation and for testing how external finance and infrastructure exposure propagate into domestic political and social dynamics.

## Backtesting Design

Use a layered validation procedure.

### Layer 1: Descriptive fit

Can the simulator reproduce broad historical trajectories and cross-country ordering?

### Layer 2: Turning points

Can it capture meaningful breaks such as legitimacy collapse, democratization, fiscal recovery, or conflict onset?

### Layer 3: Mechanism discrimination

Can competing theoretical modules be distinguished by their fit to history?

## Suggested Evaluation Protocol

1. choose a small target panel of countries and years
2. calibrate on an initial historical window
3. run hindcasts into a held-out period
4. compare against:
   - persistence baseline
   - linear panel baseline
   - simple machine-learning baseline
5. inspect failure cases manually
6. revise mechanisms before adding complexity

## Forecasting Protocol

Forecasts should be generated only in the following form:

- conditional on a clear scenario
- with uncertainty bounds
- with a record of backtest performance on related outcomes

Acceptable examples:

- conditional conflict-risk forecasts under alternative food-price shocks
- conditional flourishing forecasts under different state-capacity reforms

Unacceptable examples:

- point predictions with no uncertainty
- broad civilizational forecasts with no historical validation record

## Explanation Protocol

Every forecast or hindcast should be accompanied by a mechanism report.

The report should answer:

- which state variables moved most
- which institutional and psychological channels mattered
- whether biology-sensitive assumptions changed the result
- which counterfactual changes would have altered the trajectory

## Engineering Requirements

The data pipeline should support:

- versioned dataset snapshots
- reproducible download and transformation scripts
- country-code reconciliation
- missing-data rules
- train, validation, and test splits by time
- experiment tracking for parameter sets and scores

## First Build Target

A strong first empirical milestone is:

simulate a limited set of countries from 1990 onward, map latent governance and state-capacity variables to QoG and companion indicators, and test whether the simulator can hindcast changes in institutional quality, internal instability, and conflict risk better than simple baselines.
