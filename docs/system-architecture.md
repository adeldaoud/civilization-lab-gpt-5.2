# System Architecture

## Design Principles

1. Separate scientific simulation from rendering.
2. Keep agent policies interchangeable behind one interface.
3. Model society at multiple scales instead of only at the individual level.
4. Use real-world geography and data where possible.
5. Preserve replayability, interpretability, and experiment control.
6. Require successful backtesting before trusting forecasts.
7. Treat forecasting as a downstream use case, not the first milestone.
8. Do not let any single dataset define the simulator ontology.

## Recommended Architecture

### 1. Headless simulation core

The core engine should run without any graphics and own the authoritative world state.

Suggested responsibilities:

- time stepping
- event scheduling
- state transitions
- resource accounting
- diplomacy and conflict resolution
- logging and replay export
- policy execution budgets

### 2. Pluggable decision engines

Every agent should implement the same abstract loop:

- `observe(state_slice)`
- `update_internal_state()`
- `propose_actions()`
- `select_action()`
- `learn_or_reflect()`

Supported backends:

- `RulePolicy`: explicit rules, utilities, thresholds, institutional constraints
- `RLPolicy`: trained policy networks for bounded decision problems
- `LLMPolicy`: language-model reasoning over structured summaries and tools
- `HybridPolicy`: scripted action constraints with learned or LLM choice inside the action set

This is the key design choice that allows the simulator to compare agent paradigms fairly.

### 3. Visualization client

The visual client should subscribe to state snapshots and event streams rather than own game logic.

Initial visual targets:

- world map and terrain layers
- civilization overview dashboards
- diplomacy view
- conflict escalation timeline
- class tension and trust heatmaps
- replay mode for major historical paths

### 4. Empirical data and validation layer

The simulator needs a dedicated empirical layer rather than ad hoc data loading.

Suggested responsibilities:

- ingest country-year and subnational datasets
- harmonize country codes, year coverage, and missingness rules
- define mappings from observed variables to latent simulator state
- calibrate uncertain parameters against historical trajectories
- run hindcasts and rolling-origin backtests
- score explanatory and predictive performance

The main initial target should be country-year validation against QoG-centered panels, combined with project-level and geospatial evidence from sources such as AidData, then expanded to conflict, trade, climate, and survey datasets.

## World Model

### Geography

The world should be Earth-based, not a fantasy map.

Recommended representation:

- global hex or hierarchical cell grid using a geospatial index such as `H3` or `S2`
- base layers for elevation, climate, coastlines, rivers, arable land, minerals, energy, and disease ecology
- transport graph for sea lanes, rivers, roads, and chokepoints

### Political units

The world state should distinguish:

- cells
- regions
- countries
- alliances
- empires or federations

Countries should have:

- territory
- resource endowments
- infrastructure
- institutions
- legitimacy
- military capacity
- trade dependence
- demographic composition
- links to observed historical indicators for calibration and validation

## Social Model

Each civilization should include at least three levels of agency.

### Leadership layer

- leader
- cabinet or ministries
- military command
- central bank or treasury if applicable

### Institutional layer

- executive institutions
- legislature or elite bargaining bodies
- bureaucracy
- courts
- religious institutions
- media and information networks

### Population layer

Do not start by simulating every individual human.
Represent the population as households or cohorts first.

Suggested cohort dimensions:

- class
- occupation
- ethnicity
- religion
- ideology
- education
- age structure
- urban or rural status
- regional identity

## Biology, Psychology, Sociology Modules

This simulator should allow explicit modules for causal assumptions about human behavior.

### Biology module

Represents relatively slow-changing traits and constraints, for example:

- baseline aggression propensity
- stress reactivity
- reproductive pressure
- health burden
- sleep, hunger, and fatigue effects

### Psychology module

Represents cognition and affect at the agent or cohort level:

- trust
- fear
- status motivation
- reciprocity
- loss aversion
- identity salience
- trauma and memory

### Sociology module

Represents institutions and emergent social structure:

- norm enforcement
- inequality
- legitimacy
- polarization
- collective efficacy
- propaganda exposure
- organizational capacity

Each module should write to a shared latent state so the simulator can test alternative theories cleanly.

## Simulation Loop

Recommended cadence:

1. update environment and resource stocks
2. update cohort needs, sentiments, and health
3. update institutions and government capacities
4. run agent decisions
5. resolve trade, taxation, migration, protest, repression, diplomacy, and conflict
6. log events and state deltas
7. emit snapshots for analytics and visualization

Use multiple time scales:

- daily or weekly for micro state changes
- monthly or quarterly for policy
- annual for demographic, institutional, and macro outcomes

Backtesting should happen primarily at the annual country-year level first, even if the internal simulator runs on finer time steps.

## Learning and AI Training

The simulator should produce structured trajectories suitable for model training.

Potential outputs:

- state-action-reward traces for RL
- event narratives for LLM finetuning
- counterfactual experiment corpora
- graph snapshots for world-model learning

Secondary long-term goal:

train a civilization analysis model on simulation traces plus historical data, but only after the simulator is stable and calibrated.

## Calibration and validation workflow

Recommended order:

1. define a latent state that is theoretically meaningful
2. map observed QoG and companion variables into that latent state
3. calibrate parameters on an early historical window
4. run hindcasts on held-out years and countries
5. inspect failures before adding more model complexity

Do not optimize only for one-step prediction.
The system should also explain pathway dynamics, such as why trust, legitimacy, fiscal capacity, and conflict risk changed together.

## Initial Technical Boundaries

Version 1 should not attempt all of the following at once:

- photorealistic globe rendering
- fully open-ended free-text action spaces
- millions of individual agents
- real-time multiplayer human participation

Start with a bounded but expressive simulator and expand after the first validation loop.
