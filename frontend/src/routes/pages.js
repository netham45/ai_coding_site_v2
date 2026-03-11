import { createElement, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import EmptyState from "../components/primitives/EmptyState.js";
import ErrorState from "../components/primitives/ErrorState.js";
import LoadingState from "../components/primitives/LoadingState.js";
import StatusBadge from "../components/primitives/StatusBadge.js";
import NodeDetailTabs, { normalizeDetailTab } from "../components/detail/NodeDetailTabs.js";
import { getProjectBootstrap, listNodeKinds, listProjects } from "../lib/api/projects.js";
import { createTopLevelNode } from "../lib/api/topLevelCreation.js";
import { queryKeys } from "../lib/query/keys.js";

function PageFrame({ title, testId, children }) {
  return createElement(
    "section",
    { className: "page-frame", "data-testid": testId },
    createElement("h2", { className: "page-frame__title" }, title),
    children,
  );
}

function projectReadinessTone(project) {
  return project.bootstrap_ready ? "success" : "warning";
}

function projectReadinessLabel(project) {
  return project.bootstrap_ready ? "bootstrap ready" : "readiness problem";
}

function projectFailurePresentation(error) {
  if (error?.status === 401) {
    return {
      title: "Daemon authentication invalid",
      body: "The configured bearer token was rejected. Update the browser session token and retry.",
      testId: "projects-auth-invalid",
    };
  }
  if (error?.code === "ERR_NETWORK" || error?.status === null || error?.code === "daemon_unavailable") {
    return {
      title: "Daemon unreachable",
      body: "The website could not reach the configured daemon API. Check the daemon URL and that the daemon is running.",
      testId: "projects-daemon-unreachable",
    };
  }
  return {
    title: "Unable to load projects",
    body: error?.message ?? "Unknown API error",
    testId: "projects-generic-error",
  };
}

function DaemonContextCard({ daemonContext }) {
  return createElement(
    "section",
    { className: "project-context-card", "data-testid": "project-daemon-context" },
    [
      createElement(
        "div",
        { key: "header", className: "project-context-card__header" },
        [
          createElement("h3", { key: "title", className: "project-context-card__title" }, daemonContext.daemon_app_name),
          createElement(StatusBadge, {
            key: "reachable",
            label: daemonContext.reachability_state,
            tone: daemonContext.reachability_state === "reachable" ? "success" : "danger",
          }),
        ],
      ),
      createElement(
        "div",
        { key: "meta", className: "project-context-card__meta" },
        [
          createElement("span", { key: "version" }, `Version ${daemonContext.daemon_version}`),
          createElement("span", { key: "authority" }, `Authority ${daemonContext.authority}`),
          createElement("span", { key: "backend" }, `Sessions ${daemonContext.session_backend}`),
          createElement("span", { key: "auth" }, `Auth ${daemonContext.auth_status}`),
        ],
      ),
    ],
  );
}

function ProjectCatalogItem({ project, showSourcePath = true }) {
  const content = [
    createElement(
      "div",
      { key: "header", className: "project-card__header" },
      [
        createElement("strong", { key: "label" }, project.label),
        createElement(StatusBadge, {
          key: "status",
          label: projectReadinessLabel(project),
          tone: projectReadinessTone(project),
        }),
      ],
    ),
    showSourcePath ? createElement("span", { key: "path" }, project.source_path) : null,
    project.default_branch
      ? createElement("span", { key: "branch", className: "project-card__subtle" }, `Branch ${project.default_branch}`)
      : null,
    project.head_commit_sha
      ? createElement(
          "span",
          { key: "head", className: "project-card__subtle" },
          `HEAD ${project.head_commit_sha.slice(0, 12)}`,
        )
      : null,
    !project.bootstrap_ready && project.readiness_message
      ? createElement("span", { key: "reason", className: "project-card__warning" }, project.readiness_message)
      : null,
  ].filter(Boolean);

  if (project.bootstrap_ready) {
    return createElement(
      Link,
      {
        to: `/projects/${project.project_id}`,
        className: "project-card",
        "data-testid": `project-link-${project.project_id}`,
      },
      content,
    );
  }

  return createElement(
    "div",
    {
      className: "project-card project-card--disabled",
      "data-testid": `project-card-${project.project_id}`,
    },
    content,
  );
}

function ProjectCatalogList({ projects }) {
  return createElement(
    "div",
    { className: "project-catalog", "data-testid": "project-catalog" },
    projects.map((project) => createElement(ProjectCatalogItem, { key: project.project_id, project })),
  );
}

export function ProjectsIndexPage() {
  const projectQuery = useQuery({
    queryKey: queryKeys.projects(),
    queryFn: async () => (await listProjects()).data,
  });

  if (projectQuery.isLoading) {
    return createElement(
      PageFrame,
      { title: "Projects", testId: "page-projects-index" },
      createElement(LoadingState, { label: "Loading project catalog." }),
    );
  }

  if (projectQuery.isError) {
    const failure = projectFailurePresentation(projectQuery.error);
    return createElement(
      PageFrame,
      { title: "Projects", testId: "page-projects-index" },
      createElement(
        "div",
        { "data-testid": failure.testId },
        createElement(ErrorState, { title: failure.title, body: failure.body }),
      ),
    );
  }

  const daemonContext = projectQuery.data?.daemon_context ?? null;
  const projects = projectQuery.data?.projects ?? [];
  return createElement(
    PageFrame,
    { title: "Projects", testId: "page-projects-index" },
    [
      createElement(
        "p",
        { key: "lede", className: "page-frame__lede" },
        "Choose a source repo under repos/ to enter the website operator flow.",
      ),
      daemonContext ? createElement(DaemonContextCard, { key: "context", daemonContext }) : null,
      projects.length
        ? createElement(ProjectCatalogList, { key: "catalog", projects })
        : createElement(EmptyState, {
            key: "empty",
            title: "No projects found",
            body: "No source repos are currently available under repos/.",
          }),
    ],
  );
}

function TopLevelCreationForm({ project, topLevelKinds }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState({
    kind: "",
    title: "",
    prompt: "",
  });
  const [isConfirming, setIsConfirming] = useState(false);

  const mutation = useMutation({
    mutationFn: (payload) => createTopLevelNode(project.project_id, payload),
    onSuccess: async (response) => {
      const payload = response.data;
      await queryClient.invalidateQueries({ queryKey: queryKeys.projects() });
      await queryClient.invalidateQueries({ queryKey: queryKeys.projectBootstrap(project.project_id) });
      navigate(payload.route_hint?.url ?? `/projects/${project.project_id}/nodes/${payload.node.node_id}/overview`);
    },
  });

  const isReadyToConfirm = draft.kind.trim() && draft.title.trim() && draft.prompt.trim();

  function updateField(field, value) {
    setDraft((current) => ({ ...current, [field]: value }));
    if (isConfirming) {
      setIsConfirming(false);
    }
  }

  function onRequestConfirm(event) {
    event.preventDefault();
    if (!isReadyToConfirm || mutation.isPending) {
      return;
    }
    setIsConfirming(true);
  }

  function onKeepEditing() {
    setIsConfirming(false);
  }

  async function onConfirmCreate() {
    await mutation.mutateAsync({
      kind: draft.kind.trim(),
      title: draft.title.trim(),
      prompt: draft.prompt.trim(),
      start_run: true,
    });
  }

  return createElement(
    "form",
    {
      className: "form-card",
      onSubmit: onRequestConfirm,
      "data-testid": "top-level-create-form",
    },
    [
      createElement(
        "div",
        { key: "header", className: "form-card__header" },
        createElement("div", null, [
          createElement("p", { key: "eyebrow", className: "form-card__eyebrow" }, "Top-Level Creation"),
          createElement("h3", { key: "title", className: "form-card__title" }, `Create in ${project.label}`),
        ]),
        createElement(StatusBadge, { label: "project selected", tone: "success" }),
      ),
      createElement(
        "label",
        { key: "kind", className: "field-group" },
        [
          createElement("span", { key: "label", className: "field-group__label" }, "Node kind"),
          createElement(
            "select",
            {
              key: "input",
              className: "field-group__input field-group__input--select",
              value: draft.kind,
              onChange: (event) => updateField("kind", event.target.value),
              "data-testid": "top-level-kind-select",
            },
            [
              createElement("option", { key: "blank", value: "" }, "Select a top-level kind"),
              ...topLevelKinds.map((definition) =>
                createElement("option", { key: definition.kind, value: definition.kind }, definition.kind),
              ),
            ],
          ),
        ],
      ),
      createElement(
        "label",
        { key: "title", className: "field-group" },
        [
          createElement("span", { key: "label", className: "field-group__label" }, "Title"),
          createElement("input", {
            key: "input",
            className: "field-group__input",
            type: "text",
            value: draft.title,
            maxLength: 255,
            onChange: (event) => updateField("title", event.target.value),
            "data-testid": "top-level-title-input",
          }),
        ],
      ),
      createElement(
        "label",
        { key: "prompt", className: "field-group" },
        [
          createElement("span", { key: "label", className: "field-group__label" }, "Prompt"),
          createElement("textarea", {
            key: "input",
            className: "field-group__input field-group__input--textarea",
            rows: 8,
            value: draft.prompt,
            onChange: (event) => updateField("prompt", event.target.value),
            "data-testid": "top-level-prompt-input",
          }),
        ],
      ),
      mutation.isError
        ? createElement(ErrorState, {
            key: "error",
            title: "Unable to create node",
            body: mutation.error.message,
          })
        : null,
      isConfirming
        ? createElement(
            "div",
            {
              key: "confirm",
              className: "confirmation-strip",
              "data-testid": "top-level-create-confirmation",
            },
            [
              createElement(
                "p",
                { key: "text", className: "confirmation-strip__text" },
                "Create node now and immediately start the first run?",
              ),
              createElement(
                "div",
                { key: "actions", className: "confirmation-strip__actions" },
                [
                  createElement(
                    "button",
                    {
                      key: "confirm",
                      type: "button",
                      className: "button button--primary",
                      onClick: onConfirmCreate,
                      disabled: mutation.isPending,
                      "data-testid": "confirm-create-node",
                    },
                    mutation.isPending ? "creating..." : "create node",
                  ),
                  createElement(
                    "button",
                    {
                      key: "edit",
                      type: "button",
                      className: "button button--secondary",
                      onClick: onKeepEditing,
                      disabled: mutation.isPending,
                      "data-testid": "keep-editing-button",
                    },
                    "keep editing",
                  ),
                ],
              ),
            ],
          )
        : createElement(
            "div",
            { key: "submit", className: "form-card__footer" },
            createElement(
              "button",
              {
                type: "submit",
                className: "button button--primary",
                disabled: !isReadyToConfirm || mutation.isPending,
                "data-testid": "create-node-trigger",
              },
              "Create Node",
            ),
          ),
    ],
  );
}

export function ProjectPage() {
  const { projectId } = useParams();
  const projectQuery = useQuery({
    queryKey: queryKeys.projects(),
    queryFn: async () => (await listProjects()).data,
  });
  const nodeKindsQuery = useQuery({
    queryKey: queryKeys.nodeKinds(),
    queryFn: async () => (await listNodeKinds()).data,
  });
  const projectBootstrapQuery = useQuery({
    queryKey: queryKeys.projectBootstrap(projectId),
    queryFn: async () => (await getProjectBootstrap(projectId)).data,
    enabled: Boolean(projectId),
  });

  const project = useMemo(
    () => (projectQuery.data?.projects ?? []).find((entry) => entry.project_id === projectId) ?? null,
    [projectId, projectQuery.data],
  );
  const topLevelKinds = useMemo(() => {
    const catalog = nodeKindsQuery.data;
    if (!catalog) {
      return [];
    }
    const allowed = new Set(catalog.top_level_kinds ?? []);
    return (catalog.definitions ?? []).filter((definition) => allowed.has(definition.kind));
  }, [nodeKindsQuery.data]);

  if (projectQuery.isLoading || nodeKindsQuery.isLoading || projectBootstrapQuery.isLoading) {
    return createElement(
      PageFrame,
      { title: `Project ${projectId}`, testId: "page-project-detail" },
      createElement(LoadingState, { label: "Loading project and top-level node options." }),
    );
  }

  if (projectQuery.isError) {
    return createElement(
      PageFrame,
      { title: `Project ${projectId}`, testId: "page-project-detail" },
      createElement(ErrorState, { title: "Unable to load project catalog", body: projectQuery.error.message }),
    );
  }

  if (nodeKindsQuery.isError) {
    return createElement(
      PageFrame,
      { title: `Project ${projectId}`, testId: "page-project-detail" },
      createElement(ErrorState, { title: "Unable to load node kinds", body: nodeKindsQuery.error.message }),
    );
  }

  if (projectBootstrapQuery.isError) {
    return createElement(
      PageFrame,
      { title: `Project ${projectId}`, testId: "page-project-detail" },
      createElement(ErrorState, { title: "Unable to load project bootstrap", body: projectBootstrapQuery.error.message }),
    );
  }

  if (!project) {
    return createElement(
      PageFrame,
      { title: `Project ${projectId}`, testId: "page-project-detail" },
      createElement(ErrorState, {
        title: "Project not found",
        body: `The project '${projectId}' is not available under repos/.`,
      }),
    );
  }

  const rootNodeId = projectBootstrapQuery.data?.root_node_id ?? null;
  if (rootNodeId) {
    return createElement(Navigate, {
      to: `/projects/${projectId}/nodes/${rootNodeId}/overview`,
      replace: true,
    });
  }

  return createElement(
    PageFrame,
    { title: `Project ${projectId}`, testId: "page-project-detail" },
    createElement("p", { className: "page-frame__lede" }, `Source repo: ${project.source_path}`),
    createElement("div", { className: "project-detail-grid" }, [
      createElement(
        "section",
        { key: "catalog", className: "project-panel", "data-testid": "project-selection-panel" },
        [
          createElement("h3", { key: "title", className: "project-panel__title" }, "Available Projects"),
          projectQuery.data?.daemon_context
            ? createElement(DaemonContextCard, {
                key: "context",
                daemonContext: projectQuery.data.daemon_context,
              })
            : null,
          createElement(ProjectCatalogList, { key: "list", projects: projectQuery.data?.projects ?? [] }),
        ],
      ),
      createElement(
        "section",
        { key: "form", className: "project-panel" },
        project.bootstrap_ready
          ? createElement(TopLevelCreationForm, { project, topLevelKinds })
          : createElement(ErrorState, {
              title: "Project is not bootstrap ready",
              body: project.readiness_message ?? "This project cannot be used for top-level workflow start yet.",
            }),
      ),
    ]),
  );
}

export function NodePage() {
  const { projectId, nodeId } = useParams();
  return createElement(Navigate, {
    to: `/projects/${projectId}/nodes/${nodeId}/overview`,
    replace: true,
  });
}

export function NodeTabPage() {
  const { projectId, nodeId, tab } = useParams();
  const activeTab = normalizeDetailTab(tab ?? "overview");
  return createElement(
    PageFrame,
    { title: `Node ${nodeId} / ${tab}`, testId: "page-node-tab" },
    createElement("p", { className: "page-frame__lede" }, "Route-driven node detail tabs reuse the daemon inspection and bounded mutation surfaces directly."),
    createElement(StatusBadge, { label: activeTab, tone: "info" }),
    createElement(NodeDetailTabs, { projectId, nodeId, activeTab }),
  );
}

export function PrimitiveGalleryPage() {
  return createElement(
    PageFrame,
    { title: "Primitive Gallery", testId: "page-primitive-gallery" },
    createElement("p", null, "Shared primitive scaffold for loading, empty, error, and status states."),
    createElement("div", { className: "primitive-gallery" }, [
      createElement(LoadingState, { key: "loading", label: "Gallery loading placeholder" }),
      createElement(EmptyState, { key: "empty", title: "Empty placeholder", body: "No rows have been loaded." }),
      createElement(ErrorState, { key: "error", title: "Error placeholder", body: "This route demonstrates the shared error primitive." }),
      createElement(StatusBadge, { key: "status", label: "waiting user input", tone: "neutral" }),
    ]),
  );
}
