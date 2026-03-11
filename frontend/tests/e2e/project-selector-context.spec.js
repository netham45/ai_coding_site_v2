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
    await run({ baseURL: `http://127.0.0.1:${port}/api`, token, screenshotPath: (name) => testInfo.outputPath(name) });
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

test("project selector shows daemon context and readiness cues", async ({ page }, testInfo) => {
  await withScenario(testInfo, "project_catalog_readiness_problem", 7795, async ({ baseURL, token, screenshotPath }) => {
    await seedApi(page, baseURL, token);
    await page.goto("/projects");

    await expect(page.getByTestId("project-daemon-context")).toBeVisible();
    await expect(page.getByTestId("project-link-repo_alpha")).toBeVisible();
    await expect(page.getByTestId("project-card-repo_broken")).toBeVisible();
    await expect(page.getByText("Directory is not a git repository.")).toBeVisible();
    await page.screenshot({ path: screenshotPath("project-selector-readiness.png"), fullPage: true });

    await page.goto("/projects/repo_broken");
    await expect(page.getByTestId("page-project-detail")).toBeVisible();
    await expect(page.getByText("Project is not bootstrap ready")).toBeVisible();
    await expect(page.getByTestId("top-level-create-form")).toHaveCount(0);
  });
});

test("project selector shows invalid-auth state", async ({ page }) => {
  await withScenario({ outputPath: () => "" }, "project_catalog_single", 7796, async ({ baseURL }) => {
    await seedApi(page, baseURL, "wrong-token");
    await page.goto("/projects");

    await expect(page.getByTestId("projects-auth-invalid")).toBeVisible();
    await expect(page.getByText("The configured bearer token was rejected.")).toBeVisible();
  });
});

test("project selector shows daemon-unreachable state", async ({ page }) => {
  await seedApi(page, "http://127.0.0.1:7797/api", "scenario-token");
  await page.goto("/projects");

  await expect(page.getByTestId("projects-daemon-unreachable")).toBeVisible();
  await expect(page.getByText("The website could not reach the configured daemon API.")).toBeVisible();
});
