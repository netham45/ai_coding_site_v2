# Task: Implement The Packaged Resource Install Fix

## Goal

Fix the build/install contract so the packaged `aicoding` distribution includes the required `resources/` tree and add regression coverage that proves a built wheel contains canonical YAML and prompt assets.

## Rationale

- Rationale: The daemon and CLI load built-in YAML and prompt assets from `PACKAGE_ROOT / "resources"`, so the package is broken if the distribution omits that tree.
- Reason for existence: This task exists to turn the packaged-resource fix plan into code, verification, and a local reinstall that resolves the currently observed startup failure.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`
- `plan/features/39_F12_tmux_session_manager.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/tasks/2026-03-11_packaged_resource_install_fix_plan.md`
- `pyproject.toml`
- `src/aicoding/resources.py`
- `tests/unit/test_resources.py`

## Scope

- Database: not applicable.
- CLI: packaged CLI entrypoints must be able to resolve the same built-in assets as the daemon.
- Daemon: packaged daemon startup must be able to load built-in runtime policy and recovery prompt assets.
- YAML: include the built-in/system and schema YAML assets in build/install artifacts.
- Prompts: include the packaged default prompt assets in build/install artifacts.
- Tests: add a regression test that inspects a built wheel for canonical packaged resources.
- Performance: negligible.
- Notes: update development logs and task indexes for the implementation pass.

## Verification

- Packaging/resource tests: `python3 -m pytest tests/unit/test_resources.py tests/integration/test_resource_loading.py tests/integration/test_packaging_resources.py -q`
- Documentation checks: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Local runtime smoke: `python3 -m pip install -e .[dev]`

## Exit Criteria

- Build/install metadata includes `src/aicoding/resources/**`.
- A built wheel contains canonical built-in YAML and prompt assets.
- The local environment is reinstalled so `python3 -m aicoding.daemon.main` no longer uses the broken stale install.
- Verification commands pass.
- The development log records the resulting status honestly.
