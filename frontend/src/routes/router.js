import { createBrowserRouter, createMemoryRouter, createRoutesFromElements, Route } from "react-router-dom";
import { createElement } from "react";
import AppShell from "../components/shell/AppShell.js";
import {
  NodePage,
  NodeTabPage,
  PrimitiveGalleryPage,
  ProjectPage,
  ProjectsIndexPage,
} from "./pages.js";

function buildRouteElements() {
  return createRoutesFromElements(
    createElement(
      Route,
      { path: "/", element: createElement(AppShell) },
      createElement(Route, { index: true, element: createElement(ProjectsIndexPage) }),
      createElement(Route, { path: "projects", element: createElement(ProjectsIndexPage) }),
      createElement(Route, { path: "projects/:projectId", element: createElement(ProjectPage) }),
      createElement(Route, { path: "projects/:projectId/nodes/:nodeId", element: createElement(NodePage) }),
      createElement(Route, {
        path: "projects/:projectId/nodes/:nodeId/:tab",
        element: createElement(NodeTabPage),
      }),
      createElement(Route, { path: "debug/primitives", element: createElement(PrimitiveGalleryPage) }),
    ),
  );
}

export function buildRouter(initialEntries = ["/projects"]) {
  return createMemoryRouter(buildRouteElements(), { initialEntries });
}

export function buildBrowserRouter() {
  return createBrowserRouter(buildRouteElements());
}
