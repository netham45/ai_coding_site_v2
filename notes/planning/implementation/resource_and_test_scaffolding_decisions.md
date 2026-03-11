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
- the performance harness now applies a uniform 25% elapsed-time budget uplift during xdist-backed parallel runs because the repository-authoritative `-n auto` proof intentionally saturates the host and the baseline thresholds were authored for serial execution
- real daemon E2E harnesses must not leave uvicorn stdout/stderr on undrained `PIPE`s during long-lived runs; they now write to per-harness log files instead so deep git/merge flows remain inspectable without risking subprocess backpressure stalls
- real daemon E2E harnesses export an explicit `AICODING_DAEMON_REQUEST_TIMEOUT_SECONDS` budget because long merge/reconcile flows are valid runtime behavior and should not fail solely due to the CLI's default request timeout

### Scope boundary

- scaffold files are placeholders only and intentionally do not claim full schema completeness
- this phase establishes loadable paths and test harnesses, not authored workflow content
