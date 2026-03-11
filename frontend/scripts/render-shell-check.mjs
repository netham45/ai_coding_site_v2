import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import AppShell from "../src/components/shell/AppShell.js";
import { ProjectsIndexPage } from "../src/routes/pages.js";
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
  projects: [
    {
      project_id: "repo_alpha",
      label: "repo_alpha",
      source_path: "repos/repo_alpha",
    },
  ],
});

const html = renderToStaticMarkup(
  createElement(QueryClientProvider, { client: queryClient },
    createElement(
      MemoryRouter,
      { initialEntries: ["/projects"] },
      createElement(
        Routes,
        null,
        createElement(
          Route,
          { path: "/", element: createElement(AppShell) },
          createElement(Route, { path: "projects", element: createElement(ProjectsIndexPage) }),
        ),
      ),
    ),
  ),
);

if (!html.includes('data-testid="app-shell"')) {
  throw new Error("Expected the app shell marker to render.");
}

if (!html.includes("AI Coding UI Shell")) {
  throw new Error("Expected the shell heading to render.");
}

if (!html.includes('data-testid="project-catalog"')) {
  throw new Error("Expected the seeded project catalog to render.");
}

console.log("render-shell-check: ok");
