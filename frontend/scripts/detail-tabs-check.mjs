import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import AppShell from "../src/components/shell/AppShell.js";
import { NodeTabPage } from "../src/routes/pages.js";
import { queryKeys } from "../src/lib/query/keys.js";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      staleTime: Infinity,
    },
  },
});

queryClient.setQueryData(queryKeys.projectBootstrap("repo_alpha"), {
  project: { project_id: "repo_alpha", label: "repo_alpha", source_path: "repos/repo_alpha" },
  root_node_id: "node-root",
  top_level_nodes: [],
  route_hint: { project_id: "repo_alpha", node_id: "node-root", tab: "overview", url: "/projects/repo_alpha/nodes/node-root/overview" },
});
queryClient.setQueryData(queryKeys.projectTree("repo_alpha", "node-root"), {
  root_node_id: "node-root",
  generated_at: "2026-03-11T00:00:00Z",
  nodes: [
    {
      node_id: "node-root",
      parent_node_id: null,
      depth: 0,
      kind: "epic",
      tier: "epic",
      title: "Website UI bootstrap",
      authoritative_node_version_id: "node-version-root",
      latest_created_node_version_id: "node-version-root",
      lifecycle_state: "READY",
      run_status: "RUNNING",
      scheduling_status: "already_running",
      blocker_count: 0,
      blocker_state: "none",
      has_children: false,
      child_count: 0,
      child_rollups: { total: 0, ready: 0, running: 0, paused_for_user: 0, blocked: 0, failed: 0, complete: 0, superseded: 0, not_compiled: 0 },
      created_at: "2026-03-11T00:00:00Z",
      last_updated_at: "2026-03-11T00:00:00Z",
    },
  ],
});
queryClient.setQueryData(queryKeys.nodeOverview("node-root"), {
  node_id: "node-root",
  parent_node_id: null,
  kind: "epic",
  tier: "epic",
  title: "Website UI bootstrap",
  prompt: "Create the initial website UI workflow.",
  created_via: "manual",
  lifecycle_state: "READY",
  run_status: "RUNNING",
  current_run_id: "run-root",
  current_subtask_id: "subtask-root",
  current_subtask_attempt: 1,
  pause_flag_name: null,
  is_resumable: false,
  authoritative_node_version_id: "node-version-root",
  latest_created_node_version_id: "node-version-root",
  compiled_workflow_id: "workflow-root",
  active_branch_name: "node-root-v1",
  seed_commit_sha: "abc123",
  final_commit_sha: null,
});
queryClient.setQueryData(["node", "node-root", "lineage"], {
  logical_node_id: "node-root",
  authoritative_node_version_id: "node-version-root",
  latest_created_node_version_id: "node-version-root",
  versions: [{ id: "node-version-root" }],
});
queryClient.setQueryData(queryKeys.nodeWorkflow("node-root"), {
  id: "workflow-root",
  node_version_id: "node-version-root",
  logical_node_id: "node-root",
  source_hash: "hash-root",
  built_in_library_version: "test",
  created_at: "2026-03-11T00:00:00Z",
  source_document_count: 4,
  task_count: 2,
  subtask_count: 3,
  compile_context: {},
  resolved_yaml: {},
  tasks: [
    {
      id: "task-a",
      task_key: "research_context",
      ordinal: 1,
      title: "Research",
      description: null,
      config_json: {},
      subtasks: [
        {
          id: "subtask-a1",
          compiled_task_id: "task-a",
          source_subtask_key: "research_context.collect",
          ordinal: 1,
          subtask_type: "research",
          title: "Collect context",
          prompt_text: "Review current structure.",
          command_text: null,
          environment_policy_ref: null,
          environment_request_json: null,
          retry_policy_json: null,
          block_on_user_flag: null,
          pause_summary_prompt: null,
          source_file_path: null,
          source_hash: "hash-a1",
          inserted_by_hook: false,
          inserted_by_hook_id: null,
          depends_on_compiled_subtask_ids: [],
        },
      ],
    },
    {
      id: "task-b",
      task_key: "execute_node",
      ordinal: 2,
      title: "Execute",
      description: null,
      config_json: {},
      subtasks: [
        {
          id: "subtask-b1",
          compiled_task_id: "task-b",
          source_subtask_key: "execute_node.run_leaf_prompt",
          ordinal: 1,
          subtask_type: "execute_node",
          title: "Run implementation prompt",
          prompt_text: "Implement the next website shell slice.",
          command_text: "npm run test:unit",
          environment_policy_ref: "environments/local_default.yaml",
          environment_request_json: { policy_id: "local_default" },
          retry_policy_json: { max_attempts: 2 },
          block_on_user_flag: null,
          pause_summary_prompt: null,
          source_file_path: "builtin/subtasks/execute_node.yaml",
          source_hash: "hash-b1",
          inserted_by_hook: false,
          inserted_by_hook_id: null,
          depends_on_compiled_subtask_ids: ["subtask-a1"],
        },
      ],
    },
  ],
});
queryClient.setQueryData(queryKeys.nodeCurrentSubtask("node-root"), {
  run: {
    id: "run-root",
    logical_node_id: "node-root",
    node_version_id: "node-version-root",
    trigger_reason: "workflow_start",
    run_status: "RUNNING",
  },
  state: {
    node_run_id: "run-root",
    lifecycle_state: "RUNNING",
    current_task_id: "task-b",
    current_compiled_subtask_id: "subtask-b1",
    current_subtask_attempt: 2,
    last_completed_compiled_subtask_id: "subtask-a1",
    execution_cursor_json: {},
    failure_count_from_children: 0,
    failure_count_consecutive: 0,
    defer_to_user_threshold: null,
    pause_flag_name: null,
    is_resumable: false,
    working_tree_state: "clean",
    updated_at: "2026-03-11T00:05:00Z",
  },
  current_subtask: {
    id: "subtask-b1",
    compiled_task_id: "task-b",
    source_subtask_key: "execute_node.run_leaf_prompt",
    ordinal: 1,
    subtask_type: "execute_node",
    title: "Run implementation prompt",
    prompt_text: "Implement the next website shell slice.",
    command_text: "npm run test:unit",
    environment_policy_ref: "environments/local_default.yaml",
    environment_request_json: { policy_id: "local_default" },
    retry_policy_json: { max_attempts: 2 },
    block_on_user_flag: null,
    pause_summary_prompt: null,
    source_file_path: "builtin/subtasks/execute_node.yaml",
    source_hash: "hash-b1",
    inserted_by_hook: false,
    inserted_by_hook_id: null,
    depends_on_compiled_subtask_ids: ["subtask-a1"],
  },
  latest_attempt: {
    id: "attempt-root-2",
    node_run_id: "run-root",
    compiled_subtask_id: "subtask-b1",
    attempt_number: 2,
    status: "RUNNING",
    input_context_json: { compiled_subtask_id: "subtask-b1" },
    output_json: { last_heartbeat_at: "2026-03-11T00:05:00Z" },
    execution_result_json: null,
    execution_environment_json: { launch_status: "active" },
    validation_json: null,
    review_json: null,
    testing_json: null,
    summary: null,
    started_at: "2026-03-11T00:04:30Z",
    ended_at: null,
  },
});
queryClient.setQueryData(queryKeys.nodeCurrentSubtaskPrompt("node-root"), {
  node_id: "node-root",
  node_run_id: "run-root",
  compiled_subtask_id: "subtask-b1",
  prompt_id: "prompt-root-1",
  source_subtask_key: "execute_node.run_leaf_prompt",
  title: "Run implementation prompt",
  subtask_type: "execute_node",
  prompt_text: "Implement the next website shell slice.",
  command_text: "npm run test:unit",
  environment_request_json: { policy_id: "local_default" },
  stage_context_json: { startup: { node_id: "node-root" }, stage: { compiled_subtask_id: "subtask-b1" } },
});
queryClient.setQueryData(queryKeys.nodeCurrentSubtaskContext("node-root"), {
  node_id: "node-root",
  node_run_id: "run-root",
  compiled_subtask_id: "subtask-b1",
  attempt_number: 2,
  input_context_json: { compiled_subtask_id: "subtask-b1" },
  latest_summary: "Reviewed the current website shell structure.",
  stage_context_json: { startup: { node_id: "node-root" }, stage: { compiled_subtask_id: "subtask-b1" } },
});
queryClient.setQueryData(queryKeys.nodeSubtaskAttempts("node-root"), {
  node_id: "node-root",
  node_run_id: "run-root",
  attempts: [
    {
      id: "attempt-root-2",
      node_run_id: "run-root",
      compiled_subtask_id: "subtask-b1",
      attempt_number: 2,
      status: "RUNNING",
      input_context_json: { compiled_subtask_id: "subtask-b1" },
      output_json: { last_heartbeat_at: "2026-03-11T00:05:00Z" },
      execution_result_json: null,
      execution_environment_json: { launch_status: "active" },
      validation_json: null,
      review_json: null,
      testing_json: null,
      summary: null,
      started_at: "2026-03-11T00:04:30Z",
      ended_at: null,
    },
  ],
});
queryClient.setQueryData(queryKeys.subtaskAttempt("attempt-root-2"), {
  id: "attempt-root-2",
  node_run_id: "run-root",
  compiled_subtask_id: "subtask-b1",
  attempt_number: 2,
  status: "RUNNING",
  input_context_json: { compiled_subtask_id: "subtask-b1" },
  output_json: { last_heartbeat_at: "2026-03-11T00:05:00Z" },
  execution_result_json: null,
  execution_environment_json: { launch_status: "active" },
  validation_json: null,
  review_json: null,
  testing_json: null,
  summary: null,
  started_at: "2026-03-11T00:04:30Z",
  ended_at: null,
});
queryClient.setQueryData(queryKeys.nodeAncestors("node-root"), []);

