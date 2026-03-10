"""create node run child failure counters table

Revision ID: 0019_parent_failure_counters
Revises: 0018_workflow_events
Create Date: 2026-03-09 10:05:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0019_parent_failure_counters"
down_revision = "0018_workflow_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_daemon_node_states_lifecycle_state", "daemon_node_states", type_="check")
    op.drop_constraint("ck_daemon_node_states_last_command", "daemon_node_states", type_="check")
    op.drop_constraint("ck_daemon_mutation_events_command", "daemon_mutation_events", type_="check")
    op.drop_constraint("ck_daemon_mutation_events_resulting_state", "daemon_mutation_events", type_="check")
    op.create_check_constraint(
        "ck_daemon_node_states_lifecycle_state",
        "daemon_node_states",
        "lifecycle_state in ('active','paused','ready')",
    )
    op.create_check_constraint(
        "ck_daemon_node_states_last_command",
        "daemon_node_states",
        "last_command in ('node.run.start','node.pause','node.resume','node.run.retry.reset')",
    )
    op.create_check_constraint(
        "ck_daemon_mutation_events_command",
        "daemon_mutation_events",
        "command in ('node.run.start','node.pause','node.resume','node.run.retry.reset')",
    )
    op.create_check_constraint(
        "ck_daemon_mutation_events_resulting_state",
        "daemon_mutation_events",
        "resulting_state in ('active','paused','ready')",
    )
    op.create_table(
        "node_run_child_failure_counters",
        sa.Column("node_run_id", sa.Uuid(), nullable=False),
        sa.Column("child_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_class", sa.String(length=64), nullable=True),
        sa.Column("last_failure_summary", sa.Text(), nullable=True),
        sa.Column("last_failure_subtask_key", sa.String(length=128), nullable=True),
        sa.Column("last_failed_node_run_id", sa.Uuid(), nullable=True),
        sa.Column("last_decision_type", sa.String(length=64), nullable=True),
        sa.Column("last_decision_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["child_node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["last_failed_node_run_id"], ["node_runs.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.PrimaryKeyConstraint("node_run_id", "child_node_version_id"),
    )
    op.create_index(
        "ix_node_run_child_failure_counters_child_node_version_id",
        "node_run_child_failure_counters",
        ["child_node_version_id"],
    )
    op.create_index(
        "ix_node_run_child_failure_counters_last_failure_at",
        "node_run_child_failure_counters",
        ["last_failure_at"],
    )
    op.create_index(
        "ix_node_run_child_failure_counters_last_failure_class",
        "node_run_child_failure_counters",
        ["last_failure_class"],
    )
    op.create_index(
        "ix_node_run_child_failure_counters_last_decision_type",
        "node_run_child_failure_counters",
        ["last_decision_type"],
    )


def downgrade() -> None:
    op.drop_constraint("ck_daemon_mutation_events_resulting_state", "daemon_mutation_events", type_="check")
    op.drop_constraint("ck_daemon_mutation_events_command", "daemon_mutation_events", type_="check")
    op.drop_constraint("ck_daemon_node_states_last_command", "daemon_node_states", type_="check")
    op.drop_constraint("ck_daemon_node_states_lifecycle_state", "daemon_node_states", type_="check")
    op.create_check_constraint(
        "ck_daemon_node_states_lifecycle_state",
        "daemon_node_states",
        "lifecycle_state in ('active','paused')",
    )
    op.create_check_constraint(
        "ck_daemon_node_states_last_command",
        "daemon_node_states",
        "last_command in ('node.run.start','node.pause','node.resume')",
    )
    op.create_check_constraint(
        "ck_daemon_mutation_events_command",
        "daemon_mutation_events",
        "command in ('node.run.start','node.pause','node.resume')",
    )
    op.create_check_constraint(
        "ck_daemon_mutation_events_resulting_state",
        "daemon_mutation_events",
        "resulting_state in ('active','paused')",
    )
    op.drop_index(
        "ix_node_run_child_failure_counters_last_decision_type",
        table_name="node_run_child_failure_counters",
    )
    op.drop_index(
        "ix_node_run_child_failure_counters_last_failure_class",
        table_name="node_run_child_failure_counters",
    )
    op.drop_index(
        "ix_node_run_child_failure_counters_last_failure_at",
        table_name="node_run_child_failure_counters",
    )
    op.drop_index(
        "ix_node_run_child_failure_counters_child_node_version_id",
        table_name="node_run_child_failure_counters",
    )
    op.drop_table("node_run_child_failure_counters")
