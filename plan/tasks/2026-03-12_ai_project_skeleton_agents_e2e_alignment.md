# Task: Align Root And Skeleton AGENTS E2E Doctrine

## Goal

Update both the root `AGENTS.md` and `ai_project_skeleton/AGENTS.md` so they explicitly state that every feature requires full real E2E coverage, simulated workflows are never valid E2E, and the only acceptable response to a simulated E2E is to make it perform the real workflow.

## Rationale

- Rationale: The repository doctrine already rejected simulated E2E in general terms, but it did not yet state strongly enough that no feature is exempt from real E2E, that simulated workflow steps invalidate E2E outright, and that the required remediation is to fix the workflow rather than waive the E2E obligation.
- Reason for existence: This task exists to harden both the active repository doctrine and the starter skeleton doctrine around the same absolute real-E2E standard without reintroducing stack-specific assumptions into the skeleton.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`: the repository and the skeleton must preserve the same bounded-proof to real-E2E proving doctrine.
- `plan/features/33_F29_documentation_generation.md`: the root doctrine and starter documentation should stay aligned with the repository's current authoritative wording.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: doctrine changes should remain reconstructible through task plans and development logs.
- `plan/features/09_F35_project_policy_extensibility.md`: policy surfaces such as `AGENTS.md` must remain explicit and internally consistent.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `ai_project_skeleton/AGENTS.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/logs/doc_updates/2026-03-12_project_skeleton_cloneable_starter_repo_draft.md`

## Scope

- Database: not applicable for product implementation in this batch; this is a doctrine-alignment change, but both files must describe real persistence-involved E2E honestly where applicable.
- CLI: not applicable for product implementation in this batch; the change only updates how the doctrine describes proving CLI-involved workflows when a project has them.
- Daemon: not applicable for product implementation in this batch; the change only updates doctrine describing live runtime behavior and proof expectations.
- YAML: not applicable for product implementation in this batch; the change only updates configuration and proving doctrine wording.
- Prompts: not applicable for product implementation in this batch; prompts are mentioned only as part of cross-system and proving language.
- Tests: run the authoritative document-schema checks that cover changed task-plan and log surfaces, and verify the edit does not introduce wording drift in the root-governed docs.
- Performance: negligible; this is a documentation-only alignment change.
- Notes: update both `AGENTS.md` files and keep the planning and development-log artifacts current for the change.

## Verification

- `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- Both `AGENTS.md` files explicitly state that every feature requires real E2E, simulated workflow steps are never valid E2E, and defective E2E tests must be fixed rather than waived.
- The skeleton wording remains language-agnostic and framework-agnostic.
- The governing task plan and development log exist and record the actual verification command for this batch.
- The documented verification command passes.
