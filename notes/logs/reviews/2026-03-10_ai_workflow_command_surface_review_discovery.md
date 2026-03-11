# Development Log: AI Workflow Command Surface Review And Discovery

## Entry 1

- Timestamp: 2026-03-10
- Task ID: ai_workflow_command_surface_review_discovery
- Task title: AI workflow command surface review and discovery
- Status: started
- Affected systems: CLI, daemon, prompts, notes, development logs
- Summary: Started a dedicated review/discovery stage for the current AI-facing workflow command surface after the real full-tree `cat` E2E passed with visibly messy protocol behavior. The immediate purpose is to document the problem space before any remediation work begins.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/logs/e2e/2026-03-10_automated_full_tree_cat_runtime_e2e.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e.md`
  - `sed -n '1,220p' plan/tasks/README.md`
  - `sed -n '1,260p' plan/tasks/2026-03-10_workflow_overhaul_blocking_summary_callback_stage.md`
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- Result: The governing review/discovery task plan is now created. This batch is intentionally limited to planning, indexing, and logging; it does not start runtime or prompt-surface implementation fixes.
- Next step: execute the review/discovery phases from the new task plan, beginning with evidence extraction from the latest real tmux/Codex E2E transcript and current AI-facing command contracts.

## Entry 2

- Timestamp: 2026-03-10
- Task ID: ai_workflow_command_surface_review_discovery
- Task title: AI workflow command surface review and discovery
- Status: in_progress
- Affected systems: CLI, daemon, prompts, notes, development logs
- Summary: Executed Phase 1 evidence collection. Reviewed the passing but messy real full-tree `cat` tmux/Codex flow against the current prompt/runtime/CLI contract and wrote a dedicated evidence note that separates acceptable public reasoning from true workflow-protocol problems.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/logs/e2e/2026-03-10_automated_full_tree_cat_runtime_e2e.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,220p' plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `sed -n '1,220p' notes/logs/reviews/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `rg -n "workflow advance|summary register|subtask complete|review run|result-file|command_result" src/aicoding/resources/prompts src/aicoding/daemon src/aicoding/cli tests -g '!**/.venv/**'`
  - `sed -n '1,260p' notes/logs/e2e/2026-03-10_automated_full_tree_cat_runtime_e2e.md`
  - `sed -n '1,260p' notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `sed -n '1,260p' notes/specs/cli/cli_surface_spec_v2.md`
  - `sed -n '1,240p' notes/specs/prompts/prompt_library_plan.md`
  - `sed -n '1,220p' plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`
- Result: Phase 1 now has a durable evidence artifact. The note records that the main problem is not session chatter; it is the fragmented low-level command happy path, the repeated `workflow advance` races, the review-stage contract violation around `review run`, and the awkward terminal `404 active node run not found` completion surface.
- Next step: start Phase 2 inventory work by grouping the existing AI-facing command loop into low-level operator/debug primitives versus commands that are currently overexposed to AI sessions.

## Entry 3

- Timestamp: 2026-03-10
- Task ID: ai_workflow_command_surface_review_discovery
- Task title: AI workflow command surface review and discovery
- Status: in_progress
- Affected systems: CLI, daemon, prompts, notes, development logs
- Summary: Executed Phase 2 surface inventory. Reviewed the documented runtime loop and actual parser/handler surface, then grouped the current command set into AI-facing stage-loop commands, operator/debug reads, already-higher-level daemon-owned operations, and commands that appear overexposed to AI sessions.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `src/aicoding/cli/parser.py`
  - `src/aicoding/cli/handlers.py`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '220,420p' notes/specs/cli/cli_surface_spec_v2.md`
  - `sed -n '260,420p' notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `rg -n "add_parser\\(|set_defaults\\(|def handle_.*(subtask|summary|workflow|review|session|node register-layout)" src/aicoding/cli/parser.py src/aicoding/cli/handlers.py -S`
- Result: Phase 2 now has a durable inventory artifact. The main inventory conclusion is that the problem is not the total number of CLI commands; it is that the ordinary AI success path is built from too many low-level mutations, especially `summary register`, `subtask complete`, `workflow advance`, and then `subtask current` plus `subtask prompt`. The note also identifies `review run`, `workflow start`, `node quality-chain`, and `node register-layout` as existing examples of better daemon-owned command shape.
- Next step: begin Phase 3 ownership and error-policy review, focusing first on which current misuse cases should become hard daemon errors versus idempotent terminal success responses.

## Entry 4

- Timestamp: 2026-03-10
- Task ID: ai_workflow_command_surface_review_discovery
- Task title: AI workflow command surface review and discovery
- Status: in_progress
- Affected systems: CLI, daemon, prompts, notes, development logs
- Summary: Executed Phase 3 ownership and error-policy review. Read the actual daemon ownership paths for `workflow advance` and `review run`, then grouped the observed misuse cases into hard rejections, low-level-valid-but-poor AI happy-path operations, and idempotent/terminal-success candidates.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `src/aicoding/daemon/run_orchestration.py`
  - `src/aicoding/daemon/review_runtime.py`
  - `src/aicoding/daemon/app.py`
  - `src/aicoding/cli/daemon_client.py`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '560,760p' src/aicoding/cli/handlers.py`
  - `rg -n "def advance|workflow advance|review run|active node run not found|409|404|Conflict|HTTPException|raise .*not found|review.*route" src/aicoding/daemon src/aicoding/cli -S`
  - `sed -n '642,760p' src/aicoding/daemon/run_orchestration.py`
  - `sed -n '350,420p' src/aicoding/daemon/review_runtime.py`
  - `sed -n '1428,1555p' src/aicoding/daemon/app.py`
  - `sed -n '1,120p' src/aicoding/cli/daemon_client.py`
  - `sed -n '1515,1565p' src/aicoding/daemon/run_orchestration.py`
  - `sed -n '1530,1588p' src/aicoding/daemon/app.py`
- Result: Phase 3 now has a durable ownership/error-policy artifact. The central finding is that the daemon already has two different command shapes: `workflow advance` is a strict low-level cursor mutation, while `review run` is already a composite command that starts, completes, and advances the review stage. The current UX problem is therefore not lack of daemon capability; it is inconsistent use of composite command ownership across stage types.
- Next step: execute Phase 4 design recommendations based on the evidence and inventory already captured, without starting implementation.

## Entry 5

- Timestamp: 2026-03-10
- Task ID: ai_workflow_command_surface_review_discovery
- Task title: AI workflow command surface review and discovery
- Status: complete
- Affected systems: CLI, daemon, prompts, notes, development logs, task plans
- Summary: Completed Phase 4 and Phase 5 of the discovery task. Wrote the design recommendation note for a smaller composite AI-facing command surface and created the first two follow-on implementation task plans: one for composite stage-outcome command design and one for prompt migration plus protocol hardening.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase3_ownership_error_policy_note.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,220p' plan/tasks/README.md`
  - `sed -n '1,220p' plan/tasks/2026-03-10_workflow_overhaul_blocking_summary_callback_stage.md`
  - `sed -n '1,220p' plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
- Result: The review/discovery task now ends with explicit next-step implementation plans rather than a vague recommendation set. The main recommendation is to preserve low-level commands for operators and recovery while moving ordinary AI stage success onto composite daemon-owned commands that return next-stage or terminal outcomes directly.
- Next step: begin `plan/tasks/2026-03-10_ai_workflow_composite_stage_outcome_design.md` when the user is ready to move from discovery into design work.
