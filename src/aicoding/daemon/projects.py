from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from aicoding.config import Settings, get_settings
from aicoding.daemon.admission import NodeRunAdmissionSnapshot, admit_node_run
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.lifecycle import load_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.live_git import LiveGitStatusSnapshot, bootstrap_live_git_repo
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.operator_views import load_node_operator_summary
from aicoding.daemon.session_harness import SessionAdapter, SessionPoller
from aicoding.daemon.session_records import bind_primary_session
from aicoding.daemon.run_orchestration import RunProgressSnapshot, load_current_run_progress
from aicoding.daemon.errors import DaemonNotFoundError
from aicoding.daemon.workflows import WorkflowCompileAttemptSnapshot, compile_node_workflow
from aicoding.daemon.workflow_events import record_workflow_event
from aicoding.daemon.workflow_start import WorkflowStartSnapshot, _resolve_title, _session_state_payload
from aicoding.db.models import WorkflowEvent
from aicoding.source_lineage import capture_node_version_source_lineage
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import HierarchyRegistry
from aicoding.resources import ResourceCatalog
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker


@dataclass(frozen=True, slots=True)
class ProjectCatalogEntry:
    project_id: str
    label: str
    source_path: str
    bootstrap_ready: bool
    readiness_code: str
    readiness_message: str | None
    default_branch: str | None
    head_commit_sha: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "project_id": self.project_id,
            "label": self.label,
            "source_path": self.source_path,
            "bootstrap_ready": self.bootstrap_ready,
            "readiness_code": self.readiness_code,
            "readiness_message": self.readiness_message,
            "default_branch": self.default_branch,
            "head_commit_sha": self.head_commit_sha,
        }


@dataclass(frozen=True, slots=True)
class ProjectTopLevelWorkflowSnapshot:
    project: ProjectCatalogEntry
    workflow_start: WorkflowStartSnapshot
    bootstrap: LiveGitStatusSnapshot

    def to_payload(self) -> dict[str, object]:
        payload = self.workflow_start.to_payload()
        payload.update(
            {
                "project": self.project.to_payload(),
                "source_repo": self.project.to_payload(),
                "bootstrap": {
                    "repo_bootstrap_status": "bootstrapped",
                    "worker_repo_path": self.bootstrap.repo_path,
                    "branch_name": self.bootstrap.branch_name,
                    "seed_commit_sha": self.bootstrap.seed_commit_sha,
                    "head_commit_sha": self.bootstrap.head_commit_sha,
                    "working_tree_state": self.bootstrap.working_tree_state,
                },
                "route_hint": _project_route_hint(self.project.project_id, payload["node"]["node_id"]),
            }
        )
        return payload


@dataclass(frozen=True, slots=True)
class ProjectBootstrapSnapshot:
    project: ProjectCatalogEntry
    top_level_nodes: list["ProjectTopLevelNodeSummary"]

    def to_payload(self) -> dict[str, object]:
        root_node_id = None if not self.top_level_nodes else self.top_level_nodes[0].node_id
        route_hint = None if root_node_id is None else _project_route_hint(self.project.project_id, root_node_id)
        return {
            "project": self.project.to_payload(),
            "root_node_id": None if root_node_id is None else str(root_node_id),
            "route_hint": route_hint,
            "top_level_nodes": [item.to_payload() for item in self.top_level_nodes],
        }


@dataclass(frozen=True, slots=True)
class ProjectTopLevelNodeSummary:
    node_id: UUID
    kind: str
    tier: str
    title: str
    lifecycle_state: str | None
    run_status: str | None
    authoritative_node_version_id: UUID | None
    latest_created_node_version_id: UUID | None
    route_hint: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "kind": self.kind,
            "tier": self.tier,
            "title": self.title,
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
            "authoritative_node_version_id": None if self.authoritative_node_version_id is None else str(self.authoritative_node_version_id),
            "latest_created_node_version_id": None if self.latest_created_node_version_id is None else str(self.latest_created_node_version_id),
            "route_hint": dict(self.route_hint),
        }


@dataclass(frozen=True, slots=True)
class ProjectCatalogDaemonContext:
    reachability_state: str
    auth_status: str
    daemon_app_name: str
    daemon_version: str
    authority: str
    session_backend: str

    def to_payload(self) -> dict[str, object]:
        return {
            "reachability_state": self.reachability_state,
            "auth_status": self.auth_status,
            "daemon_app_name": self.daemon_app_name,
            "daemon_version": self.daemon_version,
            "authority": self.authority,
            "session_backend": self.session_backend,
        }


