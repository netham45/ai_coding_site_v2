import fs from "node:fs";
import { expect, test } from "@playwright/test";

const resultFile = process.env.PLAYWRIGHT_REAL_RESULT_FILE;

test("real daemon served project start boots from selected repo", async ({ page }) => {
  await page.goto("/projects");

  await expect(page.getByTestId("page-projects-index")).toBeVisible();
  await page.getByTestId("project-link-repo_alpha").click();

  await expect(page.getByTestId("page-project-detail")).toBeVisible();
  await expect(page.getByTestId("top-level-create-form")).toBeVisible();

  await page.getByTestId("top-level-kind-select").selectOption("epic");
  await page.getByTestId("top-level-title-input").fill("Website Project Bootstrap Epic");
  await page
    .getByTestId("top-level-prompt-input")
    .fill("Create the website project bootstrap flow from the selected source repo.");
  await page.getByTestId("create-node-trigger").click();
  await page.getByTestId("confirm-create-node").click();

  await page.waitForURL(/\/projects\/repo_alpha\/nodes\/[^/]+\/overview$/);
  await expect(page.getByTestId("page-node-tab")).toBeVisible();
  await expect(page.getByTestId("detail-tab-overview")).toBeVisible();
  await expect(page.getByText("Create the website project bootstrap flow from the selected source repo.")).toBeVisible();

  const match = page.url().match(/\/projects\/repo_alpha\/nodes\/([^/]+)\/overview$/);
  expect(match).not.toBeNull();
  const nodeId = match?.[1] ?? null;
  expect(nodeId).not.toBeNull();

  if (resultFile) {
    fs.writeFileSync(resultFile, JSON.stringify({ nodeId, url: page.url() }), "utf-8");
  }
});
