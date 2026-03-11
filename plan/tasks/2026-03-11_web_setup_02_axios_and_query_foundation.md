# Task: Web Setup 02 Axios And Query Foundation

## Goal

Implement the third website setup phase by adding the central Axios client, the shared query/cache foundation, and the initial feature API-module skeleton the later route and feature phases will build on.

## Rationale

- Rationale: The Vite/React shell now exists, but the frontend still has no approved transport layer, no shared query/cache primitives, and no stable API-module ownership split.
- Reason for existence: This task exists to freeze the central data-access architecture early so later website features do not scatter raw HTTP calls, invent inconsistent cache keys, or bypass the daemon-client model.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/28_F23_testing_framework_integration.md`
- `plan/web/setup/02_axios_and_query_foundation.md`
- `plan/web/features/00_project_bootstrap_and_selection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_frontend_communication_and_data_access.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_phase_1_setup_and_scaffold.md`
- `notes/planning/implementation/frontend_website_vite_react_bootstrap_decisions.md`

## Scope

- Database: not applicable; this phase does not change durable product-state schema.
- CLI: not applicable; no Python CLI contract changes in this phase.
- Daemon: define the website-side daemon client shape and error normalization without changing daemon endpoints.
- Website: add the central Axios client, error normalization, shared TanStack Query foundation, query-key helpers, and the initial API-module skeleton.
- YAML: not applicable; no YAML behavior or schema changes in this phase.
- Prompts: not applicable; no prompt assets or prompt contracts change in this phase.
- Tests: prove the central client and query foundation work through bounded deterministic checks.
- Performance: keep the request foundation predictable and lightweight, with stable defaults rather than ad hoc fetch logic.
- Notes: document the API-module boundaries, query-key conventions, and bounded proof approach for the frontend communication layer.

## Planned Changes

1. Add Axios and TanStack Query dependencies to the frontend workspace.
2. Add a central Axios client and shared error-normalization module.
3. Add shared query-client and provider modules plus query-key helpers.
4. Add the initial feature API-module skeleton files.
5. Update the frontend app entrypoint to use the shared query provider.
6. Add a bounded proof script for the client and query foundation.
7. Document the resulting module and query-key conventions.

## Verification

Canonical verification commands for this task:

```bash
cd frontend && npm install
cd frontend && npm run test:unit
cd frontend && npm run build
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- A central Axios client exists in the frontend workspace.
- Shared frontend error normalization exists.
- Shared query/cache foundation exists.
- Initial feature API-module skeleton files exist.
- Stable query-key conventions are defined in code and documented in notes.
- The bounded proof demonstrates the client and query foundation work.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
