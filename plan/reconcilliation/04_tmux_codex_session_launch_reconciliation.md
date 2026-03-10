# Tmux Codex Session Launch Reconciliation

## Goal

Replace the current shell-only tmux launch path with a real Codex-backed session launch path.

The intended result is:

- fresh primary tmux sessions export the current-stage prompt to disk under `./prompt_logs/<project_name>/...`
- fresh primary tmux sessions launch Codex with an instruction equivalent to:
  - `codex --yolo "Please read the prompt from <cli command to run the tool to retrieve the prompt for the current stage> and run the prompt"`
- recovery from a dead expected tmux session uses:
  - `codex --yolo resume --last`
- the launch, prompt-log, and resume behavior are durably inspectable across database, CLI, daemon, tmux, and E2E surfaces

## Rationale

- Rationale: The current real tmux boundary is not actually end to end because `session_manager.py` still launches an interactive shell instead of Codex.
- Reason for existence: This phase exists to define the exact implementation path for moving from shell-backed tmux sessions to Codex-backed runtime execution without silently weakening recovery, inspectability, or prompt traceability.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/features/55_F03_rendering_and_compiled_payload_freeze_stage.md`
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`

## Scope

- Database: persist launch-command metadata, prompt-log path metadata, provider/resume metadata, and recovery events needed to explain tmux/Codex behavior.
- CLI: expose one canonical current-stage prompt retrieval command that Codex can be told to run verbatim, and support writing the same prompt to disk for session-bootstrap auditability.
- Daemon: build Codex launch plans for fresh sessions, build `resume --last` plans for dead-session recovery, and stop treating an interactive shell as the primary execution target.
- YAML: continue selecting prompts and stage payloads declaratively, while leaving launch-command construction and recovery decisions in code.
- Prompts: ensure the exact compiled prompt delivered by the CLI retrieval command is the same payload written under `./prompt_logs/<project_name>`.
- Notes: reconcile the runtime loop, session recovery, verification command, and E2E notes with the new launch model.
- Tests: add bounded, integration, and real E2E proof for prompt export, Codex launch, tmux creation, prompt-log persistence, and dead-session resume behavior.
- Performance: keep the bootstrap path operationally acceptable despite one prompt export and one disk write per launched or replaced session.

## Current State

The current implementation does not satisfy the requested end-to-end boundary:

- `src/aicoding/daemon/session_manager.py` builds fresh session launch commands with `default_interactive_shell_command()`
- that command is currently `/bin/bash -lc 'exec /bin/bash -li'` or the equivalent configured shell
- the real tmux E2E proof therefore starts a shell, not Codex
- no durable prompt-log path exists under `./prompt_logs/<project_name>`
- dead-session recovery is not yet reduced to the provider-specific `codex --yolo resume --last` rule

## Invariants

1. Fresh primary-session launch must target Codex, not an interactive shell.
2. The fresh-session bootstrap path must tell Codex to read the exact current-stage compiled prompt through the CLI surface, not by reassembling prompt text ad hoc in tmux startup code.
3. Every fresh primary-session launch must write the prompt to a durable file under `./prompt_logs/<project_name>/`.
4. The exported prompt file must correspond to the exact prompt returned by the CLI retrieval command for the node, node version, node run, compiled subtask, and launch attempt that caused the session launch.
5. The project-name segment in `./prompt_logs/<project_name>/` must be derived deterministically from the session working directory or another documented project identity source; it may not drift between launches for the same project.
6. Session launch metadata must remain durably inspectable, including the effective launch mode, launch command, working directory, tmux session name, and prompt-log path.
7. If the expected tmux session is dead and the recovery path chooses resume, the replacement launch command must be `codex --yolo resume --last`.
8. YAML remains responsible for prompt selection and compiled stage identity; code remains responsible for tmux launch construction, prompt export plumbing, and recovery decisions.

## Likely Implementation Surface

Primary files:

- `src/aicoding/daemon/session_manager.py`
- `src/aicoding/daemon/session_records.py`
- `src/aicoding/daemon/session_harness.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/app.py`

Likely supporting files:

- `src/aicoding/resources/prompts/packs/default/runtime/session_bootstrap.md`
- `src/aicoding/resources/prompts/packs/default/runtime/replacement_session_bootstrap.md`
- `tests/unit/test_session_manager.py`
- `tests/integration/test_session_cli_and_daemon.py`
- `tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`

