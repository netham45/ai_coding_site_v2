# Plan Directory

## Purpose

This directory contains implementation planning artifacts for this repository.

These plans are derived from the full `notes/` corpus, not from one note in isolation.
At the time this plan set was started, the repository contained 82 Markdown files under `notes/`.

Implementation assumptions for the current planning pass:

- PostgreSQL is the production database
- Python is the implementation language for the daemon and CLI
- FastAPI + Uvicorn is the default daemon/API stack
- SQLAlchemy + Alembic is the default DB/migration stack
- Pydantic is the default model/config stack
- pytest is the default testing framework
- bearer-token daemon auth is backed by a local magic-cookie file

Default execution posture for the current planning pass:

- FastAPI remains async at the request layer
- synchronous PostgreSQL access is acceptable if it is used deliberately and tested for concurrency and latency impact

The primary synthesis anchors for the first planning pass are:

- `notes/major_feature_inventory.md`
- `notes/spec_traceability_matrix.md`
- `notes/implementation_slicing_plan.md`
- `notes/code_vs_yaml_delineation.md`
- `notes/yaml_builtins_checklist.md`
- `notes/prompt_library_plan.md`
- `notes/default_yaml_library_plan.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/database_schema_spec_v2.md`
- `notes/cli_surface_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/git_rectification_spec_v2.md`
- `notes/review_testing_docs_yaml_plan.md`
- `notes/pseudocode/README.md`
- `notes/pseudocode/modules/*.md`

This plan set should be maintained as implementation progresses.

---

## Planning Rules

Every implementation phase must explicitly consider:

1. database
2. CLI
3. daemon
4. YAML
5. prompts
6. tests
7. performance
8. note updates

No feature is complete until:

- all affected system surfaces are implemented
- the relevant notes are updated for newly discovered limitations or elaborations
- exhaustive tests exist
- performance implications have been measured or guarded where appropriate

The code/YAML boundary for every phase must stay aligned with:

- `notes/code_vs_yaml_delineation.md`

Short version:

- YAML declares structure, policy, prompts, and workflow intent
- code enforces legality, safety, persistence, scheduling, recovery, and orchestration decisions

---

## Structure

- `setup/`
  - project/bootstrap phases
  - establishes PostgreSQL, Python project layout, daemon/CLI skeletons, YAML/prompt/test scaffolding
- `features/`
  - one implementation phase per tracked feature
  - every feature phase follows the five-system rule
  - additional support phases may exist when a tracked feature is too large to implement safely in one pass
  - command-family phases and schema-family phases should be split out whenever "CLI" or "YAML" is too coarse to drive implementation safely
  - database schema families and built-in YAML library families should also be split out whenever a single phase would hide test obligations or ownership boundaries
- `checklists/`
  - verification phases
  - closes inventory, workflow, CLI, database, YAML-library, and test-coverage gaps

## Order

1. complete the phases in `setup/`
2. implement the phases in `features/` in dependency order
3. run the verification phases in `checklists/`

The old single-file plan has been replaced by this directory structure so each phase can be tracked independently.
