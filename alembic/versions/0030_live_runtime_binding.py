"""bind live runtime rows to node versions

Revision ID: 0030_live_runtime_binding
Revises: 0029_incr_parent_merge_state
Create Date: 2026-03-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0030_live_runtime_binding"
down_revision = "0029_incr_parent_merge_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("daemon_node_states", sa.Column("node_version_id", sa.Uuid(), nullable=True))
    op.add_column("node_lifecycle_states", sa.Column("node_version_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_daemon_node_states_node_version_id",
        "daemon_node_states",
        "node_versions",
        ["node_version_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_node_lifecycle_states_node_version_id",
        "node_lifecycle_states",
        "node_versions",
        ["node_version_id"],
        ["id"],
    )
    op.create_index("ix_daemon_node_states_node_version_id", "daemon_node_states", ["node_version_id"], unique=False)
    op.create_index("ix_node_lifecycle_states_node_version_id", "node_lifecycle_states", ["node_version_id"], unique=False)
    op.execute(
        """
        update daemon_node_states as dns
        set node_version_id = lncv.authoritative_node_version_id
        from logical_node_current_versions as lncv
        where dns.node_id ~* '^[0-9a-f-]{36}$'
          and cast(dns.node_id as uuid) = lncv.logical_node_id
        """
    )
    op.execute(
        """
        update node_lifecycle_states as nls
        set node_version_id = lncv.authoritative_node_version_id
        from logical_node_current_versions as lncv
        where nls.node_id ~* '^[0-9a-f-]{36}$'
          and cast(nls.node_id as uuid) = lncv.logical_node_id
        """
    )


def downgrade() -> None:
    op.drop_index("ix_node_lifecycle_states_node_version_id", table_name="node_lifecycle_states")
    op.drop_index("ix_daemon_node_states_node_version_id", table_name="daemon_node_states")
    op.drop_constraint("fk_node_lifecycle_states_node_version_id", "node_lifecycle_states", type_="foreignkey")
    op.drop_constraint("fk_daemon_node_states_node_version_id", "daemon_node_states", type_="foreignkey")
    op.drop_column("node_lifecycle_states", "node_version_id")
    op.drop_column("daemon_node_states", "node_version_id")
