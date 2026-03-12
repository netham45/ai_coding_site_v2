from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import Field, ValidationError, model_validator

from aicoding.models.base import AICodingModel


class RelevantUserFlowInventoryValidationError(ValueError):
    """Raised when the relevant user flow inventory is invalid."""


ALLOWED_RELEVANCE_STATUSES = {"active", "partial", "deferred"}
ALLOWED_SYSTEM_EFFECT_STATUSES = {"affected", "not_applicable"}
ALLOWED_PROOF_STATUSES = {
    "planned",
    "in_progress",
    "implemented",
    "partial",
    "verified",
    "flow_complete",
    "blocked",
    "deferred",
}


class RelevantUserFlowRelevance(AICodingModel):
    status: str
    rationale: str
    discovered_from: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_relevance(self) -> "RelevantUserFlowRelevance":
        self.status = self.status.strip()
        self.rationale = self.rationale.strip()
        if self.status not in ALLOWED_RELEVANCE_STATUSES:
            raise ValueError(
                "relevance status must be one of: active, partial, deferred"
            )
        if not self.rationale:
            raise ValueError("relevance rationale may not be blank")
        return self


class RelevantUserFlowScope(AICodingModel):
    database: str
    cli: str
    daemon: str
    website_ui: str
    yaml: str
    prompts: str

    @model_validator(mode="after")
    def validate_scope(self) -> "RelevantUserFlowScope":
        for field_name in (
            "database",
            "cli",
            "daemon",
            "website_ui",
            "yaml",
            "prompts",
        ):
            value = getattr(self, field_name).strip()
            if value not in ALLOWED_SYSTEM_EFFECT_STATUSES:
                raise ValueError(
                    f"{field_name} must be one of: affected, not_applicable"
                )
            setattr(self, field_name, value)
        return self


class RelevantUserFlowCommands(AICodingModel):
    bounded: list[str] = Field(min_length=1)
    e2e: list[str] = Field(min_length=1)
    docs: list[str] = Field(min_length=1)


class RelevantUserFlowProof(AICodingModel):
    bounded_status: str
    real_e2e_status: str
    primary_e2e_target: str

    @model_validator(mode="after")
    def validate_proof(self) -> "RelevantUserFlowProof":
        self.bounded_status = self.bounded_status.strip()
        self.real_e2e_status = self.real_e2e_status.strip()
        self.primary_e2e_target = self.primary_e2e_target.strip()
        for field_name in ("bounded_status", "real_e2e_status"):
            value = getattr(self, field_name)
            if value not in ALLOWED_PROOF_STATUSES:
                raise ValueError(
                    f"{field_name} must use the adopted proof status vocabulary"
                )
        if not self.primary_e2e_target:
            raise ValueError("primary_e2e_target may not be blank")
        return self


class RelevantUserFlow(AICodingModel):
    flow_id: str
    title: str
    canonical_md: str
    summary: str
    relevance: RelevantUserFlowRelevance
    scope: RelevantUserFlowScope
    invariants: list[str] = Field(min_length=1)
    canonical_commands: RelevantUserFlowCommands
    proof: RelevantUserFlowProof
    related_notes: list[str] = Field(min_length=1)
    change_triggers: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_flow(self) -> "RelevantUserFlow":
        self.flow_id = self.flow_id.strip()
        self.title = self.title.strip()
        self.canonical_md = self.canonical_md.strip()
        self.summary = self.summary.strip()
        if not self.flow_id:
            raise ValueError("flow_id may not be blank")
        if not self.title:
            raise ValueError("title may not be blank")
        if not self.canonical_md:
            raise ValueError("canonical_md may not be blank")
        if not self.summary:
            raise ValueError("summary may not be blank")
        return self


class RelevantUserFlowInventory(AICodingModel):
    schema_version: int
    inventory_id: str
    purpose: str
    interpretation_rules: list[str] = Field(min_length=1)
    flows: list[RelevantUserFlow] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_inventory(self) -> "RelevantUserFlowInventory":
        self.inventory_id = self.inventory_id.strip()
        self.purpose = self.purpose.strip()
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")
        if self.inventory_id != "relevant_user_flow_inventory":
            raise ValueError("inventory_id must equal 'relevant_user_flow_inventory'")
        if not self.purpose:
            raise ValueError("purpose may not be blank")
        flow_ids = [flow.flow_id for flow in self.flows]
        if len(flow_ids) != len(set(flow_ids)):
            raise ValueError("flow inventory may not contain duplicate flow_id values")
        canonical_docs = [flow.canonical_md for flow in self.flows]
        if len(canonical_docs) != len(set(canonical_docs)):
            raise ValueError(
                "flow inventory may not contain duplicate canonical_md values"
            )
        return self


def load_relevant_user_flow_inventory(path: Path) -> RelevantUserFlowInventory:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RelevantUserFlowInventoryValidationError(
            f"invalid YAML in {path.name}: {exc}"
        ) from exc

    if not isinstance(raw, dict):
        raise RelevantUserFlowInventoryValidationError(
            f"{path.name} must contain a top-level mapping"
        )

    try:
        return RelevantUserFlowInventory.model_validate(raw)
    except ValidationError as exc:
        raise RelevantUserFlowInventoryValidationError(
            f"invalid relevant user flow inventory {path.name}: {exc}"
        ) from exc

