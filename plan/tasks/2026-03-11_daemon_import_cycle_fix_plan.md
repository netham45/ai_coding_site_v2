# Task: Fix The Daemon Import Cycle Exposed By The Source-Tree Runtime

## Goal

Capture the concrete implementation plan required to remove the circular import between `child_reconcile`, `git_conflicts`, and `incremental_parent_merge` that now blocks daemon startup once the environment imports the repo source tree correctly.

## Rationale

- Rationale: The packaged-resource fix exposed the next real startup blocker: the source tree currently has a daemon import cycle that was masked while runtime commands were loading a stale installed package copy.
- Reason for existence: This task exists to preserve the exact import chain, propose a coherent module-boundary fix, and prevent the repository from regressing into another fragile cross-module daemon import knot.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `src/aicoding/daemon/child_reconcile.py`
- `src/aicoding/daemon/git_conflicts.py`
- `src/aicoding/daemon/incremental_parent_merge.py`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: no schema change is expected.
- CLI: no CLI-surface change is expected, but CLI and daemon startup imports must succeed from the repo source tree.
- Daemon: break the circular import cleanly by moving the shared reconcile-context persistence helper to a lower-level module or equivalent neutral boundary.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: add or update startup/import tests so repo-local daemon imports fail fast if another cycle is introduced.
- Performance: negligible.
- Notes: document the discovered cycle and the chosen module-boundary fix in development logs; update notes only if the refactor changes any architectural boundary worth preserving.

## Verification

- Planned bounded verification:
  - `python3 -m pytest tests/integration/test_resource_loading.py tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q`
  - `timeout 8 python3 -m aicoding.daemon.main`

## Exit Criteria

- The circular import no longer blocks `python3 -m aicoding.daemon.main`.
- The shared reconcile-context persistence logic lives at a module boundary that does not require `git_conflicts` to import `child_reconcile`.
- The daemon-related bounded tests and repo-local startup smoke pass in the source-tree import path.
- The governing task plan is listed in `plan/tasks/README.md`.
- The development log records the diagnosis and resulting status honestly.

## Findings To Preserve

1. The current failing import chain is:
   - `aicoding.daemon.app`
   - `aicoding.daemon.admission`
   - `aicoding.daemon.run_orchestration`
   - `aicoding.daemon.incremental_parent_merge`
   - `aicoding.daemon.child_reconcile`
   - `aicoding.daemon.git_conflicts`
   - back to `aicoding.daemon.child_reconcile`
2. `child_reconcile.py` imports `MergeEventSnapshot`, `has_unresolved_merge_conflicts`, and `record_merge_event_in_session` from `git_conflicts.py`.
3. `git_conflicts.py` imports `persist_parent_reconcile_context_in_session` from `child_reconcile.py`.
4. `incremental_parent_merge.py` also imports `persist_parent_reconcile_context_in_session` from `child_reconcile.py`.
5. The most obvious shared dependency to extract is the reconcile-context persistence helper, which is infrastructure/state-write logic rather than child-reconcile business logic.

## Proposed Execution Stages

### Stage 1: Extract The Shared Helper

- Move `persist_parent_reconcile_context_in_session(...)` and its private persistence helper out of `child_reconcile.py` into a new lower-level daemon module such as:
  - `src/aicoding/daemon/reconcile_context.py`
  - or another neutral name that clearly describes durable run-cursor context persistence.
- Keep the extracted module free of imports from `git_conflicts.py`, `child_reconcile.py`, or `incremental_parent_merge.py`.

### Stage 2: Rewire Imports

- Update `git_conflicts.py` to import the extracted helper from the new neutral module.
- Update `incremental_parent_merge.py` to import the extracted helper from the new neutral module.
- Update `child_reconcile.py` to import or reference the helper from that same module if it still needs it.
- Re-check that no top-level import path recreates the cycle through a different module.

### Stage 3: Add Regression Coverage

- Add a small bounded import/startup test that imports `create_app` or launches a minimal daemon startup path from the repo source tree.
- Keep the regression at the lowest layer that clearly proves the module graph is acyclic.

### Stage 4: Rerun The Previously Blocked Runtime Proof

- Rerun the resource-loading and daemon/session integration slices that were blocked once the editable install started importing the repo source tree.
- Rerun `timeout 8 python3 -m aicoding.daemon.main` to prove startup no longer dies at import time.
