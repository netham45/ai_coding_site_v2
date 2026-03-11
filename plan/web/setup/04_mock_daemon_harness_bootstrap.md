# Web Setup 04: Mock Daemon Harness Bootstrap

## Goal

Establish deterministic daemon-presented scenarios for browser testing.

## Scope

- Database: use deterministic seeded state where needed.
- CLI: not applicable.
- Daemon: define scenario-backed HTTP behavior for browser tests.
- YAML: not applicable.
- Prompts: not applicable.
- Tests: prove the harness can serve deterministic project/tree/action data.
- Performance: scenarios should be cheap to boot.
- Notes: document scenario families and harness expectations.

## Exit Criteria

- deterministic daemon scenario mode or equivalent exists for browser tests.
- at least one project and one tree scenario are proven.
- harness shape is documented.
