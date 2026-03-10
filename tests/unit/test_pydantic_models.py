from __future__ import annotations

import pytest
from pydantic import ValidationError

from aicoding.daemon.models import (
    ApiErrorResponse,
    ChildFailureCounterCatalogResponse,
    ChildFailureCounterResponse,
    ChildSessionResultResponse,
    ChildSessionResponse,
    DaemonStatusResponse,
    DocumentationBuildResponse,
    DocumentationCatalogResponse,
    DocumentationOutputResponse,
    GitBranchResponse,
    MutationEnvelope,
    ParentDecisionCatalogResponse,
    ParentDecisionResponse,
    ParentFailureDecisionResponse,
    ProvenanceRefreshResponse,
    PromptHistoryCatalogResponse,
    PromptHistoryRecordResponse,
    ProviderSessionRecoveryActionResponse,
    ProviderSessionRecoveryStatusResponse,
    RationaleResponse,
    SchemaCompatibilityResponse,
    SessionRecoveryActionResponse,
    SessionRecoveryStatusResponse,
    SessionStateResponse,
    EntityCatalogResponse,
    EntityHistoryCatalogResponse,
    EntityHistoryEntryResponse,
    EntityRelationCatalogResponse,
    EntityRelationResponse,
    EntityResponse,
    SubtaskPromptResponse,
    SummaryHistoryCatalogResponse,
    SummaryHistoryRecordResponse,
    SummaryRegistrationResponse,
)
from aicoding.resources import load_resource_catalog


def test_mutation_envelope_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        MutationEnvelope.model_validate({"node_id": "node-1", "unexpected": True})


def test_daemon_status_response_serializes_stably() -> None:
    response = DaemonStatusResponse(
        status="ok",
        authority="daemon",
        background_tasks=["session_recovery"],
        write_probe={"write_path": "available"},
        schema_compatibility=SchemaCompatibilityResponse(
            current_revision="0028_subtask_execution_results",
            expected_revision="0028_subtask_execution_results",
            status="up_to_date",
            compatible=True,
        ),
        session_backend="fake",
    )

    assert response.model_dump() == {
        "status": "ok",
        "authority": "daemon",
        "background_tasks": ["session_recovery"],
        "write_probe": {"write_path": "available"},
        "schema_compatibility": {
            "current_revision": "0028_subtask_execution_results",
            "expected_revision": "0028_subtask_execution_results",
            "status": "up_to_date",
            "compatible": True,
        },
        "session_backend": "fake",
    }

    assert ApiErrorResponse(error="daemon_unavailable", message="database unavailable").model_dump_json()


def test_resource_catalog_builds_typed_resource_metadata() -> None:
    catalog = load_resource_catalog()

    descriptor = catalog.describe("yaml_builtin_system", "nodes/epic.yaml")
    loaded = catalog.load_text("prompt_pack_default", "layouts/generate_phase_layout.md")
    yaml_metadata = catalog.yaml_metadata("yaml_builtin_system", "nodes/epic.yaml")
    prompt_metadata = catalog.prompt_metadata("prompt_pack_default", "layouts/generate_phase_layout.md")

    assert descriptor.model_dump()["group"] == "yaml_builtin_system"
    assert descriptor.absolute_path.name == "epic.yaml"
    assert "phase layout" in loaded.content
    assert yaml_metadata.model_dump() == {
        "source_group": "yaml_builtin_system",
        "family": "nodes",
        "relative_path": "nodes/epic.yaml",
        "extension": ".yaml",
    }
    assert prompt_metadata.model_dump() == {
        "source_group": "prompt_pack_default",
        "scope": "layouts",
        "pack": "default",
        "relative_path": "layouts/generate_phase_layout.md",
        "extension": ".md",
    }


def test_git_branch_response_serializes_stably() -> None:
    response = GitBranchResponse(
        node_version_id="version-1",
        logical_node_id="node-1",
        version_number=1,
        title="Epic",
        tier="epic",
        node_kind="epic",
        node_status="authoritative",
        active_branch_name="tier/epic/epic/epic__abc123/v1",
        expected_branch_name="tier/epic/epic/epic__abc123/v1",
        branch_generation_number=1,
        expected_branch_generation_number=1,
        seed_commit_sha="abcdef1",
        final_commit_sha="1234abc",
        branch_status="valid",
        violations=[],
    )

    assert response.model_dump()["branch_status"] == "valid"


