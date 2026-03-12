import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import AppShell from "../src/components/shell/AppShell.js";
import { ProjectPage } from "../src/routes/pages.js";
import { queryKeys } from "../src/lib/query/keys.js";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      staleTime: Infinity,
    },
  },
});

queryClient.setQueryData(queryKeys.projects(), {
  daemon_context: {
    reachability_state: "reachable",
    auth_status: "valid",
    daemon_app_name: "AI Coding Daemon",
    daemon_version: "0.1.0",
    authority: "daemon",
    session_backend: "fake",
  },
  projects: [
    {
      project_id: "repo_alpha",
      label: "repo_alpha",
      source_path: "repos/repo_alpha",
      bootstrap_ready: true,
      readiness_code: "ready",
      readiness_message: null,
      default_branch: "main",
      head_commit_sha: "abc1234def56",
    },
  ],
});
queryClient.setQueryData(queryKeys.projectBootstrap("repo_alpha"), {
  project: {
    project_id: "repo_alpha",
    label: "repo_alpha",
    source_path: "repos/repo_alpha",
  },
  root_node_id: null,
  route_hint: null,
  top_level_nodes: [],
});
queryClient.setQueryData(queryKeys.nodeKinds(), {
  definitions: [
    {
      kind: "epic",
      tier: "epic",
      description: "Epic node",
      allow_parentless: true,
      allowed_parent_kinds: [],
      allowed_child_kinds: ["phase"],
    },
    {
      kind: "task",
      tier: "task",
      description: "Task node",
      allow_parentless: true,
      allowed_parent_kinds: [],
      allowed_child_kinds: [],
    },
  ],
  top_level_kinds: ["epic", "task"],
});

const html = renderToStaticMarkup(
  createElement(
    QueryClientProvider,
    { client: queryClient },
    createElement(
      MemoryRouter,
      { initialEntries: ["/projects/repo_alpha"] },
      createElement(
        Routes,
        null,
        createElement(
          Route,
          { path: "/", element: createElement(AppShell) },
          createElement(Route, { path: "projects/:projectId", element: createElement(ProjectPage) }),
        ),
      ),
    ),
  ),
);

if (!html.includes('data-testid="top-level-create-form"')) {
  throw new Error("Expected the top-level creation form to render.");
}

if (!html.includes('data-testid="top-level-kind-select"')) {
  throw new Error("Expected the top-level kind selector to render.");
}

if (!html.includes('data-testid="top-level-title-input"')) {
  throw new Error("Expected the top-level title field to render.");
}

if (!html.includes('data-testid="top-level-prompt-input"')) {
  throw new Error("Expected the top-level prompt field to render.");
}

if (!html.includes('data-testid="project-daemon-context"')) {
  throw new Error("Expected the daemon context card to render on the project page.");
}

if (!html.includes('data-testid="project-top-level-nodes-panel"')) {
  throw new Error("Expected the existing top-level nodes panel to render on the project page.");
}

console.log("project-bootstrap-check: ok");
