# Workflow Profile Subfeature Plan 04d: Top-Level Legality Enforcement

## Parent Area

- `04 Startup Request And Profile Persistence`

## Parent Slice

- `draft_feature_plans/02_profile_aware_startup_and_creation.md`

## Goal

Reject illegal kind/profile combinations before top-level startup succeeds.

## Implementation Subtasks

- enforce parentless legality rules by node kind and selected profile
- reject unsupported profile selections with stable blocked/error responses
- make legality failures inspectable through operator read surfaces
