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

const html = renderToStaticMarkup(
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

if (!html.includes('data-testid="detail-tabs"')) {
  throw new Error("Expected the detail tab nav to render.");
}

if (!html.includes('data-testid="detail-tab-overview"')) {
  throw new Error("Expected the overview tab content to render.");
}

if (!html.includes('data-testid="overview-summary-card"')) {
  throw new Error("Expected the overview summary card to render.");
}

console.log("detail-tabs-check: ok");
