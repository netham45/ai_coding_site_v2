import { spawn } from "node:child_process";
import { expect, test } from "@playwright/test";
import { apiStorageKeys } from "../../src/lib/api/client.js";

function waitForMockDaemon(child, port) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error("Timed out waiting for mock daemon.")), 10_000);

    child.stdout.on("data", (chunk) => {
      const text = chunk.toString();
      if (text.includes(`listening:${port}`)) {
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

async function withScenario(testInfo, scenarioId, port, run) {
  const token = "scenario-token";
  const child = spawn("node", ["./mock-daemon/server.mjs"], {
    cwd: new URL("../../", import.meta.url),
    env: {
      ...process.env,
      MOCK_DAEMON_SCENARIO: scenarioId,
      MOCK_DAEMON_TOKEN: token,
      MOCK_DAEMON_PORT: String(port),
    },
    stdio: ["ignore", "pipe", "inherit"],
  });

  await waitForMockDaemon(child, port);

  try {
    await run({
      baseURL: `http://127.0.0.1:${port}/api`,
      token,
      screenshotPath: (name) => testInfo.outputPath(name),
    });
  } finally {
    child.kill("SIGTERM");
  }
}

async function seedApi(page, baseURL, token) {
  await page.addInitScript(
    ({ resolvedBaseURL, resolvedToken, storageKeys }) => {
      window.localStorage.setItem(storageKeys.baseURL, resolvedBaseURL);
      window.localStorage.setItem(storageKeys.token, resolvedToken);
    },
    {
      resolvedBaseURL: baseURL,
      resolvedToken: token,
      storageKeys: apiStorageKeys,
    },
  );
}

test("empty project catalog is browser-proven and captured for visual review", async ({ page }, testInfo) => {
  await withScenario(testInfo, "empty_project_catalog", 7792, async ({ baseURL, token, screenshotPath }) => {
    await seedApi(page, baseURL, token);
    await page.goto("/projects");

    await expect(page.getByTestId("page-projects-index")).toBeVisible();
    await expect(page.getByText("No projects found")).toBeVisible();
    await page.screenshot({ path: screenshotPath("empty-project-catalog.png"), fullPage: true });
  });
});

test("top-level creation validation failure is browser-proven", async ({ page }) => {
  await withScenario({ outputPath: () => "" }, "top_level_create_failure", 7793, async ({ baseURL, token }) => {
    await seedApi(page, baseURL, token);
    await page.goto("/projects/repo_alpha");

    await page.getByTestId("top-level-kind-select").selectOption("epic");
    await page.getByTestId("top-level-title-input").fill("Website UI bootstrap");
    await page.getByTestId("top-level-prompt-input").fill("Create the initial website UI workflow.");
    await page.getByTestId("create-node-trigger").click();
    await page.getByTestId("confirm-create-node").click();

    await expect(page.getByText("Unable to create node")).toBeVisible();
    await expect(page.getByText("mock top-level creation validation failure")).toBeVisible();
  });
});

test("live candidate prompt block and browser back-forward behavior are proven", async ({ page }, testInfo) => {
  await withScenario(testInfo, "prompt_candidate_blocked", 7794, async ({ baseURL, token, screenshotPath }) => {
    await seedApi(page, baseURL, token);
    await page.goto("/projects/repo_alpha/nodes/node-task-1/prompts");

    await expect(page.getByTestId("detail-tab-prompts")).toBeVisible();
    await expect(page.getByTestId("prompt-live-candidate-notice")).toBeVisible();
    await expect(page.getByTestId("request-save-and-regenerate")).toBeDisabled();
    await page.screenshot({ path: screenshotPath("prompt-live-candidate-blocked.png"), fullPage: true });

    await page.getByTestId("detail-tab-link-runs").click();
    await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/runs$/);
    await page.goBack();
    await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/prompts$/);
    await expect(page.getByTestId("prompt-live-candidate-notice")).toBeVisible();
    await page.goForward();
    await expect(page).toHaveURL(/\/projects\/repo_alpha\/nodes\/node-task-1\/runs$/);
  });
});

test("representative loading, empty, and error states are browser-proven across shared surfaces", async ({ page }) => {
  await withScenario({ outputPath: () => "" }, "shared_state_matrix", 7802, async ({ baseURL, token }) => {
    await seedApi(page, baseURL, token);

    await page.goto("/projects");
    await expect(page.getByText("Loading project catalog.")).toBeVisible();
    await expect(page.getByTestId("project-link-repo_alpha")).toBeVisible();

    await page.goto("/projects/repo_alpha/nodes/node-root/overview");
    await expect(page.getByText("Loading project bootstrap.")).toBeVisible();
    await expect(page.getByTestId("tree-sidebar")).toBeVisible();

    await page.goto("/projects/repo_alpha/nodes/node-loading-actions/actions");
    await expect(page.getByText("Loading actions.")).toBeVisible();
    await expect(page.getByTestId("action-card-pause-run")).toBeVisible();

    await page.goto("/projects/repo_alpha/nodes/node-empty-actions/actions");
    await expect(page.getByTestId("empty-state")).toContainText("No actions");

    await page.goto("/projects/repo_alpha/nodes/node-error-actions/actions");
    await expect(page.getByTestId("error-state")).toContainText("Could not load actions");
    await expect(page.getByText("mock action catalog failure")).toBeVisible();

    await page.goto("/projects/repo_alpha/nodes/node-empty-prompts/prompts");
    await expect(page.getByText("Loading prompts.")).toBeVisible();
    await expect(page.getByTestId("empty-state")).toContainText("No prompt history");

    await page.goto("/projects/repo_alpha/nodes/node-error-prompts/prompts");
    await expect(page.getByTestId("error-state")).toContainText("Could not load prompt history");
    await expect(page.getByText("mock prompt history failure")).toBeVisible();
  });
});

test("tree error state is browser-proven", async ({ page }) => {
  await withScenario({ outputPath: () => "" }, "tree_error_matrix", 7803, async ({ baseURL, token }) => {
    await seedApi(page, baseURL, token);
    await page.goto("/projects/repo_alpha/nodes/node-root/overview");

    await expect(page.getByTestId("error-state")).toContainText("Unable to load hierarchy tree");
    await expect(page.getByText("mock tree load failure")).toBeVisible();
  });
});
