import { spawn } from "node:child_process";

const port = 7790;
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

  const actions = await getJson("/api/nodes/node-task-1/actions");
  if (!Array.isArray(actions.actions) || actions.actions.length < 2) {
    throw new Error("Expected deterministic action catalog state.");
  }

  const startRun = actions.actions.find((item) => item.action_id === "start_run");
  const pauseRun = actions.actions.find((item) => item.action_id === "pause_run");
  if (!startRun?.legal || pauseRun?.legal) {
    throw new Error("Expected deterministic action legality state.");
  }

  const admitted = await postJson("/api/node-runs/start", { node_id: "node-task-1" });
  if (admitted.status !== "admitted") {
    throw new Error("Expected bounded action mutation scenario.");
  }

  console.log("action-surface-check: ok");
} finally {
  child.kill("SIGTERM");
}
