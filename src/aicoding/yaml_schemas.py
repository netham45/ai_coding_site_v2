from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import yaml
from pydantic import Field, ValidationError, model_validator

from aicoding.db.models import YamlSchemaValidationRecord
from aicoding.hierarchy import NodeDefinitionDocument
from aicoding.models.base import AICodingModel
from aicoding.resources import ResourceCatalog, load_resource_catalog


class ValidationCheckDefinition(AICodingModel):
    type: str
    path: str | None = None
    command: str | None = None
    exit_code: int | None = None
    schema_name: str | None = Field(default=None, alias="schema")
    value: str | None = None
    pattern: str | None = None

    @model_validator(mode="after")
    def validate_check_fields(self) -> "ValidationCheckDefinition":
        supported_types = {
            "ai_json_status",
            "command_exit_code",
            "dependencies_satisfied",
            "docs_built",
            "file_contains",
            "file_exists",
            "file_updated",
            "git_clean",
            "git_dirty",
            "json_schema",
            "provenance_updated",
            "session_bound",
            "summary_written",
            "yaml_schema",
        }
        if self.type not in supported_types:
            raise ValueError(f"unsupported validation check type '{self.type}'")
        if self.type in {"docs_built", "file_contains", "file_exists", "file_updated"} and not self.path:
            raise ValueError("path is required for this validation check type")
        if self.type == "file_contains" and not self.pattern:
            raise ValueError("pattern is required for file_contains validation checks")
        if self.type == "command_exit_code":
            if self.exit_code is None:
                raise ValueError("exit_code is required for command_exit_code validation checks")
        if self.type in {"ai_json_status"} and self.value is None:
            raise ValueError("value is required for ai_json_status validation checks")
        if self.type in {"json_schema", "yaml_schema"} and not self.schema_name:
            raise ValueError("schema is required for schema validation checks")
        return self


class OutputDefinition(AICodingModel):
    type: str
    path: str | None = None
    value: str | None = None


class RetryPolicy(AICodingModel):
    max_attempts: int = Field(ge=1)
    backoff_seconds: int = Field(default=0, ge=0)


class FailureAction(AICodingModel):
    action: str


class RenderContextDefinition(AICodingModel):
    inherits: bool = True
    variables: dict[str, str | int | float | bool] = Field(default_factory=dict)


class SubtaskRequirement(AICodingModel):
    subtask_complete: str


class SubtaskDefinitionDocument(AICodingModel):
    kind: str = "subtask_definition"
    id: str
    type: str
    title: str
    description: str
    requires: list[SubtaskRequirement] = Field(default_factory=list)
    prompt: str | None = None
    command: str | None = None
    args: dict[str, object] = Field(default_factory=dict)
    env: dict[str, str] = Field(default_factory=dict)
    environment_policy_ref: str | None = None
    checks: list[ValidationCheckDefinition] = Field(default_factory=list)
    outputs: list[OutputDefinition] = Field(default_factory=list)
    retry_policy: RetryPolicy
    block_on_user_flag: str | None = None
    pause_summary_prompt: str | None = None
    render_context: RenderContextDefinition | None = None
    on_failure: FailureAction

    @model_validator(mode="after")
    def ensure_payload(self) -> "SubtaskDefinitionDocument":
        if self.type in {"run_prompt", "review", "build_context", "write_summary"} and not self.prompt:
            raise ValueError("prompt is required for this subtask type")
        if self.type in {"run_command", "run_tests", "validate", "build_docs", "update_provenance", "merge_children"} and not self.command:
            raise ValueError("command is required for this subtask type")
        return self


class TaskPolicy(AICodingModel):
    max_subtask_retries: int = Field(ge=0)
    on_failure: str


class TaskDefinitionDocument(AICodingModel):
    kind: str = "task_definition"
    id: str
    name: str
    description: str
    applies_to_kinds: list[str]
    policy: TaskPolicy
    uses_reviews: list[str] = Field(default_factory=list)
    uses_testing: list[str] = Field(default_factory=list)
    uses_docs: list[str] = Field(default_factory=list)
    subtasks: list[SubtaskDefinitionDocument] = Field(min_length=1)


