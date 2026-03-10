# Flow YAML Schema And Harness Decisions

## Purpose

Record the Phase 1 decisions for adding flow YAML assets under `flows/` without silently changing the authority model of the existing markdown flow documents.

## Decisions

1. The existing numbered markdown files in `flows/` remain the authoritative narrative flow contracts for now.
2. New `.yaml` files in `flows/` are allowed as executable simulation-derived flow assets.
3. Flow YAML assets use a repository-local strict schema instead of being folded into the runtime YAML schema families.
4. Flow YAML assets are documentation-and-test contracts, not daemon runtime input.
5. A flow YAML asset must include:
   - `id`
   - `name`
   - `purpose`
   - `simulation_sources`
   - `covers`
   - `entry_conditions`
   - `task_flow`
   - `required_subtasks`
   - `required_capabilities`
   - `expected_tests`
   - `known_limitations`
6. The YAML `id` must match the filename stem so traceability stays stable and test failures are obvious.

## Why this shape

- The runtime YAML schema layer is for orchestration configuration and policy, not planning artifacts.
- The flow YAML assets need strict validation, but they should not become part of the daemon compile surface.
- Keeping markdown authoritative avoids rewriting the existing flow set while still allowing executable missing-flow closure work.

## Follow-on work

- Add the missing simulation-derived flow YAML files under `flows/`.
- Add integration tests that bind each new YAML flow asset to a concrete pytest contract.
- Update `flows/README.md` and traceability notes as the YAML set grows.
