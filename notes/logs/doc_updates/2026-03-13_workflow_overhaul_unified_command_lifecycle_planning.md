# Workflow Overhaul Unified Command Lifecycle Planning

## Entry 1

- Timestamp: 2026-03-13T00:00:00-06:00
- Task ID: 2026-03-13_workflow_overhaul_unified_command_lifecycle_planning
- Task title: Workflow overhaul unified command lifecycle planning
- Status: started
- Affected systems: notes, YAML planning context, daemon planning context, CLI planning context, prompts planning context, website UI planning context, development logs, document consistency tests
- Summary: Began turning the unified command lifecycle idea into a workflow-overhaul planning asset by inventorying all built-in subtask command kinds, adjacent action surfaces, and the draft-plan scaffolding needed for one-file-per-command planning.
- Plans and notes consulted:
  - `plan/tasks/2026-03-13_workflow_overhaul_unified_command_lifecycle_planning.md`
  - `AGENTS.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/yaml/yaml_schemas_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
- Commands and tests run:
  - `find src/aicoding/resources/yaml/builtin/system-yaml/tasks -maxdepth 1 -type f | sort`
  - `find src/aicoding/resources/yaml/builtin/system-yaml/subtasks -maxdepth 1 -type f | sort`
  - `sed -n '1,220p' src/aicoding/resources/yaml/builtin/system-yaml/tasks/execute_node.yaml`
  - `sed -n '1,220p' src/aicoding/resources/yaml/builtin/system-yaml/tasks/wait_for_children.yaml`
  - `sed -n '1,260p' src/aicoding/daemon/interventions.py`
  - `sed -n '1,260p' notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `sed -n '1,260p' notes/specs/yaml/yaml_schemas_spec_v2.md`
- Result: In progress. The repo already has a concrete built-in command library, but lifecycle semantics are spread across YAML, compile-time metadata, daemon mutation paths, and intervention surfaces.
- Next step: Add the unified-command-lifecycle future-plan note, add the draft feature slice plus one draft plan per built-in subtask command, update the draft indexes, rerun the document-family tests, and record the final result.

## Entry 2

- Timestamp: 2026-03-13T06:26:25-06:00
- Task ID: 2026-03-13_workflow_overhaul_unified_command_lifecycle_planning
- Task title: Workflow overhaul unified command lifecycle planning
- Status: complete
- Affected systems: notes, YAML planning context, daemon planning context, CLI planning context, prompts planning context, website UI planning context, development logs, document consistency tests
- Summary: Added the unified command lifecycle note family, created the draft feature slice for the contract change, and added one draft subfeature plan per built-in subtask command so the full command inventory is represented in the workflow-overhaul draft tree.
- Plans and notes consulted:
  - `plan/tasks/2026-03-13_workflow_overhaul_unified_command_lifecycle_planning.md`
  - `plan/future_plans/workflow_overhaul/2026-03-13_unified_command_lifecycle_contract.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/yaml/yaml_schemas_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
- Commands and tests run:
  - `find src/aicoding/resources/yaml/builtin/system-yaml/tasks -maxdepth 1 -type f | sort`
  - `find src/aicoding/resources/yaml/builtin/system-yaml/subtasks -maxdepth 1 -type f | sort`
  - `sed -n '1,220p' src/aicoding/resources/yaml/builtin/system-yaml/tasks/execute_node.yaml`
  - `sed -n '1,220p' src/aicoding/resources/yaml/builtin/system-yaml/tasks/wait_for_children.yaml`
  - `sed -n '1,260p' src/aicoding/daemon/interventions.py`
  - `sed -n '1,260p' notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `sed -n '1,260p' notes/specs/yaml/yaml_schemas_spec_v2.md`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result: Passed. The document surfaces now include the unified lifecycle direction, the new draft feature slice, the command subfeature index and README, and per-command plans for all built-in subtask command kinds. The document consistency tests passed for the updated state.
- Next step: Add the unified command lifecycle feature into the checklist and E2E traceability surfaces if it becomes an active implementation slice rather than planning-only scope.
