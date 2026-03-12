# Stage 03: Feature Delivery

## Purpose

Feature delivery is where the repository starts shipping real capability while keeping plans, logs, notes, checklists, and bounded proof aligned.

## Required Outcomes

- each meaningful feature has a governing plan
- each feature has a current checklist
- development logs record actual progress and proving
- affected systems are considered explicitly
- bounded tests exist for active changes

## Required Artifacts

- feature plans under `plan/features/`
- task plans under `plan/tasks/`
- feature checklists under `plan/checklists/`
- feature logs under `notes/logs/features/`

## Common Failure Modes

- implementing first and documenting later
- forgetting to update notes when implementation reveals new constraints
- claiming a feature is done because code exists
- using vague overall statuses that hide missing E2E proof

## Exit Condition

This stage is operating correctly when new features can be added repeatedly without contributors needing to invent process rules each time.
