## Phase 50: Session Attach, Resume, And Control Commands

- The core session-control commands (`session show`, `session events`, `session attach`, `session resume`, and `session nudge`) were already implemented, so this slice focused on making the read-side control surfaces directly actionable.
- Primary-session reads now expose the daemon's `recommended_action` alongside `recovery_classification`. This lets operators and AI clients decide whether the correct next step is `session attach`, `session resume`, or replacement-oriented recovery without issuing a second control lookup.
- The recommendation is derived from the same provider-agnostic recovery classifier already used by `session resume` and `node recovery-status`; the session read path does not invent a separate decision model.
- Prompt assets for interrupted-session recovery were updated to instruct clients to inspect the current durable session row and follow the daemon-provided recommendation before choosing attach vs resume behavior.
- This slice deliberately did not add a standalone `session heartbeat` mutation. Session freshness still comes from bind/attach/resume, screen polling, and idle/nudge flows.