def list_projects(*, settings: Settings | None = None) -> list[ProjectCatalogEntry]:
    active_settings = settings or get_settings()
    repos_root = _repos_root(active_settings)
    if not repos_root.exists():
        return []

    projects = []
    for child in sorted(repos_root.iterdir(), key=lambda path: path.name.lower()):
        if not child.is_dir():
            continue
        relative_path = child.relative_to(_workspace_root(active_settings)).as_posix()
        readiness = _inspect_project_readiness(child)
        projects.append(
            ProjectCatalogEntry(
                project_id=child.name,
                label=child.name,
                source_path=relative_path,
                bootstrap_ready=readiness["bootstrap_ready"],
                readiness_code=readiness["readiness_code"],
                readiness_message=readiness["readiness_message"],
                default_branch=readiness["default_branch"],
                head_commit_sha=readiness["head_commit_sha"],
            )
        )
    return projects


def get_project(project_id: str, *, settings: Settings | None = None) -> ProjectCatalogEntry:
    normalized = project_id.strip()
    if not normalized:
        raise DaemonNotFoundError("project not found")

    for project in list_projects(settings=settings):
        if project.project_id == normalized:
            return project
    raise DaemonNotFoundError(f"project '{normalized}' not found")


def start_project_top_level_workflow(
    session_factory: sessionmaker[Session],
    *,
    hierarchy_registry: HierarchyRegistry,
    resource_catalog: ResourceCatalog,
    project_id: str,
    kind: str,
    title: str | None,
    prompt: str,
    start_run: bool,
    adapter: SessionAdapter | None = None,
    poller: SessionPoller | None = None,
    settings: Settings | None = None,
) -> ProjectTopLevelWorkflowSnapshot:
    project = get_project(project_id, settings=settings)
    workflow_start, bootstrap = _start_project_top_level_workflow(
        session_factory,
        hierarchy_registry=hierarchy_registry,
        resource_catalog=resource_catalog,
        project=project,
        kind=kind,
        title=title,
        prompt=prompt,
        start_run=start_run,
        adapter=adapter,
        poller=poller,
        settings=settings,
    )
    with session_scope(session_factory) as session:
        record_workflow_event(
            session,
            logical_node_id=UUID(str(workflow_start.node["node_id"])),
            node_version_id=workflow_start.node_version_id,
            node_run_id=None,
            event_scope="website_project",
            event_type="top_level_created",
            payload_json={
                "project_id": project.project_id,
                "source_path": project.source_path,
            },
        )
    return ProjectTopLevelWorkflowSnapshot(project=project, workflow_start=workflow_start, bootstrap=bootstrap)


def load_project_bootstrap(
    session_factory: sessionmaker[Session],
    *,
    project_id: str,
    settings: Settings | None = None,
) -> ProjectBootstrapSnapshot:
    project = get_project(project_id, settings=settings)
    with query_session_scope(session_factory) as session:
        row = (
            session.execute(
                select(WorkflowEvent)
                .where(
                    WorkflowEvent.event_scope == "website_project",
                    WorkflowEvent.event_type == "top_level_created",
                )
                .order_by(WorkflowEvent.created_at.desc(), WorkflowEvent.id.desc())
            )
            .scalars()
            .all()
        )
        top_level_node_ids: list[UUID] = []
        seen_node_ids: set[UUID] = set()
        for item in row:
            payload = dict(item.payload_json or {})
            if payload.get("project_id") == project.project_id:
                if item.logical_node_id in seen_node_ids:
                    continue
                seen_node_ids.add(item.logical_node_id)
                top_level_node_ids.append(item.logical_node_id)
    top_level_nodes: list[ProjectTopLevelNodeSummary] = []
    for node_id in top_level_node_ids:
        try:
            summary = load_node_operator_summary(session_factory, node_id=node_id)
        except DaemonNotFoundError:
            continue
        top_level_nodes.append(
            ProjectTopLevelNodeSummary(
                node_id=summary.node_id,
                kind=summary.kind,
                tier=summary.tier,
                title=summary.title,
                lifecycle_state=summary.lifecycle_state,
                run_status=summary.run_status,
                authoritative_node_version_id=summary.authoritative_node_version_id,
                latest_created_node_version_id=summary.latest_created_node_version_id,
                route_hint=_project_route_hint(project.project_id, summary.node_id),
            )
        )
    return ProjectBootstrapSnapshot(project=project, top_level_nodes=top_level_nodes)


def _workspace_root(settings: Settings) -> Path:
    return settings.workspace_root or Path.cwd()


def _repos_root(settings: Settings) -> Path:
    return _workspace_root(settings) / "repos"


def _project_route_hint(project_id: str, node_id: UUID | str) -> dict[str, object]:
    node_id_str = str(node_id)
    return {
        "project_id": project_id,
        "node_id": node_id_str,
        "tab": "overview",
        "url": f"/projects/{project_id}/nodes/{node_id_str}/overview",
    }


