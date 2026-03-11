import { createElement } from "react";
import { Link, Outlet, useLocation, useParams } from "react-router-dom";
import HierarchyTree from "./HierarchyTree.js";
import StatusBadge from "../primitives/StatusBadge.js";

function renderSelectionSummary(params) {
  if (params.nodeId) {
    return `Selected node: ${params.nodeId}`;
  }
  if (params.projectId) {
    return `Project: ${params.projectId}`;
  }
  return "No project selected";
}

export default function AppShell() {
  const location = useLocation();
  const params = useParams();

  return createElement(
    "div",
    { className: "app-frame", "data-testid": "app-shell" },
    createElement(
      "header",
      { className: "app-frame__topbar", "data-testid": "top-bar" },
      createElement(
        "div",
        { className: "app-frame__topbar-main" },
        createElement("p", { className: "app-frame__eyebrow" }, "Operator Website"),
        createElement("h1", { className: "app-frame__title" }, "AI Coding UI Shell"),
      ),
      createElement(
        "div",
        { className: "app-frame__topbar-status" },
        createElement(StatusBadge, { label: "bootstrap", tone: "info" }),
        createElement("span", { className: "app-frame__summary", "data-testid": "selection-summary" }, renderSelectionSummary(params)),
      ),
    ),
    createElement(
      "div",
      { className: "app-frame__body" },
      createElement(
        "aside",
        { className: "app-frame__sidebar", "data-testid": "shell-sidebar" },
        createElement(
          "nav",
          { className: "app-frame__nav" },
          createElement(Link, { to: "/projects", "data-testid": "nav-projects" }, "Projects"),
          createElement("span", { className: "app-frame__nav-path", "data-testid": "route-path" }, location.pathname),
        ),
        createElement(HierarchyTree),
      ),
      createElement(
        "main",
        { className: "app-frame__content", "data-testid": "shell-content" },
        createElement(Outlet, null),
      ),
    ),
  );
}
