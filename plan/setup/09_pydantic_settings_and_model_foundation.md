# Phase S09: Pydantic Settings And Model Foundation

## Goal

Standardize settings, request/response models, and internal typed configuration using Pydantic.

## Scope

- Database: define typed DB config/settings models.
- CLI: define typed config and command input/output models where appropriate.
- Daemon: define typed API request/response/auth/settings models.
- YAML: define typed internal models for loaded YAML and prompt metadata where useful before schema validation/compilation.
- Prompts: define prompt metadata and placeholder models where applicable.
- Tests: exhaustively test config parsing, invalid env/config values, model validation, and serialization stability.
- Performance: benchmark settings/model parsing in startup-sensitive paths.
- Notes: update setup/model notes if Pydantic usage boundaries need clarification.

## Exit Criteria

- settings and model patterns are explicit and consistent across CLI and daemon.