def _start_project_top_level_workflow(
    session_factory: sessionmaker[Session],
    *,
    hierarchy_registry: HierarchyRegistry,
    resource_catalog: ResourceCatalog,
    project: ProjectCatalogEntry,
    kind: str,
    title: str | None,
    prompt: str,
    start_run: bool,
    adapter: SessionAdapter | None,
    poller: SessionPoller | None,
    settings: Settings | None,
) -> tuple[WorkflowStartSnapshot, LiveGitStatusSnapshot]:
    definition = hierarchy_registry.get(kind)
    if not definition.parent_constraints.allow_parentless:
        raise DaemonConflictError(f"node kind '{kind}' is not a top-level kind")

    resolved_title = _resolve_title(title=title, prompt=prompt)
    resolved_prompt = prompt.strip()
    if not resolved_prompt:
        raise DaemonConflictError("prompt must not be blank")

    creation = create_manual_node(
        session_factory,
        hierarchy_registry,
        kind=kind,
        title=resolved_title,
        prompt=resolved_prompt,
        parent_node_id=None,
    )
    capture_node_version_source_lineage(
        session_factory,
        node_version_id=creation.node_version_id,
        catalog=resource_catalog,
    )
    bootstrap = bootstrap_live_git_repo(
        session_factory,
        version_id=creation.node_version_id,
        source_repo_path=_project_source_repo_path(project, settings=settings),
    )
    compile_attempt = compile_node_workflow(
        session_factory,
        logical_node_id=creation.node.node_id,
        catalog=resource_catalog,
    )
    lifecycle = load_node_lifecycle(session_factory, str(creation.node.node_id))
    run_admission: NodeRunAdmissionSnapshot | None = None
    run_progress: RunProgressSnapshot | None = None
    session_payload: dict[str, object] | None = None
    status = "compile_failed"

    if compile_attempt.status == "compiled":
        lifecycle = transition_node_lifecycle(
            session_factory,
            node_id=str(creation.node.node_id),
            target_state="READY",
        )
        status = "compiled"
        if start_run:
            run_admission = admit_node_run(
                session_factory,
                node_id=creation.node.node_id,
                trigger_reason="workflow_start",
            )
            if run_admission.status == "admitted":
                run_progress = load_current_run_progress(session_factory, logical_node_id=creation.node.node_id)
                if adapter is not None and poller is not None:
                    session_payload = _session_state_payload(
                        bind_primary_session(
                            session_factory,
                            logical_node_id=creation.node.node_id,
                            adapter=adapter,
                            poller=poller,
                        )
                    )
                lifecycle = load_node_lifecycle(session_factory, str(creation.node.node_id))
                status = "started"
            else:
                lifecycle = load_node_lifecycle(session_factory, str(creation.node.node_id))
                status = "start_blocked"

    return (
        WorkflowStartSnapshot(
            status=status,
            requested_start_run=start_run,
            resolved_title=resolved_title,
            node=creation.node.to_payload(),
            node_version_id=creation.node_version_id,
            compile=compile_attempt,
            lifecycle=lifecycle.to_payload(),
            run_admission=None if run_admission is None else run_admission.to_payload(),
            run_progress=None if run_progress is None else run_progress.to_payload(),
            session=session_payload,
        ),
        bootstrap,
    )


def _project_source_repo_path(project: ProjectCatalogEntry, *, settings: Settings | None = None) -> Path:
    active_settings = settings or get_settings()
    return _workspace_root(active_settings) / project.source_path


def build_project_catalog_daemon_context(*, settings: Settings, daemon_version: str, session_backend: str) -> ProjectCatalogDaemonContext:
    return ProjectCatalogDaemonContext(
        reachability_state="reachable",
        auth_status="valid",
        daemon_app_name=settings.daemon_app_name,
        daemon_version=daemon_version,
        authority="daemon",
        session_backend=session_backend,
    )


def _inspect_project_readiness(project_path: Path) -> dict[str, object]:
    if not project_path.exists():
        return {
            "bootstrap_ready": False,
            "readiness_code": "missing_directory",
            "readiness_message": "Project directory does not exist.",
            "default_branch": None,
            "head_commit_sha": None,
        }

    is_git_result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=project_path,
        text=True,
        capture_output=True,
        check=False,
    )
    if is_git_result.returncode != 0 or is_git_result.stdout.strip().lower() != "true":
        return {
            "bootstrap_ready": False,
            "readiness_code": "not_git_repo",
            "readiness_message": "Directory is not a git repository.",
            "default_branch": None,
            "head_commit_sha": None,
        }

    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_path,
        text=True,
        capture_output=True,
        check=False,
    )
    if head_result.returncode != 0:
        return {
            "bootstrap_ready": False,
            "readiness_code": "head_unreadable",
            "readiness_message": "Git repository does not have a readable HEAD commit.",
            "default_branch": None,
            "head_commit_sha": None,
        }

    branch_result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"],
        cwd=project_path,
        text=True,
        capture_output=True,
        check=False,
    )
    branch_name = branch_result.stdout.strip() if branch_result.returncode == 0 else None
    return {
        "bootstrap_ready": True,
        "readiness_code": "ready",
        "readiness_message": None,
        "default_branch": branch_name,
        "head_commit_sha": head_result.stdout.strip(),
    }
