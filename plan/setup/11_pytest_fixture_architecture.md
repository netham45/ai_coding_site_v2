# Phase S11: pytest Fixture Architecture

## Goal

Define the fixture and test-helper architecture that all later exhaustive tests will build on.

## Scope

- Database: define DB fixture layering for isolated schema/test data/session patterns.
- CLI: define CLI invocation fixtures and output/assertion helpers.
- Daemon: define daemon app/client fixtures, auth fixtures, and fake-or-real DB-backed request fixtures.
- YAML: define resource-loading and schema/compile fixture helpers.
- Prompts: define prompt-pack and render-context fixtures.
- Tests: test the test infrastructure itself, including isolation, determinism, and fixture misuse cases.
- Performance: benchmark fixture startup overhead to keep the test suite sustainable.
- Notes: update testing notes if fixture structure needs stronger rules.

## Exit Criteria

- later phases can add exhaustive tests without re-inventing infrastructure.