Potential new helper surface:

- a small Python bootstrap helper under `src/aicoding/daemon/` or `src/aicoding/runtime/` that:
  - resolves the exact CLI command Codex should be instructed to run for the bound node
  - writes the prompt file under `./prompt_logs/<project_name>/...` as a separate audit artifact
  - executes the effective `codex --yolo "Please read the prompt from <cli command to run the tool to retrieve the prompt for the current stage> and run the prompt"` command

## Design Approach

Use a code-owned bootstrap helper rather than embedding the full CLI-command assembly and file-write logic directly into one shell-quoted tmux command string.

The fresh-session path should become:

1. daemon admits or reuses the active run
2. daemon builds a launch plan that targets the bootstrap helper instead of `default_interactive_shell_command()`
3. the bootstrap helper resolves the session working directory and project name
4. the bootstrap helper derives the exact CLI command Codex should run to retrieve the current-stage prompt for the bound node
5. the bootstrap helper writes the prompt file under `./prompt_logs/<project_name>/...` as an audit log of the prompt that same CLI command returns
6. the bootstrap helper executes:
   - `codex --yolo "Please read the prompt from <cli command to run the tool to retrieve the prompt for the current stage> and run the prompt"`
7. durable session state records the effective prompt-log path, CLI retrieval command, and Codex launch metadata

The dead-session resume path should become:

1. daemon detects that the expected tmux session is missing
2. recovery classification selects the Codex resume path rather than launching a fresh shell
3. the replacement session launch plan executes:
   - `codex --yolo resume --last`
4. durable session history records that the session was resumed through the provider-specific `resume --last` path

## Canonical CLI Contract

The plan should not rely on tmux startup code scraping API JSON manually.

Use one explicit CLI contract for current-stage prompt retrieval. The Codex instruction should reference that command directly, not the prompt-log path.

- keep `subtask prompt --node <node_id>` as the retrieval command Codex is instructed to run, while the bootstrap helper separately writes that command's output to disk
- or extend `subtask prompt --node <node_id>` with a `--write-file <path>` option while still keeping the retrieval command itself as the thing Codex is told to run

The implementation should prefer the option that:

- avoids shell-redirection fragility
- preserves the exact command contract the user specified for Codex
- writes exactly the prompt payload intended for the current stage
- is easy to assert in unit, integration, and E2E tests

## Prompt-Log Path Contract

The prompt-log directory should be rooted in the session working directory:

- `./prompt_logs/<project_name>/`

The stored file path should be deterministic and collision-safe, for example:

- `./prompt_logs/<project_name>/<logical_node_id>/<node_run_id>/<compiled_subtask_id>.md`

Minimum required metadata encoded either in path or durable records:

- project name
- logical node id
- node run id
- compiled subtask id
- prompt template identity or source lineage if needed for diagnosis

The plan does not require the exact final filename today, but it does require deterministic derivation and durable inspectability.

## Database And Audit Requirements

Durable records should make the launch path reconstructible.

At minimum the implementation should ensure that current session history can explain:

- whether the session was a fresh Codex launch or a `resume --last` recovery
- the effective tmux session name
- the effective working directory
- the effective launch command
- the exact CLI retrieval command referenced in the Codex instruction
- the prompt-log path used for fresh launch, if applicable
- the node, run, and compiled subtask identity associated with that launch

This can likely be satisfied by extending the existing `session_events` payload and, if needed, adding durable prompt-log metadata to existing prompt-history rows rather than inventing a parallel audit table immediately.

## Failure Handling Requirements

- if the CLI retrieval command cannot produce the current-stage prompt, the session launch must fail explicitly and durably rather than dropping into an empty shell
- if prompt-log file creation fails, the session launch must fail explicitly and durably
- if `codex` is unavailable on the host path, the bind or replacement operation must fail with an inspectable launch error
- if `codex --yolo resume --last` fails, the system must preserve enough durable recovery evidence for an operator to diagnose the failed resume path
- the runtime must not claim a successful session bind if the tmux session exists but the intended Codex bootstrap command never launched successfully

## Expected Test Layers

