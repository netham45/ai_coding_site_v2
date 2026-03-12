import { createElement, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import LoadingState from "../primitives/LoadingState.js";
import EmptyState from "../primitives/EmptyState.js";
import ErrorState from "../primitives/ErrorState.js";
import StatusBadge from "../primitives/StatusBadge.js";
import {
  attachNodeSession,
  getNodeActions,
  pauseNodeRun,
  providerResumeNodeSession,
  reconcileNodeChildren,
  resumeNodeRun,
  resumeNodeSession,
  startNodeRun,
} from "../../lib/api/actions.js";
import { getNodeLineage, getNodeOverview, getNodeRationale, getNodeSources } from "../../lib/api/nodes.js";
import { getNodeVersion, getPromptHistory, regenerateNode, supersedeNode } from "../../lib/api/prompts.js";
import { getSessions } from "../../lib/api/sessions.js";
import { getSummaryHistory } from "../../lib/api/summaries.js";
import { queryKeys } from "../../lib/query/keys.js";
import {
  getCurrentSubtask,
  getCurrentSubtaskContext,
  getCurrentSubtaskPrompt,
  getCurrentWorkflow,
  getRunProgress,
  getRuns,
  getSubtaskAttempt,
  getSubtaskAttempts,
} from "../../lib/api/workflows.js";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "workflow", label: "Workflow" },
  { id: "runs", label: "Runs" },
  { id: "prompts", label: "Prompts" },
  { id: "actions", label: "Actions" },
  { id: "summaries", label: "Summaries" },
  { id: "sessions", label: "Sessions" },
  { id: "provenance", label: "Provenance" },
];

function DetailCard({ title, children, testId, actions = null }) {
  return createElement(
    "section",
    { className: "detail-card", "data-testid": testId },
    [
      createElement(
        "div",
        { key: "header", className: "detail-card__header" },
        [
          createElement("h3", { key: "title", className: "detail-card__title" }, title),
          actions,
        ],
      ),
      children,
    ],
  );
}

function KeyValueList({ rows }) {
  return createElement(
    "dl",
    { className: "key-value-list" },
    rows.map((row) =>
      createElement(
        "div",
        { key: row.label, className: "key-value-list__row" },
        [
          createElement("dt", { key: "label" }, row.label),
          createElement("dd", { key: "value" }, row.value ?? "n/a"),
        ],
      ),
    ),
  );
}

function RawJsonToggle({ payload, testId }) {
  const [open, setOpen] = useState(false);
  return createElement(
    "div",
    { className: "raw-json-toggle" },
    [
      createElement(
        "button",
        {
          key: "button",
          type: "button",
          className: "button button--secondary",
          onClick: () => setOpen((current) => !current),
          "data-testid": `${testId}-toggle`,
        },
        open ? "hide raw json" : "show raw json",
      ),
      open
        ? createElement(
            "pre",
            { key: "json", className: "raw-json-toggle__pre", "data-testid": `${testId}-panel` },
            JSON.stringify(payload, null, 2),
          )
        : null,
    ],
  );
}

function QueryPanel({ query, loadingLabel, errorTitle, emptyTitle, emptyBody, render }) {
  if (query.isLoading) {
    return createElement(LoadingState, { label: loadingLabel });
  }
  if (query.isError) {
    return createElement(ErrorState, { title: errorTitle, body: query.error.message });
  }
  if (!query.data) {
    return createElement(EmptyState, { title: emptyTitle, body: emptyBody });
  }
  return render(query.data);
}

function OverviewPanel({ nodeId }) {
  const summaryQuery = useQuery({
    queryKey: queryKeys.nodeOverview(nodeId),
    queryFn: async () => (await getNodeOverview(nodeId)).data,
  });
  const lineageQuery = useQuery({
    queryKey: ["node", nodeId, "lineage"],
    queryFn: async () => (await getNodeLineage(nodeId)).data,
  });

  if (summaryQuery.isLoading || lineageQuery.isLoading) {
    return createElement(LoadingState, { label: "Loading node overview." });
  }
  if (summaryQuery.isError) {
    return createElement(ErrorState, { title: "Could not load overview", body: summaryQuery.error.message });
  }
  if (lineageQuery.isError) {
    return createElement(ErrorState, { title: "Could not load lineage", body: lineageQuery.error.message });
  }

  const summary = summaryQuery.data;
  const lineage = lineageQuery.data;
  return createElement(
    "div",
    { className: "detail-grid", "data-testid": "detail-tab-overview" },
    [
      createElement(
        DetailCard,
        { key: "summary", title: "Node Summary", testId: "overview-summary-card" },
        [
          createElement("p", { key: "lede", className: "detail-card__lede" }, summary.prompt),
          createElement(KeyValueList, {
            key: "list",
            rows: [
              { label: "Kind", value: summary.kind },
              { label: "Tier", value: summary.tier },
              { label: "Lifecycle", value: summary.lifecycle_state },
              { label: "Run status", value: summary.run_status },
              { label: "Current run", value: summary.current_run_id },
              { label: "Current subtask", value: summary.current_subtask_id },
              { label: "Active branch", value: summary.active_branch_name },
            ],
          }),
        ],
      ),
      createElement(
        DetailCard,
        { key: "lineage", title: "Lineage", testId: "overview-lineage-card" },
        createElement(KeyValueList, {
          rows: [
            { label: "Authoritative version", value: lineage.authoritative_node_version_id },
            { label: "Latest created version", value: lineage.latest_created_node_version_id },
            { label: "Version count", value: String(lineage.versions?.length ?? 0) },
          ],
        }),
      ),
      createElement(RawJsonToggle, { key: "json", payload: { summary, lineage }, testId: "overview-raw-json" }),
    ],
  );
}

