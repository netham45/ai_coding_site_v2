from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.db.models import CompiledSubtask, SubtaskAttempt
from aicoding.db.session import query_session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.project_policies import resolve_effective_policy
from aicoding.resources import ResourceCatalog, load_resource_catalog
from aicoding.yaml_schemas import EnvironmentPolicyDefinitionDocument

SUPPORTED_ISOLATION_MODES = {"none", "custom_profile"}


@dataclass(frozen=True, slots=True)
class EnvironmentPolicySnapshot:
    relative_path: str
    policy_id: str
    isolation_mode: str
    allow_network: bool
    runtime_profile: str | None
    mandatory: bool
    profile_declared: bool

    def to_payload(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "policy_id": self.policy_id,
            "isolation_mode": self.isolation_mode,
            "allow_network": self.allow_network,
            "runtime_profile": self.runtime_profile,
            "mandatory": self.mandatory,
            "profile_declared": self.profile_declared,
        }


@dataclass(frozen=True, slots=True)
class ExecutionEnvironmentSnapshot:
    policy_ref: str | None
    policy_id: str | None
    requested_mode: str
    resolved_mode: str
    allow_network: bool
    runtime_profile: str | None
    mandatory: bool
    launch_status: str
    launcher_kind: str
    environment_id: str | None
    fallback_reason: str | None
    failure_class: str | None
    summary: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "policy_ref": self.policy_ref,
            "policy_id": self.policy_id,
            "requested_mode": self.requested_mode,
            "resolved_mode": self.resolved_mode,
            "allow_network": self.allow_network,
            "runtime_profile": self.runtime_profile,
            "mandatory": self.mandatory,
            "launch_status": self.launch_status,
            "launcher_kind": self.launcher_kind,
            "environment_id": self.environment_id,
            "fallback_reason": self.fallback_reason,
            "failure_class": self.failure_class,
            "summary": self.summary,
        }


def list_environment_policies(catalog: ResourceCatalog | None = None) -> list[EnvironmentPolicySnapshot]:
    resource_catalog = catalog or load_resource_catalog()
    registry = load_hierarchy_registry(resource_catalog)
    effective_policy = resolve_effective_policy(resource_catalog, hierarchy_registry=registry)
    policies: list[EnvironmentPolicySnapshot] = []
    for source_group, root in (
        ("yaml_builtin_system", resource_catalog.yaml_builtin_system_dir),
        ("yaml_project", resource_catalog.yaml_project_dir),
    ):
        environments_root = root / "environments"
        if not environments_root.exists():
            continue
        for path in sorted(environments_root.glob("*.yaml")):
            relative_path = str(path.relative_to(root))
            document = EnvironmentPolicyDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
            policies.append(
                EnvironmentPolicySnapshot(
                    relative_path=relative_path,
                    policy_id=document.id,
                    isolation_mode=document.isolation_mode,
                    allow_network=document.allow_network,
                    runtime_profile=document.runtime_profile,
                    mandatory=document.mandatory,
                    profile_declared=document.runtime_profile in effective_policy.environment_profiles
                    if document.runtime_profile is not None
                    else True,
                )
            )
    return policies


