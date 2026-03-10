from __future__ import annotations

import concurrent.futures
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from aicoding.daemon.admission import add_node_dependency, admit_node_run, check_node_dependency_readiness
from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.versioning import create_superseding_node_version, initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.migrations import migration_status
from aicoding.db.models import (
    CodeEntity,
    CodeRelation,
    DocumentationOutput,
    NodeEntityChange,
    ReviewResult,
    Session as DurableSession,
    TestResult as DurableTestResult,
    ValidationResult,
)
from aicoding.db.session import create_session_factory
from aicoding.db.bootstrap import reset_public_schema
from aicoding.db.session import current_alembic_revision, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_migrations_are_repeatable(db_engine) -> None:
    config = Config("alembic.ini")

    reset_public_schema(db_engine)
    command.upgrade(config, "head")
    assert current_alembic_revision(db_engine) == "0028_subtask_execution_results"

    command.downgrade(config, "base")
    assert current_alembic_revision(db_engine) is None

    command.upgrade(config, "head")
    assert current_alembic_revision(db_engine) == "0028_subtask_execution_results"


def test_fixture_reset_clears_bootstrap_tables(db_engine) -> None:
    config = Config("alembic.ini")

    reset_public_schema(db_engine)
    command.upgrade(config, "head")
    assert "bootstrap_metadata" in inspect(db_engine).get_table_names()
    assert "daemon_node_states" in inspect(db_engine).get_table_names()
    assert "node_hierarchy_definitions" in inspect(db_engine).get_table_names()
    assert "yaml_schema_validation_records" in inspect(db_engine).get_table_names()
    assert "node_lifecycle_states" in inspect(db_engine).get_table_names()
    assert "node_versions" in inspect(db_engine).get_table_names()
    assert "logical_node_current_versions" in inspect(db_engine).get_table_names()
    assert "source_documents" in inspect(db_engine).get_table_names()
    assert "node_version_source_documents" in inspect(db_engine).get_table_names()
    assert "active_node_versions" in inspect(db_engine).get_view_names()
    assert "current_node_cursors" in inspect(db_engine).get_view_names()
    assert "pending_dependency_nodes" in inspect(db_engine).get_view_names()
    assert "latest_subtask_attempts" in inspect(db_engine).get_view_names()
    assert "active_primary_sessions" in inspect(db_engine).get_view_names()
    assert "latest_validation_results" in inspect(db_engine).get_view_names()
    assert "latest_review_results" in inspect(db_engine).get_view_names()
    assert "latest_test_results" in inspect(db_engine).get_view_names()
    assert "latest_documentation_outputs" in inspect(db_engine).get_view_names()
    assert "latest_node_entity_changes" in inspect(db_engine).get_view_names()
    assert "latest_code_relations" in inspect(db_engine).get_view_names()

    reset_public_schema(db_engine)
    assert "bootstrap_metadata" not in inspect(db_engine).get_table_names()


def test_concurrent_isolated_schemas_do_not_collide(db_engine) -> None:
    def create_and_query(schema_name: str) -> tuple[str, int]:
        with db_engine.begin() as connection:
            connection.execute(text(f'create schema "{schema_name}"'))
            connection.execute(text(f'create table "{schema_name}".probe (value integer)'))
            connection.execute(text(f'insert into "{schema_name}".probe(value) values (1)'))
            count = connection.execute(text(f'select count(*) from "{schema_name}".probe')).scalar_one()
            connection.execute(text(f'drop schema "{schema_name}" cascade'))
        return schema_name, count

    schema_names = ["concurrency_a", "concurrency_b"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(create_and_query, schema_names))

    assert sorted(results) == [("concurrency_a", 1), ("concurrency_b", 1)]