function describeJsonValue(value) {
  if (value == null) {
    return "n/a";
  }
  if (typeof value === "string") {
    return value;
  }
  return JSON.stringify(value);
}

function WorkflowTaskTree({
  tasks,
  currentSubtaskId,
  expandedTaskIds,
  onToggleTask,
  selectedSubtaskId,
  onSelectSubtask,
}) {
  if (!tasks?.length) {
    return createElement(EmptyState, { title: "No tasks", body: "The compiled workflow has no tasks." });
  }

  return createElement(
    "div",
    { className: "workflow-task-tree", "data-testid": "workflow-task-tree" },
    tasks.map((task) => {
      const isExpanded = expandedTaskIds.has(task.id);
      return createElement(
        "section",
        { key: task.id, className: "workflow-task-group", "data-testid": `workflow-task-${task.id}` },
        [
          createElement(
            "button",
            {
              key: "toggle",
              type: "button",
              className: "workflow-task-toggle",
              onClick: () => onToggleTask(task.id),
              "data-testid": `workflow-task-toggle-${task.id}`,
              "aria-expanded": isExpanded ? "true" : "false",
            },
            `${isExpanded ? "Hide" : "Show"} ${task.task_key} (${task.subtasks.length} subtasks)`,
          ),
          isExpanded
            ? createElement(
                "div",
                { key: "subtasks", className: "workflow-subtask-list" },
                task.subtasks.map((subtask) => {
                  const isSelected = selectedSubtaskId === subtask.id;
                  const isCurrent = currentSubtaskId === subtask.id;
                  return createElement(
                    "button",
                    {
                      key: subtask.id,
                      type: "button",
                      className: `workflow-subtask-row ${isSelected ? "workflow-subtask-row--selected" : ""}`,
                      onClick: () => onSelectSubtask(subtask.id),
                      "data-testid": `workflow-subtask-${subtask.id}`,
                    },
                    [
                      createElement(
                        "div",
                        { key: "main", className: "workflow-subtask-row__main" },
                        [
                          createElement("strong", { key: "title" }, subtask.title ?? subtask.source_subtask_key),
                          createElement(
                            "span",
                            { key: "meta", className: "workflow-subtask-row__meta" },
                            `${subtask.subtask_type} • ordinal ${subtask.ordinal}`,
                          ),
                        ],
                      ),
                      isCurrent
                        ? createElement(StatusBadge, {
                            key: "current",
                            label: "current",
                            tone: "info",
                          })
                        : null,
                    ],
                  );
                }),
              )
            : null,
        ],
      );
    }),
  );
}

function AttemptHistoryList({ attempts, selectedAttemptId, onSelectAttempt }) {
  if (!attempts?.length) {
    return createElement(EmptyState, {
      title: "No attempts yet",
      body: "No subtask attempts have been recorded for this node yet.",
    });
  }

  return createElement(
    "div",
    { className: "workflow-attempt-list", "data-testid": "workflow-attempt-list" },
    attempts.map((attempt) =>
      createElement(
        "button",
        {
          key: attempt.id,
          type: "button",
          className: `workflow-attempt-row ${selectedAttemptId === attempt.id ? "workflow-attempt-row--selected" : ""}`,
          onClick: () => onSelectAttempt(attempt.id),
          "data-testid": `workflow-attempt-${attempt.id}`,
        },
        [
          createElement(
            "div",
            { key: "main", className: "workflow-attempt-row__main" },
            [
              createElement("strong", { key: "title" }, `Attempt ${attempt.attempt_number}`),
              createElement(
                "span",
                { key: "meta", className: "workflow-attempt-row__meta" },
                `${attempt.compiled_subtask_id} • ${attempt.started_at ?? "not started"}`,
              ),
            ],
          ),
          createElement(StatusBadge, {
            key: "status",
            label: attempt.status.toLowerCase(),
            tone: attempt.status === "COMPLETE" ? "success" : attempt.status === "FAILED" ? "danger" : "info",
          }),
        ],
      ),
    ),
  );
}

