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
  project: {
    project_id: "repo_alpha",
    label: "repo_alpha",
    source_path: "repos/repo_alpha",
  },
  root_node_id: "node-root",
  top_level_nodes: [
    {
      node_id: "node-root",
      kind: "epic",
      tier: "epic",
      title: "Website UI bootstrap",
      lifecycle_state: "READY",
      run_status: "RUNNING",
      authoritative_node_version_id: "node-version-root",
      latest_created_node_version_id: "node-version-root",
      route_hint: {
        project_id: "repo_alpha",
        node_id: "node-root",
        tab: "overview",
        url: "/projects/repo_alpha/nodes/node-root/overview",
      },
    },
  ],
  route_hint: {
    project_id: "repo_alpha",
    node_id: "node-root",
    tab: "overview",
    url: "/projects/repo_alpha/nodes/node-root/overview",
  },
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
      has_children: true,
      child_count: 1,
      child_rollups: {
        total: 1,
        ready: 0,
        running: 0,
        paused_for_user: 0,
        blocked: 0,
        failed: 0,
        complete: 1,
        superseded: 0,
        not_compiled: 0,
      },
      created_at: "2026-03-11T00:00:00Z",
      last_updated_at: "2026-03-11T00:00:00Z",
    },
    {
      node_id: "node-phase-1",
      parent_node_id: "node-root",
      depth: 1,
      kind: "phase",
      tier: "phase",
      title: "Phase blocked by children",
      authoritative_node_version_id: "node-version-phase-1",
      latest_created_node_version_id: "node-version-phase-1",
      lifecycle_state: "READY",
      run_status: null,
      scheduling_status: "blocked",
      blocker_count: 1,
      blocker_state: "blocked",
      has_children: true,
      child_count: 1,
      child_rollups: {
        total: 1,
        ready: 0,
        running: 0,
        paused_for_user: 0,
        blocked: 1,
        failed: 0,
        complete: 0,
        superseded: 0,
        not_compiled: 0,
      },
      created_at: "2026-03-11T00:00:00Z",
      last_updated_at: "2026-03-11T00:00:00Z",
    },
  ],
});
queryClient.setQueryData(queryKeys.nodeAncestors("node-root"), []);

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
          createElement(Route, {
            path: "projects/:projectId/nodes/:nodeId/:tab",
            element: createElement(NodeTabPage),
          }),
        ),
      ),
    ),
  ),
);

if (!html.includes('data-testid="tree-sidebar"')) {
  throw new Error("Expected the hierarchy tree sidebar to render.");
}

if (!html.includes('data-testid="tree-node-node-root"')) {
  throw new Error("Expected the selected tree node to render.");
}

if (!html.includes('data-testid="tree-filter-input"')) {
  throw new Error("Expected the tree filter input to render.");
}

if (!html.includes('data-testid="tree-filter-lifecycle"')) {
  throw new Error("Expected the lifecycle tree filter to render.");
}

if (!html.includes('data-testid="tree-filter-kind"')) {
  throw new Error("Expected the kind tree filter to render.");
}

if (!html.includes('data-testid="tree-filter-blocked-only"')) {
  throw new Error("Expected the blocked-only tree filter to render.");
}

if (!html.includes('data-testid="tree-filter-active-only"')) {
  throw new Error("Expected the active-only tree filter to render.");
}

if (!html.includes('data-testid="tree-breadcrumb"')) {
  throw new Error("Expected the tree breadcrumb to render.");
}

if (!html.includes('data-testid="tree-toggle-node-root"')) {
  throw new Error("Expected the tree expand/collapse toggle to render.");
}

console.log("explorer-tree-check: ok");
