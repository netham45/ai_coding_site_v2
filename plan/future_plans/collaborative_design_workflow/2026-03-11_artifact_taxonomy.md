# Artifact Taxonomy

## Purpose

Define the likely durable artifact kinds that collaborative-design work would produce so later notes can reference stable names.

This is a working note.

## Core Rule

If the design loop depends on an output for review, recovery, or audit, that output should have a stable artifact category.

## Candidate Artifact Kinds

### Review Input Artifacts

- `review_questionnaire`
- `review_answers`
- `requirement_capture`
- `requirement_confirmation`

### Draft And Revision Artifacts

- `design_draft_summary`
- `implementation_diff`
- `revision_summary`
- `effective_design_policy_summary`

### Preview Artifacts

- `screenshot_desktop`
- `screenshot_mobile`
- `interactive_preview_url`
- `target_url_snapshot`

### Debug Artifacts

- `browser_console`
- `network_failures`
- `playwright_trace`
- `startup_log`

### Verification Artifacts

- `design_verification_report`
- `accessibility_report`
- `responsive_render_report`
- `drift_detection_report`

### Decision Artifacts

- `approval_decision`
- `stop_with_known_gaps_decision`
- `escalation_decision`
- `override_record`

## Why This Matters

Without a stable artifact vocabulary:

- notes drift
- APIs drift
- CLI output drifts
- later implementation plans have to rename the same ideas repeatedly

## Recommended Next Step

If this bundle expands further, the next useful artifact is probably a lifecycle note mapping when each artifact kind must exist.
