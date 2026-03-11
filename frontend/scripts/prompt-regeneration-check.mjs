import { spawn } from "node:child_process";

const port = 7789;
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

async function postJson(path, payload = {}) {
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
    MOCK_DAEMON_SCENARIO: "project_catalog_single",
    MOCK_DAEMON_TOKEN: token,
    MOCK_DAEMON_PORT: String(port),
  },
  stdio: ["ignore", "pipe", "inherit"],
});

try {
  await waitForReady(child);

  const lineageBefore = await getJson("/api/nodes/node-task-1/lineage");
  const promptHistory = await getJson("/api/nodes/node-task-1/prompt-history");
  const versionBefore = await getJson(`/api/node-versions/${lineageBefore.latest_created_node_version_id}`);

  if (versionBefore.prompt !== "Build the React shell.") {
    throw new Error("Expected deterministic initial prompt version state.");
  }
  if (!Array.isArray(promptHistory.prompts) || promptHistory.prompts.length !== 1) {
    throw new Error("Expected deterministic prompt history state.");
  }

  const supersede = await postJson("/api/nodes/node-task-1/supersede", {
    title: versionBefore.title,
    prompt: "Build the React shell with a real routed detail layout.",
  });
  if (supersede.status !== "candidate") {
    throw new Error("Expected supersede to yield a candidate version.");
  }

  const regenerate = await postJson("/api/nodes/node-task-1/regenerate");
  if (regenerate.root_node_version_id !== supersede.id) {
    throw new Error("Expected regenerate to target the latest candidate version.");
  }

  const lineageAfter = await getJson("/api/nodes/node-task-1/lineage");
  if (lineageAfter.latest_created_node_version_id !== supersede.id) {
    throw new Error("Expected lineage to advance to the new candidate version.");
  }

  const versionAfter = await getJson(`/api/node-versions/${lineageAfter.latest_created_node_version_id}`);
  if (versionAfter.prompt !== "Build the React shell with a real routed detail layout.") {
    throw new Error("Expected edited prompt to persist on the latest created version.");
  }

  console.log("prompt-regeneration-check: ok");
} finally {
  child.kill("SIGTERM");
}
