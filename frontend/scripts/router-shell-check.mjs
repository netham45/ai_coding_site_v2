import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import AppShell from "../src/components/shell/AppShell.js";
import { NodeTabPage, PrimitiveGalleryPage, ProjectsIndexPage } from "../src/routes/pages.js";
import { queryKeys } from "../src/lib/query/keys.js";

function renderRoute(initialEntries, childRoute) {
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
  return renderToStaticMarkup(
    createElement(QueryClientProvider, { client: queryClient },
      createElement(
        MemoryRouter,
        { initialEntries },
        createElement(
          Routes,
          null,
          createElement(Route, { path: "/", element: createElement(AppShell) }, childRoute),
        ),
      ),
    ),
  );
}

const projectRouteHtml = renderRoute(
  ["/projects"],
  createElement(Route, { path: "projects", element: createElement(ProjectsIndexPage) }),
);
const nodeRouteHtml = renderRoute(
  ["/projects/repo_alpha/nodes/node-root/overview"],
  createElement(Route, {
    path: "projects/:projectId/nodes/:nodeId/:tab",
    element: createElement(NodeTabPage),
  }),
);
const galleryHtml = renderRoute(
  ["/debug/primitives"],
  createElement(Route, { path: "debug/primitives", element: createElement(PrimitiveGalleryPage) }),
);

if (!projectRouteHtml.includes('data-testid="page-projects-index"')) {
  throw new Error("Expected the projects route scaffold to render.");
}

if (!nodeRouteHtml.includes('data-testid="page-node-tab"')) {
  throw new Error("Expected the node tab route scaffold to render.");
}

if (!galleryHtml.includes('data-testid="loading-state"')) {
  throw new Error("Expected shared loading primitive to render.");
}

if (!galleryHtml.includes('data-testid="empty-state"')) {
  throw new Error("Expected shared empty primitive to render.");
}

if (!galleryHtml.includes('data-testid="error-state"')) {
  throw new Error("Expected shared error primitive to render.");
}

if (!galleryHtml.includes('data-testid="status-badge-waiting-user-input"')) {
  throw new Error("Expected shared status badge primitive to render.");
}

console.log("router-shell-check: ok");
