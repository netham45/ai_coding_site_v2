"""create dependency graph and blocker tables

Revision ID: 0009_dependency_admission
Revises: 0008_immutable_workflows
Create Date: 2026-03-08 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0009_dependency_admission"
down_revision = "0008_immutable_workflows"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "node_dependencies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("depends_on_node_version_id", sa.Uuid(), nullable=False),
        sa.Column("dependency_type", sa.String(length=16), nullable=False),
        sa.Column("required_state", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("dependency_type in ('child', 'sibling')", name="ck_node_dependencies_dependency_type"),
        sa.CheckConstraint("node_version_id <> depends_on_node_version_id", name="ck_node_dependencies_not_self"),
        sa.ForeignKeyConstraint(["depends_on_node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("node_version_id", "depends_on_node_version_id", name="uq_node_dependencies_pair"),
    )
    op.create_index(op.f("ix_node_dependencies_node_version_id"), "node_dependencies", ["node_version_id"], unique=False)
    op.create_index(op.f("ix_node_dependencies_depends_on_node_version_id"), "node_dependencies", ["depends_on_node_version_id"], unique=False)
    op.create_index(op.f("ix_node_dependencies_dependency_type"), "node_dependencies", ["dependency_type"], unique=False)

    op.create_table(
        "node_dependency_blockers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("node_version_id", sa.Uuid(), nullable=False),
        sa.Column("dependency_id", sa.Uuid(), nullable=True),
        sa.Column("blocker_kind", sa.String(length=32), nullable=False),
        sa.Column("target_node_version_id", sa.Uuid(), nullable=True),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dependency_id"], ["node_dependencies.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["target_node_version_id"], ["node_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_node_dependency_blockers_node_version_id"), "node_dependency_blockers", ["node_version_id"], unique=False)
    op.create_index(op.f("ix_node_dependency_blockers_dependency_id"), "node_dependency_blockers", ["dependency_id"], unique=False)
    op.create_index(op.f("ix_node_dependency_blockers_blocker_kind"), "node_dependency_blockers", ["blocker_kind"], unique=False)
    op.create_index(op.f("ix_node_dependency_blockers_target_node_version_id"), "node_dependency_blockers", ["target_node_version_id"], unique=False)
    op.create_index(op.f("ix_node_dependency_blockers_created_at"), "node_dependency_blockers", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_node_dependency_blockers_created_at"), table_name="node_dependency_blockers")
    op.drop_index(op.f("ix_node_dependency_blockers_target_node_version_id"), table_name="node_dependency_blockers")
    op.drop_index(op.f("ix_node_dependency_blockers_blocker_kind"), table_name="node_dependency_blockers")
    op.drop_index(op.f("ix_node_dependency_blockers_dependency_id"), table_name="node_dependency_blockers")
    op.drop_index(op.f("ix_node_dependency_blockers_node_version_id"), table_name="node_dependency_blockers")
    op.drop_table("node_dependency_blockers")

    op.drop_index(op.f("ix_node_dependencies_dependency_type"), table_name="node_dependencies")
    op.drop_index(op.f("ix_node_dependencies_depends_on_node_version_id"), table_name="node_dependencies")
    op.drop_index(op.f("ix_node_dependencies_node_version_id"), table_name="node_dependencies")
    op.drop_table("node_dependencies")
