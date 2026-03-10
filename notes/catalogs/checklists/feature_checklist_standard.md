# Feature Checklist Standard

## Purpose

This note defines the canonical feature-checklist system for repository implementation and verification status.

The feature checklist layer exists so feature status is no longer inferred from scattered plans, notes, code, or tests.

## Canonical Artifacts

- Checklist directory guide: `notes/catalogs/checklists/README.md`
- Checklist standard: `notes/catalogs/checklists/feature_checklist_standard.md`
- Checklist backfill and current status surface: `notes/catalogs/checklists/feature_checklist_backfill.md`
- Architectural inventory only: `notes/catalogs/inventory/major_feature_inventory.md`
- E2E target mapping: `plan/e2e_tests/06_e2e_feature_matrix.md`

`major_feature_inventory.md` remains the architectural capability inventory.

It does not carry canonical implementation or verification status.

## Checklist Scope

Every meaningful feature or tightly related feature batch must have a checklist entry.

Every checklist entry must explicitly track:

- included feature plan paths
- affected systems
- database status
- CLI/API status
- daemon/runtime status
- YAML/schema status
- prompt status
- notes/documentation status
- bounded test status
- E2E target
- E2E status
- performance/resilience status where applicable
- known limitations
- overall status

Grouped checklist entries are allowed when the grouped features form one coherent family, but every included feature plan must be listed explicitly.

## Status Values

### Per-system and supporting-status values

Use only:

- `not_applicable`
- `planned`
- `in_progress`
- `implemented`
- `verified`
- `partial`
- `blocked`
- `deferred`

### Overall status values

Use only:

- `planned`
- `in_progress`
- `implemented`
- `partial`
- `verified`
- `flow_complete`
- `release_ready`
- `blocked`
- `deferred`

## Status Rules

- `not_applicable` must be written explicitly for unaffected systems.
- `bounded tests` and `E2E` must be tracked separately.
- `verified`, `flow_complete`, and `release_ready` are forbidden unless the documented canonical verification command for that claimed layer was actually run.
- Overall feature status must not exceed the weakest required affected-system status.
- A feature may be `implemented` while E2E status is still `planned`, `in_progress`, or `partial`.
- A feature may not be described as complete if real E2E proof for its intended scope is still missing.

## Backfill Method

Phase DU-01 backfills the current checklist layer from:

- `plan/features/*.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- the current `src/` and `tests/` tree

The initial backfill is intentionally conservative:

- `implemented` means the repository contains concrete code or assets for the feature family and at least bounded-proof coverage appears to exist.
- `partial` means code or assets exist, but the family still has visible runtime, proving, or scope gaps.
- `planned` means the target or contract is documented, but the backfill did not find enough evidence to claim implementation safely.
- `verified` is reserved for checklist claims whose canonical command has been run in the current state of the repo.

## Canonical Template

Use this shape for new entries:

```md
## FC-XX: Short Feature Family Name

- Included feature plans: `plan/features/...md`, `plan/features/...md`
- Affected systems: Database, CLI, Daemon, YAML, Prompts, Notes
- Status: Database `implemented`; CLI `implemented`; Daemon `implemented`; YAML `not_applicable`; Prompts `not_applicable`; Notes `implemented`; Bounded tests `implemented`; E2E target `tests/e2e/...`; E2E status `planned`; Performance/resilience `partial`; Overall `implemented`.
- Known limitations: Short, concrete statement of the current proving or scope gap.
```

## Canonical Verification Commands

Phase DU-01 verification command:

```bash
python3 -m pytest tests/unit/test_feature_checklist_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_notes_quickstart_docs.py
```

If future checklist work changes the file paths or enforcement tests, this command must be updated here and in any other authoritative place that claims the checklist layer is verified.
