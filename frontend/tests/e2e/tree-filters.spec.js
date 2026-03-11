import { spawn } from "node:child_process";
import { expect, test } from "@playwright/test";
import { apiStorageKeys } from "../../src/lib/api/client.js";

const mockDaemonPort = 7798;
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
      MOCK_DAEMON_SCENARIO: "tree_filter_matrix",
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

test("tree filter panel supports lifecycle, kind, blocked-only, active-only, and text filters", async ({ page }) => {
  await page.goto("/projects/repo_alpha/nodes/node-root/overview");

  await expect(page.getByTestId("tree-filter-panel")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-root")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-phase-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-plan-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-task-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-task-2")).toBeVisible();

  await page.getByTestId("tree-filter-lifecycle").selectOption("COMPLETE");
  await expect(page.getByTestId("tree-node-node-task-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-root")).toHaveCount(0);
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-root\/overview$/);

  await page.getByTestId("tree-filter-lifecycle").selectOption("");
  await page.getByTestId("tree-filter-kind").selectOption("phase");
  await expect(page.getByTestId("tree-node-node-phase-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-plan-1")).toHaveCount(0);

  await page.getByTestId("tree-filter-kind").selectOption("");
  await page.getByTestId("tree-filter-blocked-only").check();
  await expect(page.getByTestId("tree-node-node-phase-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-plan-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-task-2")).toHaveCount(0);

  await page.getByTestId("tree-filter-blocked-only").uncheck();
  await page.getByTestId("tree-filter-active-only").check();
  await expect(page.getByTestId("tree-node-node-root")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-task-2")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-phase-1")).toHaveCount(0);

  await page.getByTestId("tree-filter-active-only").uncheck();
  await page.getByTestId("tree-filter-input").fill("React");
  await expect(page.getByTestId("tree-node-node-task-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-task-2")).toHaveCount(0);
});