def test_migration_status_reports_uninitialized_then_up_to_date(db_engine) -> None:
    config = Config("alembic.ini")

    reset_public_schema(db_engine)
    before = migration_status(db_engine, config)
    assert before == {
        "current_revision": None,
        "expected_revision": "0028_subtask_execution_results",
        "status": "uninitialized",
        "compatible": False,
    }

    command.upgrade(config, "head")

    after = migration_status(db_engine, config)
    assert after == {
        "current_revision": "0028_subtask_execution_results",
        "expected_revision": "0028_subtask_execution_results",
        "status": "up_to_date",
        "compatible": True,
    }


def test_runtime_state_views_reflect_live_state(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)

    sync_hierarchy_definitions(factory, registry)

    running_node = create_hierarchy_node(factory, registry, kind="epic", title="Running Epic", prompt="boot")
    seed_node_lifecycle(factory, node_id=str(running_node.node_id), initial_state="DRAFT")
    running_version = initialize_node_version(factory, logical_node_id=running_node.node_id)
    create_manual_node(
        factory,
        registry,
        kind="phase",
        title="Manual Child",
        prompt="child prompt",
        parent_node_id=running_node.node_id,
    )
    compile_node_workflow(factory, logical_node_id=running_node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(running_node.node_id), target_state="READY")
    admission = admit_node_run(factory, node_id=running_node.node_id)

    blocked_node = create_hierarchy_node(factory, registry, kind="epic", title="Blocked Epic", prompt="boot")
    seed_node_lifecycle(factory, node_id=str(blocked_node.node_id), initial_state="DRAFT")
    blocked_version = initialize_node_version(factory, logical_node_id=blocked_node.node_id)
    candidate_version = create_superseding_node_version(factory, logical_node_id=blocked_node.node_id)
    add_node_dependency(factory, node_id=blocked_node.node_id, depends_on_node_id=running_node.node_id)
    readiness = check_node_dependency_readiness(factory, node_id=blocked_node.node_id)

    assert admission.status == "admitted"
    assert readiness.status == "blocked"

    with migrated_public_schema.begin() as connection:
        active_versions = connection.execute(
            text("select logical_node_id from active_node_versions order by logical_node_id")
        ).mappings().all()
        authoritative_rows = connection.execute(
            text("select logical_node_id from authoritative_node_versions where logical_node_id = :node_id"),
            {"node_id": str(blocked_node.node_id)},
        ).mappings().all()
        candidate_rows = connection.execute(
            text("select id, logical_node_id from candidate_node_versions where logical_node_id = :node_id"),
            {"node_id": str(blocked_node.node_id)},
        ).mappings().all()
        latest_run_row = connection.execute(
            text(
                """
                select node_version_id, run_number, run_status
                from latest_node_runs
                where node_version_id = :node_version_id
                """
            ),
            {"node_version_id": str(running_version.id)},
        ).mappings().one()
        cursor_row = connection.execute(
            text(
                """
                select logical_node_id, node_run_id, run_status, lifecycle_state
                from current_node_cursors
                where logical_node_id = :node_id
                """
            ),
            {"node_id": str(running_node.node_id)},
        ).mappings().one()
        blocker_row = connection.execute(
            text(
                """
                select node_version_id, blocker_kind, required_state
                from pending_dependency_nodes
                where node_version_id = :node_version_id
                """
            ),
            {"node_version_id": str(blocked_version.id)},
        ).mappings().one()
        authority_row = connection.execute(
            text(
                """
                select parent_node_version_id, authority_mode
                from latest_parent_child_authority
                where parent_node_version_id = :node_version_id
                """
            ),
            {"node_version_id": str(running_version.id)},
        ).mappings().one()

    assert {row["logical_node_id"] for row in active_versions} >= {
        running_node.node_id,
        blocked_node.node_id,
    }
    assert authoritative_rows == [{"logical_node_id": blocked_node.node_id}]
    assert candidate_rows == [{"id": candidate_version.id, "logical_node_id": blocked_node.node_id}]
    assert latest_run_row == {
        "node_version_id": running_version.id,
        "run_number": 1,
        "run_status": "RUNNING",
    }
    assert cursor_row == {
        "logical_node_id": running_node.node_id,
        "node_run_id": admission.current_run_id,
        "run_status": "RUNNING",
        "lifecycle_state": "RUNNING",
    }
    assert blocker_row == {
        "node_version_id": blocked_version.id,
        "blocker_kind": "blocked_on_dependency",
        "required_state": "COMPLETE",
    }
    assert authority_row == {
        "parent_node_version_id": running_version.id,
        "authority_mode": "manual",
    }


