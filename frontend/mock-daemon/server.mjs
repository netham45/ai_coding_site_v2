import http from "node:http";
import { URL } from "node:url";
import { SCENARIOS } from "./scenarios.js";

const DEFAULT_TOKEN = "scenario-token";

function json(res, statusCode, payload) {
  res.writeHead(statusCode, {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  });
  res.end(JSON.stringify(payload));
}

function unauthorized(res) {
  json(res, 401, { error: "unauthorized", message: "Invalid bearer token.", detail: "invalid bearer token" });
}

function notFound(res, message = "not found") {
  json(res, 404, { detail: message });
}

function badRequest(res, message = "bad request") {
  json(res, 400, { detail: message });
}

function conflict(res, message = "conflict") {
  json(res, 409, { detail: message });
}

function parseBearerToken(req) {
  const header = req.headers.authorization ?? "";
  const [scheme, token] = header.split(" ");
  if (scheme !== "Bearer" || !token) {
    return null;
  }
  return token;
}

function updateTreeVersionPointers(scenario, nodeId, versionId) {
  for (const tree of Object.values(scenario.treeByNodeId ?? {})) {
    const row = tree.nodes?.find((entry) => entry.node_id === nodeId);
    if (row) {
      row.latest_created_node_version_id = versionId;
      row.last_updated_at = "2026-03-11T00:10:00Z";
    }
  }
}

