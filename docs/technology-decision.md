# Technology Decision

## Decision Summary

Use a decoupled architecture:

- `Python` headless simulation core
- `Unity` visualization client for the first serious 3D interface
- optional `Unreal + Cesium` later for globe-scale cinematic geospatial rendering

Do not use `Minecraft` as the primary production environment for this project.

## Option Review

### Minecraft

Strengths:

- proven for open-ended many-agent experiments
- directly relevant because Project Sid used it
- low barrier for sandbox-style emergent behavior

Weaknesses:

- poor fit for realistic Earth geography
- weak fit for institutional, economic, and state-level modeling
- visual language is limiting for a serious social science simulator
- difficult to present nuanced geopolitical and class dynamics cleanly

Conclusion:

Useful as inspiration for emergence and agent autonomy, not as the main platform.

### Unity

Strengths:

- better balance of research speed and custom simulation tooling
- strong C# application layer plus easy integration with Python services
- mature support for custom visualizations, UI, and data-driven interfaces
- more practical than Unreal for a first integrated simulator client

Weaknesses:

- less visually powerful than Unreal for a globe-scale flagship experience
- large-scale agent rendering still requires disciplined performance engineering

Conclusion:

Best default choice for the first visual client.

### Unreal Engine

Strengths:

- strongest visual fidelity
- large-world support is attractive for planetary simulation
- `Cesium for Unreal` provides high-accuracy WGS84 globe support and streaming geospatial content

Weaknesses:

- heavier engineering burden for a research-first team
- slower iteration for experimentation, tooling, and ML workflows
- risk of spending too much effort on presentation before the science is stable

Conclusion:

Best reserved for a later showcase client or a second-phase geospatial front end.

## Recommended Build Order

### Phase 1

Build:

- Python core simulator
- notebook and dashboard analytics
- 2D or 2.5D map viewer

Goal:

validate ontology, mechanics, calibration, and experiment workflow

### Phase 2

Build:

- Unity client
- replay system
- diplomacy and society dashboards
- event visualization

Goal:

make the simulator legible and beautiful without coupling science to rendering

### Phase 3

Build only if needed:

- Unreal or Cesium front end
- real-globe geospatial streaming
- cinematic scenario presentation

Goal:

public-facing demonstration and advanced geospatial immersion

## Practical Engineering Stack

Suggested implementation split:

- `sim-core/`: Python simulation engine
- `policy-lab/`: agent backends and training code
- `data-pipeline/`: ingestion, feature engineering, calibration
- `viz-client/`: Unity project
- `api/`: snapshot and replay services

## Source Notes

Why these recommendations:

- Project Sid demonstrated that large-scale agent societies can emerge in `Minecraft`, but its main lessons for this project are architectural: concurrency, coherence, and social benchmarks.
- AI Economist is a stronger template for modular simulation design because it separates agents, governments, environment state, and learning.
- Cesium for Unreal is important specifically because your project wants geography that follows the planet closely.