def test_session_attempt_and_gate_history_views_reflect_latest_records(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)

    sync_hierarchy_definitions(factory, registry)

    node = create_hierarchy_node(factory, registry, kind="epic", title="History Epic", prompt="boot")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(factory, logical_node_id=node.node_id)
    compile_result = compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admission = admit_node_run(factory, node_id=node.node_id)

    with session_scope(factory) as session:
        active_session = DurableSession(
            id=uuid4(),
            node_version_id=version.id,
            node_run_id=admission.current_run_id,
            session_role="primary",
            provider="tmux",
            provider_session_id="provider-1",
            tmux_session_name="tmux-1",
            cwd="/tmp/history-epic",
            status="BOUND",
            started_at=datetime.now(timezone.utc),
            last_heartbeat_at=datetime.now(timezone.utc),
        )
        stale_session = DurableSession(
            id=uuid4(),
            node_version_id=version.id,
            node_run_id=admission.current_run_id,
            session_role="primary",
            provider="tmux",
            provider_session_id="provider-0",
            tmux_session_name="tmux-0",
            cwd="/tmp/history-epic",
            status="LOST",
            started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            ended_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
        session.add_all([active_session, stale_session])
        session.flush()

        compiled_subtask_id = session.execute(
            text(
                """
                select id
                from compiled_subtasks
                where compiled_workflow_id = :workflow_id
                order by ordinal
                limit 1
                """
            ),
            {"workflow_id": str(compile_result.compiled_workflow.id)},
        ).scalar_one()

        session.execute(
            text(
                """
                insert into subtask_attempts (
                    id,
                    node_run_id,
                    compiled_subtask_id,
                    attempt_number,
                    status,
                    started_at,
                    ended_at
                ) values (
                    :id,
                    :node_run_id,
                    :compiled_subtask_id,
                    :attempt_number,
                    :status,
                    :started_at,
                    :ended_at
                )
                """
            ),
            {
                "id": str(uuid4()),
                "node_run_id": str(admission.current_run_id),
                "compiled_subtask_id": str(compiled_subtask_id),
                "attempt_number": 1,
                "status": "FAILED",
                "started_at": datetime.now(timezone.utc) - timedelta(minutes=3),
                "ended_at": datetime.now(timezone.utc) - timedelta(minutes=2),
            },
        )
        latest_attempt_id = uuid4()
        session.execute(
            text(
                """
                insert into subtask_attempts (
                    id,
                    node_run_id,
                    compiled_subtask_id,
                    attempt_number,
                    status,
                    started_at
                ) values (
                    :id,
                    :node_run_id,
                    :compiled_subtask_id,
                    :attempt_number,
                    :status,
                    :started_at
                )
                """
            ),
            {
                "id": str(latest_attempt_id),
                "node_run_id": str(admission.current_run_id),
                "compiled_subtask_id": str(compiled_subtask_id),
                "attempt_number": 2,
                "status": "RUNNING",
                "started_at": datetime.now(timezone.utc) - timedelta(minutes=1),
            },
        )

        session.add_all(
            [
                ValidationResult(
                    id=uuid4(),
                    node_version_id=version.id,
                    node_run_id=admission.current_run_id,
                    compiled_subtask_id=compiled_subtask_id,
                    check_type="summary_written",
                    status="failed",
                    summary="older validation",
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
                ),
                ValidationResult(
                    id=uuid4(),
                    node_version_id=version.id,
                    node_run_id=admission.current_run_id,
                    compiled_subtask_id=compiled_subtask_id,
                    check_type="summary_written",
                    status="passed",
                    summary="latest validation",
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
                ),
                ReviewResult(
                    id=uuid4(),
                    node_version_id=version.id,
                    node_run_id=admission.current_run_id,
                    compiled_subtask_id=compiled_subtask_id,
                    review_definition_id="review-a",
                    scope="node",
                    status="revise",
                    summary="older review",
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
                ),
                ReviewResult(
                    id=uuid4(),
                    node_version_id=version.id,
                    node_run_id=admission.current_run_id,
                    compiled_subtask_id=compiled_subtask_id,
                    review_definition_id="review-a",
                    scope="node",
                    status="passed",
                    summary="latest review",
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
                ),
                DurableTestResult(
                    id=uuid4(),
                    node_version_id=version.id,
                    node_run_id=admission.current_run_id,
                    compiled_subtask_id=compiled_subtask_id,
                    testing_definition_id="suite-a",
                    suite_name="pytest",
                    status="failed",
                    summary="older test",
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
                ),
                DurableTestResult(
                    id=uuid4(),
                    node_version_id=version.id,
                    node_run_id=admission.current_run_id,
                    compiled_subtask_id=compiled_subtask_id,
                    testing_definition_id="suite-a",
                    suite_name="pytest",
                    status="passed",
                    summary="latest test",
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
                ),
            ]
        )

    with migrated_public_schema.begin() as connection:
        latest_attempt = connection.execute(
            text(
                """
                select id, attempt_number, status
                from latest_subtask_attempts
                where node_run_id = :node_run_id and compiled_subtask_id = :compiled_subtask_id
                """
            ),
            {
                "node_run_id": str(admission.current_run_id),
                "compiled_subtask_id": str(compiled_subtask_id),
            },
        ).mappings().one()
        active_primary = connection.execute(
            text(
                """
                select id, status
                from active_primary_sessions
                where node_run_id = :node_run_id
                """
            ),
            {"node_run_id": str(admission.current_run_id)},
        ).mappings().all()
        latest_validation = connection.execute(
            text(
                """
                select status, summary
                from latest_validation_results
                where node_run_id = :node_run_id and compiled_subtask_id = :compiled_subtask_id and check_type = 'summary_written'
                """
            ),
            {
                "node_run_id": str(admission.current_run_id),
                "compiled_subtask_id": str(compiled_subtask_id),
            },
        ).mappings().one()
        latest_review = connection.execute(
            text(
                """
                select status, summary
                from latest_review_results
                where node_run_id = :node_run_id and compiled_subtask_id = :compiled_subtask_id and review_definition_id = 'review-a'
                """
            ),
            {
                "node_run_id": str(admission.current_run_id),
                "compiled_subtask_id": str(compiled_subtask_id),
            },
        ).mappings().one()
        latest_test = connection.execute(
            text(
                """
                select status, summary
                from latest_test_results
                where node_run_id = :node_run_id and compiled_subtask_id = :compiled_subtask_id and testing_definition_id = 'suite-a'
                """
            ),
            {
                "node_run_id": str(admission.current_run_id),
                "compiled_subtask_id": str(compiled_subtask_id),
            },
        ).mappings().one()

    assert latest_attempt == {
        "id": latest_attempt_id,
        "attempt_number": 2,
        "status": "RUNNING",
    }
    assert active_primary == [{"id": active_session.id, "status": "BOUND"}]
    assert latest_validation == {"status": "passed", "summary": "latest validation"}
    assert latest_review == {"status": "passed", "summary": "latest review"}
    assert latest_test == {"status": "passed", "summary": "latest test"}


def test_provenance_and_documentation_views_reflect_latest_records(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)

    sync_hierarchy_definitions(factory, registry)

    node = create_hierarchy_node(factory, registry, kind="epic", title="Audit Epic", prompt="boot")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    with session_scope(factory) as session:
        documentation_old = DocumentationOutput(
            id=uuid4(),
            logical_node_id=node.node_id,
            node_version_id=version.id,
            doc_definition_id="docs/default_doc_views",
            scope="local",
            view_name="overview",
            output_path="docs/audit-old.md",
            content="old doc",
            content_hash="doc-old",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
        )
        documentation_new = DocumentationOutput(
            id=uuid4(),
            logical_node_id=node.node_id,
            node_version_id=version.id,
            doc_definition_id="docs/default_doc_views",
            scope="local",
            view_name="overview",
            output_path="docs/audit-new.md",
            content="new doc",
            content_hash="doc-new",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
        entity = CodeEntity(
            id=uuid4(),
            entity_type="function",
            canonical_name="pkg.audit.run",
            file_path="src/pkg/audit.py",
            signature="def run()",
            stable_hash="entity-stable-hash",
        )
        target_entity = CodeEntity(
            id=uuid4(),
            entity_type="function",
            canonical_name="pkg.audit.helper",
            file_path="src/pkg/audit.py",
            signature="def helper()",
            stable_hash="target-stable-hash",
        )
        change_old = NodeEntityChange(
            id=uuid4(),
            node_version_id=version.id,
            entity_id=entity.id,
            change_type="added",
            match_confidence="medium",
            match_reason="new_entity",
            rationale_summary="older rationale",
            observed_canonical_name="pkg.audit.run",
            observed_file_path="src/pkg/audit.py",
            observed_signature="def run()",
            observed_stable_hash="entity-stable-hash",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
        )
        change_new = NodeEntityChange(
            id=uuid4(),
            node_version_id=version.id,
            entity_id=entity.id,
            change_type="modified",
            match_confidence="high",
            match_reason="exact_hash",
            rationale_summary="latest rationale",
            observed_canonical_name="pkg.audit.run",
            observed_file_path="src/pkg/audit.py",
            observed_signature="def run()",
            observed_stable_hash="entity-stable-hash",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
        relation_old = CodeRelation(
            id=uuid4(),
            node_version_id=version.id,
            from_entity_id=entity.id,
            to_entity_id=target_entity.id,
            relation_type="contains",
            source="ast_exact",
            confidence=0.2,
            rationale_summary="older relation",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
        )
        relation_new = CodeRelation(
            id=uuid4(),
            node_version_id=version.id,
            from_entity_id=entity.id,
            to_entity_id=target_entity.id,
            relation_type="contains",
            source="ast_exact",
            confidence=0.9,
            rationale_summary="latest relation",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
        session.add_all(
            [
                entity,
                target_entity,
                documentation_old,
                documentation_new,
                change_old,
                change_new,
                relation_old,
                relation_new,
            ]
        )

    with migrated_public_schema.begin() as connection:
        latest_doc = connection.execute(
            text(
                """
                select output_path, content_hash
                from latest_documentation_outputs
                where logical_node_id = :node_id and scope = 'local' and view_name = 'overview'
                """
            ),
            {"node_id": str(node.node_id)},
        ).mappings().one()
        latest_change = connection.execute(
            text(
                """
                select change_type, rationale_summary
                from latest_node_entity_changes
                where node_version_id = :node_version_id and entity_id = :entity_id
                """
            ),
            {"node_version_id": str(version.id), "entity_id": str(entity.id)},
        ).mappings().one()
        latest_relation = connection.execute(
            text(
                """
                select confidence, rationale_summary
                from latest_code_relations
                where
                  node_version_id = :node_version_id
                  and from_entity_id = :entity_id
                  and to_entity_id = :target_entity_id
                  and relation_type = 'contains'
                """
            ),
            {
                "node_version_id": str(version.id),
                "entity_id": str(entity.id),
                "target_entity_id": str(target_entity.id),
            },
        ).mappings().one()

    assert latest_doc == {"output_path": "docs/audit-new.md", "content_hash": "doc-new"}
    assert latest_change == {"change_type": "modified", "rationale_summary": "latest rationale"}
    assert latest_relation == {"confidence": 0.9, "rationale_summary": "latest relation"}
