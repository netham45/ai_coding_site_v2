# Context Bundle

## Active runtime identity

- Node ID: `daeb4ba3-da89-43d1-be12-3845e77b3f72`
- Node title: `Discovery And Framing`
- Node kind: `phase`
- Run ID: `41e449f4-6ae8-4fe8-a8f9-b7564f2fba34`
- Compiled workflow ID: `eab22718-6ae7-4125-8722-9afbef5cbc69`
- Compiled subtask ID: `be30f895-e582-465d-bc7f-cda2796dcb78`
- Source subtask key: `research_context.build_context`
- Prompt log: `prompt_logs/ai_coding_site_v2/daeb4ba3-da89-43d1-be12-3845e77b3f72/41e449f4-6ae8-4fe8-a8f9-b7564f2fba34/38b5e1e1-d66e-4e6b-acd1-c647decdbf7d.md`

## Requested product scope

The parent epic request is to create an ncurses-based TUI text editor that:

- opens files
- shows an Escape-triggered menu with at least `open`, `save`, `save as`, `new`, and `close`
- supports multiple windows
- follows the full orchestration tree shape: epic -> phases -> plans -> tasks
- serves as an evaluation project for the orchestrator itself

The current phase is discovery only. Its acceptance criteria are:

- scope is clarified
- risks and unknowns are captured

## Repository context

- This repository is the orchestrator implementation, not an existing ncurses editor codebase.
- The current codebase centers on a Python CLI/daemon stack under `src/aicoding`, YAML-defined workflow assets, PostgreSQL-backed runtime state, prompt packs, and a React/Vite operator UI under `frontend/`.
- The built-in default epic decomposition already creates a phase named `Discovery And Framing`, followed by `Implementation`, which means this phase should frame the editor work and feed later planning rather than start editor implementation directly.
- `git status --short` shows a heavily dirty workspace with many unrelated tracked and untracked changes. Follow-on work must avoid reverting or broadening into those existing edits.

## Prior summaries and durable signals

- The current stage history contains only a bootstrap subtask summary for this phase run.
- `summaries/parent_subtask.md` had accumulated unrelated content from an earlier node run before being refreshed during this session, which indicates the current runtime summary artifact path is reused across nodes and can mislead downstream readers if not rewritten carefully.
- No existing `summaries/research_context.md` was present for this node before this pass.

## Delivery framing

- The current phase should produce a small, concrete framing output that later plan generation can use.
- A minimal downstream delivery strategy is likely:
  1. choose the editor implementation stack and runtime model
  2. define buffer/file/menu/window behavior precisely enough to decompose
  3. split later implementation into executable plan and task slices without duplicating discovery work
- The MVP implied by the request is a single-process ncurses editor with file I/O, an Escape menu, and multiple-window management. Advanced editor features such as search, syntax highlighting, undo history, or mouse support are not explicitly required yet.

## Open questions and risks

### Product and implementation risks

- The implementation language for the editor is not specified. `ncurses` suggests C or C++, while the repository stack is Python-focused; a Python `curses` implementation might satisfy intent but not the literal library choice.
- "Multiple windows" is ambiguous. It could mean split panes, multiple buffers, independent editor regions, or a window manager-style surface.
- File handling semantics are unspecified: encoding, unsaved-change prompts, large-file behavior, path browsing, and new-file lifecycle remain open.
- The Escape menu interaction is only partially specified. Navigation, dismissal behavior, keyboard bindings, and how menu actions map onto windows/buffers are still undefined.
- It is not yet clear whether the ncurses editor should live as a separate generated project/repo artifact or as code inside this orchestrator repository.

### Orchestrator/runtime risks discovered during this pass

- The startup prompt told the session to inspect `workflow binding`, but the current CLI exposes `workflow current` instead. That is a prompt/CLI contract mismatch.
- Shared summary artifact paths are being reused across different node runs, which can leak stale context into a later stage unless the file is replaced rather than appended.
- The phase is running in a workspace with substantial unrelated edits, so any implementation stage that assumes a clean worktree would be unsafe.

## Recommended next-step constraints for downstream planning

- Lock the editor implementation language and terminal-library choice before generating task-level implementation work.
- Define the exact meaning of multiple windows and the minimum menu interaction model before decomposing into executable plans.
- Keep the first implementation scope to an MVP editor core: file open/save, new/close, Escape menu, and deterministic window management.
- Treat the prompt/CLI command mismatch and reusable summary-file behavior as operational risks to avoid repeating in later runtime prompts and summaries.
