# Workflow Profile Subfeature Plan 04c: Version Persistence

## Parent Area

- `04 Startup Request And Profile Persistence`

## Parent Slice

- `draft_feature_plans/02_profile_aware_startup_and_creation.md`

## Goal

Persist the selected workflow profile durably on node versions.

## Implementation Subtasks

- add selected-profile storage to the durable node-version model
- expose persisted selected-profile data in reads even when compile fails
- define migration and backfill posture for existing nodes without profile selection data
