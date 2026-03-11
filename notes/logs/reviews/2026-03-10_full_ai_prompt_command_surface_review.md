# Development Log: Full AI Prompt Command Surface Review

## Entry 1

- Timestamp: 2026-03-10
- Task ID: full_ai_prompt_command_surface_review
- Task title: Full AI prompt command surface review
- Status: started
- Affected systems: CLI, daemon, YAML, prompts, notes, development logs
- Summary: Started a broader review of the full AI-facing command surface across all prompts and adjacent prompt-synthesis paths. This expands beyond the earlier transcript-driven workflow review so the repository can identify all weird prompt-taught command systems before any fixes begin.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_full_ai_prompt_command_surface_review.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase3_ownership_error_policy_note.md`
  - `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,220p' plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `sed -n '1,260p' notes/logs/reviews/2026-03-10_ai_workflow_command_surface_review_discovery.md`
  - `rg -n "python3 -m aicoding\\.cli\\.main|workflow advance|subtask complete|subtask fail|summary register|review run|testing run|node register-layout|materialize-children|session nudge|session recover|workflow start|subtask current|subtask prompt|subtask context|subtask start|subtask heartbeat|subtask retry|node quality-chain|node validate|node review|node test" src/aicoding/resources/prompts src/aicoding/daemon/workflows.py src/aicoding/daemon/run_orchestration.py -S`
- Result: The broader review is now formally opened under its own governing task plan and log. Initial inventory confirms that the earlier transcript issues are only one subset of the full prompt-taught command surface.
- Next step: execute Phase 1 by enumerating every authored prompt file and every prompt-synthesis path that teaches AI sessions CLI usage.

## Entry 2

- Timestamp: 2026-03-10
- Task ID: full_ai_prompt_command_surface_review
- Task title: Full AI prompt command surface review
- Status: in_progress
- Affected systems: CLI, daemon, prompts, notes, development logs
- Summary: Completed the first broad pass across the full prompt pack and adjacent prompt-synthesis sources. The review now identifies several weird AI command subsystems beyond the original transcript, including overlapping `runtime/*` and `recovery/*` prompt families, a separate workflow-rendered parent orchestration system, and a synthesized command-subtask reporting system in runtime code.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_full_ai_prompt_command_surface_review.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/cli/cli_surface_spec_v2.md`
  - `notes/specs/prompts/prompt_library_plan.md`
  - `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
  - `AGENTS.md`
- Commands and tests run:
  - `rg --files src/aicoding/resources/prompts/packs/default`
  - `rg -n "python3 -m aicoding\\.cli\\.main|workflow advance|subtask complete|subtask fail|summary register|review run|testing run|node register-layout|materialize-children|session nudge|session recover|workflow start|subtask current|subtask prompt|subtask context|subtask start|subtask heartbeat|subtask retry|node quality-chain|node validate|node review|node test" src/aicoding/resources/prompts src/aicoding/daemon/workflows.py src/aicoding/daemon/run_orchestration.py -S`
  - `sed -n '1,220p'` over the overlapping `runtime/*`, `recovery/*`, `pause/*`, `testing/*`, `quality/*`, `docs/*`, and bootstrap prompt files
- Result: The review note now captures the first comprehensive findings. The main new conclusion is that the repository does not just have one messy AI workflow. It has multiple partially overlapping prompt-taught command systems with different ownership assumptions and different degrees of explicit command guidance.
- Next step: continue the review with a command-by-command matrix and a sharper split between executional prompt families and analysis-only prompt families.