function buildServer({ scenarioId, token = DEFAULT_TOKEN }) {
  const scenario = SCENARIOS[scenarioId];
  if (!scenario) {
    throw new Error(`Unknown scenario '${scenarioId}'.`);
  }

  return http.createServer((req, res) => {
    if (req.method === "OPTIONS") {
      res.writeHead(204, {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      });
      res.end();
      return;
    }

    const requestToken = parseBearerToken(req);
    if (requestToken !== token) {
      unauthorized(res);
      return;
    }

    const url = new URL(req.url ?? "/", "http://127.0.0.1");
    const path = url.pathname;

    if (path === "/bootstrap") {
      json(res, 200, {
        auth_token_file: ".runtime/daemon.token",
        auth_token_source: "settings",
      });
      return;
    }

    if (path === "/api/projects") {
      json(res, 200, scenario.projectCatalog);
      return;
    }

    const bootstrapMatch = path.match(/^\/api\/projects\/([^/]+)\/bootstrap$/);
    if (bootstrapMatch && req.method === "GET") {
      const projectId = bootstrapMatch[1];
      const payload = scenario.projectBootstrapByProjectId?.[projectId];
      if (!payload) {
        notFound(res, `project '${projectId}' not found`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    if (path === "/api/node-kinds") {
      json(res, 200, scenario.nodeKinds);
      return;
    }

    const createMatch = path.match(/^\/api\/projects\/([^/]+)\/top-level-nodes$/);
    if (createMatch && req.method === "POST") {
      const projectId = createMatch[1];
      const createError = scenario.topLevelCreateErrorByProjectId?.[projectId];
      if (createError) {
        json(res, createError.status ?? 400, { detail: createError.detail ?? "top-level creation failed" });
        return;
      }
      const payload = scenario.topLevelCreateResponseByProjectId?.[projectId];
      if (!payload) {
        notFound(res, `project '${projectId}' not found`);
        return;
      }

      const chunks = [];
      req.on("data", (chunk) => chunks.push(chunk));
      req.on("end", () => {
        try {
          const parsed = chunks.length ? JSON.parse(Buffer.concat(chunks).toString("utf-8")) : {};
          if (!parsed.kind || !parsed.title || !parsed.prompt) {
            badRequest(res, "kind, title, and prompt are required");
            return;
          }
          if (scenario.projectBootstrapByProjectId?.[projectId] && payload.route_hint) {
            scenario.projectBootstrapByProjectId[projectId] = {
              ...scenario.projectBootstrapByProjectId[projectId],
              root_node_id: payload.route_hint.node_id,
              route_hint: payload.route_hint,
            };
          }
          json(res, 200, payload);
        } catch {
          badRequest(res, "invalid json body");
        }
      });
      return;
    }

    const treeMatch = path.match(/^\/api\/nodes\/([^/]+)\/tree$/);
    if (treeMatch) {
      const nodeId = treeMatch[1];
      const payload = scenario.treeByNodeId[nodeId];
      if (!payload) {
        notFound(res, `tree scenario not found for node '${nodeId}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const nodeVersionMatch = path.match(/^\/api\/node-versions\/([^/]+)$/);
    if (nodeVersionMatch) {
      const versionId = nodeVersionMatch[1];
      const payload = scenario.nodeVersionById?.[versionId];
      if (!payload) {
        notFound(res, `node-version scenario not found for version '${versionId}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const summaryMatch = path.match(/^\/api\/nodes\/([^/]+)\/summary$/);
    if (summaryMatch) {
      const payload = scenario.nodeSummaryByNodeId?.[summaryMatch[1]];
      if (!payload) {
        notFound(res, `summary scenario not found for node '${summaryMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const lineageMatch = path.match(/^\/api\/nodes\/([^/]+)\/lineage$/);
    if (lineageMatch) {
      const payload = scenario.nodeLineageByNodeId?.[lineageMatch[1]];
      if (!payload) {
        notFound(res, `lineage scenario not found for node '${lineageMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const promptHistoryMatch = path.match(/^\/api\/nodes\/([^/]+)\/prompt-history$/);
    if (promptHistoryMatch) {
      const nodeId = promptHistoryMatch[1];
      const payload = scenario.promptHistoryByNodeId?.[nodeId];
      if (!payload) {
        notFound(res, `prompt-history scenario not found for node '${nodeId}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const supersedeMatch = path.match(/^\/api\/nodes\/([^/]+)\/supersede$/);
    if (supersedeMatch && req.method === "POST") {
      const nodeId = supersedeMatch[1];
      const template = scenario.supersedeTemplateByNodeId?.[nodeId];
      const lineage = scenario.nodeLineageByNodeId?.[nodeId];
      if (!template || !lineage) {
        notFound(res, `supersede scenario not found for node '${nodeId}'`);
        return;
      }

      if (lineage.latest_created_node_version_id !== lineage.authoritative_node_version_id) {
        conflict(res, "logical node already has a live candidate version");
        return;
      }

      const chunks = [];
      req.on("data", (chunk) => chunks.push(chunk));
      req.on("end", () => {
        try {
          const parsed = chunks.length ? JSON.parse(Buffer.concat(chunks).toString("utf-8")) : {};
          if (!parsed.prompt || !String(parsed.prompt).trim()) {
            badRequest(res, "prompt is required");
            return;
          }
          const nextVersion = {
            ...template,
            title: String(parsed.title ?? template.title),
            prompt: String(parsed.prompt),
          };
          scenario.nodeVersionById[nextVersion.id] = nextVersion;
          scenario.nodeLineageByNodeId[nodeId] = {
            ...lineage,
            latest_created_node_version_id: nextVersion.id,
            versions: [...(lineage.versions ?? []), { id: nextVersion.id }],
          };
          if (scenario.nodeSummaryByNodeId?.[nodeId]) {
            scenario.nodeSummaryByNodeId[nodeId] = {
              ...scenario.nodeSummaryByNodeId[nodeId],
              latest_created_node_version_id: nextVersion.id,
            };
          }
          if (scenario.regenerateResponseByNodeId?.[nodeId]) {
            scenario.regenerateResponseByNodeId[nodeId] = {
              ...scenario.regenerateResponseByNodeId[nodeId],
              root_node_version_id: nextVersion.id,
              created_candidate_version_ids: [nextVersion.id],
              stable_candidate_version_ids: [nextVersion.id],
            };
          }
          updateTreeVersionPointers(scenario, nodeId, nextVersion.id);
          json(res, 200, nextVersion);
        } catch {
          badRequest(res, "invalid json body");
        }
      });
      return;
    }

    const regenerateMatch = path.match(/^\/api\/nodes\/([^/]+)\/regenerate$/);
    if (regenerateMatch && req.method === "POST") {
      const nodeId = regenerateMatch[1];
      const payload = scenario.regenerateResponseByNodeId?.[nodeId];
      if (!payload) {
        notFound(res, `regenerate scenario not found for node '${nodeId}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const workflowMatch = path.match(/^\/api\/nodes\/([^/]+)\/workflow\/current$/);
    if (workflowMatch) {
      const payload = scenario.workflowByNodeId?.[workflowMatch[1]];
      if (!payload) {
        notFound(res, `workflow scenario not found for node '${workflowMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const runsMatch = path.match(/^\/api\/nodes\/([^/]+)\/runs$/);
    if (runsMatch) {
      const payload = scenario.runsByNodeId?.[runsMatch[1]];
      if (!payload) {
        notFound(res, `runs scenario not found for node '${runsMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const summariesMatch = path.match(/^\/api\/nodes\/([^/]+)\/summary-history$/);
    if (summariesMatch) {
      const payload = scenario.summariesByNodeId?.[summariesMatch[1]];
      if (!payload) {
        notFound(res, `summaries scenario not found for node '${summariesMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const sessionsMatch = path.match(/^\/api\/nodes\/([^/]+)\/sessions$/);
    if (sessionsMatch) {
      const payload = scenario.sessionsByNodeId?.[sessionsMatch[1]];
      if (!payload) {
        notFound(res, `sessions scenario not found for node '${sessionsMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const sourcesMatch = path.match(/^\/api\/nodes\/([^/]+)\/sources$/);
    if (sourcesMatch) {
      const payload = scenario.sourcesByNodeId?.[sourcesMatch[1]];
      if (!payload) {
        notFound(res, `sources scenario not found for node '${sourcesMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const rationaleMatch = path.match(/^\/api\/nodes\/([^/]+)\/rationale$/);
    if (rationaleMatch) {
      const payload = scenario.rationaleByNodeId?.[rationaleMatch[1]];
      if (!payload) {
        notFound(res, `rationale scenario not found for node '${rationaleMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    const actionsMatch = path.match(/^\/api\/nodes\/([^/]+)\/actions$/);
    if (actionsMatch) {
      const nodeId = actionsMatch[1];
      const payload = scenario.actionCatalogByNodeId?.[nodeId];
      if (!payload) {
        notFound(res, `action scenario not found for node '${nodeId}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    if (path === "/api/node-runs/start" && req.method === "POST") {
      json(res, 200, { status: "admitted", node_run_id: "mock-run-started" });
      return;
    }

    const runProgressMatch = path.match(/^\/api\/node-runs\/([^/]+)$/);
    if (runProgressMatch) {
      const payload = scenario.runProgressByNodeId?.[runProgressMatch[1]];
      if (!payload) {
        notFound(res, `run-progress scenario not found for node '${runProgressMatch[1]}'`);
        return;
      }
      json(res, 200, payload);
      return;
    }

    if (path === "/api/nodes/pause" && req.method === "POST") {
      json(res, 200, { status: "accepted", command: "node.pause" });
      return;
    }

    if (path === "/api/nodes/resume" && req.method === "POST") {
      json(res, 200, { status: "accepted", command: "node.resume" });
      return;
    }

    if (path === "/api/sessions/attach" && req.method === "POST") {
      json(res, 200, { status: "running", backend: "tmux", session_name: "mock-attach" });
      return;
    }

    if (path === "/api/sessions/resume" && req.method === "POST") {
      json(res, 200, { status: "resumed", recovery_status: { recommended_action: "resume_existing_session" }, session: null });
      return;
    }

    if (path === "/api/sessions/provider-resume" && req.method === "POST") {
      json(res, 200, {
        status: "resumed",
        provider_recovery_status: { provider_recommended_action: "rebind_provider_session" },
        recovery_status: { recommended_action: "resume_existing_session" },
        session: null,
      });
      return;
    }

    const reconcileChildrenMatch = path.match(/^\/api\/nodes\/([^/]+)\/children\/reconcile$/);
    if (reconcileChildrenMatch && req.method === "POST") {
      json(res, 200, { status: "reconciled", parent_node_id: reconcileChildrenMatch[1] });
      return;
    }

    notFound(res);
  });
}

const scenarioId = process.env.MOCK_DAEMON_SCENARIO ?? "project_catalog_single";
const token = process.env.MOCK_DAEMON_TOKEN ?? DEFAULT_TOKEN;
const port = Number(process.env.MOCK_DAEMON_PORT ?? "7788");

const server = buildServer({ scenarioId, token });
server.listen(port, "127.0.0.1", () => {
  console.log(`mock-daemon:${scenarioId}:listening:${port}`);
});
