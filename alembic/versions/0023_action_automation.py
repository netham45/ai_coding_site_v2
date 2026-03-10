"""expand authority action constraints for cancel automation

Revision ID: 0023_action_automation
Revises: 0022_documentation_outputs
Create Date: 2026-03-09 11:20:00
"""
from __future__ import annotations

from alembic import op


revision = "0023_action_automation"
down_revision = "0022_documentation_outputs"
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
        "lifecycle_state in ('active','paused','ready','cancelled')",
    )
    op.create_check_constraint(
        "ck_daemon_node_states_last_command",
        "daemon_node_states",
        "last_command in ('node.run.start','node.pause','node.resume','node.run.retry.reset','node.cancel')",
    )
    op.create_check_constraint(
        "ck_daemon_mutation_events_command",
        "daemon_mutation_events",
        "command in ('node.run.start','node.pause','node.resume','node.run.retry.reset','node.cancel')",
    )
    op.create_check_constraint(
        "ck_daemon_mutation_events_resulting_state",
        "daemon_mutation_events",
        "resulting_state in ('active','paused','ready','cancelled')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_daemon_mutation_events_resulting_state", "daemon_mutation_events", type_="check")
    op.drop_constraint("ck_daemon_mutation_events_command", "daemon_mutation_events", type_="check")
    op.drop_constraint("ck_daemon_node_states_last_command", "daemon_node_states", type_="check")
    op.drop_constraint("ck_daemon_node_states_lifecycle_state", "daemon_node_states", type_="check")
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