class LayoutChildDefinition(AICodingModel):
    id: str
    kind: str
    tier: int | str
    name: str
    goal: str
    rationale: str
    dependencies: list[str] = Field(default_factory=list)
    acceptance: list[str] = Field(default_factory=list)
    ordinal: int = Field(ge=1)


class LayoutDefinitionDocument(AICodingModel):
    kind: str = "layout_definition"
    id: str
    name: str
    description: str
    children: list[LayoutChildDefinition] = Field(min_length=1)


class ValidationDefinitionDocument(AICodingModel):
    kind: str = "validation_definition"
    id: str
    name: str
    description: str
    check: ValidationCheckDefinition


class ReviewAppliesTo(AICodingModel):
    node_kinds: list[str] = Field(default_factory=list)
    task_ids: list[str] = Field(default_factory=list)
    lifecycle_points: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_selector(self) -> "ReviewAppliesTo":
        if not self.node_kinds and not self.task_ids and not self.lifecycle_points:
            raise ValueError("at least one applies_to selector is required")
        return self


class ReviewInputs(AICodingModel):
    include_parent_requirements: bool = False
    include_child_summaries: bool = False
    include_acceptance_criteria: bool = False
    include_changed_files: bool = False
    include_validation_results: bool = False
    include_test_results: bool = False


class ReviewResultActions(AICodingModel):
    pass_action: str
    revise_action: str
    fail_action: str


class ReviewDefinitionDocument(AICodingModel):
    kind: str = "review_definition"
    id: str
    name: str
    applies_to: ReviewAppliesTo
    scope: str
    description: str
    inputs: ReviewInputs
    prompt: str
    criteria: list[str] = Field(min_length=1)
    on_result: ReviewResultActions

    @model_validator(mode="after")
    def validate_review_definition(self) -> "ReviewDefinitionDocument":
        if not self.scope.strip():
            raise ValueError("scope must not be empty")
        return self


class TestingCommand(AICodingModel):
    command: str
    working_directory: str
    env: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_command(self) -> "TestingCommand":
        if not self.command.strip():
            raise ValueError("command must not be empty")
        if not self.working_directory.strip():
            raise ValueError("working_directory must not be empty")
        return self


class TestingRetryPolicy(AICodingModel):
    max_attempts: int = Field(ge=1)
    rerun_failed_only: bool = False


class TestingPassRules(AICodingModel):
    require_exit_code_zero: bool = True
    max_failed_tests: int = Field(default=0, ge=0)


class TestingResultActions(AICodingModel):
    pass_action: str
    fail_action: str


class TestingDefinitionDocument(AICodingModel):
    kind: str = "testing_definition"
    id: str
    name: str
    applies_to: ReviewAppliesTo
    scope: str
    description: str
    commands: list[TestingCommand] = Field(min_length=1)
    retry_policy: TestingRetryPolicy
    pass_rules: TestingPassRules
    on_result: TestingResultActions

    @model_validator(mode="after")
    def validate_testing_definition(self) -> "TestingDefinitionDocument":
        if not self.scope.strip():
            raise ValueError("scope must not be empty")
        return self


class DocsInputs(AICodingModel):
    include_static_analysis: bool = False
    include_entity_relations: bool = False
    include_node_summaries: bool = False
    include_prompt_history: bool = False
    include_review_results: bool = False
    include_test_results: bool = False


class DocsOutput(AICodingModel):
    path: str
    view: str

    @model_validator(mode="after")
    def validate_output(self) -> "DocsOutput":
        if not self.path.strip():
            raise ValueError("path must not be empty")
        if not self.view.strip():
            raise ValueError("view must not be empty")
        return self


class DocsDefinitionDocument(AICodingModel):
    kind: str = "docs_definition"
    id: str
    name: str
    applies_to: ReviewAppliesTo
    scope: str
    description: str
    inputs: DocsInputs
    outputs: list[DocsOutput] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_docs_definition(self) -> "DocsDefinitionDocument":
        if not self.scope.strip():
            raise ValueError("scope must not be empty")
        return self


class HookAppliesTo(AICodingModel):
    tiers: list[int | str] = Field(default_factory=list)
    node_kinds: list[str] = Field(default_factory=list)
    task_ids: list[str] = Field(default_factory=list)
    subtask_types: list[str] = Field(default_factory=list)


