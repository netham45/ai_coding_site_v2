from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
import logging
from uuid import UUID

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from sqlalchemy import inspect

from aicoding.bootstrap import bootstrap_status
from aicoding.config import get_settings
from aicoding.daemon.auth import initialize_auth_context, require_bearer_token
from aicoding.daemon.admission import (
    add_node_dependency,
    admit_node_run,
    check_node_dependency_readiness,
    list_node_blockers,
    list_node_dependencies,
    validate_node_dependency_graph,
)
from aicoding.daemon.actions import list_node_actions
from aicoding.daemon.background import BackgroundTaskRegistry
from aicoding.daemon.branches import (
    load_node_branch_metadata,
    load_node_version_branch_metadata,
    record_final_commit,
    record_seed_commit,
)
from aicoding.daemon.child_reconcile import collect_child_results, inspect_parent_reconcile
from aicoding.daemon.child_sessions import load_child_session_result, pop_child_session, push_child_session
from aicoding.daemon.history import get_prompt_record, get_summary_record, list_prompt_history, list_summary_history
from aicoding.daemon.interventions import apply_node_intervention, list_node_interventions
from aicoding.daemon.live_git import (
    abort_live_merge,
    bootstrap_live_git_repo,
    execute_live_merge_children,
    finalize_live_git_state,
    show_live_git_status,
)
from aicoding.daemon.database import durable_write_probe
from aicoding.daemon.docs_runtime import build_node_docs, build_tree_docs, list_docs_for_node, show_docs_for_node
from aicoding.daemon.environments import load_attempt_environment, load_current_subtask_environment, list_environment_policies
from aicoding.daemon.git_conflicts import (
    list_merge_conflicts_for_node,
    list_merge_conflicts_for_version,
    list_merge_events_for_node,
    record_merge_conflict,
    resolve_merge_conflict,
)
from aicoding.daemon.dependencies import (
    ensure_database_available,
    get_auth_context_dependency,
    get_background_registry,
    get_db_engine,
    get_db_session_factory,
    get_hierarchy_registry,
    get_resource_catalog,
    get_session_adapter,
    get_session_poller,
    get_settings_dependency,
)
from aicoding.daemon.errors import DaemonConflictError, DaemonUnavailableError
from aicoding.daemon.frontend_runtime import serve_frontend_asset, serve_frontend_index
from aicoding.daemon.regeneration import (
    list_rebuild_events_for_node,
    rectify_upstream,
    regenerate_node_and_descendants,
)
from aicoding.daemon.quality_chain import run_turnkey_quality_chain
from aicoding.daemon.projects import (
    build_project_catalog_daemon_context,
    list_projects,
    load_project_bootstrap,
    start_project_top_level_workflow,
)
from aicoding.daemon.rebuild_coordination import inspect_cutover_readiness, inspect_rebuild_coordination
from aicoding.daemon.reproducibility import load_node_audit_snapshot, load_run_audit_snapshot
from aicoding.daemon.review_runtime import (
    list_review_results_for_node,
    load_review_summary_for_node,
    load_review_summary_for_run,
)
from aicoding.daemon.testing_runtime import (
    evaluate_testing_subtask,
    list_test_results_for_node,
    load_testing_summary_for_node,
    load_testing_summary_for_run,
)
from aicoding.daemon.workflow_start import start_top_level_workflow
from aicoding.daemon.validation_runtime import (
    evaluate_validation_subtask,
    list_validation_results_for_node,
    load_validation_summary_for_node,
    load_validation_summary_for_run,
)
from aicoding.daemon.session_records import auto_nudge_idle_primary_sessions
from aicoding.daemon.models import (
    ApiErrorResponse,
    AuthContextResponse,
    ChildSessionPopRequest,
    ChildSessionPushRequest,
    ChildSessionResponse,
    ChildSessionResultResponse,
    ChildReconciliationRequest,
    ChildReconciliationResponse,
    ChildResultCollectionResponse,
    ChildFailureCounterCatalogResponse,
    CompositeStageOutcomeResponse,
    CommitRecordRequest,
    CompiledWorkflowResponse,
    CompileFailureCatalogResponse,
    DaemonStatusResponse,
    DependencyBlockerResponse,
    DependencyReadinessResponse,
    DependencyValidationResponse,
    DocumentationBuildResponse,
    DocumentationCatalogResponse,
    DocumentationOutputResponse,
    EffectivePolicyResponse,
    EnvironmentPolicyCatalogResponse,
    EnvironmentPolicyResponse,
    AttemptEnvironmentResponse,
    CurrentSubtaskEnvironmentResponse,
    EntityCatalogResponse,
    EntityHistoryCatalogResponse,
    EntityHistoryEntryResponse,
    EntityRelationCatalogResponse,
    EntityRelationResponse,
    EntityResponse,
    GitBranchResponse,
    HealthResponse,
    HierarchyNodeResponse,
    InterventionActionResponse,
    InterventionApplyRequest,
    InterventionCatalogResponse,
    LiveGitFinalizeResponse,
    LiveGitBootstrapRequest,
    LiveGitStatusResponse,
    MaterializationResponse,
    LayoutRegistrationRequest,
    LayoutRegistrationResponse,
    MergeConflictCatalogResponse,
    MergeConflictRecordRequest,
    MergeConflictResolveRequest,
    MergeConflictResponse,
    MergeEventCatalogResponse,
    MergeEventResponse,
    MutationAcceptedResponse,
    MutationEnvelope,
    PauseApprovalRequest,
    ParentDecisionCatalogResponse,
    ParentDecisionResponse,
    ParentFailureDecisionRequest,
    ParentFailureDecisionResponse,
    NodeCreateRequest,
    WorkflowStartRequest,
    NodeDependencyCatalogResponse,
    NodeDependencyCreateRequest,
    NodeDependencyResponse,
    NodeEventCatalogResponse,
    NodeEventResponse,
    NodeKindCatalogResponse,
    NodeKindDefinitionResponse,
    NodeAuthorityStateResponse,
    NodeAuditResponse,
    NodeActionCatalogResponse,
    NodeLineageResponse,
    NodeOperatorSummaryResponse,
    NodePauseStateResponse,
    NodeCursorUpdateRequest,
    NodeLifecycleStateResponse,
    NodeLifecycleTransitionRequest,
    NodeSupersedeRequest,
    NodeVersionSourceLineageResponse,
    NodeVersionCatalogResponse,
    NodeVersionResponse,
    NodeRunAdmissionResponse,
    NodeRunCatalogResponse,
    NodeRunResponse,
    RunAuditResponse,
    ParentReconcileResponse,
    PromptHistoryCatalogResponse,
    PromptHistoryRecordResponse,
    QualityChainResponse,
    RebuildCoordinationResponse,
    ProvenanceRefreshResponse,
    RationaleResponse,
    RunProgressResponse,
    OverrideChainResponse,
    PolicyImpactResponse,
    ProjectCatalogEntryResponse,
    ProjectCatalogResponse,
    ProjectBootstrapResponse,
    ProjectPolicyCatalogResponse,
    ProjectPolicyResponse,
    ProjectRouteHintResponse,
    ProjectTopLevelNodeCreateRequest,
    ProjectTopLevelNodeCreateResponse,
    RebuildHistoryResponse,
    CutoverReadinessResponse,
    RebuildEventResponse,
    RegenerationResponse,
    ReviewResultCatalogResponse,
    ReviewRunRequest,
    ReviewSummaryResponse,
    ResolvedYamlCatalogResponse,
    SchemaCompatibilityResponse,
    ProviderSessionRecoveryActionResponse,
    ProviderSessionRecoveryStatusResponse,
    SessionNudgeResponse,
    SessionRecoveryActionResponse,
    SessionRecoveryStatusResponse,
    SessionStateResponse,
    SessionCatalogResponse,
    SessionAuditResponse,
    SessionEventCatalogResponse,
    SessionEventResponse,
    SubtaskAttemptCatalogResponse,
    SubtaskAttemptResponse,
    SubtaskContextResponse,
    SubtaskReportCommandRequest,
    SubtaskMutationRequest,
    SubtaskPromptResponse,
    SubtaskSucceedRequest,
    SummaryRegistrationRequest,
    SummaryRegistrationResponse,
    SummaryHistoryCatalogResponse,
    SummaryHistoryRecordResponse,
    TestResultCatalogResponse,
    TestResultResponse,
    TestingSummaryResponse,
    ValidationResultCatalogResponse,
    ValidationResultResponse,
    ValidationSummaryResponse,
    TreeCatalogResponse,
    TreeNodeResponse,
    WorkflowChainResponse,
    WorkflowCompileAttemptResponse,
    WorkflowStartResponse,
    WorkflowEventResponse,
    WorkflowHookCatalogResponse,
    YamlSchemaCatalogResponse,
    YamlValidationRequest,
    YamlValidationResponse,
)
from aicoding.project_policies import list_project_policies, policy_impact_for_node_kind, resolve_effective_policy
from aicoding.daemon.hierarchy import get_hierarchy_node, list_ancestors, list_children, sync_hierarchy_definitions
from aicoding.daemon.lifecycle import load_node_lifecycle, transition_node_lifecycle, update_node_cursor
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.materialization import (
    inspect_child_reconciliation,
    inspect_materialized_children,
    materialize_layout_children,
    register_generated_layout,
    reconcile_child_authority,
)
from aicoding.daemon.orchestration import apply_authority_mutation, load_authority_state
from aicoding.daemon.parent_failures import handle_child_failure_at_parent, list_child_failure_counters, list_parent_decision_history
from aicoding.daemon.provenance import (
    refresh_node_provenance,
    show_entity_by_name,
    show_entity_history,
    show_entity_relations,
    show_node_rationale,
)
from aicoding.daemon.operator_views import (
    list_node_events,
    list_sibling_nodes,
    load_node_operator_summary,
    load_pause_state,
    load_tree_catalog,
)
from aicoding.daemon.run_orchestration import (
    approve_paused_run,
    advance_workflow,
    cancel_active_run,
    complete_current_subtask,
    fail_current_subtask,
    heartbeat_current_subtask,
    list_node_runs,
    list_subtask_attempts_for_node,
    load_current_subtask_context,
    load_current_subtask_prompt,
    load_current_run_progress,
    load_subtask_attempt,
    report_command_subtask,
    register_summary,
    retry_current_subtask,
    succeed_current_subtask,
    start_subtask_attempt,
    sync_paused_run,
    sync_resumed_run,
)
from aicoding.daemon.session_harness import SessionPoller, build_session_adapter
from aicoding.daemon.session_records import (
    attach_primary_session,
    auto_advance_incremental_parent_merge_and_refresh_children,
    auto_bind_ready_child_runs,
    bind_primary_session,
    get_session_by_id,
    get_session_for_node,
    list_session_events,
    list_sessions_for_node,
    load_provider_recovery_status,
    load_recovery_status,
    nudge_primary_session,
    recover_primary_session_provider_specific,
    recover_primary_session,
    resume_primary_session,
    show_current_primary_session,
)
from aicoding.daemon.versioning import (
    create_superseding_node_version,
    cutover_candidate_version,
    list_node_versions,
    load_node_lineage,
    load_node_version,
)
from aicoding.daemon.workflows import (
    compile_node_workflow,
    compile_node_version_workflow,
    list_compile_failures_for_node,
    list_compile_failures_for_version,
    list_compile_failures_for_workflow,
    load_current_workflow,
    load_node_version_workflow,
    load_workflow_hook_policy,
    load_workflow_hook_policy_for_node,
    load_workflow_hook_policy_for_version,
    load_override_chain,
    load_override_chain_for_node,
    load_workflow_override_resolution,
    load_workflow_override_resolution_for_node,
    load_workflow_override_resolution_for_version,
    load_resolved_yaml,
    load_resolved_yaml_for_node,
    load_resolved_yaml_for_version,
    load_workflow,
    load_workflow_chain,
    load_workflow_chain_for_node,
    load_workflow_chain_for_version,
    load_workflow_hooks,
    load_workflow_hooks_for_node,
    load_workflow_hooks_for_version,
    load_workflow_source_discovery,
    load_workflow_source_discovery_for_node,
    load_workflow_source_discovery_for_version,
    load_workflow_schema_validation,
    load_workflow_schema_validation_for_node,
    load_workflow_schema_validation_for_version,
    load_workflow_sources,
    load_workflow_sources_for_node,
    load_workflow_sources_for_version,
    load_workflow_rendering,
    load_workflow_rendering_for_node,
    load_workflow_rendering_for_version,
)
from aicoding.db.bootstrap import database_status
from aicoding.db.migrations import migration_status
from aicoding.db.session import create_engine_from_settings, create_session_factory
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.logging import configure_logging
from aicoding.resources import load_resource_catalog
from aicoding.source_lineage import capture_node_version_source_lineage, load_node_version_source_lineage
from aicoding.yaml_schemas import persist_yaml_validation_report, schema_family_descriptors, validate_yaml_document