function WorkflowPanel({ nodeId }) {
  const workflowQuery = useQuery({
    queryKey: queryKeys.nodeWorkflow(nodeId),
    queryFn: async () => (await getCurrentWorkflow(nodeId)).data,
  });

  const currentSubtaskQuery = useQuery({
    queryKey: queryKeys.nodeCurrentSubtask(nodeId),
    queryFn: async () => (await getCurrentSubtask(nodeId)).data,
  });

  const currentPromptQuery = useQuery({
    queryKey: queryKeys.nodeCurrentSubtaskPrompt(nodeId),
    queryFn: async () => (await getCurrentSubtaskPrompt(nodeId)).data,
    enabled: Boolean(currentSubtaskQuery.data?.current_subtask?.id),
  });

  const currentContextQuery = useQuery({
    queryKey: queryKeys.nodeCurrentSubtaskContext(nodeId),
    queryFn: async () => (await getCurrentSubtaskContext(nodeId)).data,
    enabled: Boolean(currentSubtaskQuery.data?.current_subtask?.id),
  });

  const attemptsQuery = useQuery({
    queryKey: queryKeys.nodeSubtaskAttempts(nodeId),
    queryFn: async () => (await getSubtaskAttempts(nodeId)).data,
    enabled: Boolean(currentSubtaskQuery.data?.state?.node_run_id),
  });

  const [expandedTaskIds, setExpandedTaskIds] = useState(() => new Set());
  const [selectedSubtaskId, setSelectedSubtaskId] = useState(null);
  const [selectedAttemptId, setSelectedAttemptId] = useState(null);

  const taskMap = useMemo(() => {
    const tasks = workflowQuery.data?.tasks ?? [];
    const map = new Map();
    for (const task of tasks) {
      map.set(task.id, task);
    }
    return map;
  }, [workflowQuery.data]);

  const subtaskMap = useMemo(() => {
    const map = new Map();
    for (const task of workflowQuery.data?.tasks ?? []) {
      for (const subtask of task.subtasks ?? []) {
        map.set(subtask.id, { ...subtask, task_id: task.id, task_key: task.task_key, task_title: task.title ?? task.task_key });
      }
    }
    return map;
  }, [workflowQuery.data]);

  const currentSubtask = currentSubtaskQuery.data?.current_subtask ?? null;
  const attempts = attemptsQuery.data?.attempts ?? [];
  const firstTaskId = workflowQuery.data?.tasks?.[0]?.id ?? null;
  const firstSubtaskId = workflowQuery.data?.tasks?.find((task) => task.subtasks?.length)?.subtasks?.[0]?.id ?? null;
  const effectiveExpandedTaskIds = expandedTaskIds.size
    ? expandedTaskIds
    : new Set([currentSubtask?.compiled_task_id ?? firstTaskId].filter(Boolean));
  const effectiveSelectedSubtaskId = selectedSubtaskId ?? currentSubtask?.id ?? firstSubtaskId;
  const effectiveSelectedAttemptId = selectedAttemptId ?? currentSubtaskQuery.data?.latest_attempt?.id ?? attempts[0]?.id ?? null;

  useEffect(() => {
    const workflow = workflowQuery.data;
    if (!workflow?.tasks?.length) {
      return;
    }
    setExpandedTaskIds((current) => {
      const next = new Set(current);
      if (!next.size) {
        next.add(workflow.tasks[0].id);
      }
      if (currentSubtask?.compiled_task_id) {
        next.add(currentSubtask.compiled_task_id);
      }
      return next;
    });
  }, [currentSubtask?.compiled_task_id, workflowQuery.data]);

  useEffect(() => {
    const workflow = workflowQuery.data;
    if (!workflow?.tasks?.length) {
      return;
    }
    const firstSubtaskId = workflow.tasks.find((task) => task.subtasks?.length)?.subtasks?.[0]?.id ?? null;
    const preferredSubtaskId = currentSubtask?.id ?? firstSubtaskId;
    if (!preferredSubtaskId) {
      return;
    }
    setSelectedSubtaskId((current) => (current && subtaskMap.has(current) ? current : preferredSubtaskId));
  }, [currentSubtask?.id, subtaskMap, workflowQuery.data]);

  useEffect(() => {
    if (!attempts.length) {
      setSelectedAttemptId(null);
      return;
    }
    const preferredAttemptId = currentSubtaskQuery.data?.latest_attempt?.id ?? attempts[0].id;
    setSelectedAttemptId((current) => (current && attempts.some((attempt) => attempt.id === current) ? current : preferredAttemptId));
  }, [attempts, currentSubtaskQuery.data?.latest_attempt?.id]);

  const selectedSubtask = effectiveSelectedSubtaskId ? subtaskMap.get(effectiveSelectedSubtaskId) ?? null : null;

  const selectedAttemptQuery = useQuery({
    queryKey: queryKeys.subtaskAttempt(effectiveSelectedAttemptId),
    queryFn: async () => (await getSubtaskAttempt(effectiveSelectedAttemptId)).data,
    enabled: Boolean(effectiveSelectedAttemptId),
  });

  function toggleTask(taskId) {
    setExpandedTaskIds((current) => {
      const next = new Set(current);
      if (next.has(taskId)) {
        next.delete(taskId);
      } else {
        next.add(taskId);
      }
      return next;
    });
  }

  return createElement(QueryPanel, {
    query: workflowQuery,
    loadingLabel: "Loading workflow detail.",
    errorTitle: "Could not load workflow",
    emptyTitle: "No workflow loaded",
    emptyBody: "This node does not currently have a compiled workflow.",
    render: (workflow) =>
      createElement(
        "div",
        { className: "detail-grid", "data-testid": "detail-tab-workflow" },
        [
          createElement(
            DetailCard,
            { key: "summary", title: "Workflow Summary", testId: "workflow-summary-card" },
            createElement(KeyValueList, {
              rows: [
                { label: "Workflow id", value: workflow.id },
                { label: "Task count", value: String(workflow.task_count) },
                { label: "Subtask count", value: String(workflow.subtask_count) },
                { label: "Source docs", value: String(workflow.source_document_count) },
                { label: "Created", value: workflow.created_at },
                { label: "Current task", value: currentSubtaskQuery.data?.state?.current_task_id },
                { label: "Current subtask", value: currentSubtask?.id },
              ],
            }),
          ),
          createElement(
            DetailCard,
            { key: "tasks", title: "Workflow Tasks", testId: "workflow-tasks-card" },
            createElement(WorkflowTaskTree, {
              tasks: workflow.tasks,
              currentSubtaskId: currentSubtask?.id ?? null,
              expandedTaskIds: effectiveExpandedTaskIds,
              onToggleTask: toggleTask,
              selectedSubtaskId: effectiveSelectedSubtaskId,
              onSelectSubtask: setSelectedSubtaskId,
            }),
          ),
          currentSubtaskQuery.isError && currentSubtaskQuery.error?.status !== 404
            ? createElement(
                DetailCard,
                { key: "current-error", title: "Current Execution", testId: "workflow-current-subtask-card" },
                createElement(ErrorState, {
                  title: "Could not load current subtask",
                  body: currentSubtaskQuery.error.message,
                }),
              )
            : createElement(
                DetailCard,
                { key: "current", title: "Current Execution", testId: "workflow-current-subtask-card" },
                currentSubtask
                  ? createElement(KeyValueList, {
                      rows: [
                        { label: "Run id", value: currentSubtaskQuery.data?.run?.id ?? currentSubtaskQuery.data?.state?.node_run_id },
                        { label: "Task", value: taskMap.get(currentSubtask.compiled_task_id)?.title ?? taskMap.get(currentSubtask.compiled_task_id)?.task_key ?? currentSubtask.compiled_task_id },
                        { label: "Subtask key", value: currentSubtask.source_subtask_key },
                        { label: "Subtask type", value: currentSubtask.subtask_type },
                        { label: "Attempt", value: String(currentSubtaskQuery.data?.state?.current_subtask_attempt ?? "") || "n/a" },
                        { label: "Depends on", value: currentSubtask.depends_on_compiled_subtask_ids?.length ? currentSubtask.depends_on_compiled_subtask_ids.join(", ") : "none" },
                      ],
                    })
                  : createElement(EmptyState, {
                      title: "No active subtask",
                      body: "This node is not currently executing a compiled subtask.",
                    }),
              ),
          selectedSubtask
            ? createElement(
                DetailCard,
                { key: "selected-subtask", title: "Selected Subtask", testId: "workflow-selected-subtask-card" },
                [
                  createElement(KeyValueList, {
                    key: "list",
                    rows: [
                      { label: "Subtask id", value: selectedSubtask.id },
                      { label: "Task", value: selectedSubtask.task_title },
                      { label: "Subtask key", value: selectedSubtask.source_subtask_key },
                      { label: "Type", value: selectedSubtask.subtask_type },
                      { label: "Prompt", value: selectedSubtask.prompt_text ?? "none" },
                      { label: "Command", value: selectedSubtask.command_text ?? "none" },
                      { label: "Environment policy", value: selectedSubtask.environment_policy_ref ?? "none" },
                      { label: "Retry policy", value: describeJsonValue(selectedSubtask.retry_policy_json) },
                    ],
                  }),
                  currentPromptQuery.data && selectedSubtask.id === currentPromptQuery.data.compiled_subtask_id
                    ? createElement(
                        "div",
                        { key: "prompt", className: "detail-card__notice", "data-testid": "workflow-current-prompt-card" },
                        [
                          createElement(StatusBadge, { key: "badge", label: "current prompt", tone: "info" }),
                          createElement("p", { key: "text" }, currentPromptQuery.data.prompt_text ?? currentPromptQuery.data.command_text ?? "No prompt text available."),
                        ],
                      )
                    : null,
                  currentContextQuery.data && selectedSubtask.id === currentContextQuery.data.compiled_subtask_id
                    ? createElement(
                        "div",
                        { key: "context", className: "detail-card__notice", "data-testid": "workflow-current-context-card" },
                        [
                          createElement(StatusBadge, { key: "badge", label: "current context", tone: "neutral" }),
                          createElement(
                            "p",
                            { key: "text" },
                            `Latest summary: ${currentContextQuery.data.latest_summary ?? "none"} • attempt ${currentContextQuery.data.attempt_number ?? "n/a"}`,
                          ),
                        ],
                      )
                    : null,
                ],
              )
            : null,
          attemptsQuery.isError && attemptsQuery.error?.status !== 404
            ? createElement(
                DetailCard,
                { key: "attempt-error", title: "Attempt History", testId: "workflow-attempt-history-card" },
                createElement(ErrorState, {
                  title: "Could not load subtask attempts",
                  body: attemptsQuery.error.message,
                }),
              )
            : createElement(
                DetailCard,
                { key: "attempts", title: "Attempt History", testId: "workflow-attempt-history-card" },
                createElement(AttemptHistoryList, {
                  attempts,
                  selectedAttemptId: effectiveSelectedAttemptId,
                  onSelectAttempt: setSelectedAttemptId,
                }),
              ),
          effectiveSelectedAttemptId
            ? createElement(
                DetailCard,
                { key: "attempt-detail", title: "Selected Attempt", testId: "workflow-selected-attempt-card" },
                selectedAttemptQuery.isLoading
                  ? createElement(LoadingState, { label: "Loading selected attempt." })
                  : selectedAttemptQuery.isError
                    ? createElement(ErrorState, {
                        title: "Could not load subtask attempt",
                        body: selectedAttemptQuery.error.message,
                      })
                    : [
                        createElement(KeyValueList, {
                          key: "list",
                          rows: [
                            { label: "Attempt id", value: selectedAttemptQuery.data.id },
                            { label: "Status", value: selectedAttemptQuery.data.status },
                            { label: "Compiled subtask", value: selectedAttemptQuery.data.compiled_subtask_id },
                            { label: "Started", value: selectedAttemptQuery.data.started_at },
                            { label: "Ended", value: selectedAttemptQuery.data.ended_at },
                            { label: "Summary", value: selectedAttemptQuery.data.summary ?? "none" },
                          ],
                        }),
                        createElement(RawJsonToggle, {
                          key: "json",
                          payload: selectedAttemptQuery.data,
                          testId: "workflow-selected-attempt-json",
                        }),
                      ],
              )
            : null,
          createElement(RawJsonToggle, { key: "json", payload: workflow, testId: "workflow-raw-json" }),
        ],
      ),
  });
}