class HookCondition(AICodingModel):
    changed_entity_types: list[str] = Field(default_factory=list)
    paths_match: list[str] = Field(default_factory=list)


class HookRunStep(AICodingModel):
    type: str
    command: str | None = None
    prompt: str | None = None
    render_context: RenderContextDefinition | None = None
    checks: list[ValidationCheckDefinition] = Field(default_factory=list)


class HookDefinitionDocument(AICodingModel):
    kind: str = "hook_definition"
    id: str
    when: str
    applies_to: HookAppliesTo
    if_: HookCondition = Field(alias="if")
    run: list[HookRunStep] = Field(min_length=1)


class RectificationDefinitionDocument(AICodingModel):
    kind: str = "rectification_definition"
    id: str
    name: str
    description: str
    trigger: str
    entry_task: str
    subtasks: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_rectification_definition(self) -> "RectificationDefinitionDocument":
        if not self.trigger.strip():
            raise ValueError("trigger must not be empty")
        if not self.entry_task.strip():
            raise ValueError("entry_task must not be empty")
        if len(set(self.subtasks)) != len(self.subtasks):
            raise ValueError("rectification subtasks must be unique")
        return self


class RuntimeDefinitionDocument(AICodingModel):
    kind: str = "runtime_definition"
    id: str
    name: str
    description: str
    commands: list[str] = Field(default_factory=list)
    thresholds: dict[str, int | bool | str] = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_runtime_definition(self) -> "RuntimeDefinitionDocument":
        if not self.commands:
            raise ValueError("runtime definitions must declare at least one command")
        if not self.actions:
            raise ValueError("runtime definitions must declare at least one action")
        if not self.thresholds:
            raise ValueError("runtime definitions must declare at least one threshold")
        if any(not command.strip() for command in self.commands):
            raise ValueError("runtime definition commands must not be empty")
        if any(not action.strip() for action in self.actions):
            raise ValueError("runtime definition actions must not be empty")
        if len(set(self.actions)) != len(self.actions):
            raise ValueError("runtime definition actions must be unique")
        return self


class RuntimePolicyDefinitionDocument(AICodingModel):
    kind: str = "runtime_policy_definition"
    id: str
    name: str
    description: str
    defaults: dict[str, int | bool | str]
    runtime_policy_refs: list[str] = Field(default_factory=list)
    hook_refs: list[str] = Field(default_factory=list)
    review_refs: list[str] = Field(default_factory=list)
    testing_refs: list[str] = Field(default_factory=list)
    docs_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_runtime_policy_definition(self) -> "RuntimePolicyDefinitionDocument":
        if not self.defaults:
            raise ValueError("runtime policy definitions must declare defaults")
        for field_name in ("runtime_policy_refs", "hook_refs", "review_refs", "testing_refs", "docs_refs"):
            values = getattr(self, field_name)
            if len(set(values)) != len(values):
                raise ValueError(f"{field_name} entries must be unique")
        return self


class EnvironmentPolicyDefinitionDocument(AICodingModel):
    kind: str = "environment_policy_definition"
    id: str
    isolation_mode: str
    allow_network: bool = False
    runtime_profile: str | None = None
    mandatory: bool = False

    @model_validator(mode="after")
    def validate_environment_policy(self) -> "EnvironmentPolicyDefinitionDocument":
        supported_modes = {"none", "container", "namespace", "custom_profile"}
        if self.isolation_mode not in supported_modes:
            raise ValueError(f"unsupported isolation_mode '{self.isolation_mode}'")
        if self.isolation_mode == "custom_profile" and not self.runtime_profile:
            raise ValueError("runtime_profile is required for custom_profile isolation")
        if self.isolation_mode != "custom_profile" and self.runtime_profile:
            raise ValueError("runtime_profile is only valid for custom_profile isolation")
        return self


class ProjectPolicyDefinitionDocument(AICodingModel):
    id: str
    description: str
    defaults: dict[str, int | bool | str]
    runtime_policy_refs: list[str] = Field(default_factory=list)
    hook_refs: list[str] = Field(default_factory=list)
    review_refs: list[str] = Field(default_factory=list)
    testing_refs: list[str] = Field(default_factory=list)
    docs_refs: list[str] = Field(default_factory=list)
    enabled_node_kinds: list[str] = Field(default_factory=list)
    prompt_pack: str = "default"
    environment_profiles: list[str] = Field(default_factory=list)