def test_documentation_responses_serialize_stably() -> None:
    output = DocumentationOutputResponse(
        id="doc-1",
        logical_node_id="node-1",
        node_version_id="version-1",
        doc_definition_id="build_local_node_docs",
        scope="local",
        view_name="local_node",
        output_path="docs/generated/node.md",
        content="# Node",
        content_hash="abc123",
        metadata_json={"description": "doc"},
        created_at="2026-03-09T00:00:00+00:00",
    )
    catalog = DocumentationCatalogResponse(node_id="node-1", documents=[output])
    build = DocumentationBuildResponse(node_id="node-1", node_version_id="version-1", mode="node", documents=[output])

    assert catalog.model_dump()["documents"][0]["scope"] == "local"
    assert build.model_dump()["mode"] == "node"


def test_session_recovery_response_serializes_stably() -> None:
    response = SessionRecoveryActionResponse(
        status="reused_existing_session",
        recovery_status=SessionRecoveryStatusResponse(
            node_id="node-1",
            node_version_id="version-1",
            node_run_id="run-1",
            session_id="session-1",
            recovery_classification="healthy",
            recommended_action="resume_existing_session",
            reason=None,
            is_resumable=True,
            pause_flag_name=None,
            tmux_session_name="node-node-1",
            tmux_session_exists=True,
            provider="fake",
            provider_session_id_present=False,
            heartbeat_age_seconds=1.5,
            duplicate_active_primary_sessions=1,
        ),
        session=SessionStateResponse(
            backend="fake",
            session_name="node-node-1",
            status="resumed",
            session_id="session-1",
            node_run_id="run-1",
            node_version_id="version-1",
            session_role="primary",
            provider="fake",
            last_heartbeat_at="2026-03-08T00:00:00+00:00",
            event_count=4,
            latest_event_type="recovery_resumed_existing",
            recovery_classification="healthy",
            pane_text="$ session-ready\n",
            idle_seconds=1.5,
            in_alt_screen=False,
        ),
    )

    assert response.model_dump()["recovery_status"]["recovery_classification"] == "healthy"
    assert response.model_dump()["session"]["status"] == "resumed"


def test_provider_session_recovery_response_serializes_stably() -> None:
    recovery_status = SessionRecoveryStatusResponse(
        node_id="node-1",
        node_version_id="version-1",
        node_run_id="run-1",
        session_id="session-1",
        recovery_classification="lost",
        recommended_action="create_replacement_session",
        reason="tmux_session_missing",
        is_resumable=True,
        pause_flag_name=None,
        tmux_session_name="missing-session",
        tmux_session_exists=False,
        provider="fake",
        provider_session_id_present=True,
        heartbeat_age_seconds=3.0,
        duplicate_active_primary_sessions=1,
    )
    response = ProviderSessionRecoveryActionResponse(
        status="provider_session_rebound",
        provider_recovery_status=ProviderSessionRecoveryStatusResponse(
            node_id="node-1",
            node_version_id="version-1",
            node_run_id="run-1",
            session_id="session-1",
            provider="fake",
            provider_session_id="provider-1",
            provider_supported=True,
            provider_session_exists=True,
            tmux_session_name="missing-session",
            tmux_session_exists=False,
            provider_rebind_possible=True,
            provider_recommended_action="rebind_provider_session",
            provider_reason="provider_session_restorable",
            recovery_status=recovery_status,
        ),
        recovery_status=recovery_status,
        session=SessionStateResponse(
            backend="fake",
            session_name="provider-1",
            status="resumed",
            session_id="session-1",
            node_run_id="run-1",
            node_version_id="version-1",
            session_role="primary",
            provider="fake",
            provider_session_id="provider-1",
            last_heartbeat_at="2026-03-08T00:00:00+00:00",
            event_count=6,
            latest_event_type="provider_recovery_rebound",
            recovery_classification="healthy",
            pane_text="$ provider-ready\n",
            idle_seconds=1.0,
            in_alt_screen=False,
        ),
    )

    assert response.model_dump()["provider_recovery_status"]["provider_rebind_possible"] is True
    assert response.model_dump()["provider_recovery_status"]["recovery_status"]["recovery_classification"] == "lost"
    assert response.model_dump()["session"]["provider_session_id"] == "provider-1"


