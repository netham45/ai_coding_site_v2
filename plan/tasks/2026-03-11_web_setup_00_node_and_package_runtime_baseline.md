# Task: Web Setup 00 Node And Package Runtime Baseline

## Goal

Implement the first website setup phase by creating the minimal frontend workspace baseline, freezing the canonical frontend working directory and package-manager choice, and documenting the phase-00 command surface needed before Vite/React bootstrap begins.

## Rationale

- Rationale: The website doctrine and `plan/web` family now exist, but the repo still has no actual frontend workspace or canonical Node/package command surface.
- Reason for existence: This task exists to turn the first web setup plan from an abstract placeholder into a concrete baseline the later Vite/React, Axios/query, and Playwright phases can build on without re-litigating directory layout or package-management choices.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/28_F23_testing_framework_integration.md`
- `plan/web/setup/00_node_and_package_runtime_baseline.md`
- `plan/web/setup/01_vite_and_react_bootstrap.md`
- `plan/web/setup/03_playwright_bootstrap.md`
- `plan/web/verification/00_browser_harness_and_e2e_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`

## Scope

- Database: not applicable; phase 00 does not change durable product-state schema.
- CLI: not applicable; this phase does not change the Python CLI command surface.
- Daemon: document the expected future relationship between the frontend workspace and daemon-served or daemon-proxied hosting so later phases do not diverge from the daemon-authority model.
- Website: create the dedicated frontend workspace baseline, freeze the canonical working directory, choose the package manager, and add the initial package manifest and workspace README.
- YAML: not applicable; no YAML schema or declarative workflow assets change in this phase.
- Prompts: not applicable; no prompt assets or prompt-delivery contracts change in this phase.
- Tests: prove the local Node runtime is usable and that package installation succeeds in the chosen frontend workspace.
- Performance: not applicable for this baseline phase beyond avoiding unnecessary tooling churn.
- Notes: add a focused implementation note recording the phase-00 decisions and command surface so later web phases can cite one canonical baseline.

## Planned Changes

1. Create the canonical frontend working directory.
2. Add the minimal `package.json` needed to freeze package-manager and runtime expectations without prematurely bootstrapping Vite/React.
3. Add frontend workspace documentation covering the baseline commands and the intended relationship to later setup phases.
4. Update `.gitignore` so Node workspace artifacts do not pollute the repo.
5. Add a focused note capturing the frontend baseline decisions and command surface.
6. Record the work in a setup-family development log.

## Verification

Canonical verification commands for this task:

```bash
node -v
npm -v
cd frontend && npm install
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py
```

## Exit Criteria

- The repo contains a dedicated canonical frontend working directory.
- The frontend workspace has a minimal package manifest that freezes the package-manager/runtime baseline without yet claiming Vite/React bootstrap is complete.
- The canonical frontend command surface for this phase is documented in-repo.
- Node workspace artifacts such as `node_modules/` are ignored appropriately.
- A focused note records the baseline decisions for later web setup phases.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