class OverrideCompatibility(AICodingModel):
    min_schema_version: int | str | None = None
    built_in_version: str | None = None


class OverrideDefinitionDocument(AICodingModel):
    id: str | None = None
    target_family: str
    target_id: str
    compatibility: OverrideCompatibility = Field(default_factory=OverrideCompatibility)
    merge_mode: str
    value: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def ensure_supported_target(self) -> "OverrideDefinitionDocument":
        supported = {
            "node_definition",
            "task_definition",
            "layout_definition",
            "hook_definition",
            "review_definition",
            "testing_definition",
            "docs_definition",
            "rectification_definition",
            "project_policy_definition",
            "runtime_policy_definition",
            "prompt_reference_definition",
        }
        if self.target_family not in supported:
            raise ValueError(f"unsupported override target family '{self.target_family}'")
        if self.merge_mode not in {"replace", "deep_merge", "append_list", "replace_list"}:
            raise ValueError(f"unsupported merge_mode '{self.merge_mode}'")
        if not self.value:
            raise ValueError("override value must not be empty")
        return self


class PromptReferenceDefinitionDocument(AICodingModel):
    kind: str = "prompt_reference_definition"
    id: str
    name: str
    description: str
    references: dict[str, str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_prompt_reference_definition(self) -> "PromptReferenceDefinitionDocument":
        for key, value in self.references.items():
            if "." not in key:
                raise ValueError("prompt reference keys must use dotted identifiers")
            if value.startswith("prompts/"):
                raise ValueError("prompt reference values must be relative to the prompt pack root")
            if not value.endswith(".md"):
                raise ValueError("prompt reference values must point to markdown prompt assets")
        return self


class SchemaFamilyDescriptor(AICodingModel):
    family: str
    source_group: str
    relative_glob: str
    validator_model: str
    status: str


class ValidationIssue(AICodingModel):
    message: str
    location: list[str | int]


class YamlValidationReport(AICodingModel):
    record_id: str
    source_group: str
    relative_path: str
    family: str
    valid: bool
    issue_count: int
    issues: list[ValidationIssue]
    validated_at: str


FAMILY_MODELS = {
    "node_definition": NodeDefinitionDocument,
    "task_definition": TaskDefinitionDocument,
    "subtask_definition": SubtaskDefinitionDocument,
    "layout_definition": LayoutDefinitionDocument,
    "validation_definition": ValidationDefinitionDocument,
    "review_definition": ReviewDefinitionDocument,
    "testing_definition": TestingDefinitionDocument,
    "docs_definition": DocsDefinitionDocument,
    "hook_definition": HookDefinitionDocument,
    "rectification_definition": RectificationDefinitionDocument,
    "runtime_definition": RuntimeDefinitionDocument,
    "runtime_policy_definition": RuntimePolicyDefinitionDocument,
    "environment_policy_definition": EnvironmentPolicyDefinitionDocument,
    "project_policy_definition": ProjectPolicyDefinitionDocument,
    "override_definition": OverrideDefinitionDocument,
    "prompt_reference_definition": PromptReferenceDefinitionDocument,
}


def schema_family_descriptors() -> list[SchemaFamilyDescriptor]:
    return [
        SchemaFamilyDescriptor(
            family=family,
            source_group="yaml_builtin_system",
            relative_glob=f"{directory}/*.yaml",
            validator_model=model.__name__,
            status="active",
        )
        for family, directory, model in (
            ("node_definition", "nodes", NodeDefinitionDocument),
            ("task_definition", "tasks", TaskDefinitionDocument),
            ("subtask_definition", "subtasks", SubtaskDefinitionDocument),
            ("layout_definition", "layouts", LayoutDefinitionDocument),
            ("validation_definition", "validations", ValidationDefinitionDocument),
            ("review_definition", "reviews", ReviewDefinitionDocument),
            ("testing_definition", "testing", TestingDefinitionDocument),
            ("docs_definition", "docs", DocsDefinitionDocument),
            ("hook_definition", "hooks", HookDefinitionDocument),
            ("rectification_definition", "rectification", RectificationDefinitionDocument),
            ("runtime_definition", "runtime", RuntimeDefinitionDocument),
            ("runtime_policy_definition", "policies", RuntimePolicyDefinitionDocument),
            ("environment_policy_definition", "environments", EnvironmentPolicyDefinitionDocument),
            ("prompt_reference_definition", "prompts", PromptReferenceDefinitionDocument),
        )
    ] + [
        SchemaFamilyDescriptor(
            family="project_policy_definition",
            source_group="yaml_project",
            relative_glob="project-policies/*.yaml",
            validator_model=ProjectPolicyDefinitionDocument.__name__,
            status="active",
        ),
        SchemaFamilyDescriptor(
            family="override_definition",
            source_group="yaml_overrides",
            relative_glob="**/*.yaml",
            validator_model=OverrideDefinitionDocument.__name__,
            status="active",
        )
    ]


def identify_yaml_family(relative_path: str, source_group: str = "yaml_builtin_system") -> str:
    if source_group == "yaml_overrides":
        return "override_definition"
    section = Path(relative_path).parts[0]
    if source_group in {"yaml_project", "yaml_project_policies"} and section == "project-policies":
        return "project_policy_definition"
    return {
        "nodes": "node_definition",
        "tasks": "task_definition",
        "subtasks": "subtask_definition",
        "layouts": "layout_definition",
        "validations": "validation_definition",
        "reviews": "review_definition",
        "testing": "testing_definition",
        "docs": "docs_definition",
        "hooks": "hook_definition",
        "rectification": "rectification_definition",
        "runtime": "runtime_definition",
        "policies": "runtime_policy_definition",
        "environments": "environment_policy_definition",
        "prompts": "prompt_reference_definition",
    }[section]


WRAPPED_DOCUMENT_KEYS = {
    "node_definition": "node_definition",
    "project_policy_definition": "project_policy_definition",
}


def unwrap_yaml_document_payload(family: str, raw: dict[str, object]) -> dict[str, object]:
    key = WRAPPED_DOCUMENT_KEYS.get(family)
    if key is None:
        return raw
    payload = raw.get(key)
    if not isinstance(payload, dict):
        raise KeyError(key)
    return payload


def wrap_yaml_document_payload(family: str, raw: dict[str, object]) -> dict[str, object]:
    key = WRAPPED_DOCUMENT_KEYS.get(family)
    if key is None:
        return raw
    return {key: raw}


def validate_yaml_document(catalog: ResourceCatalog, *, source_group: str, relative_path: str) -> YamlValidationReport:
    family = identify_yaml_family(relative_path, source_group)
    raw = yaml.safe_load(catalog.read_text(source_group, relative_path))
    if family == "project_policy_definition":
        raw = unwrap_yaml_document_payload(family, raw)
    issues: list[ValidationIssue] = []
    try:
        payload = FAMILY_MODELS[family].model_validate(raw)
        _validate_prompt_assets(catalog, family=family, payload=payload)
        _validate_runtime_policy_assets(catalog, family=family, payload=payload)
        valid = True
    except ValidationError as exc:
        valid = False
        for error in exc.errors():
            issues.append(ValidationIssue(message=error["msg"], location=list(error["loc"])))
    except ValueError as exc:
        valid = False
        issues.append(ValidationIssue(message=str(exc), location=[]))
    validated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return YamlValidationReport(
        record_id=str(uuid4()),
        source_group=source_group,
        relative_path=relative_path,
        family=family,
        valid=valid,
        issue_count=len(issues),
        issues=issues,
        validated_at=validated_at,
    )


def _validate_prompt_assets(catalog: ResourceCatalog, *, family: str, payload: AICodingModel) -> None:
    prompt_values = list(_iter_prompt_values(family, payload))
    if not prompt_values:
        return
    for field_name, prompt_value in prompt_values:
        if not prompt_value.startswith("prompts/"):
            raise ValueError(f"{field_name} must start with 'prompts/'")
        relative_prompt_path = prompt_value.removeprefix("prompts/")
        if not catalog.resolve("prompt_pack_default", relative_prompt_path).exists():
            raise ValueError(f"{field_name} references missing prompt asset '{prompt_value}'")


def _iter_prompt_values(family: str, payload: AICodingModel) -> list[tuple[str, str]]:
    if family == "review_definition":
        return [("prompt", payload.prompt)]  # type: ignore[attr-defined]
    if family == "hook_definition":
        values: list[tuple[str, str]] = []
        for index, step in enumerate(payload.run):  # type: ignore[attr-defined]
            if step.prompt:
                values.append((f"run[{index}].prompt", step.prompt))
        return values
    if family == "prompt_reference_definition":
        return [(f"references.{key}", f"prompts/{value}") for key, value in payload.references.items()]  # type: ignore[attr-defined]
    return []


def _validate_runtime_policy_assets(catalog: ResourceCatalog, *, family: str, payload: AICodingModel) -> None:
    if family == "runtime_definition":
        for index, action in enumerate(payload.actions):  # type: ignore[attr-defined]
            relative_path = f"subtasks/{action}.yaml"
            if not catalog.resolve("yaml_builtin_system", relative_path).exists():
                raise ValueError(f"actions[{index}] references missing subtask asset '{relative_path}'")
        return
    if family != "runtime_policy_definition":
        return
    ref_groups = {
        "runtime_policy_refs": "runtime",
        "hook_refs": "hooks",
        "review_refs": "reviews",
        "testing_refs": "testing",
        "docs_refs": "docs",
    }
    for field_name, directory in ref_groups.items():
        for index, ref in enumerate(getattr(payload, field_name)):  # type: ignore[attr-defined]
            normalized = _normalize_relative_yaml_ref(ref, directory)
            if not catalog.resolve("yaml_builtin_system", normalized).exists():
                raise ValueError(f"{field_name}[{index}] references missing YAML asset '{normalized}'")


def _normalize_relative_yaml_ref(reference: str, directory: str) -> str:
    relative_path = reference.removeprefix(f"{directory}/")
    if not relative_path.endswith(".yaml"):
        relative_path = f"{relative_path}.yaml"
    return f"{directory}/{relative_path}"


def validate_builtin_yaml_set(catalog: ResourceCatalog | None = None) -> list[YamlValidationReport]:
    resource_catalog = catalog or load_resource_catalog()
    reports: list[YamlValidationReport] = []
    root = resource_catalog.yaml_builtin_system_dir
    for path in sorted(root.rglob("*.yaml")):
        relative_path = str(path.relative_to(root))
        reports.append(validate_yaml_document(resource_catalog, source_group="yaml_builtin_system", relative_path=relative_path))
    project_root = resource_catalog.yaml_project_policies_dir
    if project_root.exists():
        for path in sorted(project_root.rglob("*.yaml")):
            relative_path = str(path.relative_to(resource_catalog.yaml_project_dir))
            reports.append(validate_yaml_document(resource_catalog, source_group="yaml_project", relative_path=relative_path))
    overrides_root = resource_catalog.yaml_overrides_dir
    if overrides_root.exists():
        for path in sorted(overrides_root.rglob("*.yaml")):
            relative_path = str(path.relative_to(overrides_root))
            reports.append(validate_yaml_document(resource_catalog, source_group="yaml_overrides", relative_path=relative_path))
    return reports


def persist_yaml_validation_report(session_factory, report: YamlValidationReport) -> None:
    from aicoding.db.session import session_scope

    with session_scope(session_factory) as session:
        session.add(
            YamlSchemaValidationRecord(
                id=UUID(report.record_id),
                source_group=report.source_group,
                relative_path=report.relative_path,
                family=report.family,
                is_valid=report.valid,
                issue_count=report.issue_count,
                issues_json=[issue.model_dump() for issue in report.issues],
            )
        )


def latest_yaml_validation_report(session_factory, *, source_group: str, relative_path: str) -> YamlValidationReport | None:
    from aicoding.db.session import query_session_scope

    with query_session_scope(session_factory) as session:
        row = (
            session.query(YamlSchemaValidationRecord)
            .filter_by(source_group=source_group, relative_path=relative_path)
            .order_by(YamlSchemaValidationRecord.validated_at.desc())
            .first()
        )
        if row is None:
            return None
        return YamlValidationReport(
            record_id=str(row.id),
            source_group=row.source_group,
            relative_path=row.relative_path,
            family=row.family,
            valid=row.is_valid,
            issue_count=row.issue_count,
            issues=[ValidationIssue.model_validate(issue) for issue in row.issues_json],
            validated_at=row.validated_at.isoformat(),
        )
