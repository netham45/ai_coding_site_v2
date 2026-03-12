from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.branches import record_final_commit, record_seed_commit
from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.git_conflicts import MergeConflictSnapshot, MergeEventSnapshot, record_merge_conflict, record_merge_event
from aicoding.daemon.workflow_events import record_workflow_event
from aicoding.db.models import LogicalNodeCurrentVersion, NodeLifecycleState, NodeVersion, ParentIncrementalMergeLane
from aicoding.db.session import query_session_scope, session_scope


@dataclass(frozen=True, slots=True)
class LiveGitStatusSnapshot:
    node_id: UUID
    node_version_id: UUID
    repo_path: str
    branch_name: str
    head_commit_sha: str | None
    seed_commit_sha: str | None
    final_commit_sha: str | None
    working_tree_state: str

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "repo_path": self.repo_path,
            "branch_name": self.branch_name,
            "head_commit_sha": self.head_commit_sha,
            "seed_commit_sha": self.seed_commit_sha,
            "final_commit_sha": self.final_commit_sha,
            "working_tree_state": self.working_tree_state,
        }


@dataclass(frozen=True, slots=True)
class LiveMergeResultSnapshot:
    node_id: UUID
    node_version_id: UUID
    status: str
    repo_path: str
    merge_events: list[MergeEventSnapshot]
    conflicts: list[MergeConflictSnapshot]
    head_commit_sha: str | None
    working_tree_state: str

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "status": self.status,
            "repo_path": self.repo_path,
            "merge_events": [item.to_payload() for item in self.merge_events],
            "conflicts": [item.to_payload() for item in self.conflicts],
            "head_commit_sha": self.head_commit_sha,
            "working_tree_state": self.working_tree_state,
        }


@dataclass(frozen=True, slots=True)
class LiveFinalizeResultSnapshot:
    node_id: UUID
    node_version_id: UUID
    status: str
    repo_path: str
    final_commit_sha: str
    working_tree_state: str

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "status": self.status,
            "repo_path": self.repo_path,
            "final_commit_sha": self.final_commit_sha,
            "working_tree_state": self.working_tree_state,
        }