function RunsPanel({ nodeId }) {
  const progressQuery = useQuery({
    queryKey: ["node", nodeId, "run-progress"],
    queryFn: async () => (await getRunProgress(nodeId)).data,
  });
  const runsQuery = useQuery({
    queryKey: queryKeys.nodeRuns(nodeId),
    queryFn: async () => (await getRuns(nodeId)).data,
  });
  if (progressQuery.isLoading || runsQuery.isLoading) {
    return createElement(LoadingState, { label: "Loading runs." });
  }
  if (progressQuery.isError) {
    return createElement(ErrorState, { title: "Could not load run progress", body: progressQuery.error.message });
  }
  if (runsQuery.isError) {
    return createElement(ErrorState, { title: "Could not load run history", body: runsQuery.error.message });
  }
  const progress = progressQuery.data;
  const runs = runsQuery.data;
  return createElement(
    "div",
    { className: "detail-grid", "data-testid": "detail-tab-runs" },
    [
      createElement(
        DetailCard,
        { key: "current", title: "Current Run", testId: "runs-current-card" },
        createElement(KeyValueList, {
          rows: [
            { label: "Run id", value: progress.run?.id ?? progress.node_run_id },
            { label: "Trigger", value: progress.run?.trigger_reason },
            { label: "Current subtask", value: progress.current_subtask?.compiled_subtask_id ?? progress.state?.current_compiled_subtask_id },
            { label: "Attempt", value: String(progress.current_attempt?.attempt_number ?? "") || "n/a" },
          ],
        }),
      ),
      createElement(
        DetailCard,
        { key: "history", title: "Run History", testId: "runs-history-card" },
        runs.runs?.length
          ? createElement(
              "ul",
              { className: "detail-list" },
              runs.runs.map((run) => createElement("li", { key: run.id }, `${run.id} • ${run.status} • ${run.trigger_reason}`)),
            )
          : createElement(EmptyState, { title: "No runs", body: "This node has no recorded runs yet." }),
      ),
      createElement(RawJsonToggle, { key: "json", payload: { progress, runs }, testId: "runs-raw-json" }),
    ],
  );
}

