# Development Log: Packaged Resource Install Fix Plan

## Entry 1

- Timestamp: 2026-03-11
- Task ID: packaged_resource_install_fix_plan
- Task title: Plan the packaged resource install fix
- Status: started
- Affected systems: CLI, daemon, YAML, prompts, notes, tests, development logs
- Summary: Started a root-cause review of the daemon startup failure that reports missing built-in runtime policy and prompt assets from `site-packages`.
- Plans and notes consulted:
  - `pyproject.toml`
  - `src/aicoding/resources.py`
  - `src/aicoding/bootstrap.py`
  - `tests/unit/test_resources.py`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 - <<'PY' ... import aicoding; print(aicoding.__file__) ... PY`
  - `python3 -m pip show -f aicoding`
  - `find src/aicoding/resources -maxdepth 4 -type f`
  - `find /home/netham45/.local/lib/python3.12/site-packages/aicoding/resources -maxdepth 4 -type f`
  - `find build -maxdepth 4 -type f`
  - `PYTHONPATH=src python3 - <<'PY' ... import aicoding ... PY`
- Result: Confirmed that the daemon is importing the installed `site-packages` package, that the installed/build artifact omits the `resources/` tree entirely, and that a repo-local `PYTHONPATH=src` launch can see the missing files, which isolates the fault to packaging/install behavior rather than source-tree contents.
- Next step: Write the governing task plan, register it in the task index, run the task-plan document checks, and preserve the findings and staged fix path.

## Entry 2

- Timestamp: 2026-03-11
- Task ID: packaged_resource_install_fix_plan
- Task title: Plan the packaged resource install fix
- Status: complete
- Affected systems: CLI, daemon, YAML, prompts, notes, tests, development logs
- Summary: Added a task plan that captures the root cause, the immediate workaround, the required package-data fix, the needed regression coverage, and a startup-hardening follow-up for missing packaged assets.
- Plans and notes consulted:
  - `plan/tasks/2026-03-11_packaged_resource_install_fix_plan.md`
  - `pyproject.toml`
  - `src/aicoding/resources.py`
  - `src/aicoding/bootstrap.py`
  - `tests/unit/test_resources.py`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Result: Passed. The repository now has a concrete fix plan for the packaged-resource failure, including the evidence that the build/install artifact currently omits the `resources/` tree and the recommendation to use `PYTHONPATH=src` only as a temporary workaround.
- Next step: Execute the implementation by adding explicit package-data rules, adding a packaging regression test, and rerunning daemon startup and the blocked integration slices.