- unit proof for fresh-session launch-plan construction
- unit proof for dead-session resume-plan construction
- unit proof for prompt-log path derivation and project-name derivation
- integration proof for the CLI retrieval command and any `--write-file` support added to it
- integration proof that session bind records launch metadata durably
- real tmux E2E proof that the pane contains a Codex launch rather than `/bin/bash`
- real E2E proof that the prompt file exists under `./prompt_logs/<project_name>/`
- real E2E proof that the prompt file content matches the current-stage prompt surface
- real E2E proof that the Codex launch instruction references the CLI retrieval command rather than the prompt-log path
- real E2E proof that a dead tmux session results in a replacement launch using `codex --yolo resume --last`
- real E2E follow-on proof in `test_e2e_full_epic_tree_runtime_real.py` that live Codex launch is now the decomposition boundary instead of a shell placeholder

## Canonical Verification Commands

Document consistency checks after planning and note updates:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

Bounded and integration checks after implementation:

```bash
python3 -m pytest tests/unit/test_session_manager.py tests/integration/test_session_cli_and_daemon.py -q
```

Real tmux and full-tree E2E checks after implementation:

```bash
python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q
```

## Phases

### Phase 1: Reconcile the launch contract

- replace the shell-only launch-plan builder with a Codex-aware launch-plan builder
- define one explicit launch mode for fresh sessions and one explicit launch mode for dead-session resume
- stop treating `/bin/bash -lc 'exec /bin/bash -li'` as a passing runtime target for real E2E decomposition

Exit criteria:

- the code-owned launch-plan contract is explicit and no longer shell-default

### Phase 2: Add canonical prompt retrieval and logging

- keep one canonical CLI command for current-stage prompt retrieval and ensure the Codex launch instruction references that command directly
- add or extend file-writing support so the same prompt is also written to a specified file path
- ensure the command uses the authoritative current compiled subtask, not ad hoc recomposition
- keep the exported payload aligned with the existing `subtask prompt --node <node_id>` surface

Exit criteria:

- one canonical CLI path can retrieve the exact current-stage prompt for Codex and write the same prompt to disk deterministically

### Phase 3: Add the Codex bootstrap helper

- implement the helper that assembles the CLI retrieval command, writes prompt logs, and launches Codex for fresh sessions
- derive `project_name` deterministically from the working directory or another documented project identity
- record prompt-log metadata and CLI retrieval command metadata durably during launch

Exit criteria:

- a fresh tmux bind can create a prompt-log file and launch Codex with the intended CLI-based instruction

### Phase 4: Add the dead-session resume path

- detect when the expected tmux session is missing
- switch the replacement launch plan to `codex --yolo resume --last`
- record durable recovery metadata that distinguishes resume from fresh bootstrap

Exit criteria:

- replacement bind after a dead tmux session launches `codex --yolo resume --last`

### Phase 5: Reconcile tests and notes

- update bounded tests, integration tests, and real E2E tests
- update runtime/spec/recovery/verification notes to reflect Codex launch and resume accurately
- keep the full-tree E2E test failing only on the next real product gap after Codex launch is in place

Exit criteria:

- the docs, tests, and real runtime surface all describe the same Codex-backed behavior

## Risks

- quoting and shell-escaping become fragile if the implementation tries to inline everything into one tmux command instead of using a helper
- `resume --last` may depend on current working directory semantics, so the working-directory invariant must be controlled carefully
- prompt-log files can become stale or ambiguous if the file naming contract is not deterministic
- durable prompt-log and launch metadata can drift from actual launch behavior if tests verify only one system surface
- the real next blocker after Codex launch may shift from session bootstrap to prompt/result handoff or decomposition result capture

## Completion Criteria

This phase is complete only when:

1. fresh tmux session launch targets Codex rather than an interactive shell
2. fresh launch writes the current-stage prompt under `./prompt_logs/<project_name>/`
3. fresh launch instructs Codex to read the prompt from the CLI retrieval command rather than from the prompt-log path
4. dead-session recovery uses `codex --yolo resume --last`
5. launch and recovery metadata are durably inspectable
6. bounded, integration, and real E2E tests prove the new behavior honestly
7. the runtime and recovery notes no longer describe shell-only tmux launch as the intended model

## Initial Status

- status: `planned`
- implementation expectation: `moderate`
- primary current blocker: the live session manager still launches a shell instead of Codex
