# Provider Identity And Recovery Questions

## Why This Note Exists

The main planning risk is assuming that Codex, Gemini, and Claude all expose session recovery in the same way.

That is unlikely.

This note captures the discovery checklist that should be answered before implementation planning turns into active feature work.

## Current Confirmed Gap

The repo already uses provider-oriented terms such as `provider` and `provider_session_id`, but current runtime behavior does not yet populate a true provider-owned session identifier.

Today that means:

- provider-aware recovery surfaces can exist
- but they cannot yet deliver true direct provider resume semantics

## Provider Discovery Checklist

For each candidate provider CLI, answer all of the following:

1. How is a new session started non-interactively?
2. Is there a machine-readable status command?
3. Can a stable provider session id be captured immediately after startup?
4. Can a specific existing session be resumed by id?
5. If not by id, is there at least a reliable cwd-scoped or transcript-scoped resume model?
6. What trust, consent, login, or setup prompts can appear before the actual task prompt runs?
7. Can those prompts be detected and handled safely inside tmux automation?
8. Is there a supported way to inspect whether the provider session still exists?
9. What failure modes are expected when the provider session is gone but tmux still exists?
10. What artifacts on disk, if any, influence restore semantics?

## Codex-Specific Discovery Target

The user-proposed direction is:

- after startup, run `/status`
- capture the session UUID
- store it durably
- resume by explicit session id later

Before any implementation plan should claim that path, verify:

- whether `/status` is stable enough to parse
- whether the UUID is always present
- whether explicit session-id resume is supported in the current Codex CLI
- whether the contract is safe under tmux detachment and daemon restarts

## Gemini And Claude Unknowns

At the time of this planning note, the repo review did not establish equivalent session-tracking contracts for Gemini or Claude.

Those remain explicit research items.

The future implementation should not assume:

- identical command syntax
- identical identity semantics
- identical recovery capabilities

Possible outcomes to plan for:

- one provider supports explicit resume by id
- one supports only last-session or cwd-scoped restore
- one supports no durable session restore worth automating

The provider abstraction must tolerate that asymmetry.

## Recommended Planning Sequence

1. Confirm the real Codex session-id capture and explicit-resume story.
2. Update the authoritative runtime notes once the exact Codex contract is known.
3. Define the provider capability model in code and notes.
4. Research Gemini and Claude against that capability model.
5. Only then open the implementation task plans and checklist entries for real runtime support.