function PromptEditor({ value, disabled, onChange }) {
  return createElement(
    "label",
    { className: "field-group" },
    [
      createElement("span", { key: "label", className: "field-group__label" }, "Prompt"),
      createElement("textarea", {
        key: "input",
        className: "field-group__input field-group__input--textarea prompt-editor__textarea",
        rows: 10,
        value,
        disabled,
        onChange: (event) => onChange(event.target.value),
        "data-testid": "prompt-editor-input",
      }),
    ],
  );
}

function PromptHistoryList({ prompts }) {
  if (!prompts?.length) {
    return createElement(EmptyState, {
      title: "No prompt history",
      body: "No delivered prompts have been recorded for this node yet.",
    });
  }

  return createElement(
    "ul",
    { className: "detail-list detail-list--stacked", "data-testid": "prompt-history-list" },
    prompts.map((prompt) =>
      createElement(
        "li",
        { key: prompt.id, className: "prompt-history-item" },
        [
          createElement(
            "div",
            { key: "meta", className: "prompt-history-item__meta" },
            `${prompt.prompt_role} • ${prompt.source_subtask_key ?? "node"} • ${prompt.delivered_at}`,
          ),
          createElement("pre", { key: "content", className: "prompt-history-item__content" }, prompt.content),
        ],
      ),
    ),
  );
}

