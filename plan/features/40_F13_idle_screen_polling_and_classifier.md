# Phase F13-S1: Idle Screen Polling And Classifier

## Goal

Implement the concrete idle classifier for active sessions using bounded screen-state polling.

## Scope

- Database: persist idle-detection and nudge-related events with timestamps and classifier reasons.
- CLI: expose enough state for operators to understand why a session was treated as idle.
- Daemon: poll screen/alt-screen state, compare snapshots over time, and classify sessions as active, quiet, or idle.
- YAML: runtime policy may define poll interval, comparison windows, and nudge thresholds.
- Prompts: idle nudgers must restate the current stage and next required CLI actions accurately.
- Tests: exhaustively cover unchanged-screen detection, false-positive resistance, polling gaps, and escalation thresholds.
- Performance: benchmark polling cost and classifier overhead under many concurrent sessions.
- Notes: update idle/nudge notes when the classifier is frozen.
