# Application Decompilation Working Notes

This folder captures a future idea for taking an existing application and turning it into a structured reconstruction workflow.

This is a working-note bundle, not an implementation plan.

Nothing in this folder should be read as an implementation, verification, or completion claim for the current repository.

## Bundle Contents

- `2026-03-11_application_decompilation_overview.md`

## Working Intent

The main question in this bundle is:

How do we take an existing application, observe and decompose it well enough to:

- generate high-confidence unit, integration, and E2E test targets
- recover architecture and behavioral invariants with explicit confidence levels
- synthesize epics, phases, plans, and tasks for rebuilding the application
- use prompts as first-class decomposition assets rather than ad hoc notes
- optionally validate a reconstruction against the original application

This bundle is deliberately exploratory.

It assumes this idea would only make sense after the repository has much stronger support for:

- profile-aware workflow decomposition from `workflow_overhaul/`
- reusable project and lifecycle scaffolding from `project_skeleton_generator/`

The goal here is to preserve the shape of the idea without pretending it is implementation-ready.