function PromptPanel({ projectId, nodeId }) {
  const queryClient = useQueryClient();
  const [draftPrompt, setDraftPrompt] = useState("");
  const [isConfirming, setIsConfirming] = useState(false);
  const [lastMutation, setLastMutation] = useState(null);

  const overviewQuery = useQuery({
    queryKey: queryKeys.nodeOverview(nodeId),
    queryFn: async () => (await getNodeOverview(nodeId)).data,
  });
  const lineageQuery = useQuery({
    queryKey: ["node", nodeId, "lineage"],
    queryFn: async () => (await getNodeLineage(nodeId)).data,
  });
  const latestVersionId = lineageQuery.data?.latest_created_node_version_id ?? null;
  const versionQuery = useQuery({
    queryKey: ["node-version", latestVersionId],
    queryFn: async () => (await getNodeVersion(latestVersionId)).data,
    enabled: Boolean(latestVersionId),
  });
  const promptHistoryQuery = useQuery({
    queryKey: queryKeys.nodePrompts(nodeId),
    queryFn: async () => (await getPromptHistory(nodeId)).data,
  });

  useEffect(() => {
    if (versionQuery.data?.prompt) {
      setDraftPrompt(versionQuery.data.prompt);
      setIsConfirming(false);
    }
  }, [versionQuery.data?.id, versionQuery.data?.prompt]);

  const mutation = useMutation({
    mutationFn: async ({ title, prompt }) => {
      const supersedeResponse = await supersedeNode(nodeId, { title, prompt });
      const regenerateResponse = await regenerateNode(nodeId);
      return {
        supersede: supersedeResponse.data,
        regenerate: regenerateResponse.data,
      };
    },
    onSuccess: async (payload) => {
      setLastMutation(payload);
      setIsConfirming(false);
      await queryClient.invalidateQueries({
        predicate: (query) => {
          const [family, id] = query.queryKey;
          return (family === "node" && id === nodeId) || (family === "project" && id === projectId);
        },
      });
    },
  });

  if (overviewQuery.isLoading || lineageQuery.isLoading || versionQuery.isLoading || promptHistoryQuery.isLoading) {
    return createElement(LoadingState, { label: "Loading prompts." });
  }
  if (overviewQuery.isError) {
    return createElement(ErrorState, { title: "Could not load node summary", body: overviewQuery.error.message });
  }
  if (lineageQuery.isError) {
    return createElement(ErrorState, { title: "Could not load lineage", body: lineageQuery.error.message });
  }
  if (versionQuery.isError) {
    return createElement(ErrorState, { title: "Could not load node version", body: versionQuery.error.message });
  }
  if (promptHistoryQuery.isError) {
    return createElement(ErrorState, { title: "Could not load prompt history", body: promptHistoryQuery.error.message });
  }

  const overview = overviewQuery.data;
  const lineage = lineageQuery.data;
  const version = versionQuery.data;
  const promptHistory = promptHistoryQuery.data;
  const hasLiveCandidate =
    Boolean(lineage.authoritative_node_version_id) &&
    Boolean(lineage.latest_created_node_version_id) &&
    lineage.authoritative_node_version_id !== lineage.latest_created_node_version_id;
  const normalizedPrompt = draftPrompt.trim();
  const baselinePrompt = version.prompt ?? "";
  const isDirty = draftPrompt !== baselinePrompt;
  const canRequestConfirmation = Boolean(normalizedPrompt) && isDirty && !hasLiveCandidate && !mutation.isPending;

  function requestConfirmation() {
    if (!canRequestConfirmation) {
      return;
    }
    setIsConfirming(true);
  }

  function keepEditing() {
    setIsConfirming(false);
  }

  function discardChanges() {
    setDraftPrompt(baselinePrompt);
    setIsConfirming(false);
    mutation.reset();
  }

  async function saveAndRegenerate() {
    await mutation.mutateAsync({
      title: version.title,
      prompt: normalizedPrompt,
      cancel_active_subtree: true,
    });
  }

  return createElement(
    "div",
    { className: "detail-grid", "data-testid": "detail-tab-prompts" },
    [
      createElement(
        DetailCard,
        { key: "metadata", title: "Prompt Version", testId: "prompts-version-card" },
        [
          createElement(KeyValueList, {
            key: "list",
            rows: [
              { label: "Node title", value: version.title },
              { label: "Editable version", value: version.id },
              { label: "Version number", value: String(version.version_number) },
              { label: "Version status", value: version.status },
              { label: "Authoritative version", value: lineage.authoritative_node_version_id },
              { label: "Latest created version", value: lineage.latest_created_node_version_id },
              { label: "Current run status", value: overview.run_status },
            ],
          }),
          hasLiveCandidate
            ? createElement(
                "div",
                { key: "blocked", className: "detail-card__notice", "data-testid": "prompt-live-candidate-notice" },
                [
                  createElement(StatusBadge, { key: "badge", label: "live candidate", tone: "warning" }),
                  createElement(
                    "p",
                    { key: "text" },
                    "Prompt supersede is blocked because this node already has a live candidate version. Resolve or cut over that candidate before creating another prompt revision.",
                  ),
                ],
              )
            : null,
        ],
      ),
      createElement(
        DetailCard,
        { key: "editor", title: "Prompt Editor", testId: "prompts-editor-card" },
        [
          createElement("p", { key: "lede", className: "detail-card__lede" }, "Edit the node prompt, then confirm save and regenerate inline."),
          createElement(PromptEditor, {
            key: "editor",
            value: draftPrompt,
            disabled: mutation.isPending || hasLiveCandidate,
            onChange: (nextValue) => {
              setDraftPrompt(nextValue);
              setLastMutation(null);
              if (isConfirming) {
                setIsConfirming(false);
              }
            },
          }),
          mutation.isError
            ? createElement(ErrorState, {
                key: "error",
                title: "Could not save and regenerate",
                body: mutation.error.message,
              })
            : null,
          lastMutation
            ? createElement(
                "div",
                { key: "success", className: "detail-card__notice", "data-testid": "prompt-regeneration-success" },
                [
                  createElement(StatusBadge, { key: "badge", label: "regeneration started", tone: "success" }),
                  createElement(
                    "p",
                    { key: "text" },
                    `Created candidate version ${lastMutation.supersede.id} and triggered regeneration rooted at ${lastMutation.regenerate.root_node_version_id}.`,
                  ),
                ],
              )
            : null,
          isConfirming
            ? createElement(
                "div",
                { key: "confirm", className: "confirmation-strip", "data-testid": "prompt-regenerate-confirmation" },
                [
                  createElement(
                    "p",
                    { key: "text", className: "confirmation-strip__text" },
                    "Save prompt changes and regenerate this node into a new version now?",
                  ),
                  createElement(
                    "div",
                    { key: "actions", className: "confirmation-strip__actions" },
                    [
                      createElement(
                        "button",
                        {
                          key: "confirm",
                          type: "button",
                          className: "button button--primary",
                          onClick: saveAndRegenerate,
                          disabled: mutation.isPending,
                          "data-testid": "confirm-save-and-regenerate",
                        },
                        mutation.isPending ? "saving..." : "save and regenerate",
                      ),
                      createElement(
                        "button",
                        {
                          key: "discard",
                          type: "button",
                          className: "button button--secondary",
                          onClick: discardChanges,
                          disabled: mutation.isPending,
                          "data-testid": "discard-prompt-changes",
                        },
                        "discard changes",
                      ),
                      createElement(
                        "button",
                        {
                          key: "edit",
                          type: "button",
                          className: "button button--secondary",
                          onClick: keepEditing,
                          disabled: mutation.isPending,
                          "data-testid": "keep-editing-prompt",
                        },
                        "keep editing",
                      ),
                    ],
                  ),
                ],
              )
            : createElement(
                "div",
                { key: "footer", className: "form-card__footer" },
                createElement(
                  "button",
                  {
                    type: "button",
                    className: "button button--primary",
                    onClick: requestConfirmation,
                    disabled: !canRequestConfirmation,
                    "data-testid": "request-save-and-regenerate",
                  },
                  "save and regenerate",
                ),
              ),
        ],
      ),
      createElement(
        DetailCard,
        { key: "history", title: "Delivered Prompt History", testId: "prompts-history-card" },
        createElement(PromptHistoryList, { prompts: promptHistory.prompts }),
      ),
      createElement(
        RawJsonToggle,
        {
          key: "json",
          payload: {
            overview,
            lineage,
            version,
            promptHistory,
            lastMutation,
          },
          testId: "prompts-raw-json",
        },
      ),
    ],
  );
}

