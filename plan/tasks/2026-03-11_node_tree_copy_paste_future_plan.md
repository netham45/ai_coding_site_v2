# Task: Capture Node-Tree Copy/Paste Future Plan

## Goal

Capture a future-plan bundle for copying or exporting a full node subtree and later importing or pasting it into a selected project as a stopped, freshly snapshotted top-level execution tree that reuses the original prompts and predefined child structure instead of regenerating children.

## Rationale

- Rationale: The repository is already moving toward richer workflow-profile, manual-tree, and browser-operator surfaces, and this idea is a natural later-stage extension that would let operators reuse and share proven orchestration structures without rerunning decomposition every time.
- Reason for existence: This task exists to preserve the user's idea in a repository-local future-plan bundle, position it explicitly after the workflow-overhaul and web-UI planning tracks, and spell out the copy, export, import, paste, snapshot, startup, skipped-generation, recursive execution, and sharing semantics clearly enough that the idea can be reviewed later without being rediscovered from memory.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: copy/paste would need to remain daemon-owned and durably inspectable rather than becoming an ad hoc filesystem shortcut.
- `plan/features/20_F15_child_node_spawning.md`: the pasted tree depends on child materialization and child startup semantics, but would intentionally bypass child generation for copied parents.
- `plan/features/21_F16_manual_tree_construction.md`: the feature sits at the boundary between manually supplied structure and layout-generated structure.
- `plan/features/37_F10_top_level_workflow_creation_commands.md`: paste would behave like a specialized top-level creation flow with a selected project, a fresh base snapshot, and a stopped initial parent.
- `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md`: recursive restart of copied descendants depends on clear readiness, dependency, and auto-start behavior.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/README.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
- `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/planning/implementation/manual_tree_construction_decisions.md`
- `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

## Scope

- Database: not applicable for implementation; this task does not change durable schema, though the future notes discuss copied-tree provenance, template identity, and paste-run snapshot records that a real implementation would likely need.
- CLI: not applicable for implementation; this task does not add copy/export/import/paste commands now, though the future notes describe likely operator-facing surfaces for local reuse and artifact sharing.
- Daemon: not applicable for implementation; this task does not change live runtime behavior, though the future notes describe a daemon-owned export/import/paste flow that creates a stopped parent and recursively starts descendants later.
- YAML: not applicable for implementation; this task does not change YAML assets, though the future notes discuss how pasted parents would be treated as having predefined children instead of generating them from layouts.
- Prompts: not applicable for implementation; this task does not change active prompt packs, though the future notes describe reusing the original prompts of copied nodes during replay.
- Tests: run the authoritative document tests needed for the new task plan and development log surfaces.
- Performance: negligible for this task; documentation-only planning work, with future-note discussion of export payload size, import validation cost, paste latency, and large-tree replay costs.
- Notes: add a non-authoritative future-plan bundle under `plan/future_plans/` that preserves the original idea, describes the end-to-end copy/export/import/paste/replay model, places the idea after the workflow-overhaul and web-UI planning tracks, and records the main open questions and invariants.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- `plan/future_plans/node_tree_copy_paste/` exists as a non-authoritative working-note bundle.
- The bundle preserves the original starting idea in its own note.
- The bundle explains that copy should span from the selected top-level node down through all descendants to the bottom-level subtasks.
- The bundle explains that copied trees should also be exportable so they can be passed around and shared.
- The bundle explains that paste may consume either a locally copied tree or an imported exported-tree artifact.
- The bundle explains that paste should target a selected project and create a fresh base-repo snapshot at the pasted epic level.
- The bundle explains that the pasted tree should begin stopped rather than immediately running.
- The bundle explains that parent nodes should reuse their original prompts and start their already-defined children recursively.
- The bundle explains that the child-generation stage is the part being skipped for copied parents, because the pasted parents already carry predefined children.
- The bundle explains that copied or imported nodes may need an explicit state meaning predefined children exist but descendant git environments are not built yet while dependencies are still incomplete.
- The bundle records the main invariants, risks, and open questions around provenance, exportability, prompt reuse, child authority, and replay behavior.
- The bundle states explicitly that the idea should be considered after the workflow-overhaul and frontend/web-UI planning work rather than as a current implementation commitment.
- `plan/future_plans/README.md` lists the new bundle.
- The governing task plan and development log exist and cite each other.
- The documented verification command passes.
