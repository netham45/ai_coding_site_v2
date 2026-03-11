import { spawn } from "node:child_process";
import { expect, test } from "@playwright/test";
import { apiStorageKeys } from "../../src/lib/api/client.js";

const mockDaemonPort = 7791;
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
      MOCK_DAEMON_SCENARIO: "healthy_tree_small",
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

test("workflow, summaries, sessions, and blocked action routes are browser-proven", async ({ page }) => {
  await page.goto("/projects/repo_alpha/nodes/node-task-1/workflow");
  await expect(page.getByTestId("tree-sidebar")).toBeVisible();
  await expect(page.getByTestId("detail-tab-workflow")).toBeVisible();
  await expect(page.getByTestId("workflow-summary-card")).toBeVisible();

  await page.getByTestId("detail-tab-link-summaries").click();
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/summaries$/);
  await expect(page.getByTestId("detail-tab-summaries")).toBeVisible();
  await expect(page.getByTestId("summaries-list-card")).toBeVisible();

  await page.getByTestId("detail-tab-link-sessions").click();
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/sessions$/);
  await expect(page.getByTestId("detail-tab-sessions")).toBeVisible();
  await expect(page.getByTestId("sessions-list-card")).toBeVisible();

  await page.getByTestId("detail-tab-link-actions").click();
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/actions$/);
  await expect(page.getByTestId("detail-tab-actions")).toBeVisible();
  await expect(page.getByTestId("action-trigger-pause-run")).toBeDisabled();
});