def bootstrap_live_git_repo(
    session_factory: sessionmaker[Session],
    *,
    version_id: UUID,
    files: dict[str, str] | None = None,
    base_version_id: UUID | None = None,
    source_repo_path: Path | None = None,
    replace_existing: bool = False,
) -> LiveGitStatusSnapshot:
    with query_session_scope(session_factory) as session:
        version = _require_version(session, version_id)
        repo_path = _repo_path(version.id)
        branch_name = _require_branch_name(version)
        node_id = version.logical_node_id
        base_version = None if source_repo_path is not None else _resolve_bootstrap_base_version(
            session,
            version,
            explicit_base_version_id=base_version_id,
        )
        target_seed_commit = version.seed_commit_sha
    if source_repo_path is not None and base_version is not None:
        raise DaemonConflictError("live git bootstrap may not use both base_version_id and source_repo_path")
    if replace_existing and repo_path.exists():
        shutil.rmtree(repo_path)
    if source_repo_path is None and base_version is None:
        repo_path.mkdir(parents=True, exist_ok=True)
        _git(repo_path, "init", "-b", branch_name)
        _git(repo_path, "config", "user.name", "AI Coding")
        _git(repo_path, "config", "user.email", "aicoding@example.invalid")
        for relative_path, content in sorted((files or {}).items()):
            target = repo_path / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        _git(repo_path, "add", ".")
        if not (files or {}):
            _git(repo_path, "commit", "--allow-empty", "-m", "Bootstrap seed")
        else:
            _git(repo_path, "commit", "-m", "Bootstrap seed")
    elif source_repo_path is not None:
        source_repo_head = _require_source_repo_head(source_repo_path)
        checkout_commit = target_seed_commit or source_repo_head
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        clone_result = subprocess.run(
            ["git", "clone", "--no-hardlinks", str(source_repo_path), str(repo_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if clone_result.returncode != 0:
            raise DaemonConflictError(
                clone_result.stderr.strip() or clone_result.stdout.strip() or "git clone failed during source repo bootstrap"
            )
        _git(repo_path, "config", "user.name", "AI Coding")
        _git(repo_path, "config", "user.email", "aicoding@example.invalid")
        if _git_try(repo_path, "remote", "get-url", "origin").ok:
            _git(repo_path, "remote", "remove", "origin")
        _git(repo_path, "checkout", "-B", branch_name, checkout_commit)
        for relative_path, content in sorted((files or {}).items()):
            target = repo_path / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        if files:
            _git(repo_path, "add", ".")
            if _git_output(repo_path, "status", "--porcelain"):
                _git(repo_path, "commit", "-m", "Bootstrap seed override")
    else:
        parent_repo_path = _repo_path(base_version.id)
        if not parent_repo_path.exists() or not (parent_repo_path / ".git").exists():
            raise DaemonConflictError("base live git repo has not been bootstrapped")
        if base_version.seed_commit_sha is None:
            raise DaemonConflictError("base live git repo requires a recorded seed commit")
        checkout_commit = target_seed_commit or base_version.seed_commit_sha
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        clone_result = subprocess.run(
            ["git", "clone", "--no-hardlinks", str(parent_repo_path), str(repo_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if clone_result.returncode != 0:
            raise DaemonConflictError(
                clone_result.stderr.strip() or clone_result.stdout.strip() or "git clone failed during live repo bootstrap"
            )
        _git(repo_path, "config", "user.name", "AI Coding")
        _git(repo_path, "config", "user.email", "aicoding@example.invalid")
        if _git_try(repo_path, "remote", "get-url", "origin").ok:
            _git(repo_path, "remote", "remove", "origin")
        _git(repo_path, "checkout", "-B", branch_name, checkout_commit)
        for relative_path, content in sorted((files or {}).items()):
            target = repo_path / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        if files:
            _git(repo_path, "add", ".")
            if _git_output(repo_path, "status", "--porcelain"):
                _git(repo_path, "commit", "-m", "Bootstrap seed override")
    seed_commit_sha = _git_output(repo_path, "rev-parse", "HEAD")
    record_seed_commit(session_factory, version_id=version_id, commit_sha=seed_commit_sha)
    _set_working_tree_state(session_factory, logical_node_id=node_id, state="seed_ready")
    return show_live_git_status(session_factory, version_id=version_id)


def refresh_child_live_git_from_parent_head(
    session_factory: sessionmaker[Session],
    *,
    child_version_id: UUID,
) -> LiveGitStatusSnapshot:
    with session_scope(session_factory) as session:
        child_version = _require_version(session, child_version_id)
        if child_version.parent_node_version_id is None:
            raise DaemonConflictError("child refresh requires a parent node version")
        lifecycle = session.get(NodeLifecycleState, str(child_version.logical_node_id))
        if lifecycle is not None and lifecycle.node_version_id not in {None, child_version.id}:
            lifecycle = None
        if lifecycle is not None and lifecycle.run_status in {"PENDING", "RUNNING", "PAUSED"}:
            raise DaemonConflictError("child refresh requires the child to be inactive")
        if child_version.final_commit_sha is not None:
            raise DaemonConflictError("child refresh requires an unfinalized child version")
        parent_version = _require_version(session, child_version.parent_node_version_id)
        lane = session.get(ParentIncrementalMergeLane, parent_version.id)
        target_parent_head = None if lane is None else lane.current_parent_head_commit_sha
        if target_parent_head is None:
            target_parent_head = parent_version.final_commit_sha or parent_version.seed_commit_sha
        if target_parent_head is None:
            raise DaemonConflictError("child refresh requires a recorded parent head commit")
        child_version.seed_commit_sha = target_parent_head
        session.flush()
    return bootstrap_live_git_repo(
        session_factory,
        version_id=child_version_id,
        replace_existing=True,
    )


def stage_live_git_change(
    session_factory: sessionmaker[Session],
    *,
    version_id: UUID,
    files: dict[str, str],
    message: str,
    record_as_final: bool = False,
) -> LiveGitStatusSnapshot:
    with query_session_scope(session_factory) as session:
        version = _require_version(session, version_id)
        repo_path = _repo_path(version.id)
        node_id = version.logical_node_id
    if not repo_path.exists():
        raise DaemonConflictError("live git repo has not been bootstrapped")
    for relative_path, content in sorted(files.items()):
        target = repo_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    _git(repo_path, "add", ".")
    _git(repo_path, "commit", "-m", message)
    head = _git_output(repo_path, "rev-parse", "HEAD")
    if record_as_final:
        _clear_unreachable_recorded_final_commit(session_factory, version_id=version_id, repo_path=repo_path)
        record_final_commit(session_factory, version_id=version_id, commit_sha=head)
        _set_working_tree_state(session_factory, logical_node_id=node_id, state="finalized_clean")
    else:
        _set_working_tree_state(session_factory, logical_node_id=node_id, state="dirty_committed")
    return show_live_git_status(session_factory, version_id=version_id)


def execute_live_merge_children(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    ordered_child_versions: list[tuple[UUID, str, int]],
) -> LiveMergeResultSnapshot:
    if not ordered_child_versions:
        raise DaemonConflictError("live child merge requires at least one mergeable child version")
    with query_session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        parent_version = _require_version(session, selector.authoritative_node_version_id)
        parent_branch = _require_branch_name(parent_version)
        repo_path = _repo_path(parent_version.id)
        if not repo_path.exists():
            raise DaemonConflictError("parent live git repo has not been bootstrapped")
        if parent_version.seed_commit_sha is None:
            raise DaemonConflictError("parent live git repo requires a recorded seed commit")
        node_id = parent_version.logical_node_id
    _git(repo_path, "checkout", parent_branch)
    _git(repo_path, "reset", "--hard", parent_version.seed_commit_sha)
    merge_events: list[MergeEventSnapshot] = []
    conflicts: list[MergeConflictSnapshot] = []
    parent_before = _git_output(repo_path, "rev-parse", "HEAD")
    for child_version_id, child_final_commit_sha, merge_order in ordered_child_versions:
        child_repo = _repo_path(child_version_id)
        if not child_repo.exists():
            raise DaemonConflictError("child live git repo has not been bootstrapped")
        fetch_result = _git_try(repo_path, "fetch", str(child_repo), child_final_commit_sha)
        if not fetch_result.ok:
            raise DaemonConflictError(fetch_result.message)
        merge_result = _git_try(repo_path, "merge", "--no-ff", "--no-edit", "FETCH_HEAD")
        if not merge_result.ok:
            conflicted_files = _git_output(repo_path, "diff", "--name-only", "--diff-filter=U").splitlines()
            conflict = record_merge_conflict(
                session_factory,
                parent_node_version_id=_load_authoritative_version_id(session_factory, logical_node_id),
                child_node_version_id=child_version_id,
                child_final_commit_sha=child_final_commit_sha,
                parent_commit_before=parent_before,
                parent_commit_after=parent_before,
                merge_order=merge_order,
                files_json=conflicted_files or ["unknown_conflict"],
            )
            _set_working_tree_state(session_factory, logical_node_id=node_id, state="merge_conflict")
            _record_live_git_event(
                session_factory,
                logical_node_id=node_id,
                node_version_id=_load_authoritative_version_id(session_factory, logical_node_id),
                event_type="git.merge.conflict",
                payload_json={"child_node_version_id": str(child_version_id), "files": conflict.files_json},
            )
            return LiveMergeResultSnapshot(
                node_id=node_id,
                node_version_id=_load_authoritative_version_id(session_factory, logical_node_id),
                status="conflicted",
                repo_path=str(repo_path),
                merge_events=merge_events,
                conflicts=[conflict],
                head_commit_sha=parent_before,
                working_tree_state="merge_conflict",
            )
        parent_after = _git_output(repo_path, "rev-parse", "HEAD")
        event = record_merge_event(
            session_factory,
            parent_node_version_id=_load_authoritative_version_id(session_factory, logical_node_id),
            child_node_version_id=child_version_id,
            child_final_commit_sha=child_final_commit_sha,
            parent_commit_before=parent_before,
            parent_commit_after=parent_after,
            merge_order=merge_order,
        )
        merge_events.append(event)
        parent_before = parent_after
    _set_working_tree_state(session_factory, logical_node_id=node_id, state="merged_children")
    _record_live_git_event(
        session_factory,
        logical_node_id=node_id,
        node_version_id=_load_authoritative_version_id(session_factory, logical_node_id),
        event_type="git.merge.completed",
        payload_json={"merge_count": len(merge_events), "head_commit_sha": parent_before},
    )
    return LiveMergeResultSnapshot(
        node_id=node_id,
        node_version_id=_load_authoritative_version_id(session_factory, logical_node_id),
        status="merged",
        repo_path=str(repo_path),
        merge_events=merge_events,
        conflicts=[],
        head_commit_sha=parent_before,
        working_tree_state="merged_children",
    )


def execute_live_merge_children_for_version(
    session_factory: sessionmaker[Session],
    *,
    node_version_id: UUID,
    ordered_child_versions: list[tuple[UUID, str, int]],
) -> LiveMergeResultSnapshot:
    if not ordered_child_versions:
        raise DaemonConflictError("live child merge requires at least one mergeable child version")
    with query_session_scope(session_factory) as session:
        parent_version = _require_version(session, node_version_id)
        repo_path = _repo_path(parent_version.id)
        branch_name = _require_branch_name(parent_version)
        if not repo_path.exists():
            raise DaemonConflictError("parent live git repo has not been bootstrapped")
        if parent_version.seed_commit_sha is None:
            raise DaemonConflictError("parent live git repo requires a recorded seed commit")
    _git(repo_path, "checkout", branch_name)
    _git(repo_path, "reset", "--hard", parent_version.seed_commit_sha)
    merge_events: list[MergeEventSnapshot] = []
    conflicts: list[MergeConflictSnapshot] = []
    parent_before = _git_output(repo_path, "rev-parse", "HEAD")
    for child_version_id, child_final_commit_sha, merge_order in ordered_child_versions:
        child_repo = _repo_path(child_version_id)
        if not child_repo.exists():
            raise DaemonConflictError("child live git repo has not been bootstrapped")
        fetch_result = _git_try(repo_path, "fetch", str(child_repo), child_final_commit_sha)
        if not fetch_result.ok:
            raise DaemonConflictError(fetch_result.message)
        merge_result = _git_try(repo_path, "merge", "--no-ff", "--no-edit", "FETCH_HEAD")
        if not merge_result.ok:
            conflicted_files = _git_output(repo_path, "diff", "--name-only", "--diff-filter=U").splitlines()
            conflict = record_merge_conflict(
                session_factory,
                parent_node_version_id=node_version_id,
                child_node_version_id=child_version_id,
                child_final_commit_sha=child_final_commit_sha,
                parent_commit_before=parent_before,
                parent_commit_after=parent_before,
                merge_order=merge_order,
                files_json=conflicted_files or ["unknown_conflict"],
            )
            return LiveMergeResultSnapshot(
                node_id=parent_version.logical_node_id,
                node_version_id=node_version_id,
                status="conflicted",
                repo_path=str(repo_path),
                merge_events=merge_events,
                conflicts=[conflict],
                head_commit_sha=parent_before,
                working_tree_state="merge_conflict",
            )
        parent_after = _git_output(repo_path, "rev-parse", "HEAD")
        event = record_merge_event(
            session_factory,
            parent_node_version_id=node_version_id,
            child_node_version_id=child_version_id,
            child_final_commit_sha=child_final_commit_sha,
            parent_commit_before=parent_before,
            parent_commit_after=parent_after,
            merge_order=merge_order,
        )
        merge_events.append(event)
        parent_before = parent_after
    return LiveMergeResultSnapshot(
        node_id=parent_version.logical_node_id,
        node_version_id=node_version_id,
        status="merged",
        repo_path=str(repo_path),
        merge_events=merge_events,
        conflicts=conflicts,
        head_commit_sha=parent_before,
        working_tree_state="merged_children",
    )


def abort_live_merge(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> LiveGitStatusSnapshot:
    with query_session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        version = _require_version(session, selector.authoritative_node_version_id)
        repo_path = _repo_path(version.id)
        branch_name = _require_branch_name(version)
        if not repo_path.exists():
            raise DaemonConflictError("live git repo has not been bootstrapped")
        if version.seed_commit_sha is None:
            raise DaemonConflictError("seed commit is required to abort merge state")
    _git_try(repo_path, "merge", "--abort")
    _git(repo_path, "checkout", branch_name)
    _git(repo_path, "reset", "--hard", version.seed_commit_sha)
    _set_working_tree_state(session_factory, logical_node_id=logical_node_id, state="seed_ready")
    _record_live_git_event(
        session_factory,
        logical_node_id=logical_node_id,
        node_version_id=version.id,
        event_type="git.merge.aborted",
        payload_json={"seed_commit_sha": version.seed_commit_sha},
    )
    return show_live_git_status(session_factory, version_id=version.id)


def finalize_live_git_state(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> LiveFinalizeResultSnapshot:
    with query_session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        version = _require_version(session, selector.authoritative_node_version_id)
        repo_path = _repo_path(version.id)
        if not repo_path.exists():
            raise DaemonConflictError("live git repo has not been bootstrapped")
        if _git_output(repo_path, "status", "--porcelain"):
            _record_live_git_event(
                session_factory,
                logical_node_id=logical_node_id,
                node_version_id=version.id,
                event_type="git.finalize.blocked",
                payload_json={"reason": "dirty_worktree"},
            )
            raise DaemonConflictError("live git finalize requires a clean working tree")
    _git(repo_path, "commit", "--allow-empty", "-m", f"Finalize {logical_node_id}")
    final_commit_sha = _git_output(repo_path, "rev-parse", "HEAD")
    _clear_unreachable_recorded_final_commit(session_factory, version_id=version.id, repo_path=repo_path)
    record_final_commit(session_factory, version_id=version.id, commit_sha=final_commit_sha)
    _set_working_tree_state(session_factory, logical_node_id=logical_node_id, state="finalized_clean")
    _record_live_git_event(
        session_factory,
        logical_node_id=logical_node_id,
        node_version_id=version.id,
        event_type="git.finalize.completed",
        payload_json={"final_commit_sha": final_commit_sha},
    )
    return LiveFinalizeResultSnapshot(
        node_id=logical_node_id,
        node_version_id=version.id,
        status="finalized",
        repo_path=str(repo_path),
        final_commit_sha=final_commit_sha,
        working_tree_state="finalized_clean",
    )


def finalize_live_git_state_for_version(
    session_factory: sessionmaker[Session],
    *,
    node_version_id: UUID,
) -> LiveFinalizeResultSnapshot:
    with query_session_scope(session_factory) as session:
        version = _require_version(session, node_version_id)
        repo_path = _repo_path(version.id)
        if not repo_path.exists():
            raise DaemonConflictError("live git repo has not been bootstrapped")
        if _git_output(repo_path, "status", "--porcelain"):
            raise DaemonConflictError("live git finalize requires a clean working tree")
    _git(repo_path, "commit", "--allow-empty", "-m", f"Finalize {version.logical_node_id}")
    final_commit_sha = _git_output(repo_path, "rev-parse", "HEAD")
    _clear_unreachable_recorded_final_commit(session_factory, version_id=node_version_id, repo_path=repo_path)
    record_final_commit(session_factory, version_id=node_version_id, commit_sha=final_commit_sha)
    return LiveFinalizeResultSnapshot(
        node_id=version.logical_node_id,
        node_version_id=node_version_id,
        status="finalized",
        repo_path=str(repo_path),
        final_commit_sha=final_commit_sha,
        working_tree_state="finalized_clean",
    )


def show_live_git_status(session_factory: sessionmaker[Session], *, version_id: UUID) -> LiveGitStatusSnapshot:
    with query_session_scope(session_factory) as session:
        version = _require_version(session, version_id)
        branch_name = _require_branch_name(version)
        lifecycle = session.get(NodeLifecycleState, str(version.logical_node_id))
        working_tree_state = "uninitialized" if lifecycle is None or lifecycle.working_tree_state is None else lifecycle.working_tree_state
    repo_path = _repo_path(version.id)
    head = None
    if repo_path.exists() and (repo_path / ".git").exists():
        head = _git_output(repo_path, "rev-parse", "HEAD")
    return LiveGitStatusSnapshot(
        node_id=version.logical_node_id,
        node_version_id=version.id,
        repo_path=str(repo_path),
        branch_name=branch_name,
        head_commit_sha=head,
        seed_commit_sha=version.seed_commit_sha,
        final_commit_sha=version.final_commit_sha,
        working_tree_state=working_tree_state,
    )


def repo_path_for_version(version_id: UUID) -> Path:
    return Path.cwd() / ".runtime" / "git" / "node_versions" / str(version_id)


def _repo_path(version_id: UUID) -> Path:
    return repo_path_for_version(version_id)


def _clear_unreachable_recorded_final_commit(
    session_factory: sessionmaker[Session],
    *,
    version_id: UUID,
    repo_path: Path,
) -> None:
    with session_scope(session_factory) as session:
        version = _require_version(session, version_id)
        if version.final_commit_sha is None:
            return
        if _git_try(repo_path, "cat-file", "-e", f"{version.final_commit_sha}^{{commit}}").ok:
            return
        version.final_commit_sha = None
        session.flush()


def _require_source_repo_head(source_repo_path: Path) -> str:
    if not source_repo_path.exists() or not source_repo_path.is_dir():
        raise DaemonConflictError("selected source repo directory does not exist")
    if not (source_repo_path / ".git").exists():
        raise DaemonConflictError("selected source repo is not a git repository")
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=source_repo_path,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise DaemonConflictError(
            result.stderr.strip() or result.stdout.strip() or "selected source repo does not have a readable HEAD commit"
        )
    return result.stdout.strip()


def _git(repo_path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise DaemonConflictError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


@dataclass(frozen=True, slots=True)
class _GitTryResult:
    ok: bool
    message: str


def _git_try(repo_path: Path, *args: str) -> _GitTryResult:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=False,
    )
    return _GitTryResult(
        ok=result.returncode == 0,
        message=result.stderr.strip() or result.stdout.strip(),
    )


def _git_output(repo_path: Path, *args: str) -> str:
    return _git(repo_path, *args)


def _require_version(session: Session, version_id: UUID) -> NodeVersion:
    version = session.get(NodeVersion, version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _require_branch_name(version: NodeVersion) -> str:
    if not version.active_branch_name:
        raise DaemonConflictError("node version has no active branch name")
    return version.active_branch_name


def _resolve_bootstrap_base_version(
    session: Session,
    version: NodeVersion,
    *,
    explicit_base_version_id: UUID | None,
) -> NodeVersion | None:
    base_version_id = explicit_base_version_id or version.parent_node_version_id
    if base_version_id is None:
        return None
    return _require_version(session, base_version_id)


def _load_authoritative_version_id(session_factory: sessionmaker[Session], logical_node_id: UUID) -> UUID:
    with query_session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        return selector.authoritative_node_version_id


def _set_working_tree_state(session_factory: sessionmaker[Session], *, logical_node_id: UUID, state: str) -> None:
    with session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
        if lifecycle is None:
            lifecycle = NodeLifecycleState(
                node_id=str(logical_node_id),
                node_version_id=None if selector is None else selector.authoritative_node_version_id,
                lifecycle_state="DRAFT",
                working_tree_state=state,
            )
            session.add(lifecycle)
        else:
            if selector is not None:
                lifecycle.node_version_id = selector.authoritative_node_version_id
            lifecycle.working_tree_state = state
        session.flush()


def _record_live_git_event(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    node_version_id: UUID,
    event_type: str,
    payload_json: dict[str, object],
) -> None:
    with session_scope(session_factory) as session:
        record_workflow_event(
            session,
            logical_node_id=logical_node_id,
            node_version_id=node_version_id,
            node_run_id=None,
            event_scope="git_runtime",
            event_type=event_type,
            payload_json=payload_json,
        )
