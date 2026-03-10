"""create durable node run orchestration tables

Revision ID: 0010_node_run_orchestration
Revises: 0009_dependency_admission
Create Date: 2026-03-08 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0010_node_run_orchestration"
down_revision = "0009_dependency_admission"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "node_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("run_number", sa.Integer(), nullable=False),
        sa.Column("trigger_reason", sa.String(length=64), nullable=False),
        sa.Column("run_status", sa.String(length=16), nullable=False),
        sa.Column("compiled_workflow_id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["compiled_workflow_id"], ["compiled_workflows.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("node_version_id", "run_number", name="uq_node_runs_version_run_number"),
        sa.CheckConstraint("run_number > 0", name="ck_node_runs_run_number_positive"),
    )
    op.create_index(op.f("ix_node_runs_node_version_id"), "node_runs", ["node_version_id"], unique=False)
    op.create_index(op.f("ix_node_runs_compiled_workflow_id"), "node_runs", ["compiled_workflow_id"], unique=False)
    op.create_index(op.f("ix_node_runs_run_status"), "node_runs", ["run_status"], unique=False)

    op.create_table(
        "node_run_state",
        sa.Column("node_run_id", sa.Uuid(), nullable=False),
        sa.Column("lifecycle_state", sa.String(length=32), nullable=False),
        sa.Column("current_task_id", sa.Uuid(), nullable=True),
        sa.Column("current_compiled_subtask_id", sa.Uuid(), nullable=True),
        sa.Column("current_subtask_attempt", sa.Integer(), nullable=True),
        sa.Column("last_completed_compiled_subtask_id", sa.Uuid(), nullable=True),
        sa.Column("execution_cursor_json", sa.JSON(), nullable=False),
        sa.Column("failure_count_from_children", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_count_consecutive", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("defer_to_user_threshold", sa.Integer(), nullable=True),
        sa.Column("pause_flag_name", sa.String(length=64), nullable=True),
        sa.Column("is_resumable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("working_tree_state", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["current_compiled_subtask_id"], ["compiled_subtasks.id"]),
        sa.ForeignKeyConstraint(["current_task_id"], ["compiled_tasks.id"]),
        sa.ForeignKeyConstraint(["last_completed_compiled_subtask_id"], ["compiled_subtasks.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.PrimaryKeyConstraint("node_run_id"),
        sa.CheckConstraint(
            "current_subtask_attempt is null or current_subtask_attempt > 0",
            name="ck_node_run_state_attempt_positive",
        ),
        sa.CheckConstraint("failure_count_from_children >= 0", name="ck_node_run_state_child_failures_nonnegative"),
        sa.CheckConstraint("failure_count_consecutive >= 0", name="ck_node_run_state_consecutive_failures_nonnegative"),
    )
    op.create_index(op.f("ix_node_run_state_lifecycle_state"), "node_run_state", ["lifecycle_state"], unique=False)
    op.create_index(op.f("ix_node_run_state_current_task_id"), "node_run_state", ["current_task_id"], unique=False)
    op.create_index(op.f("ix_node_run_state_current_compiled_subtask_id"), "node_run_state", ["current_compiled_subtask_id"], unique=False)
    op.create_index(op.f("ix_node_run_state_pause_flag_name"), "node_run_state", ["pause_flag_name"], unique=False)

    op.create_table(
        "subtask_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("node_run_id", sa.Uuid(), nullable=False),
        sa.Column("compiled_subtask_id", sa.Uuid(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("input_context_json", sa.JSON(), nullable=True),
        sa.Column("output_json", sa.JSON(), nullable=True),
        sa.Column("changed_files_json", sa.JSON(), nullable=True),
        sa.Column("git_head_before", sa.String(length=64), nullable=True),
        sa.Column("git_head_after", sa.String(length=64), nullable=True),
        sa.Column("validation_json", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["compiled_subtask_id"], ["compiled_subtasks.id"]),
        sa.ForeignKeyConstraint(["node_run_id"], ["node_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("node_run_id", "compiled_subtask_id", "attempt_number", name="uq_subtask_attempts_identity"),
        sa.CheckConstraint("attempt_number > 0", name="ck_subtask_attempts_attempt_positive"),
    )
    op.create_index(op.f("ix_subtask_attempts_node_run_id"), "subtask_attempts", ["node_run_id"], unique=False)
    op.create_index(op.f("ix_subtask_attempts_compiled_subtask_id"), "subtask_attempts", ["compiled_subtask_id"], unique=False)
    op.create_index(op.f("ix_subtask_attempts_status"), "subtask_attempts", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_subtask_attempts_status"), table_name="subtask_attempts")
    op.drop_index(op.f("ix_subtask_attempts_compiled_subtask_id"), table_name="subtask_attempts")
    op.drop_index(op.f("ix_subtask_attempts_node_run_id"), table_name="subtask_attempts")
    op.drop_table("subtask_attempts")

    op.drop_index(op.f("ix_node_run_state_pause_flag_name"), table_name="node_run_state")
    op.drop_index(op.f("ix_node_run_state_current_compiled_subtask_id"), table_name="node_run_state")
    op.drop_index(op.f("ix_node_run_state_current_task_id"), table_name="node_run_state")
    op.drop_index(op.f("ix_node_run_state_lifecycle_state"), table_name="node_run_state")
    op.drop_table("node_run_state")

    op.drop_index(op.f("ix_node_runs_run_status"), table_name="node_runs")
    op.drop_index(op.f("ix_node_runs_compiled_workflow_id"), table_name="node_runs")
    op.drop_index(op.f("ix_node_runs_node_version_id"), table_name="node_runs")
    op.drop_table("node_runs")
