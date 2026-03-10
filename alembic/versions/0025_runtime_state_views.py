"""add runtime state views and indexes

Revision ID: 0025_runtime_state_views
Revises: 0024_runtime_env_meta
Create Date: 2026-03-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0025_runtime_state_views"
down_revision = "0024_runtime_env_meta"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_node_runs_node_version_run_number",
        "node_runs",
        ["node_version_id", "run_number"],
        unique=False,
    )
    op.create_index(
        "ix_node_dependency_blockers_node_version_created",
        "node_dependency_blockers",
        ["node_version_id", "created_at"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            create view active_node_versions as
            select nv.*
            from node_versions nv
            join logical_node_current_versions lcv
              on lcv.authoritative_node_version_id = nv.id
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view authoritative_node_versions as
            select nv.*
            from node_versions nv
            join logical_node_current_versions lcv
              on lcv.authoritative_node_version_id = nv.id
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view candidate_node_versions as
            select nv.*
            from node_versions nv
            join logical_node_current_versions lcv
              on lcv.latest_created_node_version_id = nv.id
            where lcv.latest_created_node_version_id <> lcv.authoritative_node_version_id
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view latest_node_runs as
            select distinct on (node_version_id)
              *
            from node_runs
            order by node_version_id, run_number desc
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view current_node_cursors as
            select
              lcv.logical_node_id,
              lcv.authoritative_node_version_id as node_version_id,
              lnr.id as node_run_id,
              lnr.run_number,
              lnr.run_status,
              lnr.compiled_workflow_id,
              nrs.lifecycle_state,
              nrs.current_task_id,
              nrs.current_compiled_subtask_id,
              nrs.current_subtask_attempt,
              nrs.last_completed_compiled_subtask_id,
              nrs.pause_flag_name,
              nrs.is_resumable,
              nrs.working_tree_state,
              nrs.updated_at
            from logical_node_current_versions lcv
            left join latest_node_runs lnr
              on lnr.node_version_id = lcv.authoritative_node_version_id
            left join node_run_state nrs
              on nrs.node_run_id = lnr.id
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view pending_dependency_nodes as
            select
              ndb.node_version_id,
              ndb.dependency_id,
              nd.required_state,
              ndb.blocker_kind,
              ndb.target_node_version_id,
              ndb.details_json,
              ndb.created_at
            from node_dependency_blockers ndb
            left join node_dependencies nd
              on nd.id = ndb.dependency_id
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view latest_parent_child_authority as
            select
              parent_node_version_id,
              authority_mode,
              authoritative_layout_hash,
              last_reconciled_at,
              updated_at
            from parent_child_authority
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("drop view if exists latest_parent_child_authority"))
    op.execute(sa.text("drop view if exists pending_dependency_nodes"))
    op.execute(sa.text("drop view if exists current_node_cursors"))
    op.execute(sa.text("drop view if exists latest_node_runs"))
    op.execute(sa.text("drop view if exists candidate_node_versions"))
    op.execute(sa.text("drop view if exists authoritative_node_versions"))
    op.execute(sa.text("drop view if exists active_node_versions"))
    op.drop_index("ix_node_dependency_blockers_node_version_created", table_name="node_dependency_blockers")
    op.drop_index("ix_node_runs_node_version_run_number", table_name="node_runs")
