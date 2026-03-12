from __future__ import annotations

from pydantic import AliasChoices, ConfigDict, Field

from aicoding.models.base import AICodingModel


class HealthResponse(AICodingModel):
    status: str


class MutationEnvelope(AICodingModel):
    node_id: str = Field(min_length=1)


class SubtaskMutationRequest(AICodingModel):
    node_id: str
    compiled_subtask_id: str
    output_json: dict[str, object] | None = None
    execution_result_json: dict[str, object] | None = None
    summary: str | None = None


class ReviewRunRequest(AICodingModel):
    node_id: str
    status: str
    summary: str | None = None
    findings_json: list[dict[str, object]] = Field(default_factory=list)
    criteria_json: list[dict[str, object]] | dict[str, object] | None = None


class SubtaskSucceedRequest(AICodingModel):
    node_id: str
    compiled_subtask_id: str
    summary_path: str
    content: str


class SubtaskReportCommandRequest(AICodingModel):
    node_id: str
    compiled_subtask_id: str
    execution_result_json: dict[str, object]
    failure_summary: str | None = None


class MutationAcceptedResponse(AICodingModel):
    status: str
    command: str
    node_id: str
    authority: str
    current_state: str | None = None
    current_run_id: str | None = None
    last_event_id: str | None = None


class NodeDependencyCreateRequest(AICodingModel):
    node_id: str
    depends_on_node_id: str
    required_state: str = "COMPLETE"


class NodeLifecycleTransitionRequest(MutationEnvelope):
    target_state: str
    pause_flag_name: str | None = None


class NodeCursorUpdateRequest(MutationEnvelope):
    current_task_id: str | None = None
    current_subtask_id: str | None = None
    current_subtask_attempt: int | None = Field(default=None, ge=1)
    last_completed_subtask_id: str | None = None
    execution_cursor_json: dict[str, object] | None = None
    failure_count_from_children: int | None = Field(default=None, ge=0)
    failure_count_consecutive: int | None = Field(default=None, ge=0)
    defer_to_user_threshold: int | None = Field(default=None, ge=0)
    is_resumable: bool | None = None
    pause_flag_name: str | None = None
    working_tree_state: str | None = None


class PauseApprovalRequest(MutationEnvelope):
    pause_flag_name: str | None = None
    approval_summary: str | None = None


class InterventionApplyRequest(MutationEnvelope):
    intervention_kind: str
    action: str
    summary: str | None = None
    conflict_id: str | None = None
    pause_flag_name: str | None = None


