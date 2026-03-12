You are executing parent workflow node `daeb4ba3-da89-43d1-be12-3845e77b3f72`.
Current task key: `research_context`
Current subtask key: `research_context.hook.default_hooks.1`
Current subtask title: `1`
Current subtask type: `run_prompt`

Required CLI workflow:
1. Resolve the live compiled subtask UUID with `python3 -m aicoding.cli.main subtask current --node daeb4ba3-da89-43d1-be12-3845e77b3f72`.
2. Start the attempt with `python3 -m aicoding.cli.main subtask start --node daeb4ba3-da89-43d1-be12-3845e77b3f72 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID`.
3. Inspect the current context with `python3 -m aicoding.cli.main subtask context --node daeb4ba3-da89-43d1-be12-3845e77b3f72`.
4. Execute the current subtask instructions below.
5. On success:
   - write a concise summary to `summaries/parent_subtask.md`
   - record success and let the daemon route the workflow with `python3 -m aicoding.cli.main subtask succeed --node daeb4ba3-da89-43d1-be12-3845e77b3f72 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file $(pwd)/summaries/parent_subtask.md`
6. If blocked:
   - write the blocker summary to `summaries/parent_subtask_failure.md`
   - fail the current subtask with `python3 -m aicoding.cli.main subtask fail --node daeb4ba3-da89-43d1-be12-3845e77b3f72 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file $(pwd)/summaries/parent_subtask_failure.md`
7. After a successful completion, do not stop while the parent node still has pending workflow stages.
   - follow the routed daemon outcome instead of manually chaining low-level commands
   - if the routed outcome is `next_stage`, fetch the next prompt with `PYTHONPATH=/mnt/c/Users/Nathan/Documents/GitHub/ai_coding_site_v2/src:src python3 -m aicoding.cli.main subtask prompt --node daeb4ba3-da89-43d1-be12-3845e77b3f72` and continue in the same session
   - if the routed outcome is `completed`, stop and do not probe the closed run with additional low-level workflow commands

Current subtask instructions:
Template Path: prompts/runtime/session_bootstrap.md
Prompt Pack: default
Hook Id: default_hooks
Hook Trigger: before_node_run
Hook Source: hooks/default_hooks.yaml
Insertion Phase: before_task

You are the active session for node `daeb4ba3-da89-43d1-be12-3845e77b3f72`.

Startup steps:
- inspect `session show-current` and confirm the bound node, kind, and title
- read the current workflow binding
- confirm the active subtask `research_context.hook.default_hooks.1`
- inspect the provided stage context before acting

Execution rules:
- perform only the work required by the active subtask
- use CLI surfaces for progress, summaries, and failures
- preserve auditability and avoid unrelated edits

Node Title: Discovery And Framing
Node Kind: phase
Node Version: 1
Task Key: research_context
Hook Subtask Key: research_context.hook.default_hooks.1

Node Prompt:
Establish the implementation scope, risks, and delivery strategy.

Parent Epic Request:
create a text editor using ncurses for a TUI. It should be able to open files, it should have a menu that appears when esc is pressed to offer things like open/save/save as/new/close. it should support multiple windows. you need to follow the full tree. do an epic that plans out phases that plan out plans that run tasks. tasks should do the actual work. This is a test project to evaluate the orchestrator.

Child Acceptance Criteria:
- Scope is clarified.
- Risks and unknowns are captured.

Task Definition:
kind: task_definition
id: research_context
name: Research Context
description: Build the minimum context bundle needed before planning or implementation
  proceeds.
applies_to_kinds:
- epic
- phase
- plan
policy:
  max_subtask_retries: 2
  on_failure: pause_for_user
uses_reviews: []
uses_testing: []
uses_docs: []
subtasks:
- kind: subtask_definition
  id: build_context
  type: build_context
  title: Build Context Bundle
  description: Gather current requirements, repository context, and prior summaries.
  prompt: prompts/runtime/cli_bootstrap.md
  retry_policy:
    max_attempts: 2
    backoff_seconds: 5
  on_failure:
    action: pause_for_user
- kind: subtask_definition
  id: summarize_research_context
  type: write_summary
  title: Summarize Research Context
  description: Write a durable context summary for downstream stages.
  requires:
  - subtask_complete: build_context
  prompt: prompts/runtime/missing_required_output.md
  outputs:
  - type: summary_written
    path: summaries/research_context.md
  retry_policy:
    max_attempts: 2
    backoff_seconds: 5
  on_failure:
    action: pause_for_user