function ActionPanel({ projectId, nodeId }) {
  const queryClient = useQueryClient();
  const [confirmingActionId, setConfirmingActionId] = useState(null);
  const [lastActionId, setLastActionId] = useState(null);

  const actionQuery = useQuery({
    queryKey: queryKeys.nodeActions(nodeId),
    queryFn: async () => (await getNodeActions(nodeId)).data,
    refetchInterval: 5_000,
  });

  const mutation = useMutation({
    mutationFn: async (action) => {
      if (action.action_id === "start_run") {
        return startNodeRun(nodeId);
      }
      if (action.action_id === "pause_run") {
        return pauseNodeRun(nodeId);
      }
      if (action.action_id === "resume_run") {
        return resumeNodeRun(nodeId);
      }
      if (action.action_id === "session_attach") {
        return attachNodeSession(nodeId);
      }
      if (action.action_id === "session_resume") {
        return resumeNodeSession(nodeId);
      }
      if (action.action_id === "session_provider_resume") {
        return providerResumeNodeSession(nodeId);
      }
      if (action.action_id === "regenerate_node") {
        return regenerateNode(nodeId);
      }
      if (action.action_id.startsWith("reconcile_children:")) {
        return reconcileNodeChildren(nodeId, action.action_id.split(":")[1]);
      }
      throw new Error(`Unsupported action '${action.action_id}'.`);
    },
    onSuccess: async (_response, action) => {
      setLastActionId(action.action_id);
      setConfirmingActionId(null);
      await queryClient.invalidateQueries({
        predicate: (query) => {
          const [family, id] = query.queryKey;
          return (family === "node" && id === nodeId) || (family === "project" && id === projectId);
        },
      });
    },
  });

  return createElement(QueryPanel, {
    query: actionQuery,
    loadingLabel: "Loading actions.",
    errorTitle: "Could not load actions",
    emptyTitle: "No actions",
    emptyBody: "This node does not currently expose any browser actions.",
    render: (payload) =>
      createElement(
        "div",
        { className: "detail-grid", "data-testid": "detail-tab-actions" },
        [
          ...(payload.actions?.length
            ? payload.actions.map((action) =>
                createElement(
                  DetailCard,
                  {
                    key: action.action_id,
                    title: action.label,
                    testId: `action-card-${action.action_id.replace(/[:_]/g, "-")}`,
                    actions: createElement(StatusBadge, {
                      label: action.legal ? "available" : "blocked",
                      tone: action.legal ? "success" : "warning",
                    }),
                  },
                  [
                    createElement(KeyValueList, {
                      key: "meta",
                      rows: [
                        { label: "Action id", value: action.action_id },
                        { label: "Group", value: action.group },
                        { label: "Target scope", value: action.target_scope },
                        { label: "Blocked reason", value: action.blocked_reason ?? "none" },
                      ],
                    }),
                    lastActionId === action.action_id
                      ? createElement(
                          "div",
                          { key: "success", className: "detail-card__notice", "data-testid": `action-success-${action.action_id.replace(/[:_]/g, "-")}` },
                          [
                            createElement(StatusBadge, { key: "badge", label: "action applied", tone: "success" }),
                            createElement("p", { key: "text" }, `${action.label} completed through the daemon action surface.`),
                          ],
                        )
                      : null,
                    mutation.isError && confirmingActionId === action.action_id
                      ? createElement(ErrorState, {
                          key: "error",
                          title: "Action failed",
                          body: mutation.error.message,
                        })
                      : null,
                    confirmingActionId === action.action_id
                      ? createElement(
                          "div",
                          { key: "confirm", className: "confirmation-strip", "data-testid": `action-confirm-${action.action_id.replace(/[:_]/g, "-")}` },
                          [
                            createElement(
                              "p",
                              { key: "text", className: "confirmation-strip__text" },
                              `Run '${action.label}' now?`,
                            ),
                            createElement(
                              "div",
                              { key: "actions", className: "confirmation-strip__actions" },
                              [
                                createElement(
                                  "button",
                                  {
                                    key: "confirm",
                                    type: "button",
                                    className: "button button--primary",
                                    onClick: () => mutation.mutate(action),
                                    disabled: mutation.isPending,
                                    "data-testid": `action-confirm-button-${action.action_id.replace(/[:_]/g, "-")}`,
                                  },
                                  mutation.isPending ? "running..." : action.confirmation_label,
                                ),
                                createElement(
                                  "button",
                                  {
                                    key: "cancel",
                                    type: "button",
                                    className: "button button--secondary",
                                    onClick: () => setConfirmingActionId(null),
                                    disabled: mutation.isPending,
                                  },
                                  "keep editing",
                                ),
                              ],
                            ),
                          ],
                        )
                      : createElement(
                          "div",
                          { key: "footer", className: "form-card__footer" },
                          createElement(
                            "button",
                            {
                              type: "button",
                              className: "button button--primary",
                              disabled: !action.legal || mutation.isPending,
                              onClick: () => setConfirmingActionId(action.action_id),
                              "data-testid": `action-trigger-${action.action_id.replace(/[:_]/g, "-")}`,
                            },
                            action.label,
                          ),
                        ),
                  ],
                ),
              )
            : [
                createElement(EmptyState, {
                  key: "empty",
                  title: "No actions",
                  body: "This node does not currently expose any browser actions.",
                }),
              ]),
          createElement(RawJsonToggle, { key: "json", payload, testId: "actions-raw-json" }),
        ],
      ),
  });
}

function SummariesPanel({ nodeId }) {
  const summariesQuery = useQuery({
    queryKey: queryKeys.nodeSummaries(nodeId),
    queryFn: async () => (await getSummaryHistory(nodeId)).data,
  });
  return createElement(QueryPanel, {
    query: summariesQuery,
    loadingLabel: "Loading summaries.",
    errorTitle: "Could not load summaries",
    emptyTitle: "No summaries",
    emptyBody: "This node has no recorded summaries yet.",
    render: (payload) =>
      createElement(
        "div",
        { className: "detail-grid", "data-testid": "detail-tab-summaries" },
        [
          createElement(
            DetailCard,
            { key: "list", title: "Summary History", testId: "summaries-list-card" },
            payload.summaries?.length
              ? createElement(
                  "ul",
                  { className: "detail-list" },
                  payload.summaries.map((summary) =>
                    createElement("li", { key: summary.id }, `${summary.summary_type} • ${summary.summary_scope} • ${summary.created_at}`),
                  ),
                )
              : createElement(EmptyState, { title: "No summaries", body: "This node has no recorded summaries yet." }),
          ),
          createElement(RawJsonToggle, { key: "json", payload, testId: "summaries-raw-json" }),
        ],
      ),
  });
}

