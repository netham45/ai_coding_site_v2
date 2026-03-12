# Canonical Flow E2E Profiles

Each profile below is a proposed concrete child of the base `task.e2e` profile.

These should exist so every canonical runtime journey can be assigned as its own explicit E2E task.

## Flow 01

- Profile id: `task.e2e.flow_01_create_top_level_node`
- Source journey: `01_create_top_level_node_flow`
- Goal: Prove durable top-level node creation and first workflow compile through real CLI and daemon paths.
- Main evidence:
  - node creation result
  - compiled workflow inspection
  - durable lineage and prompt visibility
- Typical trigger: startup or top-level-kind policy changes

## Flow 02

- Profile id: `task.e2e.flow_02_compile_or_recompile_workflow`
- Source journey: `02_compile_or_recompile_workflow_flow`
- Goal: Prove immutable compile output, recompile behavior, and compile diagnostics through the real compile path.
- Main evidence:
  - compiled workflow chain
  - source lineage inspection
  - compile diagnostics or failure records where applicable
- Typical trigger: compiler, YAML, hook, or rendering changes

## Flow 03

- Profile id: `task.e2e.flow_03_materialize_and_schedule_children`
- Source journey: `03_materialize_and_schedule_children_flow`
- Goal: Prove layout-driven child materialization, dependency persistence, and scheduling-state inspection.
- Main evidence:
  - child nodes created durably
  - dependency and blocker visibility
  - idempotent materialization posture
- Typical trigger: materialization, layout, or scheduling changes

## Flow 04

- Profile id: `task.e2e.flow_04_manual_tree_edit_and_reconcile`
- Source journey: `04_manual_tree_edit_and_reconcile_flow`
- Goal: Prove manual tree edits and reconciliation decisions through real operator surfaces.
- Main evidence:
  - manual child creation or reconciliation decision records
  - authority-mode inspection
  - preserved manual structure after reconciliation
- Typical trigger: manual-tree or hybrid-authority changes

## Flow 05

- Profile id: `task.e2e.flow_05_admit_and_execute_node_run`
- Source journey: `05_admit_and_execute_node_run_flow`
- Goal: Prove run admission, primary session binding, and durable subtask progression.
- Main evidence:
  - node-run admission result
  - current subtask state and attempt history
  - summary registration and workflow advancement
- Typical trigger: run-control or session-binding changes

## Flow 06

- Profile id: `task.e2e.flow_06_inspect_state_and_blockers`
- Source journey: `06_inspect_state_and_blockers_flow`
- Goal: Prove the inspect surfaces for tree state, blockers, workflow position, and source context.
- Main evidence:
  - CLI or UI inspection payloads
  - blocker explanations
  - workflow and source identity consistency
- Typical trigger: operator inspection changes

## Flow 07

- Profile id: `task.e2e.flow_07_pause_resume_and_recover`
- Source journey: `07_pause_resume_and_recover_flow`
- Goal: Prove pause, recovery classification, resume, and restart-safe session continuity.
- Main evidence:
  - pause and resume history
  - recovery-state inspection
  - live session continuity across interruption
- Typical trigger: recovery or pause-state changes

## Flow 08

- Profile id: `task.e2e.flow_08_handle_failure_and_escalate`
- Source journey: `08_handle_failure_and_escalate_flow`
- Goal: Prove durable failure capture, escalation, and parent or operator decision routing.
- Main evidence:
  - failure classification
  - blocked or escalated state
  - parent decision or intervention history
- Typical trigger: failure taxonomy or escalation changes

## Flow 09

- Profile id: `task.e2e.flow_09_run_quality_gates`
- Source journey: `09_run_quality_gates_flow`
- Goal: Prove validation, review, testing, provenance, and docs gates through the real quality chain.
- Main evidence:
  - gate results persisted durably
  - finalization readiness reflects gate state honestly
  - docs and provenance artifacts exist when required
- Typical trigger: gate ordering or quality-library changes

## Flow 10

- Profile id: `task.e2e.flow_10_regenerate_and_rectify`
- Source journey: `10_regenerate_and_rectify_flow`
- Goal: Prove regenerate, rectify, and rebuild-history behavior through the real runtime path.
- Main evidence:
  - rebuild and rectification history
  - authoritative-version movement
  - inspectable cutover posture
- Typical trigger: rectify, cutover, or rebuild-policy changes

## Flow 11

- Profile id: `task.e2e.flow_11_finalize_and_merge`
- Source journey: `11_finalize_and_merge_flow`
- Goal: Prove merge, conflict handling, and finalize behavior through real git-backed runtime paths.
- Main evidence:
  - merge or conflict event history
  - finalize response and authoritative lineage state
  - operator-visible conflict decisions
- Typical trigger: merge or finalize pipeline changes

## Flow 12

- Profile id: `task.e2e.flow_12_query_provenance_and_docs`
- Source journey: `12_query_provenance_and_docs_flow`
- Goal: Prove operator read access to provenance, rationale, entity history, and docs.
- Main evidence:
  - provenance query results
  - documentation query surfaces
  - durable auditability of rationale relationships
- Typical trigger: provenance or docs-surface changes

## Flow 13

- Profile id: `task.e2e.flow_13_human_gate_and_intervention`
- Source journey: `13_human_gate_and_intervention_flow`
- Goal: Prove human approval or intervention steps through real bounded-authority runtime surfaces.
- Main evidence:
  - intervention history
  - approval decision persistence
  - blocked resume behavior before approval
- Typical trigger: human-gate or intervention-catalog changes
