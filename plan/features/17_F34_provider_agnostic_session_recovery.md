# Phase F34: Provider-Agnostic Session Recovery

## Goal

Recover runs using durable state even when provider session identity is absent or unreliable.

## Scope

- Database: recovery-critical state and recovery event history.
- CLI: recovery-oriented inspect and resume flows.
- Daemon: recovery classification, replacement-session creation, and safe resume.
- YAML: configurable recovery policy only.
- Prompts: resume-existing and replacement-session prompts.
- Tests: exhaustive healthy, stale, lost-tmux, no-provider, and non-resumable recovery coverage.
- Performance: benchmark recovery-path latency.
- Notes: update recovery appendix if implementation reveals new recovery classes.
