# Workflow Profile Subfeature Plan 04e: Failure And Recovery Posture

## Parent Area

- `04 Startup Request And Profile Persistence`

## Parent Slice

- `draft_feature_plans/02_profile_aware_startup_and_creation.md`

## Goal

Define how selected-profile state behaves across startup failure, retry, and replacement-version recovery.

## Implementation Subtasks

- preserve selected-profile state when compile or startup fails partway through
- define retry behavior when the same version is recompiled after failure
- define replacement-version behavior when an operator changes the selected profile intentionally
