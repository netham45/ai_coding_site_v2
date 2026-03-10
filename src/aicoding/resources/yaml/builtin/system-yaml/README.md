# Built-In System YAML Library

This directory holds the packaged built-in YAML library used by the default
system.

The library is intentionally minimal but compile-grade:

- node definitions keep the current default ladder stable
- task and subtask definitions provide reusable authored execution shapes
- layouts, quality gates, runtime policies, and hooks are packaged for
  deterministic built-in loading and future compile-stage expansion
