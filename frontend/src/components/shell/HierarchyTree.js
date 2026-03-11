import { createElement, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import LoadingState from "../primitives/LoadingState.js";
import EmptyState from "../primitives/EmptyState.js";
import ErrorState from "../primitives/ErrorState.js";
import StatusBadge from "../primitives/StatusBadge.js";
import { getProjectBootstrap } from "../../lib/api/projects.js";
import { getTree } from "../../lib/api/tree.js";
import { queryKeys } from "../../lib/query/keys.js";

function toneForNode(node) {
  if (node.lifecycle_state === "COMPLETE") {
    return "success";
  }
  if (node.blocker_state === "blocked" || node.scheduling_status === "failed") {
    return "danger";
  }
  if (node.scheduling_status === "paused_for_user") {
    return "warning";
  }
  if (node.run_status === "RUNNING" || node.scheduling_status === "already_running") {
    return "info";
  }
  return "neutral";
}

function labelForNode(node) {
  if (node.scheduling_status === "paused_for_user") {
    return "waiting user input";
  }
  if (node.scheduling_status === "already_running") {
    return "in progress";
  }
  if (node.scheduling_status === "blocked") {
    return "waiting children";
  }
  if (node.scheduling_status === "failed") {
    return "reconciliation failure";
  }
  if (node.lifecycle_state === "COMPLETE") {
    return "complete";
  }
  return node.scheduling_status ?? node.lifecycle_state?.toLowerCase?.() ?? "ready";
}

function TreeNodeLink({ node, projectId, selectedNodeId, activeTab }) {
  const href = `/projects/${projectId}/nodes/${node.node_id}/${activeTab}`;
  const isSelected = selectedNodeId === node.node_id;
  return createElement(
    Link,
    {
      to: href,
      className: `tree-node ${isSelected ? "tree-node--selected" : ""}`,
      "data-testid": `tree-node-${node.node_id}`,
    },
    [
      createElement(
        "div",
        {
          key: "main",
          className: "tree-node__main",
          style: { paddingLeft: `${node.depth * 16}px` },
        },
        [
          createElement("strong", { key: "title", className: "tree-node__title" }, node.title),
          createElement("span", { key: "meta", className: "tree-node__meta" }, `${node.kind} • ${node.child_count} children`),
        ],
      ),
      createElement(
        "div",
        { key: "right", className: "tree-node__right" },
        [
          createElement(StatusBadge, { key: "status", label: labelForNode(node), tone: toneForNode(node) }),
          createElement(
            "span",
            { key: "rollup", className: "tree-node__rollup" },
            `${node.child_rollups?.running ?? 0}/${node.child_rollups?.total ?? 0} running`,
          ),
        ],
      ),
    ],
  );
}

function matchesLifecycle(node, lifecycleFilter) {
  if (!lifecycleFilter) {
    return true;
  }
  return (node.lifecycle_state ?? "").toUpperCase() === lifecycleFilter;
}

function matchesKind(node, kindFilter) {
  if (!kindFilter) {
    return true;
  }
  return node.kind === kindFilter;
}

function matchesBlocked(node, blockedOnly) {
  if (!blockedOnly) {
    return true;
  }
  return (
    node.blocker_state === "blocked" ||
    node.blocker_state === "paused_for_user" ||
    node.scheduling_status === "blocked" ||
    node.scheduling_status === "paused_for_user"
  );
}

function matchesActive(node, activeOnly) {
  if (!activeOnly) {
    return true;
  }
  return node.run_status === "RUNNING" || node.scheduling_status === "already_running" || node.lifecycle_state === "RUNNING";
}

export default function HierarchyTree() {
  const { projectId, nodeId, tab } = useParams();
  const [filterText, setFilterText] = useState("");
  const [lifecycleFilter, setLifecycleFilter] = useState("");
  const [kindFilter, setKindFilter] = useState("");
  const [blockedOnly, setBlockedOnly] = useState(false);
  const [activeOnly, setActiveOnly] = useState(false);

  const bootstrapQuery = useQuery({
    queryKey: queryKeys.projectBootstrap(projectId),
    queryFn: async () => (await getProjectBootstrap(projectId)).data,
    enabled: Boolean(projectId),
  });

  const rootNodeId = bootstrapQuery.data?.root_node_id ?? null;
  const treeQuery = useQuery({
    queryKey: queryKeys.projectTree(projectId, rootNodeId),
    queryFn: async () => (await getTree(rootNodeId)).data,
    enabled: Boolean(projectId && rootNodeId),
    refetchInterval: 5_000,
  });

  const filteredNodes = useMemo(() => {
    const nodes = treeQuery.data?.nodes ?? [];
    const query = filterText.trim().toLowerCase();
    return nodes.filter((item) => {
      const matchesText =
        !query || item.title.toLowerCase().includes(query) || item.kind.toLowerCase().includes(query);
      return (
        matchesText &&
        matchesLifecycle(item, lifecycleFilter) &&
        matchesKind(item, kindFilter) &&
        matchesBlocked(item, blockedOnly) &&
        matchesActive(item, activeOnly)
      );
    });
  }, [activeOnly, blockedOnly, filterText, kindFilter, lifecycleFilter, treeQuery.data]);

  const availableKinds = useMemo(() => {
    const kinds = new Set((treeQuery.data?.nodes ?? []).map((item) => item.kind));
    return Array.from(kinds).sort();
  }, [treeQuery.data]);

  const availableLifecycleStates = useMemo(() => {
    const values = new Set((treeQuery.data?.nodes ?? []).map((item) => item.lifecycle_state).filter(Boolean));
    return Array.from(values).sort();
  }, [treeQuery.data]);

  if (!projectId) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-empty" },
      createElement(EmptyState, { title: "No project selected", body: "Choose a project to load the hierarchy tree." }),
    );
  }

  if (bootstrapQuery.isLoading) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-loading" },
      createElement(LoadingState, { label: "Loading project bootstrap." }),
    );
  }

  if (bootstrapQuery.isError) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-error" },
      createElement(ErrorState, { title: "Unable to load project tree", body: bootstrapQuery.error.message }),
    );
  }

  if (!rootNodeId) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-no-root" },
      createElement(EmptyState, {
        title: "No root node yet",
        body: "Create a top-level node to start the explorer tree for this project.",
      }),
    );
  }

  if (treeQuery.isLoading) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-loading" },
      createElement(LoadingState, { label: "Loading hierarchy tree." }),
    );
  }

  if (treeQuery.isError) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-error" },
      createElement(ErrorState, { title: "Unable to load hierarchy tree", body: treeQuery.error.message }),
    );
  }

  return createElement(
    "div",
    { className: "sidebar-panel", "data-testid": "tree-sidebar" },
    [
      createElement(
        "div",
        { key: "header", className: "sidebar-panel__header" },
        [
          createElement("h2", { key: "title", className: "sidebar-panel__title" }, "Hierarchy"),
          createElement("span", { key: "root", className: "sidebar-panel__subtle" }, `Root: ${rootNodeId}`),
        ],
      ),
      createElement("input", {
        key: "filter",
        type: "text",
        value: filterText,
        onChange: (event) => setFilterText(event.target.value),
        placeholder: "Filter nodes by title",
        className: "sidebar-filter",
        "data-testid": "tree-filter-input",
      }),
      createElement(
        "div",
        { key: "filters", className: "tree-filter-panel", "data-testid": "tree-filter-panel" },
        [
          createElement(
            "label",
            { key: "lifecycle", className: "tree-filter-field" },
            [
              createElement("span", { key: "label" }, "Lifecycle"),
              createElement(
                "select",
                {
                  key: "input",
                  value: lifecycleFilter,
                  onChange: (event) => setLifecycleFilter(event.target.value),
                  className: "tree-filter-select",
                  "data-testid": "tree-filter-lifecycle",
                },
                [
                  createElement("option", { key: "all", value: "" }, "All lifecycle states"),
                  ...availableLifecycleStates.map((state) =>
                    createElement("option", { key: state, value: state }, state),
                  ),
                ],
              ),
            ],
          ),
          createElement(
            "label",
            { key: "kind", className: "tree-filter-field" },
            [
              createElement("span", { key: "label" }, "Kind"),
              createElement(
                "select",
                {
                  key: "input",
                  value: kindFilter,
                  onChange: (event) => setKindFilter(event.target.value),
                  className: "tree-filter-select",
                  "data-testid": "tree-filter-kind",
                },
                [
                  createElement("option", { key: "all", value: "" }, "All kinds"),
                  ...availableKinds.map((kind) => createElement("option", { key: kind, value: kind }, kind)),
                ],
              ),
            ],
          ),
          createElement(
            "label",
            { key: "blocked", className: "tree-filter-toggle" },
            [
              createElement("input", {
                key: "input",
                type: "checkbox",
                checked: blockedOnly,
                onChange: (event) => setBlockedOnly(event.target.checked),
                "data-testid": "tree-filter-blocked-only",
              }),
              createElement("span", { key: "label" }, "Blocked only"),
            ],
          ),
          createElement(
            "label",
            { key: "active", className: "tree-filter-toggle" },
            [
              createElement("input", {
                key: "input",
                type: "checkbox",
                checked: activeOnly,
                onChange: (event) => setActiveOnly(event.target.checked),
                "data-testid": "tree-filter-active-only",
              }),
              createElement("span", { key: "label" }, "Active only"),
            ],
          ),
        ],
      ),
      filteredNodes.length
        ? createElement(
            "div",
            { key: "list", className: "tree-list", "data-testid": "tree-node-list" },
            filteredNodes.map((item) =>
              createElement(TreeNodeLink, {
                key: item.node_id,
                node: item,
                projectId,
                selectedNodeId: nodeId ?? rootNodeId,
                activeTab: tab ?? "overview",
              }),
            ),
          )
        : createElement(
            EmptyState,
            {
              key: "empty",
              title: "No matching nodes",
              body: "Adjust the filter to show more of the hierarchy.",
            },
          ),
    ],
  );
}
