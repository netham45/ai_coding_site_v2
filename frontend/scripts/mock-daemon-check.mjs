import { spawn } from "node:child_process";

const port = 7788;
const token = "scenario-token";

function waitForReady(child) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error("Timed out waiting for mock daemon startup.")), 10_000);

    child.stdout.on("data", (chunk) => {
      const text = chunk.toString();
      if (text.includes(`listening:${port}`)) {
        clearTimeout(timeout);
        resolve();
      }
    });

    child.on("exit", (code) => {
      clearTimeout(timeout);
      reject(new Error(`Mock daemon exited early with code ${code}.`));
    });
  });
}

async function getJson(path) {
  const response = await fetch(`http://127.0.0.1:${port}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Expected ${path} to succeed, got ${response.status}.`);
  }

  return response.json();
}

async function postJson(path, payload) {
  const response = await fetch(`http://127.0.0.1:${port}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Expected ${path} to succeed, got ${response.status}.`);
  }

  return response.json();
}

const child = spawn("node", ["./mock-daemon/server.mjs"], {
  cwd: new URL("../", import.meta.url),
  env: {
    ...process.env,
    MOCK_DAEMON_SCENARIO: "healthy_tree_small",
    MOCK_DAEMON_TOKEN: token,
    MOCK_DAEMON_PORT: String(port),
  },
  stdio: ["ignore", "pipe", "inherit"],
});

try {
  await waitForReady(child);

  const projects = await getJson("/api/projects");
  if (projects.daemon_context?.reachability_state !== "reachable") {
    throw new Error("Expected deterministic daemon context on project catalog.");
  }
  if (!Array.isArray(projects.projects) || projects.projects.length !== 1) {
    throw new Error("Expected one deterministic project scenario.");
  }
  if (projects.projects[0].bootstrap_ready !== true) {
    throw new Error("Expected deterministic project readiness metadata.");
  }

  const bootstrap = await getJson("/api/projects/repo_alpha/bootstrap");
  if (bootstrap.root_node_id !== "node-root") {
    throw new Error("Expected deterministic project bootstrap scenario.");
  }

  const nodeKinds = await getJson("/api/node-kinds");
  if (!Array.isArray(nodeKinds.top_level_kinds) || !nodeKinds.top_level_kinds.includes("epic")) {
    throw new Error("Expected deterministic top-level node-kind scenario.");
  }

  const created = await postJson("/api/projects/repo_alpha/top-level-nodes", {
    kind: "epic",
    title: "Website UI bootstrap",
    prompt: "Create the initial website UI workflow.",
    start_run: true,
  });
  if (created.route_hint?.url !== "/projects/repo_alpha/nodes/node-root/overview") {
    throw new Error("Expected deterministic top-level creation scenario.");
  }

  const tree = await getJson("/api/nodes/node-root/tree");
  if (!Array.isArray(tree.nodes) || tree.nodes.length < 2 || !tree.generated_at) {
    throw new Error("Expected deterministic tree scenario nodes.");
  }
  if (!tree.nodes[0].authoritative_node_version_id || tree.nodes[0].child_rollups.total !== 1) {
    throw new Error("Expected expanded tree scenario fields.");
  }

  const summary = await getJson("/api/nodes/node-root/summary");
  if (summary.title !== "Website UI bootstrap") {
    throw new Error("Expected deterministic overview tab scenario.");
  }

  const workflow = await getJson("/api/nodes/node-root/workflow/current");
  if (workflow.task_count !== 2) {
    throw new Error("Expected deterministic workflow tab scenario.");
  }

  const actions = await getJson("/api/nodes/node-root/actions");
  if (!Array.isArray(actions.actions) || actions.actions[0]?.action_id !== "pause_run") {
    throw new Error("Expected deterministic action catalog scenario.");
  }

  console.log("mock-daemon-check: ok");
} finally {
  child.kill("SIGTERM");
}