const overviewHtml = renderToStaticMarkup(
  createElement(
    QueryClientProvider,
    { client: queryClient },
    createElement(
      MemoryRouter,
      { initialEntries: ["/projects/repo_alpha/nodes/node-root/overview"] },
      createElement(
        Routes,
        null,
        createElement(
          Route,
          { path: "/", element: createElement(AppShell) },
          createElement(Route, { path: "projects/:projectId/nodes/:nodeId/:tab", element: createElement(NodeTabPage) }),
        ),
      ),
    ),
  ),
);

if (!overviewHtml.includes('data-testid="detail-tabs"')) {
  throw new Error("Expected the detail tab nav to render.");
}

if (!overviewHtml.includes('data-testid="detail-tab-overview"')) {
  throw new Error("Expected the overview tab content to render.");
}

if (!overviewHtml.includes('data-testid="overview-summary-card"')) {
  throw new Error("Expected the overview summary card to render.");
}

const workflowHtml = renderToStaticMarkup(
  createElement(
    QueryClientProvider,
    { client: queryClient },
    createElement(
      MemoryRouter,
      { initialEntries: ["/projects/repo_alpha/nodes/node-root/workflow"] },
      createElement(
        Routes,
        null,
        createElement(
          Route,
          { path: "/", element: createElement(AppShell) },
          createElement(Route, { path: "projects/:projectId/nodes/:nodeId/:tab", element: createElement(NodeTabPage) }),
        ),
      ),
    ),
  ),
);

if (!workflowHtml.includes('data-testid="detail-tab-workflow"')) {
  throw new Error("Expected the workflow tab content to render.");
}

if (!workflowHtml.includes('data-testid="workflow-current-subtask-card"')) {
  throw new Error("Expected the workflow current-subtask card to render.");
}

if (!workflowHtml.includes('data-testid="workflow-selected-subtask-card"')) {
  throw new Error("Expected the workflow selected-subtask card to render.");
}

console.log("detail-tabs-check: ok");
