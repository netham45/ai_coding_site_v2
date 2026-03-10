"""add provenance and documentation audit views

Revision ID: 0027_provenance_docs_audit_views
Revises: 0026_session_history_views
Create Date: 2026-03-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0027_provenance_docs_audit_views"
down_revision = "0026_session_history_views"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_documentation_outputs_node_version_created",
        "documentation_outputs",
        ["node_version_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_documentation_outputs_logical_scope_view_created",
        "documentation_outputs",
        ["logical_node_id", "scope", "view_name", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_documentation_outputs_doc_definition_id",
        "documentation_outputs",
        ["doc_definition_id"],
        unique=False,
    )
    op.create_index(
        "ix_documentation_outputs_content_hash",
        "documentation_outputs",
        ["content_hash"],
        unique=False,
    )
    op.create_index(
        "ix_code_entities_canonical_type_path",
        "code_entities",
        ["canonical_name", "entity_type", "file_path"],
        unique=False,
    )
    op.create_index(
        "ix_node_entity_changes_version_entity_created",
        "node_entity_changes",
        ["node_version_id", "entity_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_node_entity_changes_entity_created",
        "node_entity_changes",
        ["entity_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_node_entity_changes_observed_name_created",
        "node_entity_changes",
        ["observed_canonical_name", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_code_relations_version_from_to_type_created",
        "code_relations",
        ["node_version_id", "from_entity_id", "to_entity_id", "relation_type", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_code_relations_from_relation_created",
        "code_relations",
        ["from_entity_id", "relation_type", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_code_relations_to_relation_created",
        "code_relations",
        ["to_entity_id", "relation_type", "created_at"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            create view latest_documentation_outputs as
            select distinct on (logical_node_id, scope, view_name)
              *
            from documentation_outputs
            order by logical_node_id, scope, view_name, created_at desc, id desc
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view latest_node_entity_changes as
            select distinct on (node_version_id, entity_id)
              *
            from node_entity_changes
            order by node_version_id, entity_id, created_at desc, id desc
            """
        )
    )
    op.execute(
        sa.text(
            """
            create view latest_code_relations as
            select distinct on (node_version_id, from_entity_id, to_entity_id, relation_type)
              *
            from code_relations
            order by
              node_version_id,
              from_entity_id,
              to_entity_id,
              relation_type,
              created_at desc,
              id desc
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("drop view if exists latest_code_relations"))
    op.execute(sa.text("drop view if exists latest_node_entity_changes"))
    op.execute(sa.text("drop view if exists latest_documentation_outputs"))
    op.drop_index("ix_code_relations_to_relation_created", table_name="code_relations")
    op.drop_index("ix_code_relations_from_relation_created", table_name="code_relations")
    op.drop_index("ix_code_relations_version_from_to_type_created", table_name="code_relations")
    op.drop_index("ix_node_entity_changes_observed_name_created", table_name="node_entity_changes")
    op.drop_index("ix_node_entity_changes_entity_created", table_name="node_entity_changes")
    op.drop_index("ix_node_entity_changes_version_entity_created", table_name="node_entity_changes")
    op.drop_index("ix_code_entities_canonical_type_path", table_name="code_entities")
    op.drop_index("ix_documentation_outputs_content_hash", table_name="documentation_outputs")
    op.drop_index("ix_documentation_outputs_doc_definition_id", table_name="documentation_outputs")
    op.drop_index("ix_documentation_outputs_logical_scope_view_created", table_name="documentation_outputs")
    op.drop_index("ix_documentation_outputs_node_version_created", table_name="documentation_outputs")
