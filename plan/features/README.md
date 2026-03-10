# Feature Phases

This folder contains one implementation phase per tracked feature.

Rules:

- every phase must include `Goal`, `Rationale`, and `Scope`
- every `Rationale` section must state both the architectural rationale and the reason the phase exists as a separate implementation slice
- every phase must include a `Related Features` section listing the other feature plans that should be read for context and interaction boundaries
- every phase must include a `Required Notes` section listing the note `.md` files that should be read before implementing or revising that phase
- every phase must address database, CLI, daemon, YAML, prompts, tests, performance, and notes
- tests are mandatory for completion
- exhaustive unit coverage is required for all meaningful branches and failure paths
- performance-sensitive paths must be measured
- split phases again whenever database schema families, built-in YAML families, or command families become too broad to verify safely

Use these phases in dependency order, not numeric order alone, when conflicts arise.
