# Research Framework

## Main Questions

The simulator should support three families of questions.

### Collective intelligence

- When do civilizations become more adaptive, coordinated, and knowledge-generating?
- How do institutions and class structure affect distributed problem-solving?

### Conflict and peace

- Which combinations of resource scarcity, identity threat, elite incentives, and state capacity produce war?
- Which mechanisms stabilize peace: deterrence, trade, legitimacy, norms, or institutional trust?

### Flourishing

- What does it mean for a civilization to flourish across material, social, psychological, and ecological dimensions?
- Which tradeoffs are acceptable, and for whom?

## Proposed Flourishing Index

Do not reduce flourishing to GDP.
Use a configurable multi-objective index with explicit weights.

Suggested dimensions:

- survival and public health
- nutrition and material security
- education and knowledge production
- institutional trust and legitimacy
- freedom and voice
- inequality and mobility
- social cohesion
- ecological sustainability
- innovation capacity
- cultural continuity and meaning
- peace and physical safety

The simulator should support both:

- a weighted scalar score for optimization
- a Pareto view to avoid hiding value conflicts

## Conflict Metrics

Track conflict as a progression, not only a binary war flag.

Suggested measures:

- grievance intensity
- threat perception
- elite fragmentation
- arms mobilization
- border incident frequency
- alliance commitment credibility
- protest and repression rates
- civil conflict onset
- interstate war onset
- war duration and casualty burden

## Biology-Psychology-Sociology Hypothesis Space

The simulator should let you encode explicit claims and test their macro consequences.

Examples:

- Higher biological stress reactivity may increase perceived threat and retaliatory behavior.
- Strong psychological self-regulation may dampen aggression under institutional stability.
- Weak institutions may amplify small interpersonal distrust into large-scale collective violence.
- Shared rituals and social trust may lower coordination costs and improve resilience.

These should be switchable modules rather than hidden assumptions.

## Validation Strategy

Use three validation layers.

### 1. Face validity

Experts should recognize the causal logic and emergent patterns as plausible.

### 2. Historical pattern validity

The simulator should reproduce stylized facts such as:

- state formation under geography and coercion constraints
- trade-driven growth with distributional conflict
- inequality-driven instability
- war risk under commitment problems and power transitions

### 3. Predictive usefulness

Only after calibration should the simulator be used for cautious forecasting exercises.

## Data Sources To Integrate Later

Likely data families:

- macroeconomic indicators
- demography and migration
- conflict events
- trade and sanctions
- regime type and institutional quality
- climate and land productivity
- health and education
- survey-based values and trust

Candidate sources to assess for licensing and fit:

- World Bank
- Maddison Project Database
- V-Dem
- Polity
- UCDP or ACLED
- FAOSTAT
- WorldPop

## Experimental Program

Recommended early experiments:

1. Two-country bargaining under asymmetric resources and domestic class pressure
2. State legitimacy collapse under food shock and propaganda
3. Trust formation and collapse across unequal regions
4. Cultural transmission and institution persistence across generations
5. Peace durability under trade interdependence versus military deterrence