function SessionsPanel({ nodeId }) {
  const sessionsQuery = useQuery({
    queryKey: queryKeys.nodeSessions(nodeId),
    queryFn: async () => (await getSessions(nodeId)).data,
    refetchInterval: 5_000,
  });
  return createElement(QueryPanel, {
    query: sessionsQuery,
    loadingLabel: "Loading sessions.",
    errorTitle: "Could not load sessions",
    emptyTitle: "No sessions",
    emptyBody: "This node has no active or recorded sessions.",
    render: (payload) =>
      createElement(
        "div",
        { className: "detail-grid", "data-testid": "detail-tab-sessions" },
        [
          createElement(
            DetailCard,
            { key: "list", title: "Sessions", testId: "sessions-list-card" },
            payload.sessions?.length
              ? createElement(
                  "ul",
                  { className: "detail-list" },
                  payload.sessions.map((session) =>
                    createElement(
                      "li",
                      { key: session.session_id ?? session.session_name ?? session.status },
                      `${session.status} • ${session.provider ?? session.backend} • ${session.session_role ?? "primary"}`,
                    ),
                  ),
                )
              : createElement(EmptyState, { title: "No sessions", body: "This node has no active or recorded sessions." }),
          ),
          createElement(RawJsonToggle, { key: "json", payload, testId: "sessions-raw-json" }),
        ],
      ),
  });
}

function ProvenancePanel({ nodeId }) {
  const sourcesQuery = useQuery({
    queryKey: ["node", nodeId, "sources"],
    queryFn: async () => (await getNodeSources(nodeId)).data,
  });
  const rationaleQuery = useQuery({
    queryKey: queryKeys.nodeProvenance(nodeId),
    queryFn: async () => (await getNodeRationale(nodeId)).data,
  });
  if (sourcesQuery.isLoading || rationaleQuery.isLoading) {
    return createElement(LoadingState, { label: "Loading provenance." });
  }
  if (sourcesQuery.isError) {
    return createElement(ErrorState, { title: "Could not load source lineage", body: sourcesQuery.error.message });
  }
  if (rationaleQuery.isError) {
    return createElement(ErrorState, { title: "Could not load rationale", body: rationaleQuery.error.message });
  }
  const sources = sourcesQuery.data;
  const rationale = rationaleQuery.data;
  return createElement(
    "div",
    { className: "detail-grid", "data-testid": "detail-tab-provenance" },
    [
      createElement(
        DetailCard,
        { key: "rationale", title: "Rationale", testId: "provenance-rationale-card" },
        [
          createElement("p", { key: "summary", className: "detail-card__lede" }, rationale.rationale_summary),
          createElement(KeyValueList, {
            key: "counts",
            rows: Object.entries(rationale.change_counts ?? {}).map(([label, value]) => ({
              label,
              value: String(value),
            })),
          }),
        ],
      ),
      createElement(
        DetailCard,
        { key: "sources", title: "Source Lineage", testId: "provenance-sources-card" },
        sources.source_documents?.length
          ? createElement(
              "ul",
              { className: "detail-list" },
              sources.source_documents.map((source) =>
                createElement("li", { key: source.id }, `${source.relative_path} • ${source.source_role}`),
              ),
            )
          : createElement(EmptyState, { title: "No source lineage", body: "No source documents were captured." }),
      ),
      createElement(RawJsonToggle, { key: "json", payload: { sources, rationale }, testId: "provenance-raw-json" }),
    ],
  );
}

function PanelForTab({ projectId, tab, nodeId }) {
  switch (tab) {
    case "overview":
      return createElement(OverviewPanel, { nodeId });
    case "workflow":
      return createElement(WorkflowPanel, { nodeId });
    case "runs":
      return createElement(RunsPanel, { nodeId });
    case "prompts":
      return createElement(PromptPanel, { projectId, nodeId });
    case "actions":
      return createElement(ActionPanel, { projectId, nodeId });
    case "summaries":
      return createElement(SummariesPanel, { nodeId });
    case "sessions":
      return createElement(SessionsPanel, { nodeId });
    case "provenance":
      return createElement(ProvenancePanel, { nodeId });
    default:
      return createElement(ErrorState, {
        title: "Unknown tab",
        body: `The tab '${tab}' is not available in this phase.`,
      });
  }
}

export function normalizeDetailTab(tab) {
  return TABS.some((item) => item.id === tab) ? tab : "overview";
}

export default function NodeDetailTabs({ projectId, nodeId, activeTab }) {
  return createElement(
    "div",
    { className: "node-detail-layout", "data-testid": "node-detail-layout" },
    [
      createElement(
        "nav",
        { key: "tabs", className: "detail-tabs", "data-testid": "detail-tabs" },
        TABS.map((tab) =>
          createElement(
            Link,
            {
              key: tab.id,
              to: `/projects/${projectId}/nodes/${nodeId}/${tab.id}`,
              className: `detail-tabs__link ${activeTab === tab.id ? "detail-tabs__link--active" : ""}`,
              "data-testid": `detail-tab-link-${tab.id}`,
            },
            tab.label,
          ),
        ),
      ),
      createElement(
        "div",
        { key: "panel", className: "detail-tabs__panel" },
        createElement(PanelForTab, { projectId, tab: activeTab, nodeId }),
      ),
    ],
  );
}
