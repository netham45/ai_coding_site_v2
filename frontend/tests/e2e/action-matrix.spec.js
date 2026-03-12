import { spawn } from "node:child_process";
import { expect, test } from "@playwright/test";
import { apiStorageKeys } from "../../src/lib/api/client.js";

const mockDaemonPort = 7801;
const mockDaemonToken = "scenario-token";
let mockDaemon = null;

function waitForMockDaemon(child) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error("Timed out waiting for mock daemon.")), 10_000);

    child.stdout.on("data", (chunk) => {
      const text = chunk.toString();
      if (text.includes(`listening:${mockDaemonPort}`)) {
        clearTimeout(timeout);
        resolve();
      }
    });

    child.on("exit", (code) => {
      clearTimeout(timeout);
      reject(new Error(`Mock daemon exited with code ${code}.`));
    });
  });
}

test.beforeAll(async () => {
  mockDaemon = spawn("node", ["./mock-daemon/server.mjs"], {
    cwd: new URL("../../", import.meta.url),
    env: {
      ...process.env,
      MOCK_DAEMON_SCENARIO: "action_matrix",
      MOCK_DAEMON_TOKEN: mockDaemonToken,
      MOCK_DAEMON_PORT: String(mockDaemonPort),
    },
    stdio: ["ignore", "pipe", "inherit"],
  });
  await waitForMockDaemon(mockDaemon);
});

test.afterAll(() => {
  if (mockDaemon) {
    mockDaemon.kill("SIGTERM");
  }
});

test.beforeEach(async ({ page }) => {
  await page.addInitScript(
    ({ baseURL, token, storageKeys }) => {
      window.localStorage.setItem(storageKeys.baseURL, baseURL);
      window.localStorage.setItem(storageKeys.token, token);
    },
    {
      baseURL: `http://127.0.0.1:${mockDaemonPort}/api`,
      token: mockDaemonToken,
      storageKeys: apiStorageKeys,
    },
  );
});

test("remaining agreed v1 actions are browser-executed", async ({ page }) => {
  const cases = [
    { nodeId: "node-pause", trigger: "pause-run", confirm: "pause-run", success: "pause-run" },
    { nodeId: "node-resume", trigger: "resume-run", confirm: "resume-run", success: "resume-run" },
    { nodeId: "node-attach", trigger: "session-attach", confirm: "session-attach", success: "session-attach" },
    { nodeId: "node-session-resume", trigger: "session-resume", confirm: "session-resume", success: "session-resume" },
    { nodeId: "node-provider-resume", trigger: "session-provider-resume", confirm: "session-provider-resume", success: "session-provider-resume" },
    { nodeId: "node-reconcile", trigger: "reconcile-children-accept-generated", confirm: "reconcile-children-accept-generated", success: "reconcile-children-accept-generated" },
    { nodeId: "node-regenerate", trigger: "regenerate-node", confirm: "regenerate-node", success: "regenerate-node" },
  ];

  for (const actionCase of cases) {
    await page.goto(`/projects/repo_alpha/nodes/${actionCase.nodeId}/actions`);
    await expect(page.getByTestId("detail-tab-actions")).toBeVisible();
    await page.getByTestId(`action-trigger-${actionCase.trigger}`).click();
    await expect(page.getByTestId(`action-confirm-${actionCase.trigger}`)).toBeVisible();
    await page.getByTestId(`action-confirm-button-${actionCase.confirm}`).click();
    await expect(page.getByTestId(`action-success-${actionCase.success}`)).toBeVisible();
  }
});