logger = logging.getLogger(__name__)


def _session_state_response(snapshot) -> SessionStateResponse:
    return SessionStateResponse.model_validate(
        {
            "backend": snapshot.backend,
            "session_name": snapshot.tmux_session_name,
            "status": snapshot.status.lower(),
            "session_id": str(snapshot.session_id),
            "logical_node_id": str(snapshot.logical_node_id),
            "node_run_id": None if snapshot.node_run_id is None else str(snapshot.node_run_id),
            "node_version_id": str(snapshot.node_version_id),
            "node_kind": snapshot.node_kind,
            "node_title": snapshot.node_title,
            "run_status": snapshot.run_status,
            "session_role": snapshot.session_role,
            "provider": snapshot.provider,
            "provider_session_id": snapshot.provider_session_id,
            "cwd": snapshot.cwd,
            "tmux_session_exists": snapshot.tmux_session_exists,
            "attach_command": snapshot.attach_command,
            "last_heartbeat_at": snapshot.last_heartbeat_at,
            "event_count": snapshot.event_count,
            "latest_event_type": snapshot.latest_event_type,
            "recovery_classification": snapshot.recovery_classification,
            "pane_text": snapshot.pane_text,
            "idle_seconds": snapshot.idle_seconds,
            "in_alt_screen": snapshot.in_alt_screen,
            "screen_state": snapshot.screen_state,
            "recommended_action": snapshot.recommended_action,
        }
    )


def _database_has_required_tables(engine, table_names: tuple[str, ...]) -> bool:
    inspector = inspect(engine)
    return all(inspector.has_table(name) for name in table_names)


async def _run_idle_nudge_background_loop(app: FastAPI) -> None:
    settings = app.state.settings
    idle_nudge_prompt = app.state.resource_catalog.load_text("prompt_pack_default", "recovery/idle_nudge.md").content
    repeated_nudge_prompt = app.state.resource_catalog.load_text("prompt_pack_default", "recovery/repeated_missed_step.md").content
    required_tables = ("node_versions", "sessions", "node_runs")
    while True:
        try:
            if _database_has_required_tables(app.state.db_engine, required_tables):
                auto_nudge_idle_primary_sessions(
                    app.state.db_session_factory,
                    adapter=app.state.session_adapter,
                    poller=app.state.session_poller,
                    max_nudge_count=settings.session.max_nudge_count,
                    idle_nudge_text=idle_nudge_prompt,
                    repeated_nudge_text=repeated_nudge_prompt,
                )
        except Exception:
            logger.exception("Idle nudge background loop iteration failed.")
        await asyncio.sleep(settings.session.poll_interval_seconds)