def test_child_session_models_serialize_stably() -> None:
    session_response = ChildSessionResponse(
        session_id="child-1",
        parent_session_id="parent-1",
        node_run_id="run-1",
        node_version_id="version-1",
        parent_compiled_subtask_id="subtask-1",
        reason="research_context",
        status="bound",
        tmux_session_name="child-abc",
        provider="fake",
        delegated_prompt_path="runtime/delegated_child_session.md",
        pane_text="$ child-session-ready\n",
        idle_seconds=0.0,
        in_alt_screen=False,
        started_at="2026-03-08T00:00:00+00:00",
        ended_at=None,
    )
    result_response = ChildSessionResultResponse(
        child_session_id="child-1",
        parent_compiled_subtask_id="subtask-1",
        status="success",
        summary="research done",
        findings=["one"],
        artifacts=[{"path": "notes/research.md", "type": "notes"}],
        suggested_next_actions=["continue"],
        recorded_at="2026-03-08T00:00:01+00:00",
    )

    assert session_response.model_dump()["reason"] == "research_context"
    assert result_response.model_dump()["artifacts"][0]["type"] == "notes"


def test_prompt_and_summary_history_models_serialize_stably() -> None:
    prompt_response = SubtaskPromptResponse(
        node_id="node-1",
        node_run_id="run-1",
        compiled_subtask_id="subtask-1",
        prompt_id="prompt-1",
        source_subtask_key="research_context.main",
        title="Research",
        subtask_type="run_prompt",
        prompt_text="Do the work",
        command_text=None,
    )
    summary_response = SummaryRegistrationResponse(
        summary_id="summary-1",
        node_id="node-1",
        node_run_id="run-1",
        compiled_subtask_id="subtask-1",
        attempt_number=1,
        summary_type="subtask",
        summary_path="summary.md",
        content_hash="abc123",
        content_length=12,
        registered_at="2026-03-09T00:00:00+00:00",
    )
    prompt_history = PromptHistoryCatalogResponse(
        node_id="node-1",
        prompts=[
            PromptHistoryRecordResponse(
                id="prompt-1",
                node_version_id="version-1",
                node_run_id="run-1",
                compiled_subtask_id="subtask-1",
                prompt_role="subtask_prompt",
                source_subtask_key="research_context.main",
                template_path="execution/research.md",
                template_hash="hash-1",
                content="Do the work",
                content_hash="content-hash-1",
                payload_json={"prompt_text": "Do the work"},
                delivered_at="2026-03-09T00:00:00+00:00",
            )
        ],
    )
    summary_history = SummaryHistoryCatalogResponse(
        node_id="node-1",
        summaries=[
            SummaryHistoryRecordResponse(
                id="summary-1",
                node_version_id="version-1",
                node_run_id="run-1",
                compiled_subtask_id="subtask-1",
                attempt_number=1,
                summary_type="subtask",
                summary_scope="subtask_attempt",
                summary_path="summary.md",
                content="summary body",
                content_hash="content-hash-2",
                metadata_json={"registered_by": "cli"},
                created_at="2026-03-09T00:01:00+00:00",
            )
        ],
    )

    assert prompt_response.model_dump()["prompt_id"] == "prompt-1"
    assert summary_response.model_dump()["summary_id"] == "summary-1"
    assert prompt_history.model_dump()["prompts"][0]["template_path"] == "execution/research.md"
    assert summary_history.model_dump()["summaries"][0]["summary_scope"] == "subtask_attempt"


def test_provenance_models_serialize_stably() -> None:
    response = ProvenanceRefreshResponse(
        node_id="node-1",
        node_version_id="version-1",
        prompt_record_id="prompt-1",
        summary_record_id="summary-1",
        provenance_summary_id="summary-2",
        rationale_summary="Node prompt: track changes",
        entity_count=4,
        relation_count=3,
        change_counts={"added": 4, "modified": 0, "unchanged": 0, "renamed_or_moved": 0, "removed": 0},
    )
    entity_catalog = EntityCatalogResponse(
        canonical_name="src.aicoding.daemon.app.create_app",
        entities=[
            EntityResponse(
                id="entity-1",
                entity_type="function",
                canonical_name="src.aicoding.daemon.app.create_app",
                file_path="src/aicoding/daemon/app.py",
                signature="() -> None",
                start_line=10,
                end_line=20,
                stable_hash="hash-1",
                created_at="2026-03-09T00:00:00+00:00",
                updated_at="2026-03-09T00:01:00+00:00",
            )
        ],
    )
    history_catalog = EntityHistoryCatalogResponse(
        canonical_name="src.aicoding.daemon.app.create_app",
        history=[
            EntityHistoryEntryResponse(
                id="change-1",
                node_version_id="version-1",
                logical_node_id="node-1",
                entity_id="entity-1",
                prompt_record_id="prompt-1",
                summary_record_id="summary-1",
                change_type="added",
                match_confidence="high",
                match_reason="new_entity",
                rationale_summary="track changes",
                observed_canonical_name="src.aicoding.daemon.app.create_app",
                observed_file_path="src/aicoding/daemon/app.py",
                observed_signature="() -> None",
                observed_stable_hash="hash-1",
                metadata_json={"entity_type": "function"},
                created_at="2026-03-09T00:00:00+00:00",
            )
        ],
    )
    relation_catalog = EntityRelationCatalogResponse(
        canonical_name="src.aicoding.daemon.app.create_app",
        relations=[
            EntityRelationResponse(
                id="relation-1",
                node_version_id="version-1",
                from_entity_id="entity-1",
                from_canonical_name="src.aicoding.daemon.app.create_app",
                to_entity_id="entity-2",
                to_canonical_name="src.aicoding.daemon.app.create_daemon",
                relation_type="calls",
                source="ast_exact",
                confidence=1.0,
                rationale_summary="track changes",
                created_at="2026-03-09T00:00:00+00:00",
            )
        ],
    )
    rationale = RationaleResponse(
        node_id="node-1",
        node_version_id="version-1",
        prompt_record_id="prompt-1",
        summary_record_id="summary-2",
        rationale_summary="track changes",
        change_counts=response.change_counts,
        entity_history=history_catalog.history,
    )

    assert response.model_dump()["provenance_summary_id"] == "summary-2"
    assert entity_catalog.model_dump()["entities"][0]["entity_type"] == "function"
    assert history_catalog.model_dump()["history"][0]["match_reason"] == "new_entity"
    assert relation_catalog.model_dump()["relations"][0]["relation_type"] == "calls"
    assert rationale.model_dump()["entity_history"][0]["observed_canonical_name"] == "src.aicoding.daemon.app.create_app"


