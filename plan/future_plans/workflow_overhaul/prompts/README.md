# Workflow Overhaul Prompt Drafts

This folder contains planning-stage prompt drafts for the workflow-overhaul direction.

These files are not active runtime prompt-pack assets.

They exist so the full four-tier workflow prompt contracts can be reviewed and iterated on before any implementation work begins in:

- `src/aicoding/resources/prompts/`
- YAML prompt-reference assets
- compiler or daemon prompt-selection logic

Current scope:

- `epic/`: tier base prompt, profile overlays, and epic briefing prompt
- `sub_epic/`: tier base prompt, profile overlays, and phase briefing prompt
- `plan/`: tier base prompt, profile overlays, and plan briefing prompt
- `task/`: tier base prompt and leaf profile overlays

The current prompt bundle is example-heavy at the epic tier because the self-hosted workflow-overhaul drafts mostly start there today.

That should not be read as a future restriction that only epic nodes may start at the top level.

The intended future runtime rule remains:

- top-ness is structural, not semantic
- any node kind may be created parentless when its hierarchy definition allows `allow_parentless: true`
- prompt selection should adapt to the chosen top-level kind rather than forcing every future workflow-profile narrative through an epic root
- every draft profile should be able to drive a top-level start for its own node kind when that kind is allowed to run parentless

These files should be treated as design inputs for future authoritative work, not as a source of truth for current runtime behavior.

All prompts in this folder should now be read together with:

- `../2026-03-12_prompt_contract.md`

The intended shared sections are:

- `Role`
- `Objective`
- `Lifecycle Position`
- `Inputs`
- `Allowed Actions`
- `Forbidden Actions`
- `Expected Result`
- `Completion Conditions`
- `Escalation Or Failure`
- `Response Contract`

The intended composition model is:

- put the full shared tier contract in `base.md`
- keep profile files as overlays that add or tighten profile-specific rules
- keep `global_brief.md` as the tier briefing contract where applicable

## Draft Index

### Epic tier

- `epic/base.md`
- `epic/global_brief.md`
- `epic/planning.md`
- `epic/feature.md`
- `epic/review.md`
- `epic/documentation.md`

### Sub-epic tier

- `sub_epic/base.md`
- `sub_epic/global_brief.md`
- `sub_epic/discovery.md`
- `sub_epic/implementation.md`
- `sub_epic/documentation.md`
- `sub_epic/review.md`
- `sub_epic/remediation.md`
- `sub_epic/e2e.md`

### Plan tier

- `plan/base.md`
- `plan/global_brief.md`
- `plan/authoring.md`
- `plan/execution.md`
- `plan/verification.md`

### Task tier

- `task/base.md`
- `task/implementation.md`
- `task/review.md`
- `task/verification.md`
- `task/docs.md`
- `task/e2e.md`
- `task/remediation.md`