def load_current_subtask_environment(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    with query_session_scope(session_factory) as session:
        subtask = _require_current_subtask(session, logical_node_id=logical_node_id)
        return _compiled_subtask_environment_payload(subtask)


def load_attempt_environment(session_factory: sessionmaker[Session], *, attempt_id: UUID) -> dict[str, object]:
    with query_session_scope(session_factory) as session:
        attempt = session.get(SubtaskAttempt, attempt_id)
        if attempt is None:
            raise DaemonNotFoundError("subtask attempt not found")
        return {
            "attempt_id": str(attempt.id),
            "compiled_subtask_id": str(attempt.compiled_subtask_id),
            "attempt_number": attempt.attempt_number,
            "status": attempt.status,
            "execution_environment": dict(attempt.execution_environment_json or {}),
        }


def build_execution_environment(
    request_json: dict[str, object] | None,
    *,
    attempt_id: UUID,
) -> ExecutionEnvironmentSnapshot:
    request = dict(request_json or {})
    policy_ref = _string_or_none(request.get("policy_ref"))
    policy_id = _string_or_none(request.get("policy_id"))
    requested_mode = _string_or(request.get("isolation_mode"), "none")
    allow_network = bool(request.get("allow_network", False))
    runtime_profile = _string_or_none(request.get("runtime_profile"))
    mandatory = bool(request.get("mandatory", False))

    if requested_mode == "none":
        return ExecutionEnvironmentSnapshot(
            policy_ref=policy_ref,
            policy_id=policy_id,
            requested_mode=requested_mode,
            resolved_mode="none",
            allow_network=allow_network,
            runtime_profile=runtime_profile,
            mandatory=mandatory,
            launch_status="active",
            launcher_kind="host",
            environment_id=f"host:{attempt_id}",
            fallback_reason=None,
            failure_class=None,
            summary=None,
        )

    if requested_mode == "custom_profile" and runtime_profile:
        return ExecutionEnvironmentSnapshot(
            policy_ref=policy_ref,
            policy_id=policy_id,
            requested_mode=requested_mode,
            resolved_mode="custom_profile",
            allow_network=allow_network,
            runtime_profile=runtime_profile,
            mandatory=mandatory,
            launch_status="delegated",
            launcher_kind="manual_profile",
            environment_id=f"profile:{runtime_profile}:{attempt_id}",
            fallback_reason=None,
            failure_class=None,
            summary="Subtask requires the declared custom runtime profile and must be executed through that profile.",
        )

    if mandatory:
        return ExecutionEnvironmentSnapshot(
            policy_ref=policy_ref,
            policy_id=policy_id,
            requested_mode=requested_mode,
            resolved_mode="none",
            allow_network=allow_network,
            runtime_profile=runtime_profile,
            mandatory=mandatory,
            launch_status="launch_failed",
            launcher_kind="unsupported",
            environment_id=None,
            fallback_reason=None,
            failure_class="environment_launch_failure",
            summary=f"Runtime isolation mode '{requested_mode}' is not supported by the current launcher.",
        )

    return ExecutionEnvironmentSnapshot(
        policy_ref=policy_ref,
        policy_id=policy_id,
        requested_mode=requested_mode,
        resolved_mode="none",
        allow_network=allow_network,
        runtime_profile=runtime_profile,
        mandatory=mandatory,
        launch_status="fallback_local",
        launcher_kind="host",
        environment_id=f"host:{attempt_id}",
        fallback_reason="unsupported_isolation_mode",
        failure_class=None,
        summary=f"Fell back to the host runtime because isolation mode '{requested_mode}' is not currently supported.",
    )


def validate_environment_policy_ref(
    ref: str,
    *,
    catalog: ResourceCatalog,
) -> tuple[str, str]:
    relative_path = normalize_environment_relative_path(ref)
    if (catalog.yaml_project_dir / relative_path).exists():
        return "yaml_project", relative_path
    if (catalog.yaml_builtin_system_dir / relative_path).exists():
        return "yaml_builtin_system", relative_path
    raise DaemonConflictError(f"environment policy '{ref}' was not found")


def normalize_environment_relative_path(ref: str) -> str:
    stripped = ref.strip()
    if not stripped:
        raise DaemonConflictError("environment policy reference must not be blank")
    if stripped.endswith(".yaml"):
        return stripped if stripped.startswith("environments/") else f"environments/{stripped}"
    return f"environments/{stripped}.yaml"


def _compiled_subtask_environment_payload(subtask: CompiledSubtask) -> dict[str, object]:
    return {
        "compiled_subtask_id": str(subtask.id),
        "environment_policy_ref": subtask.environment_policy_ref,
        "environment_request": dict(subtask.environment_request_json or {}),
    }


def _require_current_subtask(session: Session, *, logical_node_id: UUID) -> CompiledSubtask:
    from aicoding.daemon.run_orchestration import _load_active_run_bundle

    _, state, _ = _load_active_run_bundle(session, logical_node_id)
    if state.current_compiled_subtask_id is None:
        raise DaemonNotFoundError("current compiled subtask not found")
    subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
    if subtask is None:
        raise DaemonNotFoundError("compiled subtask not found")
    return subtask


def _string_or(value: object, default: str) -> str:
    return default if value is None else str(value)


def _string_or_none(value: object) -> str | None:
    return None if value is None else str(value)
