# Roadmap

## Phase 0: Planning and ontology

Deliverables:

- project charter
- system architecture
- variable ontology
- first scenario definitions
- empirical validation design centered on country-year backtesting

Exit criteria:

- agreement on unit of simulation
- agreement on flourishing metrics
- agreement on first vertical slice
- agreement on first QoG-based validation targets

## Phase 1: Minimal scientific core

Scope:

- Earth-based map abstraction
- a small set of countries
- leader, government, and cohort population agents
- resource flows, taxation, legitimacy, trust, and basic diplomacy
- country-year observation layer for historical calibration

Exit criteria:

- one scenario runs end to end
- rule-based agents work
- event logs support replay and analysis
- annual outputs can be aligned to observed country-year variables

## Phase 2: Social complexity

Scope:

- class structure
- religion and culture
- propaganda and information flows
- protests, repression, and institutional adaptation
- migration and urbanization

Exit criteria:

- simulator produces plausible internal political dynamics
- class and identity tensions are visible in outputs

## Phase 3: Conflict and peace lab

Scope:

- bargaining
- deterrence
- alliance formation
- sanctions
- arms races
- civil conflict and interstate war

Exit criteria:

- conflict pathways are inspectable
- peace mechanisms can be compared experimentally

## Phase 4: Learning agents

Scope:

- RL policies for bounded subproblems
- LLM policies for strategic reasoning under constraints
- hybrid agents with institutional action masks

Exit criteria:

- same scenario can run with multiple agent backends
- policy performance can be compared using common metrics

## Phase 5: Calibration and forecasting

Scope:

- historical data alignment
- parameter sweeps
- uncertainty estimates
- cautious scenario forecasting
- QoG-centered backtesting and hindcasting

Exit criteria:

- simulator reproduces selected stylized facts
- simulator beats simple baselines on at least one historical country-year target family
- forecasting claims are documented with uncertainty bounds

## Phase 6: Visual flagship

Scope:

- polished visualization client
- replay narratives
- researcher control panel
- publishable demo scenes

Exit criteria:

- non-technical audiences can inspect the simulator clearly
- visual layer helps analysis rather than hiding assumptions

## First 8 Weeks

Recommended sequence:

1. finalize ontology and metrics
2. define cell, region, country, institution, cohort, and event schemas
3. implement the minimal simulation clock and event log
4. add rule-based leader and government agents
5. add population cohorts and trust or legitimacy dynamics
6. wire in QoG-based country-year targets for the first validation loop
7. build the first map-based replay dashboard
8. run a two-country peace-versus-war experiment
