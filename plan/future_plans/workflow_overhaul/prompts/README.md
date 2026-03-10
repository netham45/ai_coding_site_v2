# Workflow Overhaul Prompt Drafts

This folder contains planning-stage prompt drafts for the workflow-overhaul direction.

These files are not active runtime prompt-pack assets.

They exist so the full four-tier workflow prompt contracts can be reviewed and iterated on before any implementation work begins in:

- `src/aicoding/resources/prompts/`
- YAML prompt-reference assets
- compiler or daemon prompt-selection logic

Current scope:

- `epic/`: top-level decomposition prompts
- `sub_epic/`: phase-like delivery-band decomposition prompts
- `plan/`: task-layout prompts for concrete execution plans
- `task/`: leaf-execution prompts for bounded work packets

These files should be treated as design inputs for future authoritative work, not as a source of truth for current runtime behavior.

## Draft Index

### Epic tier

- `epic/generic.md`
- `epic/global_brief.md`
- `epic/planning.md`
- `epic/feature.md`
- `epic/review.md`
- `epic/documentation.md`

### Sub-epic tier

- `sub_epic/generic.md`
- `sub_epic/global_brief.md`
- `sub_epic/discovery.md`
- `sub_epic/implementation.md`
- `sub_epic/documentation.md`
- `sub_epic/review.md`
- `sub_epic/remediation.md`
- `sub_epic/e2e.md`

### Plan tier

- `plan/generic.md`
- `plan/global_brief.md`
- `plan/authoring.md`
- `plan/execution.md`
- `plan/verification.md`

### Task tier

- `task/generic.md`
- `task/implementation.md`
- `task/review.md`
- `task/verification.md`
- `task/docs.md`
- `task/e2e.md`
- `task/remediation.md`
