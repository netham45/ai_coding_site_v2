# Resource And Test Scaffolding Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/05_resource_and_test_scaffolding.md`.

## Decisions

### Resource layout

- built-in packaged YAML scaffold now lives under `src/aicoding/resources/yaml/builtin/system-yaml`
- packaged default prompt-pack scaffold now lives under `src/aicoding/resources/prompts/packs/default`
- the older top-level prompt family directories remain as stable resource-group roots for loader compatibility during setup phases

### Test scaffolding

- reusable resource fixtures live in `tests/fixtures/resources.py`
- reusable placeholder compiler/runtime payload factories live in `tests/factories/resources.py`
- lightweight resource loading and benchmark helpers live in `tests/helpers/`

### Scope boundary

- scaffold files are placeholders only and intentionally do not claim full schema completeness
- this phase establishes loadable paths and test harnesses, not authored workflow content

