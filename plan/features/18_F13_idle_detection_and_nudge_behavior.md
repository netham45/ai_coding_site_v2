# Phase F13: Idle Detection And Nudge Behavior

## Goal

Detect idle sessions and nudge or escalate safely.

## Scope

- Database: nudge events and idle-related audit state.
- CLI: nudge and pause-state visibility.
- Daemon: tmux-backed idle detection, alt-screen/screen-state polling policy, bounded nudging, and escalation.
- YAML: heartbeat and idle policy declarations only.
- Prompts: idle-nudge and repeated missed-step guidance prompts.
- Tests: exhaustive threshold, false-positive, escalation, and idle-recovery coverage.
- Performance: benchmark heartbeat monitoring and polling overhead.
- Notes: update idle/tmux notes when concrete polling behavior is frozen.
