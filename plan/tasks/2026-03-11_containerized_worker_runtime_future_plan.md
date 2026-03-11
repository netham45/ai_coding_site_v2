# Task: Capture Containerized Worker Runtime Future Plan

## Goal

Capture an exploratory future-plan bundle for running worker execution inside per-run isolated containers, with YAML-provided build inputs, lifecycle-stage guidance for AI-authored runtime setup, and a grounded comparison between an OCI container approach and a lower-level systemd or namespace-managed approach.

## Rationale

- Rationale: The repository already treats isolated runtime environments as a deferred execution-policy feature, and the user's current idea is specific enough that it should be preserved as a structured future plan rather than remaining scattered across brainstorming notes.
- Reason for existence: This task exists to review the current notes around optional isolation, record the user's starting idea about AI-authored Dockerfiles and per-run containers, elaborate how that idea could fit the current orchestration model, and document a recommendation on whether the likely first implementation should use Docker-compatible OCI containers or a more manual systemd and namespace stack.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/36_F33_optional_isolated_runtime_environments.md`: this future-plan bundle is a follow-on expansion of the existing deferred isolation feature.
- `plan/features/13_F09_node_run_orchestration.md`: per-run container lifecycle would attach to node-run orchestration rather than creating a separate worker-authority model.
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`: isolated runtime setup, execution, and artifact capture would eventually need to integrate with the main execution chain.
- `plan/features/28_F23_testing_framework_integration.md`: the main motivation includes isolated test execution for ports, dependencies, and risky verification work.
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`: if runtime isolation becomes user-visible or AI-driven, the lifecycle must remain inspectable and automatable rather than hidden shell behavior.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/README.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_project_lifecycle_note_set.md`
- `plan/future_plans/project_skeleton_generator/lifecycle_note_examples/03_stage_02_setup.md`
- `plan/future_plans/project_skeleton_generator/lifecycle_note_examples/04_stage_03_feature_delivery.md`
- `notes/contracts/runtime/runtime_environment_policy_note.md`
- `notes/planning/implementation/optional_isolated_runtime_environments_decisions.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/explorations/original_concept.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: not applicable for implementation; this task does not change the current durable schema, though the future-plan notes discuss likely future image-spec, launch-record, and cleanup-audit persistence needs.
- CLI: not applicable for implementation; this task does not change the shipped CLI, though the future-plan notes discuss eventual operator and AI command surfaces for building, launching, inspecting, and cleaning up worker runtimes.
- Daemon: not applicable for implementation; this task does not change live runtime behavior, though the future-plan notes discuss how a future launcher should remain daemon-owned.
- YAML: not applicable for implementation; this task does not change the current YAML contract, though the future-plan notes discuss a future build-spec shape for Dockerfile or build-context declaration.
- Prompts: not applicable for implementation; this task does not change active prompts, though the future-plan notes discuss how lifecycle prompts might instruct AI workers to author and validate a Dockerfile before development work proceeds.
- Tests: run the authoritative document tests needed for the new task plan and development log surfaces.
- Performance: negligible for this task; documentation-only planning work, with future-note discussion of image-build caching, per-run container startup cost, and network-isolation overhead.
- Notes: add a non-authoritative future-plan bundle under `plan/future_plans/` that preserves the initial containerized-worker idea, expands it into a current-architecture review, compares Docker-compatible OCI launchers against systemd or namespace isolation, and explains how lifecycle-stage plans could incorporate AI-authored Dockerfiles without making premature implementation claims.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- `plan/future_plans/containerized_worker_runtime/` exists as a non-authoritative working-note bundle.
- The bundle preserves the user's starting idea separately from the grounded review notes.
- The bundle explains how per-run container execution fits the existing runtime-environment policy and deferred-isolation feature.
- The bundle states a clear recommendation on initial implementation direction, including why a Docker-compatible OCI runtime is likely the better first step than building a custom systemd and namespace stack.
- The bundle explains that a fresh container per run does not necessarily require a full image rebuild per run and proposes a build-spec caching model.
- The bundle describes a future YAML contract for build context, Dockerfile ownership, and runtime network posture at a high level without claiming it is already adopted.
- The bundle explains how lifecycle-stage plans could tell AI workers to create or maintain Dockerfiles and validate them as part of setup or feature-delivery work.
- `plan/future_plans/README.md` lists the new bundle.
- The governing task plan and development log exist and cite each other.
- The documented verification command passes.
