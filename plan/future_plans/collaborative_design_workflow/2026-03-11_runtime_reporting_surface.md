# Runtime Reporting Surface

## Purpose

Describe how the future daemon, CLI, and browser UI should present collaborative-design state to operators.

This is a working note.

## Main Recommendation

The reporting surface should optimize for answering:

1. what state is this design task in
2. what is blocking progress
3. what artifacts exist
4. what action is expected from me

## Minimum Reporting Fields

The operator should be able to see:

- workflow profile
- review state
- round number
- active scenario
- effective runtime mode
- progress gate
- verification gate
- completion gate
- pending operator action
- latest artifacts
- latest verification failures

## CLI Presentation

The CLI should probably favor:

- a concise summary view
- a fuller detail view
- artifact listings
- explicit next-step wording

Example summary concept:

- `State: awaiting_final_approval`
- `Pending action: approve | request revision | stop | escalate`
- `Verification gate: required_fields_render_check failed`

## Browser UI Presentation

The future browser UI should probably show:

- a status banner
- a current-round artifact panel
- a verification panel
- an action panel
- a requirement summary panel

The operator should not need to switch screens just to understand what is missing.

## Daemon Response Behavior

Daemon responses should be structured enough that:

- CLI can render text views
- browser UI can render richer cards and panels
- automation can react to explicit machine-readable fields

## Recommended Next Step

The next useful note would be a failure-and-recovery matrix for startup failures, scenario-entry failures, artifact-capture failures, and review-loop interruption.