class SessionStateResponse(AICodingModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    backend: str
    session_name: str | None = Field(default=None, validation_alias=AliasChoices("session_name", "tmux_session_name"))
    status: str
    session_id: str | None = None
    logical_node_id: str | None = None
    node_run_id: str | None = None
    node_version_id: str | None = None
    node_kind: str | None = None
    node_title: str | None = None
    run_status: str | None = None
    session_role: str | None = None
    provider: str | None = None
    provider_session_id: str | None = None
    cwd: str | None = None
    tmux_session_exists: bool | None = None
    tmux_process_alive: bool | None = None
    tmux_exit_status: int | None = None
    attach_command: str | None = None
    last_heartbeat_at: str | None = None
    event_count: int | None = None
    latest_event_type: str | None = None
    recovery_classification: str | None = None
    pane_text: str | None = None
    idle_seconds: float | None = None
    in_alt_screen: bool | None = None
    screen_state: dict[str, object] | None = None
    recommended_action: str | None = None
    terminal_failure: dict[str, object] | None = None


class SessionCatalogResponse(AICodingModel):
    node_id: str
    sessions: list[SessionStateResponse]


class SessionEventResponse(AICodingModel):
    id: str
    session_id: str
    event_type: str
    payload_json: dict[str, object]
    created_at: str


class SessionEventCatalogResponse(AICodingModel):
    session_id: str
    events: list[SessionEventResponse]


class SessionRecoveryStatusResponse(AICodingModel):
    node_id: str
    node_version_id: str
    node_run_id: str
    session_id: str | None = None
    recovery_classification: str
    recommended_action: str
    reason: str | None = None
    is_resumable: bool
    pause_flag_name: str | None = None
    tmux_session_name: str | None = None
    tmux_session_exists: bool | None = None
    tmux_process_alive: bool | None = None
    tmux_exit_status: int | None = None
    provider: str | None = None
    provider_session_id_present: bool
    heartbeat_age_seconds: float | None = None
    duplicate_active_primary_sessions: int
    terminal_failure: dict[str, object] | None = None


class ProviderSessionRecoveryStatusResponse(AICodingModel):
    node_id: str
    node_version_id: str
    node_run_id: str
    session_id: str | None = None
    provider: str | None = None
    provider_session_id: str | None = None
    provider_supported: bool
    provider_session_exists: bool | None = None
    tmux_session_name: str | None = None
    tmux_session_exists: bool | None = None
    tmux_process_alive: bool | None = None
    tmux_exit_status: int | None = None
    provider_rebind_possible: bool
    provider_recommended_action: str
    provider_reason: str | None = None
    recovery_status: SessionRecoveryStatusResponse


class SessionRecoveryActionResponse(AICodingModel):
    status: str
    recovery_status: SessionRecoveryStatusResponse
    session: SessionStateResponse | None = None


class ProviderSessionRecoveryActionResponse(AICodingModel):
    status: str
    provider_recovery_status: ProviderSessionRecoveryStatusResponse
    recovery_status: SessionRecoveryStatusResponse
    session: SessionStateResponse | None = None


class SessionNudgeResponse(AICodingModel):
    node_id: str
    session_id: str | None = None
    status: str
    action: str
    session_status: str | None = None
    idle_seconds: float | None = None
    in_alt_screen: bool | None = None
    nudge_count: int
    max_nudge_count: int
    prompt_relative_path: str | None = None
    pause_flag_name: str | None = None
    screen_state: dict[str, object] | None = None


class ChildSessionPushRequest(AICodingModel):
    node_id: str
    reason: str


class ChildSessionPopRequest(AICodingModel):
    session_id: str
    status: str
    summary: str
    findings: list[str] = []
    artifacts: list[dict[str, object]] = []
    suggested_next_actions: list[str] = []


class ChildSessionResponse(AICodingModel):
    session_id: str
    parent_session_id: str
    node_run_id: str
    node_version_id: str
    parent_compiled_subtask_id: str
    reason: str
    status: str
    tmux_session_name: str | None = None
    provider: str
    delegated_prompt_path: str
    pane_text: str | None = None
    idle_seconds: float | None = None
    in_alt_screen: bool | None = None
    started_at: str
    ended_at: str | None = None


class ChildSessionResultResponse(AICodingModel):
    child_session_id: str
    parent_compiled_subtask_id: str
    status: str
    summary: str
    findings: list[str]
    artifacts: list[dict[str, object]]
    suggested_next_actions: list[str]
    recorded_at: str


class ApiErrorResponse(AICodingModel):
    error: str
    message: str


class SchemaCompatibilityResponse(AICodingModel):
    current_revision: str | None
    expected_revision: str | None
    status: str
    compatible: bool


class DaemonStatusResponse(AICodingModel):
    status: str
    authority: str
    background_tasks: list[str]
    write_probe: dict[str, object]
    schema_compatibility: SchemaCompatibilityResponse
    session_backend: str


class AuthContextResponse(AICodingModel):
    token_file: str
    token_source: str


class NodeAuthorityStateResponse(AICodingModel):
    node_id: str
    node_version_id: str | None
    authority: str
    current_state: str
    current_run_id: str
    last_command: str
    last_event_id: str
    updated_at: str
    event_count: int


class NodeLifecycleStateResponse(AICodingModel):
    node_id: str
    node_version_id: str | None
    lifecycle_state: str
    run_status: str | None
    current_run_id: str | None
    current_task_id: str | None
    current_subtask_id: str | None
    current_subtask_attempt: int | None
    last_completed_subtask_id: str | None
    execution_cursor_json: dict[str, object]
    failure_count_from_children: int
    failure_count_consecutive: int
    defer_to_user_threshold: int
    is_resumable: bool
    pause_flag_name: str | None
    working_tree_state: str | None
    updated_at: str


class NodeCreateRequest(AICodingModel):
    kind: str
    title: str
    prompt: str
    parent_node_id: str | None = None


class WorkflowStartRequest(AICodingModel):
    kind: str
    prompt: str = Field(min_length=1)
    title: str | None = None
    start_run: bool = True


class ProjectCatalogEntryResponse(AICodingModel):
    project_id: str
    label: str
    source_path: str
    bootstrap_ready: bool = False
    readiness_code: str
    readiness_message: str | None = None
    default_branch: str | None = None
    head_commit_sha: str | None = None


class ProjectCatalogDaemonContextResponse(AICodingModel):
    reachability_state: str
    auth_status: str
    daemon_app_name: str
    daemon_version: str
    authority: str
    session_backend: str


class ProjectCatalogResponse(AICodingModel):
    daemon_context: ProjectCatalogDaemonContextResponse
    projects: list[ProjectCatalogEntryResponse]


class ProjectBootstrapResponse(AICodingModel):
    project: ProjectCatalogEntryResponse
    root_node_id: str | None = None
    route_hint: ProjectRouteHintResponse | None = None
    top_level_nodes: list["ProjectTopLevelNodeSummaryResponse"] = Field(default_factory=list)


class ProjectTopLevelNodeCreateRequest(AICodingModel):
    kind: str
    title: str | None = Field(default=None, min_length=1, max_length=255)
    prompt: str = Field(min_length=1)
    start_run: bool = True


class ProjectRepoBootstrapResponse(AICodingModel):
    repo_bootstrap_status: str
    worker_repo_path: str
    branch_name: str
    seed_commit_sha: str | None = None
    head_commit_sha: str | None = None
    working_tree_state: str


class NodeSupersedeRequest(AICodingModel):
    title: str | None = None
    prompt: str | None = None
    cancel_active_subtree: bool = False


class CommitRecordRequest(AICodingModel):
    commit_sha: str


class HierarchyNodeResponse(AICodingModel):
    node_id: str
    parent_node_id: str | None
    kind: str
    tier: str
    title: str
    prompt: str
    created_via: str


class MaterializedChildResponse(AICodingModel):
    layout_child_id: str
    node_id: str
    node_version_id: str
    kind: str
    title: str
    lifecycle_state: str
    scheduling_status: str
    scheduling_reason: str | None = None
    blockers: list["DependencyBlockerResponse"] = Field(default_factory=list)


class MaterializationResponse(AICodingModel):
    parent_node_id: str
    parent_node_version_id: str
    layout_relative_path: str
    layout_hash: str
    status: str
    authority_mode: str
    child_count: int
    created_count: int
    ready_child_count: int
    blocked_child_count: int
    children: list[MaterializedChildResponse]


class LayoutRegistrationRequest(AICodingModel):
    file_path: str


class LayoutRegistrationResponse(AICodingModel):
    node_id: str
    node_version_id: str
    status: str
    source_path: str
    registered_path: str
    layout_relative_path: str
    layout_hash: str
    child_count: int
    workflow_event_id: str


class ChildReconciliationRequest(AICodingModel):
    decision: str


class ChildReconciliationResponse(AICodingModel):
    parent_node_id: str
    parent_node_version_id: str
    authority_mode: str
    materialization_status: str
    available_decisions: list[str] = Field(default_factory=list)
    manual_child_count: int
    layout_generated_child_count: int
    layout_relative_path: str
    layout_hash: str
    children: list[MaterializedChildResponse]


class NodeOperatorSummaryResponse(AICodingModel):
    node_id: str
    parent_node_id: str | None
    kind: str
    tier: str
    title: str
    prompt: str
    created_via: str
    lifecycle_state: str | None = None
    run_status: str | None = None
    current_run_id: str | None = None
    current_subtask_id: str | None = None
    current_subtask_attempt: int | None = None
    pause_flag_name: str | None = None
    is_resumable: bool | None = None
    authoritative_node_version_id: str | None = None
    latest_created_node_version_id: str | None = None
    compiled_workflow_id: str | None = None
    active_branch_name: str | None = None
    seed_commit_sha: str | None = None
    final_commit_sha: str | None = None


class TreeNodeResponse(AICodingModel):
    node_id: str
    parent_node_id: str | None = None
    depth: int
    kind: str
    tier: str
    title: str
    authoritative_node_version_id: str | None = None
    latest_created_node_version_id: str | None = None
    lifecycle_state: str | None = None
    run_status: str | None = None
    scheduling_status: str | None = None
    blocker_count: int = 0
    blocker_state: str = "none"
    has_children: bool = False
    child_count: int = 0
    child_rollups: dict[str, int] = Field(default_factory=dict)
    created_at: str
    last_updated_at: str


class TreeCatalogResponse(AICodingModel):
    root_node_id: str
    generated_at: str
    nodes: list[TreeNodeResponse]


class ProjectRouteHintResponse(AICodingModel):
    project_id: str
    node_id: str
    tab: str
    url: str


class ProjectTopLevelNodeSummaryResponse(AICodingModel):
    node_id: str
    kind: str
    tier: str
    title: str
    lifecycle_state: str | None = None
    run_status: str | None = None
    authoritative_node_version_id: str | None = None
    latest_created_node_version_id: str | None = None
    route_hint: ProjectRouteHintResponse


class NodePauseStateResponse(AICodingModel):
    node_id: str
    lifecycle_state: str
    run_status: str | None = None
    current_run_id: str | None = None
    pause_flag_name: str | None = None
    is_resumable: bool
    pause_summary: str | None = None
    approval_required: bool = False
    approved: bool = False
    pause_summary_prompt: str | None = None


class InterventionOptionResponse(AICodingModel):
    action: str
    requires_summary: bool
    label: str


class InterventionResponse(AICodingModel):
    kind: str
    status: str
    subject_key: str
    title: str
    summary: str | None = None
    recommended_action: str | None = None
    available_actions: list[InterventionOptionResponse]
    details_json: dict[str, object]


class InterventionCatalogResponse(AICodingModel):
    node_id: str
    node_version_id: str
    pending_count: int
    interventions: list[InterventionResponse]


class InterventionActionResponse(AICodingModel):
    node_id: str
    node_version_id: str
    intervention_kind: str
    action: str
    status: str
    result_json: dict[str, object]


class NodeActionResponse(AICodingModel):
    action_id: str
    label: str
    group: str
    legal: bool
    blocked_reason: str | None = None
    confirmation_mode: str = "inline"
    confirmation_label: str
    target_scope: str = "selected_node"
    details_json: dict[str, object] = Field(default_factory=dict)


class NodeActionCatalogResponse(AICodingModel):
    node_id: str
    node_version_id: str | None = None
    actions: list[NodeActionResponse]


class NodeEventResponse(AICodingModel):
    id: str
    node_id: str
    command: str
    event_scope: str = "authority"
    previous_state: str | None = None
    resulting_state: str | None = None
    run_id: str | None = None
    payload_json: dict[str, object]
    created_at: str


class NodeEventCatalogResponse(AICodingModel):
    node_id: str
    events: list[NodeEventResponse]


class ChildFailureCounterResponse(AICodingModel):
    child_node_id: str
    child_node_version_id: str
    child_title: str
    child_kind: str
    failure_count: int
    last_failure_at: str | None = None
    last_failure_class: str | None = None
    last_failure_summary: str | None = None
    last_failure_subtask_key: str | None = None
    last_failed_node_run_id: str | None = None
    last_decision_type: str | None = None
    last_decision_at: str | None = None


class ChildFailureCounterCatalogResponse(AICodingModel):
    node_id: str
    node_run_id: str | None = None
    failure_count_from_children: int
    failure_count_consecutive: int
    counters: list[ChildFailureCounterResponse]


class ParentDecisionResponse(AICodingModel):
    id: str
    node_id: str
    node_version_id: str | None = None
    node_run_id: str | None = None
    child_node_id: str | None = None
    child_node_version_id: str | None = None
    child_node_run_id: str | None = None
    failure_class: str | None = None
    failure_origin: str | None = None
    decision_type: str
    decision_source: str | None = None
    decision_reason: str | None = None
    options_considered: list[str] = Field(default_factory=list)
    threshold_triggered: bool = False
    threshold_reason: str | None = None
    summary: str | None = None
    payload_json: dict[str, object]
    created_at: str


class ParentDecisionCatalogResponse(AICodingModel):
    node_id: str
    decisions: list[ParentDecisionResponse]


class ParentFailureDecisionRequest(AICodingModel):
    node_id: str
    child_node_id: str
    requested_action: str | None = None


class ParentFailureDecisionResponse(AICodingModel):
    node_id: str
    node_run_id: str
    child_node_id: str
    child_node_version_id: str
    child_node_run_id: str
    failure_class: str
    failure_origin: str
    decision_type: str
    decision_source: str
    decision_reason: str
    options_considered: list[str]
    threshold_triggered: bool
    threshold_reason: str | None = None
    policy_snapshot: dict[str, int]
    summary: str
    parent_lifecycle_state: str
    parent_run_status: str
    child_lifecycle_state: str
    post_action_status: str | None = None
    counters: ChildFailureCounterCatalogResponse


class NodeKindDefinitionResponse(AICodingModel):
    kind: str
    tier: str
    description: str
    allow_parentless: bool
    allowed_parent_kinds: list[str]
    allowed_child_kinds: list[str]


class NodeKindCatalogResponse(AICodingModel):
    definitions: list[NodeKindDefinitionResponse]
    top_level_kinds: list[str]


class NodeVersionResponse(AICodingModel):
    id: str
    logical_node_id: str
    parent_node_version_id: str | None
    tier: str
    node_kind: str
    title: str
    prompt: str
    description: str | None
    status: str
    version_number: int
    compiled_workflow_id: str | None = None
    supersedes_node_version_id: str | None
    active_branch_name: str | None
    branch_generation_number: int | None
    seed_commit_sha: str | None
    final_commit_sha: str | None


class NodeVersionCatalogResponse(AICodingModel):
    versions: list[NodeVersionResponse]


class NodeLineageResponse(AICodingModel):
    logical_node_id: str
    authoritative_node_version_id: str
    latest_created_node_version_id: str
    versions: list[NodeVersionResponse]


class GitBranchResponse(AICodingModel):
    node_version_id: str
    logical_node_id: str
    version_number: int
    title: str
    tier: str
    node_kind: str
    node_status: str
    active_branch_name: str | None
    expected_branch_name: str
    branch_generation_number: int | None
    expected_branch_generation_number: int
    seed_commit_sha: str | None
    final_commit_sha: str | None
    branch_status: str
    violations: list[str]


class MergeEventResponse(AICodingModel):
    id: str
    parent_node_version_id: str
    child_node_version_id: str
    child_final_commit_sha: str
    parent_commit_before: str
    parent_commit_after: str
    merge_order: int
    had_conflict: bool
    created_at: str


class MergeEventCatalogResponse(AICodingModel):
    node_id: str
    events: list[MergeEventResponse]


class MergeConflictRecordRequest(AICodingModel):
    parent_node_version_id: str
    child_node_version_id: str
    child_final_commit_sha: str
    parent_commit_before: str
    parent_commit_after: str
    merge_order: int = Field(ge=1)
    files_json: list[str]
    merge_base_sha: str | None = None


class MergeConflictResolveRequest(AICodingModel):
    resolution_summary: str
    resolution_status: str = "resolved"


class MergeConflictResponse(AICodingModel):
    id: str
    merge_event_id: str
    parent_node_version_id: str
    child_node_version_id: str
    files_json: list[str]
    merge_base_sha: str | None = None
    resolution_summary: str | None = None
    resolution_status: str
    created_at: str


class MergeConflictCatalogResponse(AICodingModel):
    node_id: str | None = None
    node_version_id: str | None = None
    conflicts: list[MergeConflictResponse]


class ChildResultResponse(AICodingModel):
    layout_child_id: str
    child_node_id: str
    child_node_version_id: str
    edge_child_node_version_id: str
    origin_type: str
    ordinal: int | None = None
    child_kind: str
    child_title: str
    lifecycle_state: str | None = None
    run_status: str | None = None
    final_commit_sha: str | None = None
    latest_summary: str | None = None
    latest_child_session_summary: str | None = None
    reconcile_status: str
    merge_order: int | None = None
    dependency_child_node_ids: list[str]
    blocking_reasons: list[str]


class ChildResultCollectionResponse(AICodingModel):
    parent_node_id: str
    parent_node_version_id: str
    authority_mode: str
    status: str
    ready_child_count: int
    waiting_child_count: int
    failed_child_count: int
    paused_child_count: int
    invalid_child_count: int
    reusable_final_count: int
    children: list[ChildResultResponse]


class ParentReconcileResponse(AICodingModel):
    parent_node_id: str
    parent_node_version_id: str
    status: str
    seed_commit_sha: str | None = None
    prompt_relative_path: str
    prompt_text: str
    child_results: ChildResultCollectionResponse
    blocking_reasons: list[str]
    merge_events: list[MergeEventResponse]
    last_reconciled_at: str | None = None
    context_json: dict[str, object]


class LiveGitStatusResponse(AICodingModel):
    node_id: str
    node_version_id: str
    repo_path: str
    branch_name: str
    head_commit_sha: str | None = None
    seed_commit_sha: str | None = None
    final_commit_sha: str | None = None
    working_tree_state: str


class LiveGitBootstrapRequest(AICodingModel):
    version_id: str
    base_version_id: str | None = None
    replace_existing: bool = False
    files_json: dict[str, str] = Field(default_factory=dict)


class LiveGitFinalizeResponse(AICodingModel):
    node_id: str
    node_version_id: str
    status: str
    repo_path: str
    final_commit_sha: str
    working_tree_state: str


class RebuildEventResponse(AICodingModel):
    id: str
    root_logical_node_id: str
    root_node_version_id: str
    target_node_version_id: str
    event_kind: str
    event_status: str
    scope: str
    trigger_reason: str
    details_json: dict[str, object]
    created_at: str


class RebuildHistoryResponse(AICodingModel):
    node_id: str
    events: list[RebuildEventResponse]


class RebuildCoordinationBlockerResponse(AICodingModel):
    blocker_type: str
    node_id: str
    node_version_id: str
    node_kind: str
    node_title: str
    scope_role: str
    lifecycle_state: str | None = None
    run_status: str | None = None
    current_run_id: str | None = None
    active_primary_session_count: int
    active_primary_session_ids: list[str]


class RebuildCoordinationResponse(AICodingModel):
    node_id: str
    scope: str
    status: str
    blockers: list[RebuildCoordinationBlockerResponse]


class CutoverBlockerResponse(AICodingModel):
    blocker_type: str
    details_json: dict[str, object]


class CutoverReadinessResponse(AICodingModel):
    logical_node_id: str
    node_version_id: str
    current_authoritative_node_version_id: str
    status: str
    blockers: list[CutoverBlockerResponse]
    stable_rebuild_event_present: bool
    unresolved_merge_conflicts: bool


class RegenerationResponse(AICodingModel):
    root_node_id: str
    root_node_version_id: str
    scope: str
    trigger_reason: str
    created_candidate_version_ids: list[str]
    stable_candidate_version_ids: list[str]
    rebuild_history: list[RebuildEventResponse]


class SourceDocumentResponse(AICodingModel):
    id: str
    source_group: str
    relative_path: str
    doc_family: str
    source_role: str
    merge_mode: str
    content_hash: str
    resolution_order: int
    is_resolved_input: bool


class NodeVersionSourceLineageResponse(AICodingModel):
    node_version_id: str
    logical_node_id: str
    source_documents: list[SourceDocumentResponse]


class NodeDependencyResponse(AICodingModel):
    id: str
    node_version_id: str
    depends_on_node_version_id: str
    dependency_type: str
    required_state: str


class NodeDependencyCatalogResponse(AICodingModel):
    node_id: str
    node_version_id: str
    dependencies: list[NodeDependencyResponse]


class DependencyBlockerResponse(AICodingModel):
    blocker_kind: str
    dependency_id: str | None = None
    node_version_id: str
    target_node_version_id: str | None = None
    details_json: dict[str, object]


class DependencyReadinessResponse(AICodingModel):
    node_id: str
    node_version_id: str
    status: str
    blockers: list[DependencyBlockerResponse]


class DependencyValidationResponse(AICodingModel):
    node_id: str
    node_version_id: str
    status: str
    dependencies: list[NodeDependencyResponse]
    blockers: list[DependencyBlockerResponse]


class NodeRunAdmissionResponse(AICodingModel):
    node_id: str
    node_version_id: str
    status: str
    reason: str | None = None
    current_state: str | None = None
    current_run_id: str | None = None
    blockers: list[DependencyBlockerResponse]


class NodeRunResponse(AICodingModel):
    id: str
    node_version_id: str
    logical_node_id: str
    run_number: int
    trigger_reason: str
    run_status: str
    compiled_workflow_id: str
    started_at: str | None = None
    ended_at: str | None = None
    summary: str | None = None


class NodeRunStateResponse(AICodingModel):
    node_run_id: str
    lifecycle_state: str
    current_task_id: str | None = None
    current_compiled_subtask_id: str | None = None
    current_subtask_attempt: int | None = None
    last_completed_compiled_subtask_id: str | None = None
    execution_cursor_json: dict[str, object]
    failure_count_from_children: int
    failure_count_consecutive: int
    defer_to_user_threshold: int | None = None
    pause_flag_name: str | None = None
    is_resumable: bool
    working_tree_state: str | None = None
    updated_at: str


class SubtaskAttemptResponse(AICodingModel):
    id: str
    node_run_id: str
    compiled_subtask_id: str
    attempt_number: int
    status: str
    input_context_json: dict[str, object] | None = None
    output_json: dict[str, object] | None = None
    execution_result_json: dict[str, object] | None = None
    execution_environment_json: dict[str, object] | None = None
    validation_json: dict[str, object] | None = None
    review_json: dict[str, object] | None = None
    testing_json: dict[str, object] | None = None
    summary: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


class RunProgressResponse(AICodingModel):
    run: NodeRunResponse
    state: NodeRunStateResponse
    current_subtask: dict[str, object] | None = None
    latest_attempt: SubtaskAttemptResponse | None = None
    terminal_failure: dict[str, object] | None = None


class CompositeStageOutcomeResponse(AICodingModel):
    node_id: str
    node_run_id: str
    accepted_compiled_subtask_id: str
    accepted_subtask_type: str
    recorded_summary_id: str
    recorded_summary_path: str
    outcome: str
    progress: RunProgressResponse


class SubtaskAttemptCatalogResponse(AICodingModel):
    node_id: str
    node_run_id: str
    attempts: list[SubtaskAttemptResponse]


class SubtaskPromptResponse(AICodingModel):
    node_id: str
    node_run_id: str
    compiled_subtask_id: str
    prompt_id: str
    source_subtask_key: str
    title: str | None = None
    subtask_type: str
    prompt_text: str | None = None
    command_text: str | None = None
    environment_request_json: dict[str, object] | None = None
    stage_context_json: dict[str, object] = Field(default_factory=dict)


class SubtaskContextResponse(AICodingModel):
    node_id: str
    node_run_id: str
    compiled_subtask_id: str
    attempt_number: int | None = None
    input_context_json: dict[str, object]
    latest_summary: str | None = None
    stage_context_json: dict[str, object] = Field(default_factory=dict)


class SummaryRegistrationRequest(AICodingModel):
    node_id: str
    summary_type: str
    summary_path: str
    content: str


class SummaryRegistrationResponse(AICodingModel):
    summary_id: str
    node_id: str
    node_run_id: str
    compiled_subtask_id: str
    attempt_number: int
    summary_type: str
    summary_path: str
    content_hash: str
    content_length: int
    registered_at: str


class ValidationResultResponse(AICodingModel):
    id: str
    node_version_id: str
    node_run_id: str | None = None
    compiled_subtask_id: str | None = None
    check_type: str
    status: str
    evidence_json: dict[str, object] | None = None
    summary: str | None = None
    created_at: str


class ValidationSummaryResponse(AICodingModel):
    node_id: str
    node_version_id: str
    node_run_id: str | None = None
    compiled_subtask_id: str | None = None
    status: str
    passed_count: int
    failed_count: int
    results: list[ValidationResultResponse]


class ValidationResultCatalogResponse(AICodingModel):
    node_id: str
    results: list[ValidationResultResponse]


class ReviewResultResponse(AICodingModel):
    id: str
    node_version_id: str
    node_run_id: str | None = None
    compiled_subtask_id: str | None = None
    review_definition_id: str | None = None
    scope: str
    status: str
    criteria_json: list[dict[str, object]] | dict[str, object] | None = None
    findings_json: list[dict[str, object]] | None = None
    summary: str | None = None
    action: str | None = None
    created_at: str


class ReviewSummaryResponse(AICodingModel):
    node_id: str
    node_version_id: str
    node_run_id: str | None = None
    compiled_subtask_id: str | None = None
    status: str
    action: str | None = None
    passed_count: int
    revise_count: int
    failed_count: int
    results: list[ReviewResultResponse]


class ReviewResultCatalogResponse(AICodingModel):
    node_id: str
    results: list[ReviewResultResponse]


class TestResultResponse(AICodingModel):
    id: str
    node_version_id: str
    node_run_id: str | None = None
    compiled_subtask_id: str | None = None
    testing_definition_id: str | None = None
    suite_name: str | None = None
    status: str
    attempt_number: int | None = None
    results_json: dict[str, object] | list[dict[str, object]] | None = None
    summary: str | None = None
    action: str | None = None
    created_at: str


class TestingSummaryResponse(AICodingModel):
    node_id: str
    node_version_id: str
    node_run_id: str | None = None
    compiled_subtask_id: str | None = None
    status: str
    action: str | None = None
    passed_count: int
    failed_count: int
    retry_allowed: bool
    retry_pending: bool
    attempt_number: int | None = None
    max_attempts: int | None = None
    rerun_failed_only: bool
    results: list[TestResultResponse]


class TestResultCatalogResponse(AICodingModel):
    node_id: str
    results: list[TestResultResponse]


class QualityChainResponse(AICodingModel):
    node_id: str
    node_version_id: str
    node_run_id: str
    run_status: str
    executed_stage_types: list[str]
    validation: ValidationSummaryResponse
    review: ReviewSummaryResponse
    testing: TestingSummaryResponse
    provenance: dict[str, object] | None = None
    docs: list[dict[str, object]] = Field(default_factory=list)
    final_summary: dict[str, object] | None = None
    progress: dict[str, object]


class NodeRunCatalogResponse(AICodingModel):
    node_id: str
    runs: list[NodeRunResponse]


class PromptHistoryRecordResponse(AICodingModel):
    id: str
    node_version_id: str
    node_run_id: str
    compiled_subtask_id: str | None = None
    prompt_role: str
    source_subtask_key: str | None = None
    template_path: str | None = None
    template_hash: str | None = None
    content: str
    content_hash: str
    payload_json: dict[str, object]
    delivered_at: str


class PromptHistoryCatalogResponse(AICodingModel):
    node_id: str
    prompts: list[PromptHistoryRecordResponse]


class SummaryHistoryRecordResponse(AICodingModel):
    id: str
    node_version_id: str
    node_run_id: str | None = None
    compiled_subtask_id: str | None = None
    attempt_number: int | None = None
    summary_type: str
    summary_scope: str
    summary_path: str | None = None
    content: str
    content_hash: str
    metadata_json: dict[str, object]
    created_at: str


class SummaryHistoryCatalogResponse(AICodingModel):
    node_id: str
    summaries: list[SummaryHistoryRecordResponse]


class ProvenanceRefreshResponse(AICodingModel):
    node_id: str
    node_version_id: str
    prompt_record_id: str | None = None
    summary_record_id: str | None = None
    provenance_summary_id: str
    rationale_summary: str
    entity_count: int
    relation_count: int
    change_counts: dict[str, int]


class EntityResponse(AICodingModel):
    id: str
    entity_type: str
    canonical_name: str
    file_path: str | None = None
    signature: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    stable_hash: str | None = None
    created_at: str
    updated_at: str


class EntityCatalogResponse(AICodingModel):
    canonical_name: str
    entities: list[EntityResponse]


class EntityHistoryEntryResponse(AICodingModel):
    id: str
    node_version_id: str
    logical_node_id: str
    entity_id: str
    prompt_record_id: str | None = None
    summary_record_id: str | None = None
    change_type: str
    match_confidence: str
    match_reason: str
    rationale_summary: str | None = None
    observed_canonical_name: str
    observed_file_path: str | None = None
    observed_signature: str | None = None
    observed_stable_hash: str | None = None
    metadata_json: dict[str, object]
    created_at: str


class EntityHistoryCatalogResponse(AICodingModel):
    canonical_name: str
    history: list[EntityHistoryEntryResponse]


class EntityRelationResponse(AICodingModel):
    id: str
    node_version_id: str
    from_entity_id: str
    from_canonical_name: str
    to_entity_id: str
    to_canonical_name: str
    relation_type: str
    source: str
    confidence: float | None = None
    rationale_summary: str | None = None
    created_at: str


class EntityRelationCatalogResponse(AICodingModel):
    canonical_name: str
    relations: list[EntityRelationResponse]


class RationaleResponse(AICodingModel):
    node_id: str
    node_version_id: str
    prompt_record_id: str | None = None
    summary_record_id: str | None = None
    rationale_summary: str
    change_counts: dict[str, int]
    entity_history: list[EntityHistoryEntryResponse]


class DocumentationOutputResponse(AICodingModel):
    id: str
    logical_node_id: str
    node_version_id: str
    doc_definition_id: str | None = None
    scope: str
    view_name: str
    output_path: str
    content: str
    content_hash: str
    metadata_json: dict[str, object]
    created_at: str


class DocumentationCatalogResponse(AICodingModel):
    node_id: str
    documents: list[DocumentationOutputResponse]


class DocumentationBuildResponse(AICodingModel):
    node_id: str
    node_version_id: str
    mode: str
    documents: list[DocumentationOutputResponse]


class WorkflowEventResponse(AICodingModel):
    id: str
    logical_node_id: str
    node_version_id: str | None = None
    node_run_id: str | None = None
    event_scope: str
    event_type: str
    payload_json: dict[str, object]
    created_at: str


class HistoricalSessionResponse(AICodingModel):
    session_id: str
    logical_node_id: str | None = None
    node_version_id: str
    node_run_id: str | None = None
    node_kind: str | None = None
    node_title: str | None = None
    run_status: str | None = None
    session_role: str
    provider: str
    provider_session_id: str | None = None
    tmux_session_name: str | None = None
    cwd: str | None = None
    status: str
    started_at: str
    last_heartbeat_at: str | None = None
    ended_at: str | None = None
    event_count: int
    latest_event_type: str | None = None
    backend: str
    pane_text: str | None = None
    idle_seconds: float | None = None
    in_alt_screen: bool | None = None
    tmux_session_exists: bool | None = None
    tmux_process_alive: bool | None = None
    tmux_exit_status: int | None = None
    attach_command: str | None = None
    screen_state: dict[str, object] | None = None
    recovery_classification: str | None = None
    recommended_action: str | None = None
    terminal_failure: dict[str, object] | None = None


class SessionAuditResponse(AICodingModel):
    session: HistoricalSessionResponse
    events: list[SessionEventResponse]


class NodeAuditResponse(AICodingModel):
    node_id: str
    node_summary: NodeOperatorSummaryResponse
    lineage: NodeLineageResponse
    authoritative_version_id: str
    current_workflow: CompiledWorkflowResponse | None = None
    workflow_chain: WorkflowChainResponse | None = None
    source_lineage: NodeVersionSourceLineageResponse
    compile_failures: list[CompileFailureResponse]
    workflow_events: list[WorkflowEventResponse]
    prompt_history: PromptHistoryCatalogResponse
    summary_history: SummaryHistoryCatalogResponse
    validation_results: list[ValidationResultResponse]
    review_results: list[ReviewResultResponse]
    test_results: list[TestResultResponse]
    sessions: list[SessionAuditResponse]
    rebuild_history: list[RebuildEventResponse]
    merge_events: list[MergeEventResponse]
    merge_conflicts: list[MergeConflictResponse]
    documentation_outputs: list[DocumentationOutputResponse]
    run_count: int


class RunAuditResponse(AICodingModel):
    node_id: str
    node_version_id: str
    node_run_id: str
    run: NodeRunResponse
    state: NodeRunStateResponse
    workflow: CompiledWorkflowResponse | None = None
    source_lineage: NodeVersionSourceLineageResponse
    attempts: list[SubtaskAttemptResponse]
    workflow_events: list[WorkflowEventResponse]
    prompts: list[PromptHistoryRecordResponse]
    summaries: list[SummaryHistoryRecordResponse]
    validation_results: list[ValidationResultResponse]
    review_results: list[ReviewResultResponse]
    test_results: list[TestResultResponse]
    sessions: list[SessionAuditResponse]


class CompiledSubtaskResponse(AICodingModel):
    id: str
    compiled_task_id: str
    source_subtask_key: str
    ordinal: int
    subtask_type: str
    title: str | None
    prompt_text: str | None
    command_text: str | None = None
    environment_policy_ref: str | None = None
    environment_request_json: dict[str, object] | None = None
    retry_policy_json: dict[str, object] | None = None
    block_on_user_flag: str | None = None
    pause_summary_prompt: str | None = None
    source_file_path: str | None = None
    source_hash: str | None = None
    inserted_by_hook: bool = False
    inserted_by_hook_id: str | None = None
    depends_on_compiled_subtask_ids: list[str] = Field(default_factory=list)


class CompiledTaskResponse(AICodingModel):
    id: str
    task_key: str
    ordinal: int
    title: str | None
    description: str | None
    config_json: dict[str, object]
    subtasks: list[CompiledSubtaskResponse]


class CompiledWorkflowResponse(AICodingModel):
    id: str
    node_version_id: str
    logical_node_id: str
    source_hash: str
    built_in_library_version: str
    created_at: str
    source_document_count: int
    task_count: int
    subtask_count: int
    compile_context: dict[str, object]
    resolved_yaml: dict[str, object]
    tasks: list[CompiledTaskResponse]


class WorkflowChainEntryResponse(AICodingModel):
    compiled_task_id: str
    compiled_subtask_id: str
    task_key: str
    task_ordinal: int
    subtask_ordinal: int
    subtask_type: str
    title: str | None
    depends_on_compiled_subtask_ids: list[str] = Field(default_factory=list)
    derived_execution_state: str | None = None
    latest_attempt_number: int | None = None
    latest_attempt_status: str | None = None
    is_current: bool = False
    latest_summary: str | None = None
    pause_flag_name: str | None = None


class WorkflowChainResponse(AICodingModel):
    compiled_workflow_id: str
    node_version_id: str
    logical_node_id: str
    compile_context: dict[str, object]
    chain: list[WorkflowChainEntryResponse]


class CompileFailureResponse(AICodingModel):
    id: str
    node_version_id: str
    logical_node_id: str
    failure_stage: str
    failure_class: str
    summary: str
    details_json: dict[str, object]
    source_hash: str | None = None
    target_family: str | None = None
    target_id: str | None = None
    compile_context: dict[str, object]
    created_at: str


class CompileFailureCatalogResponse(AICodingModel):
    failures: list[CompileFailureResponse]


class WorkflowCompileAttemptResponse(AICodingModel):
    status: str
    node_version_id: str
    logical_node_id: str
    compile_context: dict[str, object]
    compiled_workflow: CompiledWorkflowResponse | None = None
    compile_failure: CompileFailureResponse | None = None


class WorkflowStartResponse(AICodingModel):
    status: str
    requested_start_run: bool
    resolved_title: str
    node: HierarchyNodeResponse
    node_version_id: str
    compile: WorkflowCompileAttemptResponse
    lifecycle: NodeLifecycleStateResponse
    run_admission: NodeRunAdmissionResponse | None = None
    run_progress: RunProgressResponse | None = None
    session: SessionStateResponse | None = None


class ProjectTopLevelNodeCreateResponse(AICodingModel):
    status: str
    requested_start_run: bool
    resolved_title: str
    project: ProjectCatalogEntryResponse
    source_repo: ProjectCatalogEntryResponse
    bootstrap: ProjectRepoBootstrapResponse
    node: HierarchyNodeResponse
    node_version_id: str
    compile: WorkflowCompileAttemptResponse
    lifecycle: NodeLifecycleStateResponse
    run_admission: NodeRunAdmissionResponse | None = None
    run_progress: RunProgressResponse | None = None
    session: SessionStateResponse | None = None
    route_hint: ProjectRouteHintResponse


class EnvironmentPolicyResponse(AICodingModel):
    relative_path: str
    policy_id: str
    isolation_mode: str
    allow_network: bool
    runtime_profile: str | None = None
    mandatory: bool
    profile_declared: bool


class EnvironmentPolicyCatalogResponse(AICodingModel):
    policies: list[EnvironmentPolicyResponse]


class CurrentSubtaskEnvironmentResponse(AICodingModel):
    compiled_subtask_id: str
    environment_policy_ref: str | None = None
    environment_request: dict[str, object]


class AttemptEnvironmentResponse(AICodingModel):
    attempt_id: str
    compiled_subtask_id: str
    attempt_number: int
    status: str
    execution_environment: dict[str, object]


class WorkflowHookResponse(AICodingModel):
    hook_id: str
    when: str
    relative_path: str
    source_group: str
    applies_to: dict[str, object]
    run_steps: list[dict[str, object]]
    source_hash: str | None = None


class WorkflowHookSkipResponse(AICodingModel):
    hook_id: str
    when: str
    relative_path: str
    source_group: str
    reason: str


class WorkflowHookStepResponse(AICodingModel):
    hook_id: str
    when: str
    relative_path: str
    source_group: str
    insertion_phase: str
    task_key: str
    source_subtask_key: str
    subtask_type: str
    prompt_path: str | None = None
    command_text: str | None = None
    render_context: dict[str, object] = Field(default_factory=dict)
    checks: list[dict[str, object]] = Field(default_factory=list)
    source_hash: str | None = None


class WorkflowHookCatalogResponse(AICodingModel):
    compiled_workflow_id: str
    node_version_id: str
    logical_node_id: str
    compile_context: dict[str, object]
    selected_hooks: list[WorkflowHookResponse]
    skipped_hooks: list[WorkflowHookSkipResponse]
    expanded_steps: list[WorkflowHookStepResponse]


class ProjectPolicyResponse(AICodingModel):
    relative_path: str
    policy_id: str
    description: str
    defaults: dict[str, object]
    runtime_policy_refs: list[str]
    hook_refs: list[str]
    review_refs: list[str]
    testing_refs: list[str]
    docs_refs: list[str]
    enabled_node_kinds: list[str]
    prompt_pack: str
    environment_profiles: list[str]


class ProjectPolicyCatalogResponse(AICodingModel):
    policies: list[ProjectPolicyResponse]


class EffectivePolicyResponse(AICodingModel):
    base_policy_id: str
    project_policy_ids: list[str]
    defaults: dict[str, object]
    runtime_policy_refs: list[str]
    hook_refs: list[str]
    review_refs: list[str]
    testing_refs: list[str]
    docs_refs: list[str]
    enabled_node_kinds: list[str]
    prompt_pack: str
    environment_profiles: list[str]


class PolicyImpactResponse(AICodingModel):
    node_kind: str
    project_policy_ids: list[str]
    changed_defaults: dict[str, object]
    added_runtime_policy_refs: list[str]
    added_hook_refs: list[str]
    added_review_refs: list[str]
    added_testing_refs: list[str]
    added_docs_refs: list[str]
    enabled_for_node_kind: bool
    prompt_pack: str


class OverrideApplicationResponse(AICodingModel):
    override_relative_path: str
    override_id: str | None = None
    target_family: str
    target_id: str
    merge_mode: str
    field_names: list[str]
    compatibility: dict[str, object]
    warnings: list[str]


class OverrideChainResponse(AICodingModel):
    compiled_workflow_id: str
    node_version_id: str
    logical_node_id: str
    compile_context: dict[str, object]
    applied_overrides: list[OverrideApplicationResponse]
    warnings: list[str]


class ResolvedYamlDocumentResponse(AICodingModel):
    target_family: str
    target_id: str
    relative_path: str
    source_group: str
    source_role: str
    resolved_document: dict[str, object]
    applied_override_paths: list[str]


class ResolvedYamlCatalogResponse(AICodingModel):
    compiled_workflow_id: str
    node_version_id: str
    logical_node_id: str
    compile_context: dict[str, object]
    resolved_documents: list[ResolvedYamlDocumentResponse]
    warnings: list[str]


class YamlValidationRequest(AICodingModel):
    source_group: str
    relative_path: str


class YamlValidationIssueResponse(AICodingModel):
    message: str
    location: list[str | int]


class YamlValidationResponse(AICodingModel):
    record_id: str
    source_group: str
    relative_path: str
    family: str
    valid: bool
    issue_count: int
    issues: list[YamlValidationIssueResponse]
    validated_at: str


class YamlSchemaCatalogResponse(AICodingModel):
    definitions: list[dict[str, object]]