async def _run_child_auto_start_background_loop(app: FastAPI) -> None:
    settings = app.state.settings
    required_tables = (
        "logical_node_current_versions",
        "node_children",
        "hierarchy_nodes",
        "parent_incremental_merge_lanes",
        "incremental_child_merge_state",
        "node_dependency_blockers",
    )
    while True:
        try:
            if _database_has_required_tables(app.state.db_engine, required_tables):
                auto_advance_incremental_parent_merge_and_refresh_children(
                    app.state.db_session_factory,
                    hierarchy_registry=app.state.hierarchy_registry,
                    resources=app.state.resource_catalog,
                )
                auto_bind_ready_child_runs(
                    app.state.db_session_factory,
                    hierarchy_registry=app.state.hierarchy_registry,
                    resources=app.state.resource_catalog,
                    adapter=app.state.session_adapter,
                    poller=app.state.session_poller,
                )
        except Exception:
            logger.exception("Child auto-start background loop iteration failed.")
        await asyncio.sleep(settings.session.poll_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    engine = create_engine_from_settings()
    app.state.settings = settings
    app.state.auth_context = initialize_auth_context(settings)
    app.state.db_engine = engine
    app.state.db_session_factory = create_session_factory(engine=engine)
    app.state.resource_catalog = load_resource_catalog(settings)
    app.state.hierarchy_registry = load_hierarchy_registry(app.state.resource_catalog)
    app.state.background_registry = BackgroundTaskRegistry()
    app.state.session_adapter = build_session_adapter(settings)
    app.state.session_poller = SessionPoller(
        adapter=app.state.session_adapter,
        idle_threshold_seconds=settings.session_idle_threshold_seconds,
        now=app.state.session_adapter.now if getattr(app.state.session_adapter, "backend_name", "") == "fake" else (lambda: datetime.now(timezone.utc)),
    )
    app.state.background_registry.register_placeholder("session_recovery")
    app.state.background_registry.register_placeholder("idle_screen_polling")
    app.state.background_registry.register_placeholder("idle_nudge")
    app.state.background_registry.register_placeholder("child_auto_run")
    schema_status = migration_status(engine)
    if schema_status["compatible"] and inspect(engine).has_table("node_hierarchy_definitions"):
        sync_hierarchy_definitions(app.state.db_session_factory, app.state.hierarchy_registry)
    idle_nudge_task = asyncio.create_task(_run_idle_nudge_background_loop(app), name="aicoding-idle-nudge-loop")
    child_auto_start_task = asyncio.create_task(_run_child_auto_start_background_loop(app), name="aicoding-child-auto-start-loop")
    try:
        yield
    finally:
        child_auto_start_task.cancel()
        with suppress(asyncio.CancelledError):
            await child_auto_start_task
        idle_nudge_task.cancel()
        with suppress(asyncio.CancelledError):
            await idle_nudge_task
        engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.daemon_app_name, version="0.1.0", lifespan=lifespan)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ApiErrorResponse(error="request_validation_failed", message="Request validation failed.").model_dump()
            | {"details": exc.errors()},
        )

    @app.exception_handler(DaemonUnavailableError)
    async def daemon_unavailable_handler(request: Request, exc: DaemonUnavailableError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiErrorResponse(error="daemon_unavailable", message=str(exc.detail)).model_dump(),
        )

    @app.get("/healthz")
    def healthcheck() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/assets/{asset_path:path}", include_in_schema=False)
    def frontend_asset(asset_path: str) -> Response:
        return serve_frontend_asset(asset_path)

    @app.get("/bootstrap", dependencies=[Depends(require_bearer_token)])
    def bootstrap() -> dict[str, object]:
        return bootstrap_status()

    @app.get("/db/healthz", dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)])
    def db_healthcheck(engine=Depends(get_db_engine)) -> dict[str, object]:
        return database_status(engine)

    @app.get(
        "/db/schema-compatibility",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SchemaCompatibilityResponse,
    )
    def db_schema_compatibility(engine=Depends(get_db_engine)) -> SchemaCompatibilityResponse:
        return SchemaCompatibilityResponse.model_validate(migration_status(engine))

    @app.get("/foundation", dependencies=[Depends(require_bearer_token)])
    def foundation_status(
        request: Request,
        settings=Depends(get_settings_dependency),
        auth_context=Depends(get_auth_context_dependency),
        hierarchy_registry=Depends(get_hierarchy_registry),
        resources=Depends(get_resource_catalog),
    ) -> dict[str, object]:
        return {
            "app_name": settings.daemon_app_name,
            "log_level": settings.normalized_log_level,
            "resource_groups": sorted(resources.group_paths().keys()),
            "db_pool_class": request.app.state.db_engine.pool.__class__.__name__,
            "session_backend": request.app.state.session_adapter.backend_name,
            "auth_token_file": auth_context.token_file,
            "auth_token_source": auth_context.token_source,
            "node_kinds": sorted(hierarchy_registry.definitions.keys()),
        }

    @app.get("/status", dependencies=[Depends(require_bearer_token)])
    def daemon_status(
        registry=Depends(get_background_registry),
        session_factory=Depends(get_db_session_factory),
        engine=Depends(get_db_engine),
    ) -> DaemonStatusResponse:
        write_probe = durable_write_probe(session_factory)
        return DaemonStatusResponse(
            status="ok",
            authority="daemon",
            background_tasks=registry.snapshot(),
            write_probe=write_probe,
            schema_compatibility=SchemaCompatibilityResponse.model_validate(migration_status(engine)),
            session_backend=app.state.session_adapter.backend_name if hasattr(app, "state") else "unknown",
        )

    @app.get("/api/yaml/schema-families", dependencies=[Depends(require_bearer_token)], response_model=YamlSchemaCatalogResponse)
    def list_yaml_schema_families() -> YamlSchemaCatalogResponse:
        return YamlSchemaCatalogResponse(definitions=[item.model_dump() for item in schema_family_descriptors()])

    @app.get(
        "/api/policies/project",
        dependencies=[Depends(require_bearer_token)],
        response_model=ProjectPolicyCatalogResponse,
    )
    def show_project_policies(
        resources=Depends(get_resource_catalog),
        hierarchy_registry=Depends(get_hierarchy_registry),
    ) -> ProjectPolicyCatalogResponse:
        policies = list_project_policies(resources, hierarchy_registry=hierarchy_registry)
        return ProjectPolicyCatalogResponse(policies=[ProjectPolicyResponse.model_validate(item.to_payload()) for item in policies])

    @app.get(
        "/api/policies/effective",
        dependencies=[Depends(require_bearer_token)],
        response_model=EffectivePolicyResponse,
    )
    def show_effective_policy(
        resources=Depends(get_resource_catalog),
        hierarchy_registry=Depends(get_hierarchy_registry),
    ) -> EffectivePolicyResponse:
        return EffectivePolicyResponse.model_validate(resolve_effective_policy(resources, hierarchy_registry=hierarchy_registry).to_payload())

    @app.get(
        "/api/policies/environments",
        dependencies=[Depends(require_bearer_token)],
        response_model=EnvironmentPolicyCatalogResponse,
    )
    def show_environment_policies(resources=Depends(get_resource_catalog)) -> EnvironmentPolicyCatalogResponse:
        policies = list_environment_policies(resources)
        return EnvironmentPolicyCatalogResponse(
            policies=[EnvironmentPolicyResponse.model_validate(item.to_payload()) for item in policies]
        )

    @app.get(
        "/api/policies/impact/{node_kind}",
        dependencies=[Depends(require_bearer_token)],
        response_model=PolicyImpactResponse,
    )
    def show_policy_impact(
        node_kind: str,
        resources=Depends(get_resource_catalog),
        hierarchy_registry=Depends(get_hierarchy_registry),
    ) -> PolicyImpactResponse:
        return PolicyImpactResponse.model_validate(
            policy_impact_for_node_kind(node_kind, resources, hierarchy_registry=hierarchy_registry).to_payload()
        )

    @app.post(
        "/api/yaml/validate",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=YamlValidationResponse,
    )
    def validate_yaml_document_endpoint(
        payload: YamlValidationRequest,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
    ) -> YamlValidationResponse:
        report = validate_yaml_document(resources, source_group=payload.source_group, relative_path=payload.relative_path)
        persist_yaml_validation_report(session_factory, report)
        return YamlValidationResponse.model_validate(report.model_dump())

    @app.get(
        "/api/sessions/show-current",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionStateResponse,
    )
    def show_current_session(
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> SessionStateResponse:
        snapshot = show_current_primary_session(session_factory, adapter=adapter, poller=poller)
        if snapshot is None:
            return SessionStateResponse(
                backend=adapter.backend_name,
                session_name=None,
                status="none",
            )
        return _session_state_response(snapshot)

    @app.get(
        "/api/sessions/{session_id}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionStateResponse,
    )
    def show_session_by_id(
        session_id: str,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> SessionStateResponse:
        snapshot = get_session_by_id(session_factory, session_id=UUID(session_id), adapter=adapter, poller=poller)
        return _session_state_response(snapshot)

    @app.get(
        "/api/nodes/{node_id}/sessions/current",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionStateResponse,
    )
    def show_session_for_node(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> SessionStateResponse:
        snapshot = get_session_for_node(session_factory, logical_node_id=UUID(node_id), adapter=adapter, poller=poller)
        return _session_state_response(snapshot)

    @app.get(
        "/api/nodes/{node_id}/sessions",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionCatalogResponse,
    )
    def list_sessions_for_node_endpoint(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> SessionCatalogResponse:
        snapshot = list_sessions_for_node(session_factory, logical_node_id=UUID(node_id), adapter=adapter, poller=poller)
        return SessionCatalogResponse(
            node_id=node_id,
            sessions=[_session_state_response(item) for item in snapshot.sessions],
        )

    @app.get(
        "/api/sessions/{session_id}/events",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionEventCatalogResponse,
    )
    def show_session_events(
        session_id: str,
        session_factory=Depends(get_db_session_factory),
    ) -> SessionEventCatalogResponse:
        events = list_session_events(session_factory, session_id=UUID(session_id))
        return SessionEventCatalogResponse(
            session_id=session_id,
            events=[SessionEventResponse.model_validate(item.to_payload()) for item in events],
        )

    @app.post(
        "/api/sessions/bind",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionStateResponse,
    )
    def bind_session(
        payload: MutationEnvelope,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> SessionStateResponse:
        snapshot = bind_primary_session(session_factory, logical_node_id=UUID(payload.node_id), adapter=adapter, poller=poller)
        return _session_state_response(snapshot)

    @app.post(
        "/api/sessions/attach",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionStateResponse,
    )
    def attach_session(
        payload: MutationEnvelope,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> SessionStateResponse:
        snapshot = attach_primary_session(session_factory, logical_node_id=UUID(payload.node_id), adapter=adapter, poller=poller)
        return _session_state_response(snapshot)

    @app.post(
        "/api/sessions/resume",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionRecoveryActionResponse,
    )
    def resume_session(
        payload: MutationEnvelope,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> SessionRecoveryActionResponse:
        decision = recover_primary_session(session_factory, logical_node_id=UUID(payload.node_id), adapter=adapter, poller=poller)
        return SessionRecoveryActionResponse.model_validate(
            {
                "status": decision.status,
                "recovery_status": decision.recovery_status.to_payload(),
                "session": None if decision.session is None else _session_state_response(decision.session).model_dump(),
            }
        )

    @app.post(
        "/api/sessions/provider-resume",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ProviderSessionRecoveryActionResponse,
    )
    def provider_resume_session(
        payload: MutationEnvelope,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> ProviderSessionRecoveryActionResponse:
        decision = recover_primary_session_provider_specific(
            session_factory,
            logical_node_id=UUID(payload.node_id),
            adapter=adapter,
            poller=poller,
        )
        return ProviderSessionRecoveryActionResponse.model_validate(
            {
                "status": decision.status,
                "provider_recovery_status": decision.provider_recovery_status.to_payload(),
                "recovery_status": decision.recovery_status.to_payload(),
                "session": None if decision.session is None else _session_state_response(decision.session).model_dump(),
            }
        )

    @app.post(
        "/api/sessions/nudge",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionNudgeResponse,
    )
    def nudge_session(
        payload: MutationEnvelope,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
        resources=Depends(get_resource_catalog),
        settings=Depends(get_settings_dependency),
    ) -> SessionNudgeResponse:
        idle_nudge_prompt = resources.load_text("prompt_pack_default", "recovery/idle_nudge.md").content
        repeated_nudge_prompt = resources.load_text("prompt_pack_default", "recovery/repeated_missed_step.md").content
        snapshot = nudge_primary_session(
            session_factory,
            logical_node_id=UUID(payload.node_id),
            adapter=adapter,
            poller=poller,
            max_nudge_count=settings.session.max_nudge_count,
            idle_nudge_text=idle_nudge_prompt,
            repeated_nudge_text=repeated_nudge_prompt,
        )
        return SessionNudgeResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/sessions/push",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ChildSessionResponse,
    )
    def push_session(
        payload: ChildSessionPushRequest,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
        resources=Depends(get_resource_catalog),
    ) -> ChildSessionResponse:
        prompt = resources.load_text("prompt_pack_default", "runtime/delegated_child_session.md").content
        snapshot = push_child_session(
            session_factory,
            logical_node_id=UUID(payload.node_id),
            reason=payload.reason,
            adapter=adapter,
            poller=poller,
            delegated_prompt_text=prompt,
            delegated_prompt_path="runtime/delegated_child_session.md",
        )
        return ChildSessionResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/sessions/pop",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ChildSessionResultResponse,
    )
    def pop_session(
        payload: ChildSessionPopRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> ChildSessionResultResponse:
        snapshot = pop_child_session(session_factory, child_session_id=UUID(payload.session_id), result_payload=payload.model_dump())
        return ChildSessionResultResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/sessions/{session_id}/result",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ChildSessionResultResponse,
    )
    def show_child_session_result(
        session_id: str,
        session_factory=Depends(get_db_session_factory),
    ) -> ChildSessionResultResponse:
        snapshot = load_child_session_result(session_factory, child_session_id=UUID(session_id))
        return ChildSessionResultResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/nodes/{node_id}/recovery-status",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SessionRecoveryStatusResponse,
    )
    def show_recovery_status(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> SessionRecoveryStatusResponse:
        snapshot = load_recovery_status(session_factory, logical_node_id=UUID(node_id), adapter=adapter, poller=poller)
        return SessionRecoveryStatusResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/nodes/{node_id}/recovery-provider-status",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ProviderSessionRecoveryStatusResponse,
    )
    def show_provider_recovery_status(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> ProviderSessionRecoveryStatusResponse:
        snapshot = load_provider_recovery_status(
            session_factory,
            logical_node_id=UUID(node_id),
            adapter=adapter,
            poller=poller,
        )
        return ProviderSessionRecoveryStatusResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/node-runs/start",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeRunAdmissionResponse,
    )
    def start_node_run(payload: MutationEnvelope, session_factory=Depends(get_db_session_factory)) -> NodeRunAdmissionResponse:
        snapshot = admit_node_run(session_factory, node_id=UUID(payload.node_id))
        return NodeRunAdmissionResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/nodes/dependencies/add",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeDependencyResponse,
    )
    def create_node_dependency(
        payload: NodeDependencyCreateRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> NodeDependencyResponse:
        snapshot = add_node_dependency(
            session_factory,
            node_id=UUID(payload.node_id),
            depends_on_node_id=UUID(payload.depends_on_node_id),
            required_state=payload.required_state,
        )
        return NodeDependencyResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/nodes/{node_id}/dependencies",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeDependencyCatalogResponse,
    )
    def show_node_dependencies(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeDependencyCatalogResponse:
        dependencies = list_node_dependencies(session_factory, node_id=UUID(node_id))
        validation = validate_node_dependency_graph(session_factory, node_id=UUID(node_id))
        return NodeDependencyCatalogResponse(
            node_id=node_id,
            node_version_id=str(validation.node_version_id),
            dependencies=[item.to_payload() for item in dependencies],
        )

    @app.get(
        "/api/nodes/{node_id}/dependency-status",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=DependencyReadinessResponse,
    )
    def show_node_dependency_status(node_id: str, session_factory=Depends(get_db_session_factory)) -> DependencyReadinessResponse:
        return DependencyReadinessResponse.model_validate(
            check_node_dependency_readiness(session_factory, node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/dependency-validate",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=DependencyValidationResponse,
    )
    def validate_node_dependencies(node_id: str, session_factory=Depends(get_db_session_factory)) -> DependencyValidationResponse:
        return DependencyValidationResponse.model_validate(
            validate_node_dependency_graph(session_factory, node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/blockers",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=list[DependencyBlockerResponse],
    )
    def show_node_blockers(node_id: str, session_factory=Depends(get_db_session_factory)) -> list[DependencyBlockerResponse]:
        return [DependencyBlockerResponse.model_validate(item.to_payload()) for item in list_node_blockers(session_factory, node_id=UUID(node_id))]

    @app.get(
        "/api/nodes/{node_id}/git/branch",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=GitBranchResponse,
    )
    def show_node_branch_metadata(node_id: str, session_factory=Depends(get_db_session_factory)) -> GitBranchResponse:
        return GitBranchResponse.model_validate(load_node_branch_metadata(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/node-versions/{version_id}/git/branch",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=GitBranchResponse,
    )
    def show_node_version_branch_metadata(version_id: str, session_factory=Depends(get_db_session_factory)) -> GitBranchResponse:
        return GitBranchResponse.model_validate(
            load_node_version_branch_metadata(session_factory, version_id=UUID(version_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/git/merge-events",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MergeEventCatalogResponse,
    )
    def show_merge_events_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> MergeEventCatalogResponse:
        events = list_merge_events_for_node(session_factory, logical_node_id=UUID(node_id))
        return MergeEventCatalogResponse(
            node_id=node_id,
            events=[MergeEventResponse.model_validate(item.to_payload()) for item in events],
        )

    @app.get(
        "/api/nodes/{node_id}/git/merge-conflicts",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MergeConflictCatalogResponse,
    )
    def show_merge_conflicts_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> MergeConflictCatalogResponse:
        conflicts = list_merge_conflicts_for_node(session_factory, logical_node_id=UUID(node_id))
        return MergeConflictCatalogResponse(
            node_id=node_id,
            conflicts=[MergeConflictResponse.model_validate(item.to_payload()) for item in conflicts],
        )

    @app.get(
        "/api/node-versions/{version_id}/git/merge-conflicts",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MergeConflictCatalogResponse,
    )
    def show_merge_conflicts_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> MergeConflictCatalogResponse:
        conflicts = list_merge_conflicts_for_version(session_factory, node_version_id=UUID(version_id))
        return MergeConflictCatalogResponse(
            node_version_id=version_id,
            conflicts=[MergeConflictResponse.model_validate(item.to_payload()) for item in conflicts],
        )

    @app.post(
        "/api/git/merge-conflicts/record",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MergeConflictResponse,
    )
    def record_merge_conflict_endpoint(
        payload: MergeConflictRecordRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> MergeConflictResponse:
        snapshot = record_merge_conflict(
            session_factory,
            parent_node_version_id=UUID(payload.parent_node_version_id),
            child_node_version_id=UUID(payload.child_node_version_id),
            child_final_commit_sha=payload.child_final_commit_sha,
            parent_commit_before=payload.parent_commit_before,
            parent_commit_after=payload.parent_commit_after,
            merge_order=payload.merge_order,
            files_json=payload.files_json,
            merge_base_sha=payload.merge_base_sha,
        )
        return MergeConflictResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/git/merge-conflicts/{conflict_id}/resolve",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MergeConflictResponse,
    )
    def resolve_merge_conflict_endpoint(
        conflict_id: str,
        payload: MergeConflictResolveRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> MergeConflictResponse:
        snapshot = resolve_merge_conflict(
            session_factory,
            conflict_id=UUID(conflict_id),
            resolution_summary=payload.resolution_summary,
            resolution_status=payload.resolution_status,
        )
        return MergeConflictResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/node-versions/{version_id}/git/seed",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=GitBranchResponse,
    )
    def set_node_version_seed_commit(
        version_id: str,
        payload: CommitRecordRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> GitBranchResponse:
        return GitBranchResponse.model_validate(
            record_seed_commit(session_factory, version_id=UUID(version_id), commit_sha=payload.commit_sha).to_payload()
        )

    @app.post(
        "/api/node-versions/{version_id}/git/final",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=GitBranchResponse,
    )
    def set_node_version_final_commit(
        version_id: str,
        payload: CommitRecordRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> GitBranchResponse:
        return GitBranchResponse.model_validate(
            record_final_commit(session_factory, version_id=UUID(version_id), commit_sha=payload.commit_sha).to_payload()
        )

    @app.get(
        "/api/node-runs/{node_id}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def show_node_run(node_id: str, session_factory=Depends(get_db_session_factory)) -> RunProgressResponse:
        return RunProgressResponse.model_validate(load_current_run_progress(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/runs",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeRunCatalogResponse,
    )
    def show_node_runs(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeRunCatalogResponse:
        runs = list_node_runs(session_factory, logical_node_id=UUID(node_id))
        return NodeRunCatalogResponse(node_id=node_id, runs=[NodeRunResponse.model_validate(item.to_payload()) for item in runs])

    @app.get(
        "/api/nodes/{node_id}/audit",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeAuditResponse,
    )
    def show_node_audit(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeAuditResponse:
        return NodeAuditResponse.model_validate(load_node_audit_snapshot(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/node-runs/{run_id}/audit",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunAuditResponse,
    )
    def show_run_audit(run_id: str, session_factory=Depends(get_db_session_factory)) -> RunAuditResponse:
        return RunAuditResponse.model_validate(load_run_audit_snapshot(session_factory, node_run_id=UUID(run_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/runs/latest-audit",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunAuditResponse,
    )
    def show_latest_run_audit_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> RunAuditResponse:
        return RunAuditResponse.model_validate(load_run_audit_snapshot(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/subtasks/current",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def show_current_subtask(node_id: str, session_factory=Depends(get_db_session_factory)) -> RunProgressResponse:
        return RunProgressResponse.model_validate(load_current_run_progress(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/subtasks/current/prompt",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SubtaskPromptResponse,
    )
    def show_current_subtask_prompt(node_id: str, session_factory=Depends(get_db_session_factory)) -> SubtaskPromptResponse:
        return SubtaskPromptResponse.model_validate(load_current_subtask_prompt(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/subtasks/current/environment",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CurrentSubtaskEnvironmentResponse,
    )
    def show_current_subtask_environment(node_id: str, session_factory=Depends(get_db_session_factory)) -> CurrentSubtaskEnvironmentResponse:
        return CurrentSubtaskEnvironmentResponse.model_validate(
            load_current_subtask_environment(session_factory, logical_node_id=UUID(node_id))
        )

    @app.get(
        "/api/nodes/{node_id}/prompt-history",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=PromptHistoryCatalogResponse,
    )
    def show_prompt_history(node_id: str, session_factory=Depends(get_db_session_factory)) -> PromptHistoryCatalogResponse:
        snapshot = list_prompt_history(session_factory, logical_node_id=UUID(node_id))
        return PromptHistoryCatalogResponse(
            node_id=node_id,
            prompts=[PromptHistoryRecordResponse.model_validate(item.to_payload()) for item in snapshot.prompts],
        )

    @app.get(
        "/api/prompts/{prompt_id}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=PromptHistoryRecordResponse,
    )
    def show_prompt_record(prompt_id: str, session_factory=Depends(get_db_session_factory)) -> PromptHistoryRecordResponse:
        return PromptHistoryRecordResponse.model_validate(get_prompt_record(session_factory, prompt_id=UUID(prompt_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/subtasks/current/context",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SubtaskContextResponse,
    )
    def show_current_subtask_context(node_id: str, session_factory=Depends(get_db_session_factory)) -> SubtaskContextResponse:
        return SubtaskContextResponse.model_validate(load_current_subtask_context(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.post(
        "/api/subtasks/start",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def start_subtask(payload: SubtaskMutationRequest, session_factory=Depends(get_db_session_factory)) -> RunProgressResponse:
        return RunProgressResponse.model_validate(
            start_subtask_attempt(
                session_factory,
                logical_node_id=UUID(payload.node_id),
                compiled_subtask_id=UUID(payload.compiled_subtask_id),
            ).to_payload()
        )

    @app.post(
        "/api/subtasks/heartbeat",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def heartbeat_subtask(payload: SubtaskMutationRequest, session_factory=Depends(get_db_session_factory)) -> RunProgressResponse:
        return RunProgressResponse.model_validate(
            heartbeat_current_subtask(
                session_factory,
                logical_node_id=UUID(payload.node_id),
                compiled_subtask_id=UUID(payload.compiled_subtask_id),
            ).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/subtask-attempts",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SubtaskAttemptCatalogResponse,
    )
    def show_subtask_attempts_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> SubtaskAttemptCatalogResponse:
        node_run_id, attempts = list_subtask_attempts_for_node(session_factory, logical_node_id=UUID(node_id))
        return SubtaskAttemptCatalogResponse(
            node_id=node_id,
            node_run_id=str(node_run_id),
            attempts=[SubtaskAttemptResponse.model_validate(item.to_payload()) for item in attempts],
        )

    @app.get(
        "/api/subtask-attempts/{attempt_id}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SubtaskAttemptResponse,
    )
    def show_subtask_attempt(attempt_id: str, session_factory=Depends(get_db_session_factory)) -> SubtaskAttemptResponse:
        return SubtaskAttemptResponse.model_validate(load_subtask_attempt(session_factory, attempt_id=UUID(attempt_id)).to_payload())

    @app.post(
        "/api/subtasks/complete",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def complete_subtask(payload: SubtaskMutationRequest, session_factory=Depends(get_db_session_factory)) -> RunProgressResponse:
        return RunProgressResponse.model_validate(
            complete_current_subtask(
                session_factory,
                logical_node_id=UUID(payload.node_id),
                compiled_subtask_id=UUID(payload.compiled_subtask_id),
                output_json=payload.output_json,
                execution_result_json=payload.execution_result_json,
                summary=payload.summary,
            ).to_payload()
        )

    @app.post(
        "/api/subtasks/succeed",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CompositeStageOutcomeResponse,
    )
    def succeed_subtask(
        payload: SubtaskSucceedRequest,
        session_factory=Depends(get_db_session_factory),
        resource_catalog=Depends(get_resource_catalog),
    ) -> CompositeStageOutcomeResponse:
        return CompositeStageOutcomeResponse.model_validate(
            succeed_current_subtask(
                session_factory,
                logical_node_id=UUID(payload.node_id),
                compiled_subtask_id=UUID(payload.compiled_subtask_id),
                summary_path=payload.summary_path,
                content=payload.content,
                catalog=resource_catalog,
            ).to_payload()
        )

    @app.post(
        "/api/subtasks/report-command",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CompositeStageOutcomeResponse,
    )
    def report_command(
        payload: SubtaskReportCommandRequest,
        session_factory=Depends(get_db_session_factory),
        resource_catalog=Depends(get_resource_catalog),
    ) -> CompositeStageOutcomeResponse:
        return CompositeStageOutcomeResponse.model_validate(
            report_command_subtask(
                session_factory,
                logical_node_id=UUID(payload.node_id),
                compiled_subtask_id=UUID(payload.compiled_subtask_id),
                execution_result_json=payload.execution_result_json,
                failure_summary=payload.failure_summary,
                catalog=resource_catalog,
            ).to_payload()
        )

    @app.post(
        "/api/subtasks/fail",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def fail_subtask(payload: SubtaskMutationRequest, session_factory=Depends(get_db_session_factory)) -> RunProgressResponse:
        return RunProgressResponse.model_validate(
            fail_current_subtask(
                session_factory,
                logical_node_id=UUID(payload.node_id),
                compiled_subtask_id=UUID(payload.compiled_subtask_id),
                summary=payload.summary or "subtask failed",
                execution_result_json=payload.execution_result_json,
            ).to_payload()
        )

    @app.post(
        "/api/nodes/{node_id}/subtasks/retry",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def retry_subtask_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> RunProgressResponse:
        return RunProgressResponse.model_validate(
            retry_current_subtask(
                session_factory,
                logical_node_id=UUID(node_id),
            ).to_payload()
        )

    @app.post(
        "/api/subtask-attempts/{attempt_id}/retry",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def retry_subtask_by_attempt(attempt_id: str, session_factory=Depends(get_db_session_factory)) -> RunProgressResponse:
        return RunProgressResponse.model_validate(
            retry_current_subtask(
                session_factory,
                attempt_id=UUID(attempt_id),
            ).to_payload()
        )

    @app.get(
        "/api/subtask-attempts/{attempt_id}/environment",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=AttemptEnvironmentResponse,
    )
    def show_subtask_attempt_environment(attempt_id: str, session_factory=Depends(get_db_session_factory)) -> AttemptEnvironmentResponse:
        return AttemptEnvironmentResponse.model_validate(load_attempt_environment(session_factory, attempt_id=UUID(attempt_id)))

    @app.post(
        "/api/summaries/register",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SummaryRegistrationResponse,
    )
    def register_summary_endpoint(
        payload: SummaryRegistrationRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> SummaryRegistrationResponse:
        return SummaryRegistrationResponse.model_validate(
            register_summary(
                session_factory,
                logical_node_id=UUID(payload.node_id),
                summary_type=payload.summary_type,
                summary_path=payload.summary_path,
                content=payload.content,
            ).to_payload()
        )

    @app.post(
        "/api/nodes/{node_id}/docs/build-node-view",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=DocumentationBuildResponse,
    )
    def build_node_docs_endpoint(node_id: str, session_factory=Depends(get_db_session_factory)) -> DocumentationBuildResponse:
        snapshot = build_node_docs(session_factory, logical_node_id=UUID(node_id))
        return DocumentationBuildResponse(
            node_id=node_id,
            node_version_id=str(snapshot.node_version_id),
            mode=snapshot.mode,
            documents=[DocumentationOutputResponse.model_validate(item.to_payload()) for item in snapshot.documents],
        )

    @app.post(
        "/api/nodes/{node_id}/docs/build-tree",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=DocumentationBuildResponse,
    )
    def build_tree_docs_endpoint(node_id: str, session_factory=Depends(get_db_session_factory)) -> DocumentationBuildResponse:
        snapshot = build_tree_docs(session_factory, logical_node_id=UUID(node_id))
        return DocumentationBuildResponse(
            node_id=node_id,
            node_version_id=str(snapshot.node_version_id),
            mode=snapshot.mode,
            documents=[DocumentationOutputResponse.model_validate(item.to_payload()) for item in snapshot.documents],
        )

    @app.get(
        "/api/nodes/{node_id}/docs",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=DocumentationCatalogResponse,
    )
    def list_docs_endpoint(node_id: str, session_factory=Depends(get_db_session_factory)) -> DocumentationCatalogResponse:
        snapshot = list_docs_for_node(session_factory, logical_node_id=UUID(node_id))
        return DocumentationCatalogResponse(
            node_id=node_id,
            documents=[DocumentationOutputResponse.model_validate(item.to_payload()) for item in snapshot.documents],
        )

    @app.get(
        "/api/nodes/{node_id}/docs/{scope}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=DocumentationOutputResponse,
    )
    def show_docs_endpoint(node_id: str, scope: str, session_factory=Depends(get_db_session_factory)) -> DocumentationOutputResponse:
        return DocumentationOutputResponse.model_validate(
            show_docs_for_node(session_factory, logical_node_id=UUID(node_id), scope=scope).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/summary-history",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SummaryHistoryCatalogResponse,
    )
    def show_summary_history(node_id: str, session_factory=Depends(get_db_session_factory)) -> SummaryHistoryCatalogResponse:
        snapshot = list_summary_history(session_factory, logical_node_id=UUID(node_id))
        return SummaryHistoryCatalogResponse(
            node_id=node_id,
            summaries=[SummaryHistoryRecordResponse.model_validate(item.to_payload()) for item in snapshot.summaries],
        )

    @app.get(
        "/api/summaries/{summary_id}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=SummaryHistoryRecordResponse,
    )
    def show_summary_record(summary_id: str, session_factory=Depends(get_db_session_factory)) -> SummaryHistoryRecordResponse:
        return SummaryHistoryRecordResponse.model_validate(get_summary_record(session_factory, summary_id=UUID(summary_id)).to_payload())

    @app.post(
        "/api/nodes/{node_id}/provenance/refresh",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ProvenanceRefreshResponse,
    )
    def refresh_provenance_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> ProvenanceRefreshResponse:
        return ProvenanceRefreshResponse.model_validate(
            refresh_node_provenance(session_factory, logical_node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/rationale",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RationaleResponse,
    )
    def show_rationale_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> RationaleResponse:
        snapshot = show_node_rationale(session_factory, logical_node_id=UUID(node_id))
        return RationaleResponse(
            node_id=node_id,
            node_version_id=str(snapshot.node_version_id),
            prompt_record_id=None if snapshot.prompt_record_id is None else str(snapshot.prompt_record_id),
            summary_record_id=None if snapshot.summary_record_id is None else str(snapshot.summary_record_id),
            rationale_summary=snapshot.rationale_summary,
            change_counts=snapshot.change_counts,
            entity_history=[EntityHistoryEntryResponse.model_validate(item.to_payload()) for item in snapshot.entity_history],
        )

    @app.get(
        "/api/entities/by-name/{canonical_name}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=EntityCatalogResponse,
    )
    def show_entity(canonical_name: str, session_factory=Depends(get_db_session_factory)) -> EntityCatalogResponse:
        snapshot = show_entity_by_name(session_factory, canonical_name=canonical_name)
        return EntityCatalogResponse(
            canonical_name=snapshot.canonical_name,
            entities=[EntityResponse.model_validate(item.to_payload()) for item in snapshot.entities],
        )

    @app.get(
        "/api/entities/by-name/{canonical_name}/history",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=EntityHistoryCatalogResponse,
    )
    def show_entity_history_endpoint(canonical_name: str, session_factory=Depends(get_db_session_factory)) -> EntityHistoryCatalogResponse:
        snapshot = show_entity_history(session_factory, canonical_name=canonical_name)
        return EntityHistoryCatalogResponse(
            canonical_name=snapshot.canonical_name,
            history=[EntityHistoryEntryResponse.model_validate(item.to_payload()) for item in snapshot.history],
        )

    @app.get(
        "/api/entities/by-name/{canonical_name}/changed-by",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=EntityHistoryCatalogResponse,
    )
    def show_entity_changed_by(canonical_name: str, session_factory=Depends(get_db_session_factory)) -> EntityHistoryCatalogResponse:
        snapshot = show_entity_history(session_factory, canonical_name=canonical_name, changed_only=True)
        return EntityHistoryCatalogResponse(
            canonical_name=snapshot.canonical_name,
            history=[EntityHistoryEntryResponse.model_validate(item.to_payload()) for item in snapshot.history],
        )

    @app.get(
        "/api/entities/by-name/{canonical_name}/relations",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=EntityRelationCatalogResponse,
    )
    def show_entity_relations_endpoint(canonical_name: str, session_factory=Depends(get_db_session_factory)) -> EntityRelationCatalogResponse:
        snapshot = show_entity_relations(session_factory, canonical_name=canonical_name)
        return EntityRelationCatalogResponse(
            canonical_name=snapshot.canonical_name,
            relations=[EntityRelationResponse.model_validate(item.to_payload()) for item in snapshot.relations],
        )

    @app.post(
        "/api/nodes/{node_id}/workflow/advance",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def advance_node_workflow(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resource_catalog=Depends(get_resource_catalog),
    ) -> RunProgressResponse:
        return RunProgressResponse.model_validate(
            advance_workflow(session_factory, logical_node_id=UUID(node_id), catalog=resource_catalog).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/validation",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ValidationSummaryResponse,
    )
    def show_validation_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> ValidationSummaryResponse:
        return ValidationSummaryResponse.model_validate(
            load_validation_summary_for_node(session_factory, logical_node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/node-runs/{run_id}/validation",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ValidationSummaryResponse,
    )
    def show_validation_for_run(run_id: str, session_factory=Depends(get_db_session_factory)) -> ValidationSummaryResponse:
        return ValidationSummaryResponse.model_validate(
            load_validation_summary_for_run(session_factory, node_run_id=UUID(run_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/validation/results",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ValidationResultCatalogResponse,
    )
    def show_validation_results_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> ValidationResultCatalogResponse:
        results = list_validation_results_for_node(session_factory, logical_node_id=UUID(node_id))
        return ValidationResultCatalogResponse(
            node_id=node_id,
            results=[ValidationResultResponse.model_validate(item.to_payload()) for item in results],
        )

    @app.post(
        "/api/nodes/{node_id}/validation/run",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ValidationSummaryResponse,
    )
    def run_validation_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> ValidationSummaryResponse:
        return ValidationSummaryResponse.model_validate(
            evaluate_validation_subtask(session_factory, logical_node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/review",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ReviewSummaryResponse,
    )
    def show_review_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> ReviewSummaryResponse:
        return ReviewSummaryResponse.model_validate(
            load_review_summary_for_node(session_factory, logical_node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/node-runs/{run_id}/review",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ReviewSummaryResponse,
    )
    def show_review_for_run(run_id: str, session_factory=Depends(get_db_session_factory)) -> ReviewSummaryResponse:
        return ReviewSummaryResponse.model_validate(
            load_review_summary_for_run(session_factory, node_run_id=UUID(run_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/review/results",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ReviewResultCatalogResponse,
    )
    def show_review_results_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> ReviewResultCatalogResponse:
        results = list_review_results_for_node(session_factory, logical_node_id=UUID(node_id))
        return ReviewResultCatalogResponse(
            node_id=node_id,
            results=[item.to_payload() for item in results],
        )

    @app.post(
        "/api/nodes/{node_id}/review/run",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RunProgressResponse,
    )
    def run_review_for_node(
        node_id: str,
        payload: ReviewRunRequest,
        session_factory=Depends(get_db_session_factory),
        resource_catalog=Depends(get_resource_catalog),
    ) -> RunProgressResponse:
        if payload.node_id != node_id:
            raise DaemonConflictError("review request node id does not match route node id")
        progress = load_current_run_progress(session_factory, logical_node_id=UUID(node_id))
        compiled_subtask_id = progress.state.current_compiled_subtask_id
        if compiled_subtask_id is None:
            raise DaemonConflictError("active review subtask not found")
        review_subtask_id = compiled_subtask_id if isinstance(compiled_subtask_id, UUID) else UUID(compiled_subtask_id)
        start_subtask_attempt(
            session_factory,
            logical_node_id=UUID(node_id),
            compiled_subtask_id=review_subtask_id,
        )
        complete_current_subtask(
            session_factory,
            logical_node_id=UUID(node_id),
            compiled_subtask_id=review_subtask_id,
            output_json={
                "status": payload.status,
                "summary": payload.summary,
                "findings": payload.findings_json,
                "criteria_results": payload.criteria_json,
            },
            summary=payload.summary,
        )
        return RunProgressResponse.model_validate(
            advance_workflow(session_factory, logical_node_id=UUID(node_id), catalog=resource_catalog).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/testing",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=TestingSummaryResponse,
    )
    def show_testing_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> TestingSummaryResponse:
        return TestingSummaryResponse.model_validate(
            load_testing_summary_for_node(session_factory, logical_node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/node-runs/{run_id}/testing",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=TestingSummaryResponse,
    )
    def show_testing_for_run(run_id: str, session_factory=Depends(get_db_session_factory)) -> TestingSummaryResponse:
        return TestingSummaryResponse.model_validate(
            load_testing_summary_for_run(session_factory, node_run_id=UUID(run_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/testing/results",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=TestResultCatalogResponse,
    )
    def show_test_results_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> TestResultCatalogResponse:
        results = list_test_results_for_node(session_factory, logical_node_id=UUID(node_id))
        return TestResultCatalogResponse(
            node_id=node_id,
            results=[TestResultResponse.model_validate(item.to_payload()) for item in results],
        )

    @app.post(
        "/api/nodes/{node_id}/testing/run",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=TestingSummaryResponse,
    )
    def run_testing_for_node(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resource_catalog=Depends(get_resource_catalog),
    ) -> TestingSummaryResponse:
        return TestingSummaryResponse.model_validate(
            evaluate_testing_subtask(session_factory, logical_node_id=UUID(node_id), catalog=resource_catalog).to_payload()
        )

    @app.post(
        "/api/nodes/{node_id}/quality-chain/run",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=QualityChainResponse,
    )
    def run_quality_chain_for_node(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resource_catalog=Depends(get_resource_catalog),
    ) -> QualityChainResponse:
        return QualityChainResponse.model_validate(
            run_turnkey_quality_chain(
                session_factory,
                logical_node_id=UUID(node_id),
                catalog=resource_catalog,
            ).to_payload()
        )

    @app.get("/api/node-kinds", dependencies=[Depends(require_bearer_token)], response_model=NodeKindCatalogResponse)
    def list_node_kinds(hierarchy_registry=Depends(get_hierarchy_registry)) -> NodeKindCatalogResponse:
        definitions = [
            NodeKindDefinitionResponse(
                kind=record.definition.kind,
                tier=str(record.definition.tier),
                description=record.definition.description,
                allow_parentless=record.definition.parent_constraints.allow_parentless,
                allowed_parent_kinds=record.definition.parent_constraints.allowed_kinds,
                allowed_child_kinds=record.definition.child_constraints.allowed_kinds,
            )
            for record in hierarchy_registry.definitions.values()
        ]
        return NodeKindCatalogResponse(definitions=definitions, top_level_kinds=hierarchy_registry.top_level_kinds())

    @app.get("/api/projects", dependencies=[Depends(require_bearer_token)], response_model=ProjectCatalogResponse)
    def list_projects_endpoint(settings=Depends(get_settings_dependency)) -> ProjectCatalogResponse:
        return ProjectCatalogResponse(
            daemon_context=build_project_catalog_daemon_context(
                settings=settings,
                daemon_version=app.version,
                session_backend=app.state.session_adapter.backend_name if hasattr(app, "state") else "unknown",
            ).to_payload(),
            projects=[ProjectCatalogEntryResponse.model_validate(project.to_payload()) for project in list_projects(settings=settings)],
        )

    @app.get(
        "/api/projects/{project_id}/bootstrap",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ProjectBootstrapResponse,
    )
    def show_project_bootstrap(
        project_id: str,
        session_factory=Depends(get_db_session_factory),
        settings=Depends(get_settings_dependency),
    ) -> ProjectBootstrapResponse:
        return ProjectBootstrapResponse.model_validate(
            load_project_bootstrap(session_factory, project_id=project_id, settings=settings).to_payload()
        )

    @app.post(
        "/api/projects/{project_id}/top-level-nodes",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ProjectTopLevelNodeCreateResponse,
    )
    def start_project_top_level_node(
        project_id: str,
        payload: ProjectTopLevelNodeCreateRequest,
        session_factory=Depends(get_db_session_factory),
        hierarchy_registry=Depends(get_hierarchy_registry),
        resource_catalog=Depends(get_resource_catalog),
        settings=Depends(get_settings_dependency),
    ) -> ProjectTopLevelNodeCreateResponse:
        return ProjectTopLevelNodeCreateResponse.model_validate(
            start_project_top_level_workflow(
                session_factory,
                hierarchy_registry=hierarchy_registry,
                resource_catalog=resource_catalog,
                project_id=project_id,
                kind=payload.kind,
                title=payload.title,
                prompt=payload.prompt,
                start_run=payload.start_run,
                settings=settings,
            ).to_payload()
        )

    @app.post(
        "/api/workflows/start",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowStartResponse,
    )
    def start_workflow(
        payload: WorkflowStartRequest,
        session_factory=Depends(get_db_session_factory),
        hierarchy_registry=Depends(get_hierarchy_registry),
        resource_catalog=Depends(get_resource_catalog),
    ) -> WorkflowStartResponse:
        return WorkflowStartResponse.model_validate(
            start_top_level_workflow(
                session_factory,
                hierarchy_registry=hierarchy_registry,
                resource_catalog=resource_catalog,
                kind=payload.kind,
                title=payload.title,
                prompt=payload.prompt,
                start_run=payload.start_run,
            ).to_payload()
        )

    @app.post(
        "/api/nodes/create",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=HierarchyNodeResponse,
    )
    def create_node(
        payload: NodeCreateRequest,
        session_factory=Depends(get_db_session_factory),
        hierarchy_registry=Depends(get_hierarchy_registry),
    ) -> HierarchyNodeResponse:
        parent_node_id = None if payload.parent_node_id is None else UUID(payload.parent_node_id)
        sync_hierarchy_definitions(session_factory, hierarchy_registry)
        creation = create_manual_node(
            session_factory,
            hierarchy_registry,
            kind=payload.kind,
            title=payload.title,
            prompt=payload.prompt,
            parent_node_id=parent_node_id,
        )
        capture_node_version_source_lineage(session_factory, node_version_id=creation.node_version_id)
        return HierarchyNodeResponse.model_validate(creation.node.to_payload())

    @app.post(
        "/api/nodes/lifecycle/transition",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeLifecycleStateResponse,
    )
    def transition_node_lifecycle_endpoint(
        payload: NodeLifecycleTransitionRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> NodeLifecycleStateResponse:
        snapshot = transition_node_lifecycle(
            session_factory,
            node_id=payload.node_id,
            target_state=payload.target_state,
            pause_flag_name=payload.pause_flag_name,
        )
        return NodeLifecycleStateResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/nodes/cursor/update",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeLifecycleStateResponse,
    )
    def update_node_cursor_endpoint(
        payload: NodeCursorUpdateRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> NodeLifecycleStateResponse:
        snapshot = update_node_cursor(
            session_factory,
            node_id=payload.node_id,
            current_task_id=payload.current_task_id,
            current_subtask_id=payload.current_subtask_id,
            current_subtask_attempt=payload.current_subtask_attempt,
            last_completed_subtask_id=payload.last_completed_subtask_id,
            execution_cursor_json=payload.execution_cursor_json,
            failure_count_from_children=payload.failure_count_from_children,
            failure_count_consecutive=payload.failure_count_consecutive,
            defer_to_user_threshold=payload.defer_to_user_threshold,
            is_resumable=payload.is_resumable,
            pause_flag_name=payload.pause_flag_name,
            working_tree_state=payload.working_tree_state,
        )
        return NodeLifecycleStateResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/nodes/{node_id}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=HierarchyNodeResponse,
    )
    def show_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> HierarchyNodeResponse:
        return HierarchyNodeResponse.model_validate(get_hierarchy_node(session_factory, UUID(node_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/summary",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeOperatorSummaryResponse,
    )
    def show_node_summary(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeOperatorSummaryResponse:
        return NodeOperatorSummaryResponse.model_validate(load_node_operator_summary(session_factory, node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/versions",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeVersionCatalogResponse,
    )
    def show_node_versions(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeVersionCatalogResponse:
        versions = list_node_versions(session_factory, UUID(node_id))
        return NodeVersionCatalogResponse(versions=[NodeVersionResponse.model_validate(item.to_payload()) for item in versions])

    @app.get(
        "/api/nodes/{node_id}/sources",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeVersionSourceLineageResponse,
    )
    def show_node_sources(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeVersionSourceLineageResponse:
        lineage = load_node_lineage(session_factory, UUID(node_id))
        return NodeVersionSourceLineageResponse.model_validate(
            load_node_version_source_lineage(session_factory, node_version_id=lineage.authoritative_node_version_id).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/lineage",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeLineageResponse,
    )
    def show_node_lineage(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeLineageResponse:
        return NodeLineageResponse.model_validate(load_node_lineage(session_factory, UUID(node_id)).to_payload())

    @app.post(
        "/api/nodes/{node_id}/supersede",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeVersionResponse,
    )
    def supersede_node(
        node_id: str,
        payload: NodeSupersedeRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> NodeVersionResponse:
        snapshot = create_superseding_node_version(
            session_factory,
            logical_node_id=UUID(node_id),
            title=payload.title,
            prompt=payload.prompt,
        )
        capture_node_version_source_lineage(session_factory, node_version_id=snapshot.id)
        return NodeVersionResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/node-versions/{version_id}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeVersionResponse,
    )
    def show_node_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> NodeVersionResponse:
        return NodeVersionResponse.model_validate(load_node_version(session_factory, UUID(version_id)).to_payload())

    @app.get(
        "/api/node-versions/{version_id}/sources",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeVersionSourceLineageResponse,
    )
    def show_node_version_sources(version_id: str, session_factory=Depends(get_db_session_factory)) -> NodeVersionSourceLineageResponse:
        return NodeVersionSourceLineageResponse.model_validate(
            load_node_version_source_lineage(session_factory, node_version_id=UUID(version_id)).to_payload()
        )

    @app.post(
        "/api/nodes/{node_id}/workflow/compile",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowCompileAttemptResponse,
    )
    def compile_workflow_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> WorkflowCompileAttemptResponse:
        return WorkflowCompileAttemptResponse.model_validate(
            compile_node_workflow(
                session_factory,
                logical_node_id=UUID(node_id),
                catalog=app.state.resource_catalog,
            ).to_payload()
        )

    @app.post(
        "/api/node-versions/{version_id}/workflow/compile",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowCompileAttemptResponse,
    )
    def compile_workflow_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> WorkflowCompileAttemptResponse:
        return WorkflowCompileAttemptResponse.model_validate(
            compile_node_version_workflow(
                session_factory,
                version_id=UUID(version_id),
                catalog=app.state.resource_catalog,
            ).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/workflow/current",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CompiledWorkflowResponse,
    )
    def show_current_workflow(node_id: str, session_factory=Depends(get_db_session_factory)) -> CompiledWorkflowResponse:
        return CompiledWorkflowResponse.model_validate(load_current_workflow(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/node-versions/{version_id}/workflow/current",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CompiledWorkflowResponse,
    )
    def show_workflow_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> CompiledWorkflowResponse:
        return CompiledWorkflowResponse.model_validate(load_node_version_workflow(session_factory, version_id=UUID(version_id)).to_payload())

    @app.get(
        "/api/workflows/{workflow_id}",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CompiledWorkflowResponse,
    )
    def show_workflow(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> CompiledWorkflowResponse:
        return CompiledWorkflowResponse.model_validate(load_workflow(session_factory, workflow_id=UUID(workflow_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/workflow/chain",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowChainResponse,
    )
    def show_workflow_chain_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> WorkflowChainResponse:
        return WorkflowChainResponse.model_validate(load_workflow_chain_for_node(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/node-versions/{version_id}/workflow/chain",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowChainResponse,
    )
    def show_workflow_chain_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> WorkflowChainResponse:
        return WorkflowChainResponse.model_validate(load_workflow_chain_for_version(session_factory, version_id=UUID(version_id)).to_payload())

    @app.get(
        "/api/workflows/{workflow_id}/chain",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowChainResponse,
    )
    def show_workflow_chain(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> WorkflowChainResponse:
        return WorkflowChainResponse.model_validate(load_workflow_chain(session_factory, workflow_id=UUID(workflow_id)).to_payload())

    @app.get(
        "/api/workflows/{workflow_id}/sources",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_sources(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_sources(session_factory, workflow_id=UUID(workflow_id))

    @app.get(
        "/api/nodes/{node_id}/workflow/sources",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_sources_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_sources_for_node(session_factory, logical_node_id=UUID(node_id))

    @app.get(
        "/api/node-versions/{version_id}/workflow/sources",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_sources_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_sources_for_version(session_factory, version_id=UUID(version_id))

    @app.get(
        "/api/workflows/{workflow_id}/source-discovery",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_source_discovery(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_source_discovery(session_factory, workflow_id=UUID(workflow_id))

    @app.get(
        "/api/nodes/{node_id}/workflow/source-discovery",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_source_discovery_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_source_discovery_for_node(session_factory, logical_node_id=UUID(node_id))

    @app.get(
        "/api/node-versions/{version_id}/workflow/source-discovery",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_source_discovery_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_source_discovery_for_version(session_factory, version_id=UUID(version_id))

    @app.get(
        "/api/workflows/{workflow_id}/schema-validation",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_schema_validation(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_schema_validation(session_factory, workflow_id=UUID(workflow_id))

    @app.get(
        "/api/nodes/{node_id}/workflow/schema-validation",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_schema_validation_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_schema_validation_for_node(session_factory, logical_node_id=UUID(node_id))

    @app.get(
        "/api/node-versions/{version_id}/workflow/schema-validation",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_schema_validation_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_schema_validation_for_version(session_factory, version_id=UUID(version_id))

    @app.get(
        "/api/workflows/{workflow_id}/override-resolution",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_override_resolution(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_override_resolution(session_factory, workflow_id=UUID(workflow_id))

    @app.get(
        "/api/nodes/{node_id}/workflow/override-resolution",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_override_resolution_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_override_resolution_for_node(session_factory, logical_node_id=UUID(node_id))

    @app.get(
        "/api/node-versions/{version_id}/workflow/override-resolution",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_override_resolution_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_override_resolution_for_version(session_factory, version_id=UUID(version_id))

    @app.get(
        "/api/workflows/{workflow_id}/hooks",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowHookCatalogResponse,
    )
    def show_workflow_hooks(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> WorkflowHookCatalogResponse:
        return WorkflowHookCatalogResponse.model_validate(load_workflow_hooks(session_factory, workflow_id=UUID(workflow_id)))

    @app.get(
        "/api/nodes/{node_id}/workflow/hooks",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowHookCatalogResponse,
    )
    def show_workflow_hooks_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> WorkflowHookCatalogResponse:
        return WorkflowHookCatalogResponse.model_validate(
            load_workflow_hooks_for_node(session_factory, logical_node_id=UUID(node_id))
        )

    @app.get(
        "/api/node-versions/{version_id}/workflow/hooks",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=WorkflowHookCatalogResponse,
    )
    def show_workflow_hooks_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> WorkflowHookCatalogResponse:
        return WorkflowHookCatalogResponse.model_validate(
            load_workflow_hooks_for_version(session_factory, version_id=UUID(version_id))
        )

    @app.get(
        "/api/workflows/{workflow_id}/hook-policy",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_hook_policy(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_hook_policy(session_factory, workflow_id=UUID(workflow_id))

    @app.get(
        "/api/nodes/{node_id}/workflow/hook-policy",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_hook_policy_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_hook_policy_for_node(session_factory, logical_node_id=UUID(node_id))

    @app.get(
        "/api/node-versions/{version_id}/workflow/hook-policy",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_hook_policy_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_hook_policy_for_version(session_factory, version_id=UUID(version_id))

    @app.get(
        "/api/workflows/{workflow_id}/rendering",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_rendering(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_rendering(session_factory, workflow_id=UUID(workflow_id))

    @app.get(
        "/api/nodes/{node_id}/workflow/rendering",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_rendering_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_rendering_for_node(session_factory, logical_node_id=UUID(node_id))

    @app.get(
        "/api/node-versions/{version_id}/workflow/rendering",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
    )
    def show_workflow_rendering_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> dict[str, object]:
        return load_workflow_rendering_for_version(session_factory, version_id=UUID(version_id))

    @app.get(
        "/api/nodes/{node_id}/yaml/override-chain",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=OverrideChainResponse,
    )
    def show_override_chain_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> OverrideChainResponse:
        return OverrideChainResponse.model_validate(
            load_override_chain_for_node(session_factory, logical_node_id=UUID(node_id))
        )

    @app.get(
        "/api/workflows/{workflow_id}/yaml/override-chain",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=OverrideChainResponse,
    )
    def show_override_chain(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> OverrideChainResponse:
        return OverrideChainResponse.model_validate(load_override_chain(session_factory, workflow_id=UUID(workflow_id)))

    @app.get(
        "/api/nodes/{node_id}/yaml/resolved",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ResolvedYamlCatalogResponse,
    )
    def show_resolved_yaml_for_node(
        node_id: str,
        family: str | None = None,
        document_id: str | None = None,
        session_factory=Depends(get_db_session_factory),
    ) -> ResolvedYamlCatalogResponse:
        return ResolvedYamlCatalogResponse.model_validate(
            load_resolved_yaml_for_node(
                session_factory,
                logical_node_id=UUID(node_id),
                target_family=family,
                target_id=document_id,
            )
        )

    @app.get(
        "/api/node-versions/{version_id}/yaml/resolved",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ResolvedYamlCatalogResponse,
    )
    def show_resolved_yaml_for_version(
        version_id: str,
        family: str | None = None,
        document_id: str | None = None,
        session_factory=Depends(get_db_session_factory),
    ) -> ResolvedYamlCatalogResponse:
        return ResolvedYamlCatalogResponse.model_validate(
            load_resolved_yaml_for_version(
                session_factory,
                version_id=UUID(version_id),
                target_family=family,
                target_id=document_id,
            )
        )

    @app.get(
        "/api/workflows/{workflow_id}/yaml/resolved",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ResolvedYamlCatalogResponse,
    )
    def show_resolved_yaml(
        workflow_id: str,
        family: str | None = None,
        document_id: str | None = None,
        session_factory=Depends(get_db_session_factory),
    ) -> ResolvedYamlCatalogResponse:
        return ResolvedYamlCatalogResponse.model_validate(
            load_resolved_yaml(
                session_factory,
                workflow_id=UUID(workflow_id),
                target_family=family,
                target_id=document_id,
            )
        )

    @app.get(
        "/api/nodes/{node_id}/workflow/compile-failures",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CompileFailureCatalogResponse,
    )
    def show_compile_failures_for_node(node_id: str, session_factory=Depends(get_db_session_factory)) -> CompileFailureCatalogResponse:
        failures = list_compile_failures_for_node(session_factory, logical_node_id=UUID(node_id))
        return CompileFailureCatalogResponse(failures=[item.to_payload() for item in failures])

    @app.get(
        "/api/node-versions/{version_id}/workflow/compile-failures",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CompileFailureCatalogResponse,
    )
    def show_compile_failures_for_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> CompileFailureCatalogResponse:
        failures = list_compile_failures_for_version(session_factory, version_id=UUID(version_id))
        return CompileFailureCatalogResponse(failures=[item.to_payload() for item in failures])

    @app.get(
        "/api/workflows/{workflow_id}/compile-failures",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CompileFailureCatalogResponse,
    )
    def show_compile_failures_for_workflow(workflow_id: str, session_factory=Depends(get_db_session_factory)) -> CompileFailureCatalogResponse:
        failures = list_compile_failures_for_workflow(session_factory, workflow_id=UUID(workflow_id))
        return CompileFailureCatalogResponse(failures=[item.to_payload() for item in failures])

    @app.post(
        "/api/node-versions/{version_id}/cutover",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeLineageResponse,
    )
    def cutover_node_version(version_id: str, session_factory=Depends(get_db_session_factory)) -> NodeLineageResponse:
        return NodeLineageResponse.model_validate(cutover_candidate_version(session_factory, version_id=UUID(version_id)).to_payload())

    @app.post(
        "/api/nodes/{node_id}/regenerate",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RegenerationResponse,
    )
    def regenerate_node(node_id: str, session_factory=Depends(get_db_session_factory), resources=Depends(get_resource_catalog)) -> RegenerationResponse:
        return RegenerationResponse.model_validate(
            regenerate_node_and_descendants(
                session_factory,
                logical_node_id=UUID(node_id),
                catalog=resources,
            ).to_payload()
        )

    @app.post(
        "/api/nodes/{node_id}/rectify-upstream",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RegenerationResponse,
    )
    def rectify_node_upstream(node_id: str, session_factory=Depends(get_db_session_factory), resources=Depends(get_resource_catalog)) -> RegenerationResponse:
        return RegenerationResponse.model_validate(
            rectify_upstream(
                session_factory,
                logical_node_id=UUID(node_id),
                catalog=resources,
            ).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/rebuild-history",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RebuildHistoryResponse,
    )
    def show_rebuild_history(node_id: str, session_factory=Depends(get_db_session_factory)) -> RebuildHistoryResponse:
        return RebuildHistoryResponse.model_validate(
            list_rebuild_events_for_node(session_factory, logical_node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/rebuild-coordination",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=RebuildCoordinationResponse,
    )
    def show_rebuild_coordination(node_id: str, scope: str = "subtree", session_factory=Depends(get_db_session_factory)) -> RebuildCoordinationResponse:
        return RebuildCoordinationResponse.model_validate(
            inspect_rebuild_coordination(session_factory, logical_node_id=UUID(node_id), scope=scope).to_payload()
        )

    @app.get(
        "/api/node-versions/{version_id}/cutover-readiness",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=CutoverReadinessResponse,
    )
    def show_cutover_readiness(version_id: str, session_factory=Depends(get_db_session_factory)) -> CutoverReadinessResponse:
        return CutoverReadinessResponse.model_validate(
            inspect_cutover_readiness(session_factory, version_id=UUID(version_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/lifecycle",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeLifecycleStateResponse,
    )
    def show_node_lifecycle(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeLifecycleStateResponse:
        return NodeLifecycleStateResponse.model_validate(load_node_lifecycle(session_factory, node_id).to_payload())

    @app.get(
        "/api/nodes/{node_id}/children",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=list[HierarchyNodeResponse],
    )
    def show_node_children(node_id: str, session_factory=Depends(get_db_session_factory)) -> list[HierarchyNodeResponse]:
        return [HierarchyNodeResponse.model_validate(item.to_payload()) for item in list_children(session_factory, UUID(node_id))]

    @app.get(
        "/api/nodes/{node_id}/children/materialization",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MaterializationResponse,
    )
    def show_node_child_materialization(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
    ) -> MaterializationResponse:
        snapshot = inspect_materialized_children(
            session_factory,
            resources,
            logical_node_id=UUID(node_id),
        )
        return MaterializationResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/nodes/{node_id}/children/register-layout",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=LayoutRegistrationResponse,
    )
    def register_node_child_layout(
        node_id: str,
        payload: LayoutRegistrationRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> LayoutRegistrationResponse:
        snapshot = register_generated_layout(
            session_factory,
            logical_node_id=UUID(node_id),
            file_path=payload.file_path,
        )
        return LayoutRegistrationResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/nodes/{node_id}/children/materialize",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MaterializationResponse,
    )
    def materialize_node_children(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        hierarchy_registry=Depends(get_hierarchy_registry),
        resources=Depends(get_resource_catalog),
    ) -> MaterializationResponse:
        snapshot = materialize_layout_children(
            session_factory,
            hierarchy_registry,
            resources,
            logical_node_id=UUID(node_id),
        )
        return MaterializationResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/nodes/{node_id}/children/reconciliation",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ChildReconciliationResponse,
    )
    def show_node_child_reconciliation(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
    ) -> ChildReconciliationResponse:
        snapshot = inspect_child_reconciliation(
            session_factory,
            resources,
            logical_node_id=UUID(node_id),
        )
        return ChildReconciliationResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/nodes/{node_id}/children/reconcile",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ChildReconciliationResponse,
    )
    def reconcile_node_children(
        node_id: str,
        payload: ChildReconciliationRequest,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
    ) -> ChildReconciliationResponse:
        snapshot = reconcile_child_authority(
            session_factory,
            resources,
            logical_node_id=UUID(node_id),
            decision=payload.decision,
        )
        return ChildReconciliationResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/nodes/{node_id}/child-results",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ChildResultCollectionResponse,
    )
    def show_node_child_results(node_id: str, session_factory=Depends(get_db_session_factory)) -> ChildResultCollectionResponse:
        snapshot = collect_child_results(session_factory, logical_node_id=UUID(node_id))
        return ChildResultCollectionResponse.model_validate(snapshot.to_payload())

    @app.get(
        "/api/nodes/{node_id}/reconcile",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ParentReconcileResponse,
    )
    def show_parent_reconcile(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
    ) -> ParentReconcileResponse:
        snapshot = inspect_parent_reconcile(session_factory, resources, logical_node_id=UUID(node_id))
        return ParentReconcileResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/node-versions/{version_id}/git/bootstrap",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=LiveGitStatusResponse,
    )
    def bootstrap_node_version_git_state(
        version_id: str,
        payload: LiveGitBootstrapRequest,
        session_factory=Depends(get_db_session_factory),
    ) -> LiveGitStatusResponse:
        if payload.version_id != version_id:
            raise DaemonConflictError("bootstrap payload version_id must match the path version_id")
        snapshot = bootstrap_live_git_repo(
            session_factory,
            version_id=UUID(version_id),
            files=payload.files_json,
            base_version_id=None if payload.base_version_id is None else UUID(payload.base_version_id),
            replace_existing=payload.replace_existing,
        )
        return LiveGitStatusResponse.model_validate(snapshot.to_payload())

    @app.post(
        "/api/nodes/{node_id}/git/merge-children",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ParentReconcileResponse,
    )
    def merge_node_children(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
    ) -> ParentReconcileResponse:
        reconcile = inspect_parent_reconcile(session_factory, resources, logical_node_id=UUID(node_id))
        ordered_children = [
            (UUID(item["child_node_version_id"]), str(item["final_commit_sha"]), int(item["merge_order"]))
            for item in reconcile.child_results.to_payload()["children"]
            if item["merge_order"] is not None and item["final_commit_sha"] is not None
        ]
        live_result = execute_live_merge_children(session_factory, logical_node_id=UUID(node_id), ordered_child_versions=ordered_children)
        if live_result.status == "conflicted":
            raise DaemonConflictError("live child merge encountered conflicts; inspect merge-conflicts and abort or resolve before retrying")
        snapshot = ParentReconcileResponse.model_validate(
            {
                **reconcile.to_payload(),
                "status": live_result.status,
                "merge_events": [item.to_payload() for item in live_result.merge_events],
                "context_json": {
                    **reconcile.context_json,
                    "repo_path": live_result.repo_path,
                    "head_commit_sha": live_result.head_commit_sha,
                    "working_tree_state": live_result.working_tree_state,
                },
            }
        )
        return snapshot

    @app.post(
        "/api/nodes/{node_id}/git/abort-merge",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=LiveGitStatusResponse,
    )
    def abort_node_merge(node_id: str, session_factory=Depends(get_db_session_factory)) -> LiveGitStatusResponse:
        return LiveGitStatusResponse.model_validate(abort_live_merge(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.post(
        "/api/nodes/{node_id}/git/finalize",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=LiveGitFinalizeResponse,
    )
    def finalize_node_git_state(node_id: str, session_factory=Depends(get_db_session_factory)) -> LiveGitFinalizeResponse:
        return LiveGitFinalizeResponse.model_validate(finalize_live_git_state(session_factory, logical_node_id=UUID(node_id)).to_payload())

    @app.get(
        "/api/node-versions/{version_id}/git/status",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=LiveGitStatusResponse,
    )
    def show_node_version_git_status(version_id: str, session_factory=Depends(get_db_session_factory)) -> LiveGitStatusResponse:
        return LiveGitStatusResponse.model_validate(show_live_git_status(session_factory, version_id=UUID(version_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/ancestors",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=list[HierarchyNodeResponse],
    )
    def show_node_ancestors(node_id: str, session_factory=Depends(get_db_session_factory)) -> list[HierarchyNodeResponse]:
        return [HierarchyNodeResponse.model_validate(item.to_payload()) for item in list_ancestors(session_factory, UUID(node_id))]

    @app.get(
        "/api/nodes/{node_id}/siblings",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=list[NodeOperatorSummaryResponse],
    )
    def show_node_siblings(node_id: str, session_factory=Depends(get_db_session_factory)) -> list[NodeOperatorSummaryResponse]:
        return [NodeOperatorSummaryResponse.model_validate(item.to_payload()) for item in list_sibling_nodes(session_factory, node_id=UUID(node_id))]

    @app.get(
        "/api/nodes/{node_id}/tree",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=TreeCatalogResponse,
    )
    def show_tree(node_id: str, session_factory=Depends(get_db_session_factory)) -> TreeCatalogResponse:
        snapshot = load_tree_catalog(session_factory, root_node_id=UUID(node_id))
        return TreeCatalogResponse(
            root_node_id=str(snapshot.root_node_id),
            generated_at=snapshot.generated_at,
            nodes=[TreeNodeResponse.model_validate(item.to_payload()) for item in snapshot.nodes],
        )

    @app.get(
        "/api/nodes/{node_id}/actions",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeActionCatalogResponse,
    )
    def show_node_actions(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> NodeActionCatalogResponse:
        return NodeActionCatalogResponse.model_validate(
            list_node_actions(
                session_factory,
                resources,
                logical_node_id=UUID(node_id),
                adapter=adapter,
                poller=poller,
            ).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/interventions",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=InterventionCatalogResponse,
    )
    def show_node_interventions(
        node_id: str,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> InterventionCatalogResponse:
        return InterventionCatalogResponse.model_validate(
            list_node_interventions(
                session_factory,
                resources,
                logical_node_id=UUID(node_id),
                adapter=adapter,
                poller=poller,
            ).to_payload()
        )

    @app.post(
        "/api/nodes/interventions/apply",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=InterventionActionResponse,
    )
    def apply_intervention(
        payload: InterventionApplyRequest,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
        adapter=Depends(get_session_adapter),
        poller=Depends(get_session_poller),
    ) -> InterventionActionResponse:
        return InterventionActionResponse.model_validate(
            apply_node_intervention(
                session_factory,
                resources,
                logical_node_id=UUID(payload.node_id),
                intervention_kind=payload.intervention_kind,
                action=payload.action,
                summary=payload.summary,
                conflict_id=None if payload.conflict_id is None else UUID(payload.conflict_id),
                pause_flag_name=payload.pause_flag_name,
                adapter=adapter,
                poller=poller,
            ).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/pause-state",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodePauseStateResponse,
    )
    def show_pause_state(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodePauseStateResponse:
        return NodePauseStateResponse.model_validate(load_pause_state(session_factory, node_id=UUID(node_id)).to_payload())

    @app.post(
        "/api/nodes/pause/approve",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodePauseStateResponse,
    )
    def approve_node_pause(payload: PauseApprovalRequest, session_factory=Depends(get_db_session_factory)) -> NodePauseStateResponse:
        approve_paused_run(
            session_factory,
            logical_node_id=UUID(payload.node_id),
            pause_flag_name=payload.pause_flag_name,
            approval_summary=payload.approval_summary,
        )
        return NodePauseStateResponse.model_validate(load_pause_state(session_factory, node_id=UUID(payload.node_id)).to_payload())

    @app.get(
        "/api/nodes/{node_id}/events",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=NodeEventCatalogResponse,
    )
    def show_node_events(node_id: str, session_factory=Depends(get_db_session_factory)) -> NodeEventCatalogResponse:
        events = list_node_events(session_factory, node_id=UUID(node_id))
        return NodeEventCatalogResponse(node_id=node_id, events=[NodeEventResponse.model_validate(item.to_payload()) for item in events])

    @app.get(
        "/api/nodes/{node_id}/child-failures",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ChildFailureCounterCatalogResponse,
    )
    def show_child_failures(node_id: str, session_factory=Depends(get_db_session_factory)) -> ChildFailureCounterCatalogResponse:
        return ChildFailureCounterCatalogResponse.model_validate(
            list_child_failure_counters(session_factory, logical_node_id=UUID(node_id)).to_payload()
        )

    @app.get(
        "/api/nodes/{node_id}/decision-history",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ParentDecisionCatalogResponse,
    )
    def show_parent_decision_history(node_id: str, session_factory=Depends(get_db_session_factory)) -> ParentDecisionCatalogResponse:
        snapshot = list_parent_decision_history(session_factory, logical_node_id=UUID(node_id))
        return ParentDecisionCatalogResponse(
            node_id=node_id,
            decisions=[ParentDecisionResponse.model_validate(item.to_payload()) for item in snapshot.decisions],
        )

    @app.post(
        "/api/nodes/respond-to-child-failure",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=ParentFailureDecisionResponse,
    )
    def respond_to_child_failure(
        payload: ParentFailureDecisionRequest,
        session_factory=Depends(get_db_session_factory),
        resources=Depends(get_resource_catalog),
    ) -> ParentFailureDecisionResponse:
        return ParentFailureDecisionResponse.model_validate(
            handle_child_failure_at_parent(
                session_factory,
                logical_node_id=UUID(payload.node_id),
                child_node_id=UUID(payload.child_node_id),
                requested_action=payload.requested_action,
                catalog=resources,
            ).to_payload()
        )

    @app.post(
        "/api/nodes/pause",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MutationAcceptedResponse,
    )
    def pause_node(payload: MutationEnvelope, session_factory=Depends(get_db_session_factory)) -> MutationAcceptedResponse:
        sync_paused_run(session_factory, logical_node_id=UUID(payload.node_id), pause_flag_name="manual_pause")
        snapshot = apply_authority_mutation(session_factory, node_id=payload.node_id, command="node.pause")
        return MutationAcceptedResponse(
            status="accepted",
            command="node.pause",
            node_id=payload.node_id,
            authority="daemon",
            current_state=snapshot.current_state,
            current_run_id=str(snapshot.current_run_id),
            last_event_id=str(snapshot.last_event_id),
        )

    @app.post(
        "/api/nodes/resume",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MutationAcceptedResponse,
    )
    def resume_node(payload: MutationEnvelope, session_factory=Depends(get_db_session_factory)) -> MutationAcceptedResponse:
        sync_resumed_run(session_factory, logical_node_id=UUID(payload.node_id))
        snapshot = apply_authority_mutation(session_factory, node_id=payload.node_id, command="node.resume")
        return MutationAcceptedResponse(
            status="accepted",
            command="node.resume",
            node_id=payload.node_id,
            authority="daemon",
            current_state=snapshot.current_state,
            current_run_id=str(snapshot.current_run_id),
            last_event_id=str(snapshot.last_event_id),
        )

    @app.post(
        "/api/nodes/cancel",
        dependencies=[Depends(require_bearer_token), Depends(ensure_database_available)],
        response_model=MutationAcceptedResponse,
    )
    def cancel_node(payload: MutationEnvelope, session_factory=Depends(get_db_session_factory)) -> MutationAcceptedResponse:
        cancel_active_run(session_factory, logical_node_id=UUID(payload.node_id))
        snapshot = apply_authority_mutation(session_factory, node_id=payload.node_id, command="node.cancel")
        return MutationAcceptedResponse(
            status="accepted",
            command="node.cancel",
            node_id=payload.node_id,
            authority="daemon",
            current_state=snapshot.current_state,
            current_run_id=str(snapshot.current_run_id),
            last_event_id=str(snapshot.last_event_id),
        )

    @app.get("/", include_in_schema=False)
    @app.get("/projects", include_in_schema=False)
    @app.get("/projects/{full_path:path}", include_in_schema=False)
    def frontend_index(
        request: Request,
        settings=Depends(get_settings_dependency),
    ) -> Response:
        return serve_frontend_index(request, settings=settings)

    return app


app = create_app()
