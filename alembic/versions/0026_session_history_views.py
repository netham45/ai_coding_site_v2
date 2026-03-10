"""add session and history views

Revision ID: 0026_session_history_views
Revises: 0025_runtime_state_views
Create Date: 2026-03-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0026_session_history_views"
down_revision = "0025_runtime_state_views"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_subtask_attempts_run_subtask_attempt",
        "subtask_attempts",
        ["node_run_id", "compiled_subtask_id", "attempt_number"],
        unique=False,
    )
    op.create_index(
        "ix_validation_results_latest_lookup",
        "validation_results",
        ["node_version_id", "node_run_id", "compiled_subtask_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_review_results_latest_lookup",
        "review_results",
        ["node_version_id", "node_run_id", "compiled_subtask_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_test_results_latest_lookup",
        "test_results",
        ["node_version_id", "node_run_id", "compiled_subtask_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_prompts_node_version_delivered",
        "prompts",
        ["node_version_id", "delivered_at"],
        unique=False,
    )
    op.create_index(
        "ix_summaries_node_version_created",
        "summaries",
        ["node_version_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_sessions_run_role_status_started",
        "sessions",
        ["node_run_id", "session_role", "status", "started_at"],
        unique=False,
    )
    op.create_index(
        "ix_session_events_session_created",
        "session_events",
        ["session_id", "created_at"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_sessions_role_parent_shape",
        "sessions",
        "(session_role = 'primary' and parent_session_id is null) "
        "or (session_role = 'pushed_child' and parent_session_id is not null)",
    )

    op.execute(
        sa.text(
            """
            create view latest_subtask_attempts as
            select distinct on (node_run_id, compiled_subtask_id)
              *
            from subtask_attempts
            order by node_run_id, compiled_subtask_id, attempt_number desc
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view active_primary_sessions as
            select *
            from sessions
            where session_role = 'primary'
              and status in ('BOUND', 'ATTACHED', 'RESUMED', 'RUNNING')
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view latest_validation_results as
            select distinct on (node_version_id, node_run_id, compiled_subtask_id, check_type)
              *
            from validation_results
            order by
              node_version_id,
              node_run_id,
              compiled_subtask_id,
              check_type,
              created_at desc
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view latest_review_results as
            select distinct on (node_version_id, node_run_id, compiled_subtask_id, review_definition_id, scope)
              *
            from review_results
            order by
              node_version_id,
              node_run_id,
              compiled_subtask_id,
              review_definition_id,
              scope,
              created_at desc
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view latest_test_results as
            select distinct on (node_version_id, node_run_id, compiled_subtask_id, testing_definition_id, suite_name)
              *
            from test_results
            order by
              node_version_id,
              node_run_id,
              compiled_subtask_id,
              testing_definition_id,
              suite_name,
              created_at desc
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("drop view if exists latest_test_results"))
    op.execute(sa.text("drop view if exists latest_review_results"))
    op.execute(sa.text("drop view if exists latest_validation_results"))
    op.execute(sa.text("drop view if exists active_primary_sessions"))
    op.execute(sa.text("drop view if exists latest_subtask_attempts"))
    op.drop_constraint("ck_sessions_role_parent_shape", "sessions", type_="check")
    op.drop_index("ix_session_events_session_created", table_name="session_events")
    op.drop_index("ix_sessions_run_role_status_started", table_name="sessions")
    op.drop_index("ix_summaries_node_version_created", table_name="summaries")
    op.drop_index("ix_prompts_node_version_delivered", table_name="prompts")
    op.drop_index("ix_test_results_latest_lookup", table_name="test_results")
    op.drop_index("ix_review_results_latest_lookup", table_name="review_results")
    op.drop_index("ix_validation_results_latest_lookup", table_name="validation_results")
    op.drop_index("ix_subtask_attempts_run_subtask_attempt", table_name="subtask_attempts")
