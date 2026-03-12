# Multi-Provider CLI Session Runtime Working Notes

This folder contains non-authoritative working notes for a future runtime direction where primary AI sessions can be launched and recovered through arbitrary CLI coding tools instead of only the current Codex-specific path.

This bundle is exploratory.

It does not make implementation, verification, or completion claims for the current repository.

## Bundle Contents

- `2026-03-12_original_starting_idea.md`
- `2026-03-12_overview.md`
- `2026-03-12_provider_identity_and_recovery_questions.md`

## Working Intent

The main questions in this bundle are:

- how the daemon should launch different provider CLIs without hard-coding Codex bootstrap behavior into the main session path
- how the system should discover and persist true provider-owned session identity for direct resume and attach flows
- how much of session recovery can stay provider-agnostic versus where provider-specific contracts are unavoidable
- what Gemini and Claude actually expose for resume, restore, status, and session inspection

This bundle starts from the current repo reality:

- fresh primary-session bootstrap is Codex-specific today
- recovery replacement still assumes the Codex `resume --last` path
- durable `provider_session_id` does not yet represent a true provider-owned session identifier

The goal is to preserve the design direction and the open research questions before implementation work begins.
