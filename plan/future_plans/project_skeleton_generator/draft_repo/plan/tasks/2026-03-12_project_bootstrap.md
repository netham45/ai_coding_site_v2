# Task: Project Bootstrap

## Goal

Create the first governed repository scaffold with lifecycle notes, starter inventories, starter checklists, and a bounded verification surface.

## Scope

- Database: define the initial durable-state expectation and migration posture if a database is part of the product.
- CLI: define the initial operator command surface if a CLI is part of the product.
- Daemon or backend: define the runtime authority boundary and bootstrapping expectations.
- Website UI: define whether a browser surface exists now, later, or never.
- Config or YAML: define what belongs in declarative assets versus code.
- Prompts: define prompt asset expectations if AI participation is part of the system.
- Notes: create and align the initial architecture, lifecycle, inventory, and checklist surfaces.
- Tests: establish at least one bounded verification command and one document-consistency command.

## Canonical Verification

- `python3 -m pytest tests/unit/test_bootstrap_docs.py -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py -q`

## Exit Criteria

- The repo has lifecycle notes, a system inventory, a verification command catalog, and an operational-state checklist.
- The repo has a stack decision record that either captures the chosen stack or says explicitly that key choices are still open.
- The bootstrap log records what was actually done.
- The bounded bootstrap proof exists and passes.
- The repo still labels itself honestly as pre-E2E.
