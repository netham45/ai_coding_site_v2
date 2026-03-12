# Workflow Profile Subfeature Plan 01a: Model Definition

## Parent Area

- `01 Schema Family Adoption`

## Parent Slice

- `draft_feature_plans/01_workflow_profile_yaml_family_and_structural_validation.md`

## Goal

Define the core `workflow_profile_definition` document model with a frozen top-level contract.

## Implementation Subtasks

- define the top-level required fields, identity fields, and ownership of nested sections
- define nested structures for completion restrictions, child-role requirements, and compiled-subtask template data
- freeze the first-pass Pydantic validation rules for required versus optional sections
