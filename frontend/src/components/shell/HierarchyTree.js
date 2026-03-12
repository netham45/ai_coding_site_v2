import { createElement, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import LoadingState from "../primitives/LoadingState.js";
import EmptyState from "../primitives/EmptyState.js";
import ErrorState from "../primitives/ErrorState.js";
import StatusBadge from "../primitives/StatusBadge.js";
import { getNodeAncestors } from "../../lib/api/nodes.js";
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

function nodeMatchesFilters(node, { query, lifecycleFilter, kindFilter, blockedOnly, activeOnly }) {
  const matchesText = !query || node.title.toLowerCase().includes(query) || node.kind.toLowerCase().includes(query);
  const matchesLifecycle = !lifecycleFilter || (node.lifecycle_state ?? "").toUpperCase() === lifecycleFilter;
  const matchesKind = !kindFilter || node.kind === kindFilter;
  const matchesBlocked =
    !blockedOnly ||
    node.blocker_state === "blocked" ||
    node.blocker_state === "paused_for_user" ||
    node.scheduling_status === "blocked" ||
    node.scheduling_status === "paused_for_user";
  const matchesActive =
    !activeOnly ||
    node.run_status === "RUNNING" ||
    node.scheduling_status === "already_running" ||
    node.lifecycle_state === "RUNNING";
  return matchesText && matchesLifecycle && matchesKind && matchesBlocked && matchesActive;
}

function normalizeExpandedSet(value) {
  return new Set(value ?? []);
}

function TopLevelNodeLink({ node, selectedNodeId }) {
  const isSelected = selectedNodeId === node.node_id;
  return createElement(
    Link,
    {
      to: node.route_hint?.url ?? `/projects/${node.route_hint?.project_id ?? ""}/nodes/${node.node_id}/overview`,
      className: `tree-node ${isSelected ? "tree-node--selected" : ""}`,
      "data-testid": `top-level-node-${node.node_id}`,
    },
    [
      createElement(
        "div",
        { key: "main", className: "tree-node__main" },
        [
          createElement("strong", { key: "title", className: "tree-node__title" }, node.title),
          createElement("span", { key: "meta", className: "tree-node__meta" }, `${node.kind} • top-level node`),
        ],
      ),
      createElement(
        "div",
        { key: "right", className: "tree-node__right" },
        createElement(StatusBadge, {
          label: node.run_status ?? node.lifecycle_state?.toLowerCase?.() ?? "ready",
          tone: node.run_status === "RUNNING" ? "info" : node.lifecycle_state === "COMPLETE" ? "success" : "neutral",
        }),
      ),
    ],
  );
}

function TreeRow({ node, projectId, selectedNodeId, activeTab, expanded, onToggle }) {
  const href = `/projects/${projectId}/nodes/${node.node_id}/${activeTab}`;
  const isSelected = selectedNodeId === node.node_id;
  return createElement(
    "div",
    {
      className: `tree-node-row ${isSelected ? "tree-node-row--selected" : ""}`,
      style: { paddingLeft: `${node.depth * 16}px` },
      "data-testid": `tree-row-${node.node_id}`,
    },
    [
      node.has_children
        ? createElement(
            "button",
            {
              key: "toggle",
              type: "button",
              className: "tree-node__toggle",
              onClick: () => onToggle(node.node_id),
              "aria-expanded": expanded ? "true" : "false",
              "data-testid": `tree-toggle-${node.node_id}`,
            },
            expanded ? "−" : "+",
          )
        : createElement("span", { key: "spacer", className: "tree-node__toggle tree-node__toggle--spacer", "aria-hidden": "true" }, "•"),
      createElement(
        Link,
        {
          key: "link",
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
      ),
    ],
  );
}

function Breadcrumbs({ ancestors, currentNode, projectId, tab }) {
  if (!ancestors.length && !currentNode) {
    return null;
  }
  const items = [...ancestors];
  if (currentNode) {
    items.push(currentNode);
  }
  return createElement(
    "div",
    { className: "tree-breadcrumb", "data-testid": "tree-breadcrumb" },
    items.map((item, index) => {
      const isLast = index === items.length - 1;
      const label = item.title || item.node_id;
      return createElement(
        "span",
        { key: item.node_id, className: "tree-breadcrumb__item" },
        [
          isLast
            ? createElement("span", { key: "current", className: "tree-breadcrumb__current" }, label)
            : createElement(
                Link,
                {
                  key: "link",
                  to: `/projects/${projectId}/nodes/${item.node_id}/${tab}`,
                  className: "tree-breadcrumb__link",
                  "data-testid": `tree-breadcrumb-link-${item.node_id}`,
                },
                label,
              ),
          !isLast ? createElement("span", { key: "sep", className: "tree-breadcrumb__sep" }, "/") : null,
        ],
      );
    }),
  );
}

export default function HierarchyTree() {
  const { projectId, nodeId, tab } = useParams();
  const [filterText, setFilterText] = useState("");
  const [lifecycleFilter, setLifecycleFilter] = useState("");
  const [kindFilter, setKindFilter] = useState("");
  const [blockedOnly, setBlockedOnly] = useState(false);
  const [activeOnly, setActiveOnly] = useState(false);
  const [expandedNodeIds, setExpandedNodeIds] = useState(() => new Set());
  const [focusedSubtreeRootId, setFocusedSubtreeRootId] = useState(null);

  const bootstrapQuery = useQuery({
    queryKey: queryKeys.projectBootstrap(projectId),
    queryFn: async () => (await getProjectBootstrap(projectId)).data,
    enabled: Boolean(projectId),
  });

  const ancestorQuery = useQuery({
    queryKey: queryKeys.nodeAncestors(nodeId),
    queryFn: async () => (await getNodeAncestors(nodeId)).data,
    enabled: Boolean(nodeId),
  });

  const topLevelNodes = bootstrapQuery.data?.top_level_nodes ?? [];
  const rootNodeId = useMemo(() => {
    if (!nodeId) {
      return null;
    }
    if (ancestorQuery.isLoading) {
      return null;
    }
    const ancestors = ancestorQuery.data ?? [];
    if (!ancestors.length) {
      return nodeId;
    }
    return ancestors[ancestors.length - 1].node_id;
  }, [ancestorQuery.data, ancestorQuery.isLoading, nodeId]);

  const treeQuery = useQuery({
    queryKey: queryKeys.projectTree(projectId, rootNodeId),
    queryFn: async () => (await getTree(rootNodeId)).data,
    enabled: Boolean(projectId && nodeId && rootNodeId),
    refetchInterval: 5_000,
  });

  const treeState = useMemo(() => {
    const nodes = treeQuery.data?.nodes ?? [];
    const nodeById = new Map(nodes.map((node) => [node.node_id, node]));
    const childrenByParent = new Map();
    for (const node of nodes) {
      const key = node.parent_node_id ?? null;
      if (!childrenByParent.has(key)) {
        childrenByParent.set(key, []);
      }
      childrenByParent.get(key).push(node);
    }
    const selectedPathIds = [];
    let cursor = nodeId ? nodeById.get(nodeId) ?? null : null;
    while (cursor) {
      selectedPathIds.unshift(cursor.node_id);
      cursor = cursor.parent_node_id ? nodeById.get(cursor.parent_node_id) ?? null : null;
    }
    const selectedAncestorNodes = selectedPathIds
      .slice(0, Math.max(selectedPathIds.length - 1, 0))
      .map((id) => nodeById.get(id))
      .filter(Boolean);
    const selectedNode = nodeId ? nodeById.get(nodeId) ?? null : null;
    return { nodes, nodeById, childrenByParent, selectedPathIds, selectedAncestorNodes, selectedNode };
  }, [nodeId, treeQuery.data]);

  const activeTab = tab ?? "overview";
  const activeRootId = focusedSubtreeRootId ?? rootNodeId;

  useEffect(() => {
    if (!rootNodeId) {
      return;
    }
    setExpandedNodeIds((current) => {
      const next = normalizeExpandedSet(current);
      next.add(rootNodeId);
      for (const ancestorId of treeState.selectedPathIds.slice(0, -1)) {
        next.add(ancestorId);
      }
      return next;
    });
  }, [rootNodeId, treeState.selectedPathIds]);

  useEffect(() => {
    if (!focusedSubtreeRootId) {
      return;
    }
    if (nodeId === focusedSubtreeRootId) {
      return;
    }
    if (!treeState.selectedPathIds.includes(focusedSubtreeRootId)) {
      setFocusedSubtreeRootId(null);
    }
  }, [focusedSubtreeRootId, nodeId, treeState.selectedPathIds]);

  const filterConfig = useMemo(
    () => ({
      query: filterText.trim().toLowerCase(),
      lifecycleFilter,
      kindFilter,
      blockedOnly,
      activeOnly,
    }),
    [activeOnly, blockedOnly, filterText, kindFilter, lifecycleFilter],
  );

  const visibleNodes = useMemo(() => {
    const { nodeById, childrenByParent } = treeState;
    if (!activeRootId || !nodeById.size) {
      return { rows: [], expandedIds: new Set(), filterActive: false, matchingNodeIds: new Set() };
    }

    const filterActive = Boolean(
      filterConfig.query || filterConfig.lifecycleFilter || filterConfig.kindFilter || filterConfig.blockedOnly || filterConfig.activeOnly,
    );
    const matchingNodeIds = new Set();
    const filterContextNodeIds = new Set();

    if (filterActive) {
      for (const node of treeState.nodes) {
        if (!nodeById.has(node.node_id)) {
          continue;
        }
        if (!nodeMatchesFilters(node, filterConfig)) {
          continue;
        }
        matchingNodeIds.add(node.node_id);
        let cursor = node;
        while (cursor) {
          filterContextNodeIds.add(cursor.node_id);
          cursor = cursor.parent_node_id ? nodeById.get(cursor.parent_node_id) ?? null : null;
        }
      }
      filterContextNodeIds.add(activeRootId);
    }

    const effectiveExpanded = normalizeExpandedSet(expandedNodeIds);
    effectiveExpanded.add(activeRootId);
    for (const ancestorId of treeState.selectedPathIds.slice(0, -1)) {
      effectiveExpanded.add(ancestorId);
    }
    if (filterActive) {
      for (const nodeIdValue of filterContextNodeIds) {
        effectiveExpanded.add(nodeIdValue);
      }
    }

    const rows = [];
    function visit(currentNodeId, depth) {
      const node = nodeById.get(currentNodeId);
      if (!node) {
        return;
      }
      if (filterActive && !filterContextNodeIds.has(currentNodeId)) {
        return;
      }
      rows.push({ ...node, depth });
      if (!effectiveExpanded.has(currentNodeId)) {
        return;
      }
      const children = childrenByParent.get(currentNodeId) ?? [];
      for (const child of children) {
        visit(child.node_id, depth + 1);
      }
    }

    visit(activeRootId, 0);
    return { rows, expandedIds: effectiveExpanded, filterActive, matchingNodeIds };
  }, [activeRootId, expandedNodeIds, filterConfig, treeState]);

  const availableKinds = useMemo(() => {
    const kinds = new Set((treeQuery.data?.nodes ?? []).map((item) => item.kind));
    return Array.from(kinds).sort();
  }, [treeQuery.data]);

  const availableLifecycleStates = useMemo(() => {
    const values = new Set((treeQuery.data?.nodes ?? []).map((item) => item.lifecycle_state).filter(Boolean));
    return Array.from(values).sort();
  }, [treeQuery.data]);

  function toggleNode(nodeIdToToggle) {
    setExpandedNodeIds((current) => {
      const next = normalizeExpandedSet(current);
      if (next.has(nodeIdToToggle)) {
        next.delete(nodeIdToToggle);
      } else {
        next.add(nodeIdToToggle);
      }
      return next;
    });
  }

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

  if (!nodeId) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-project-roots" },
      [
        createElement(
          "div",
          { key: "header", className: "sidebar-panel__header" },
          [
            createElement("h2", { key: "title", className: "sidebar-panel__title" }, "Top-Level Nodes"),
            createElement("span", { key: "count", className: "sidebar-panel__subtle" }, `${topLevelNodes.length} total`),
          ],
        ),
        topLevelNodes.length
          ? createElement(
              "div",
              { key: "list", className: "tree-list", "data-testid": "top-level-node-list" },
              topLevelNodes.map((item) =>
                createElement(TopLevelNodeLink, {
                  key: item.node_id,
                  node: item,
                  selectedNodeId: null,
                }),
              ),
            )
          : createElement(EmptyState, {
              key: "empty",
              title: "No root node yet",
              body: "Create a top-level node to start the explorer tree for this project.",
            }),
      ],
    );
  }

  if (ancestorQuery.isLoading) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-loading" },
      createElement(LoadingState, { label: "Loading node ancestry." }),
    );
  }

  if (ancestorQuery.isError) {
    return createElement(
      "div",
      { className: "sidebar-panel", "data-testid": "tree-sidebar-error" },
      createElement(ErrorState, { title: "Unable to determine tree root", body: ancestorQuery.error.message }),
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
          createElement("span", { key: "root", className: "sidebar-panel__subtle" }, `Root: ${activeRootId}`),
        ],
      ),
      createElement(Breadcrumbs, {
        key: "breadcrumbs",
        ancestors: treeState.selectedAncestorNodes,
        currentNode: treeState.selectedNode,
        projectId,
        tab: activeTab,
      }),
      createElement(
        "div",
        { key: "focus-actions", className: "tree-focus-actions", "data-testid": "tree-focus-actions" },
        [
          nodeId && nodeId !== rootNodeId && focusedSubtreeRootId !== nodeId
            ? createElement(
                "button",
                {
                  key: "focus",
                  type: "button",
                  className: "button button--secondary tree-focus-button",
                  onClick: () => setFocusedSubtreeRootId(nodeId),
                  "data-testid": "tree-focus-selected-subtree",
                },
                "Focus selected subtree",
              )
            : null,
          focusedSubtreeRootId
            ? createElement(
                "button",
                {
                  key: "reset",
                  type: "button",
                  className: "button button--secondary tree-focus-button",
                  onClick: () => setFocusedSubtreeRootId(null),
                  "data-testid": "tree-reset-subtree-focus",
                },
                "Show full tree",
              )
            : null,
        ].filter(Boolean),
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
                  ...availableLifecycleStates.map((state) => createElement("option", { key: state, value: state }, state)),
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
      visibleNodes.rows.length
        ? createElement(
            "div",
            { key: "list", className: "tree-list", "data-testid": "tree-node-list" },
            visibleNodes.rows.map((item) =>
              createElement(TreeRow, {
                key: item.node_id,
                node: item,
                projectId,
                selectedNodeId: nodeId ?? activeRootId,
                activeTab,
                expanded: visibleNodes.expandedIds.has(item.node_id),
                onToggle: toggleNode,
              }),
            ),
          )
        : createElement(EmptyState, {
            key: "empty",
            title: "No matching nodes",
            body: "Adjust the filter or reset subtree focus to show more of the hierarchy.",
          }),
    ],
  );
}