def test_parent_failure_models_serialize_stably() -> None:
    counters = ChildFailureCounterCatalogResponse(
        node_id="node-1",
        node_run_id="run-1",
        failure_count_from_children=2,
        failure_count_consecutive=2,
        counters=[
            ChildFailureCounterResponse(
                child_node_id="child-1",
                child_node_version_id="version-1",
                child_title="Child",
                child_kind="phase",
                failure_count=2,
                last_failure_at="2026-03-09T00:00:00+00:00",
                last_failure_class="environment_failure",
                last_failure_summary="timeout",
                last_failure_subtask_key="execute_node.run",
                last_failed_node_run_id="run-2",
                last_decision_type="pause_for_user",
                last_decision_at="2026-03-09T00:00:01+00:00",
            )
        ],
    )
    decisions = ParentDecisionCatalogResponse(
        node_id="node-1",
        decisions=[
            ParentDecisionResponse(
                id="event-1",
                node_id="node-1",
                node_version_id="version-parent",
                node_run_id="run-1",
                child_node_id="child-1",
                child_node_version_id="version-1",
                child_node_run_id="run-2",
                failure_class="environment_failure",
                failure_origin="failed_to_parent",
                decision_type="parent_pause_for_user",
                decision_source="auto",
                decision_reason="threshold exceeded",
                options_considered=["retry_child", "regenerate_child", "replan_parent", "pause_for_user"],
                threshold_triggered=True,
                threshold_reason="per_child threshold exceeded",
                summary="paused",
                payload_json={"decision_type": "pause_for_user"},
                created_at="2026-03-09T00:00:01+00:00",
            )
        ],
    )
    response = ParentFailureDecisionResponse(
        node_id="node-1",
        node_run_id="run-1",
        child_node_id="child-1",
        child_node_version_id="version-1",
        child_node_run_id="run-2",
        failure_class="environment_failure",
        failure_origin="failed_to_parent",
        decision_type="pause_for_user",
        decision_source="auto",
        decision_reason="threshold exceeded",
        options_considered=["retry_child", "regenerate_child", "replan_parent", "pause_for_user"],
        threshold_triggered=True,
        threshold_reason="per_child threshold exceeded",
        policy_snapshot={"total_threshold": 3, "consecutive_threshold": 2, "per_child_threshold": 2},
        summary="paused for user",
        parent_lifecycle_state="PAUSED_FOR_USER",
        parent_run_status="PAUSED",
        child_lifecycle_state="FAILED_TO_PARENT",
        post_action_status="parent_paused",
        counters=counters,
    )

    assert counters.model_dump()["counters"][0]["last_failure_class"] == "environment_failure"
    assert decisions.model_dump()["decisions"][0]["decision_type"] == "parent_pause_for_user"
    assert decisions.model_dump()["decisions"][0]["threshold_triggered"] is True
    assert response.model_dump()["counters"]["failure_count_from_children"] == 2
    assert response.model_dump()["policy_snapshot"]["per_child_threshold"] == 2
