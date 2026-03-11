# Task: Fix Packaged Resource Installation And Import Path Drift

## Goal

Capture the implementation plan required to stop the daemon and tests from loading a broken installed `aicoding` package copy that omits non-Python resource assets.

## Rationale

- Rationale: The current runtime failure is not caused by tmux itself. The daemon is importing `aicoding` from `site-packages`, and that installed copy does not include the required YAML and prompt resource files under `aicoding/resources/`.
- Reason for existence: This task exists to preserve the diagnosis and the concrete repair plan so the repository can fix the packaging/install contract instead of repeatedly debugging missing built-in YAML and prompt assets at runtime.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`: built-in YAML is part of the implementation surface and must be present in installed/runtime environments.
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`: runtime policies and prompts are first-class assets and must be packaged with the code that loads them.
- `plan/features/39_F12_tmux_session_manager.md`: tmux-backed runtime startup depends on packaged prompt assets for bootstrap, idle-nudge, and recovery flows.
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: the daemon cannot be authoritative if its packaged runtime assets are missing.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `pyproject.toml`
- `src/aicoding/resources.py`
- `src/aicoding/bootstrap.py`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

## Scope

- Database: not applicable directly.
- CLI: ensure CLI entrypoints that import the installed package resolve the same packaged resources as the daemon.
- Daemon: fix daemon startup/runtime so packaged installs can load built-in YAML and prompt assets reliably.
- YAML: package all built-in YAML assets required under `src/aicoding/resources/yaml/`.
- Prompts: package all built-in prompt assets required under `src/aicoding/resources/prompts/`.
- Tests: add a packaging/install-oriented regression test that proves a build/install artifact contains the required resource tree or that a runtime import can resolve canonical asset files.
- Performance: not applicable.
- Notes: document the immediate repo-local workaround and the actual packaging fix path; update any setup/getting-started guidance that assumes `python3 -m aicoding...` will automatically import the repo tree in a `src/` layout.

## Verification

- Documentation checks: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- The diagnosis explicitly records that the active failure comes from importing `aicoding` from `site-packages` while the installed package lacks `aicoding/resources/...`.
- The plan includes both the short-term workaround and the real packaging fix.
- The plan includes adding regression coverage for packaged resource presence.
- The governing task plan is listed in `plan/tasks/README.md`.
- The development log exists and records the findings honestly.

## Findings To Preserve

1. `python3 -m aicoding.daemon.main` currently imports `aicoding` from `/home/netham45/.local/lib/python3.12/site-packages/aicoding/__init__.py`, not from this repo's `src/aicoding/`.
2. The installed package copy under `/home/netham45/.local/lib/python3.12/site-packages/aicoding/` does not contain `resources/` at all.
3. `load_resource_catalog()` resolves built-in assets relative to `PACKAGE_ROOT / "resources"`, so missing packaged resources produce runtime `FileNotFoundError` immediately in background loops and prompt loading.
4. `PYTHONPATH=src python3 -m aicoding.daemon.main` uses the repo tree and can see the missing files, proving the immediate fault is the installed package/build artifact, not the source tree contents.
5. `pyproject.toml` sets `include-package-data = true`, but the repository currently has no `MANIFEST.in` or explicit `[tool.setuptools.package-data]` rules that would actually include the resource trees in build artifacts.

## Proposed Execution Stages

### Stage 1: Immediate Operator Workaround

- Update the relevant setup/getting-started note to tell local contributors that, until the packaging fix lands, repo-local launches should use:

```bash
PYTHONPATH=src python3 -m aicoding.daemon.main
```

- Optionally recommend an editable install path if the repo wants `python3 -m aicoding...` without the `PYTHONPATH` prefix.

### Stage 2: Packaging Metadata Fix

- Add explicit package-data rules so `src/aicoding/resources/**` is included in build and install artifacts.
- Choose one packaging contract and document it clearly:
  - `MANIFEST.in` plus setuptools package-data rules, or
  - explicit `[tool.setuptools.package-data]` configuration in `pyproject.toml`.
- Verify that built wheels/sdists and local installs contain:
  - `aicoding/resources/yaml/builtin/system-yaml/...`
  - `aicoding/resources/yaml/schemas/...`
  - `aicoding/resources/prompts/packs/default/...`

### Stage 3: Regression Coverage

- Add a bounded test that proves the package-data contract rather than relying only on source-tree reads.
- Good target shapes:
  - a build-artifact inspection test, or
  - a runtime import test that asserts canonical packaged files exist relative to `aicoding.__file__`.
- Include canonical asset assertions for at least:
  - `resources/yaml/builtin/system-yaml/policies/default_runtime_policy.yaml`
  - `resources/prompts/packs/default/recovery/idle_nudge.md`

### Stage 4: Runtime Error-Handling Hardening

- Consider failing daemon startup fast if required built-in packaged assets are missing, instead of letting background loops log the same error repeatedly after startup.
- This is secondary to the packaging fix, but it improves operator clarity and prevents noisy startup loops.

### Stage 5: Verification And Cleanup

- Rebuild/install the package in the local environment.
- Re-run the daemon startup command without `PYTHONPATH=src` and confirm it resolves packaged assets correctly.
- Re-run the previously blocked integration slice after the packaging fix.

## Candidate Verification Commands For The Later Implementation

```bash
python3 -m pytest tests/unit/test_resources.py tests/unit/test_prompt_pack.py tests/unit/test_runtime_policy_library.py -q
python3 -m pytest tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q
python3 -m aicoding.daemon.main
```

These are implementation targets for the later fix, not a claim that the packaging issue is already resolved.
