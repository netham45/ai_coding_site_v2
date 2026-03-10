"""create code provenance and rationale tables

Revision ID: 0021_code_provenance_map
Revises: 0020_prompt_and_summary_history
Create Date: 2026-03-09 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0021_code_provenance_map"
down_revision = "0020_prompt_and_summary_history"
branch_labels = None
depends_on = None


ENTITY_TYPES = ("module", "class", "function", "method")
CHANGE_TYPES = ("added", "modified", "unchanged", "renamed_or_moved", "removed")
MATCH_CONFIDENCE = ("high", "medium", "low")
RELATION_TYPES = ("contains", "calls")
RELATION_SOURCES = ("ast_exact", "ast_inferred")


def upgrade() -> None:
    op.create_table(
        "code_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=255), nullable=True),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("start_line", sa.Integer(), nullable=True),
        sa.Column("end_line", sa.Integer(), nullable=True),
        sa.Column("stable_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "entity_type in ('module','class','function','method')",
            name="ck_code_entities_entity_type",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_entities_entity_type", "code_entities", ["entity_type"])
    op.create_index("ix_code_entities_canonical_name", "code_entities", ["canonical_name"])
    op.create_index("ix_code_entities_file_path", "code_entities", ["file_path"])
    op.create_index("ix_code_entities_stable_hash", "code_entities", ["stable_hash"])

    op.create_table(
        "node_entity_changes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("summary_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("change_type", sa.String(length=32), nullable=False),
        sa.Column("match_confidence", sa.String(length=16), nullable=False),
        sa.Column("match_reason", sa.String(length=64), nullable=False),
        sa.Column("rationale_summary", sa.Text(), nullable=True),
        sa.Column("observed_canonical_name", sa.String(length=255), nullable=False),
        sa.Column("observed_file_path", sa.String(length=255), nullable=True),
        sa.Column("observed_signature", sa.Text(), nullable=True),
        sa.Column("observed_stable_hash", sa.String(length=64), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "change_type in ('added','modified','unchanged','renamed_or_moved','removed')",
            name="ck_node_entity_changes_change_type",
        ),
        sa.CheckConstraint(
            "match_confidence in ('high','medium','low')",
            name="ck_node_entity_changes_match_confidence",
        ),
        sa.ForeignKeyConstraint(["entity_id"], ["code_entities.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["prompt_record_id"], ["prompts.id"]),
        sa.ForeignKeyConstraint(["summary_record_id"], ["summaries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_node_entity_changes_node_version_id", "node_entity_changes", ["node_version_id"])
    op.create_index("ix_node_entity_changes_entity_id", "node_entity_changes", ["entity_id"])
    op.create_index("ix_node_entity_changes_prompt_record_id", "node_entity_changes", ["prompt_record_id"])
    op.create_index("ix_node_entity_changes_summary_record_id", "node_entity_changes", ["summary_record_id"])
    op.create_index("ix_node_entity_changes_change_type", "node_entity_changes", ["change_type"])
    op.create_index("ix_node_entity_changes_match_confidence", "node_entity_changes", ["match_confidence"])
    op.create_index("ix_node_entity_changes_match_reason", "node_entity_changes", ["match_reason"])

    op.create_table(
        "code_relations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("node_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("to_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relation_type", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("rationale_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "relation_type in ('contains','calls')",
            name="ck_code_relations_relation_type",
        ),
        sa.CheckConstraint(
            "source in ('ast_exact','ast_inferred')",
            name="ck_code_relations_source",
        ),
        sa.CheckConstraint("from_entity_id <> to_entity_id", name="ck_code_relations_not_self"),
        sa.ForeignKeyConstraint(["from_entity_id"], ["code_entities.id"]),
        sa.ForeignKeyConstraint(["node_version_id"], ["node_versions.id"]),
        sa.ForeignKeyConstraint(["to_entity_id"], ["code_entities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_relations_node_version_id", "code_relations", ["node_version_id"])
    op.create_index("ix_code_relations_from_entity_id", "code_relations", ["from_entity_id"])
    op.create_index("ix_code_relations_to_entity_id", "code_relations", ["to_entity_id"])
    op.create_index("ix_code_relations_relation_type", "code_relations", ["relation_type"])
    op.create_index("ix_code_relations_source", "code_relations", ["source"])


def downgrade() -> None:
    op.drop_index("ix_code_relations_source", table_name="code_relations")
    op.drop_index("ix_code_relations_relation_type", table_name="code_relations")
    op.drop_index("ix_code_relations_to_entity_id", table_name="code_relations")
    op.drop_index("ix_code_relations_from_entity_id", table_name="code_relations")
    op.drop_index("ix_code_relations_node_version_id", table_name="code_relations")
    op.drop_table("code_relations")

    op.drop_index("ix_node_entity_changes_match_reason", table_name="node_entity_changes")
    op.drop_index("ix_node_entity_changes_match_confidence", table_name="node_entity_changes")
    op.drop_index("ix_node_entity_changes_change_type", table_name="node_entity_changes")
    op.drop_index("ix_node_entity_changes_summary_record_id", table_name="node_entity_changes")
    op.drop_index("ix_node_entity_changes_prompt_record_id", table_name="node_entity_changes")
    op.drop_index("ix_node_entity_changes_entity_id", table_name="node_entity_changes")
    op.drop_index("ix_node_entity_changes_node_version_id", table_name="node_entity_changes")
    op.drop_table("node_entity_changes")

    op.drop_index("ix_code_entities_stable_hash", table_name="code_entities")
    op.drop_index("ix_code_entities_file_path", table_name="code_entities")
    op.drop_index("ix_code_entities_canonical_name", table_name="code_entities")
    op.drop_index("ix_code_entities_entity_type", table_name="code_entities")
    op.drop_table("code_entities")
