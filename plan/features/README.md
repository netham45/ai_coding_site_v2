# Feature Phases

This folder contains one implementation phase per tracked feature.

Rules:

- every phase must address database, CLI, daemon, YAML, prompts, tests, performance, and notes
- tests are mandatory for completion
- exhaustive unit coverage is required for all meaningful branches and failure paths
- performance-sensitive paths must be measured
- split phases again whenever database schema families, built-in YAML families, or command families become too broad to verify safely

Use these phases in dependency order, not numeric order alone, when conflicts arise.
