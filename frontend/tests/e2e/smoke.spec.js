import { spawn } from "node:child_process";
import { expect, test } from "@playwright/test";
import { apiStorageKeys } from "../../src/lib/api/client.js";

const mockDaemonPort = 7788;
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
      MOCK_DAEMON_SCENARIO: "project_catalog_single",
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

test("project selection, tree navigation, and prompt regeneration flow works", async ({ page }) => {
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

  await page.goto("/");

  await expect(page.getByTestId("app-shell")).toBeVisible();
  await expect(page.getByTestId("project-daemon-context")).toBeVisible();
  await expect(page.getByTestId("project-catalog")).toBeVisible();
  await expect(page.getByTestId("project-link-repo_alpha")).toBeVisible();

  await page.getByTestId("project-link-repo_alpha").click();

  await expect(page.getByTestId("page-project-detail")).toBeVisible();
  await expect(page.getByTestId("top-level-create-form")).toBeVisible();
  await page.getByTestId("top-level-kind-select").selectOption("epic");
  await page.getByTestId("top-level-title-input").fill("Website UI bootstrap");
  await page.getByTestId("top-level-prompt-input").fill("Create the initial website UI workflow.");
  await page.getByTestId("create-node-trigger").click();

  await expect(page.getByTestId("top-level-create-confirmation")).toBeVisible();
  await page.getByTestId("confirm-create-node").click();

  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-root\/overview$/);
  await expect(page.getByTestId("page-node-tab")).toBeVisible();
  await expect(page.getByTestId("tree-sidebar")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-root")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-task-1")).toBeVisible();

  await page.goto("/projects/repo_alpha");
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-root\/overview$/);

  await page.getByTestId("tree-filter-input").fill("React");
  await expect(page.getByTestId("tree-node-node-task-1")).toBeVisible();
  await expect(page.getByTestId("tree-node-node-root")).toHaveCount(0);

  await page.getByTestId("tree-filter-input").fill("");
  await page.getByTestId("tree-node-node-task-1").click();
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/overview$/);
  await expect(page.getByTestId("detail-tab-overview")).toBeVisible();

  await page.getByTestId("detail-tab-link-runs").click();
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/runs$/);
  await expect(page.getByTestId("detail-tab-runs")).toBeVisible();

  await page.getByTestId("detail-tab-link-prompts").click();
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/prompts$/);
  await expect(page.getByTestId("detail-tab-prompts")).toBeVisible();
  await expect(page.getByTestId("prompt-history-list")).toBeVisible();

  const promptInput = page.getByTestId("prompt-editor-input");
  await expect(promptInput).toHaveValue("Build the React shell.");
  await promptInput.fill("Build the React shell with a real routed detail layout.");
  await page.getByTestId("request-save-and-regenerate").click();
  await expect(page.getByTestId("prompt-regenerate-confirmation")).toBeVisible();

  await page.getByTestId("keep-editing-prompt").click();
  await expect(page.getByTestId("prompt-regenerate-confirmation")).toHaveCount(0);

  await page.getByTestId("request-save-and-regenerate").click();
  await expect(page.getByTestId("prompt-regenerate-confirmation")).toBeVisible();
  await page.getByTestId("discard-prompt-changes").click();
  await expect(promptInput).toHaveValue("Build the React shell.");

  await promptInput.fill("Build the React shell with a real routed detail layout.");
  await page.getByTestId("request-save-and-regenerate").click();
  await page.getByTestId("confirm-save-and-regenerate").click();
  await expect(page.getByTestId("prompt-regeneration-success")).toBeVisible();
  await expect(promptInput).toHaveValue("Build the React shell with a real routed detail layout.");

  await page.getByTestId("detail-tab-link-actions").click();
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/actions$/);
  await expect(page.getByTestId("detail-tab-actions")).toBeVisible();
  await expect(page.getByTestId("action-trigger-start-run")).toBeVisible();
  await page.getByTestId("action-trigger-start-run").click();
  await expect(page.getByTestId("action-confirm-start-run")).toBeVisible();
  await page.getByTestId("action-confirm-button-start-run").click();
  await expect(page.getByTestId("action-success-start-run")).toBeVisible();

  await page.getByTestId("detail-tab-link-provenance").click();
  await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/provenance$/);
  await expect(page.getByTestId("detail-tab-provenance")).toBeVisible();
});
