import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_REAL_BASE_URL;

if (!baseURL) {
  throw new Error("PLAYWRIGHT_REAL_BASE_URL is required for real-daemon browser tests.");
}

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  outputDir: "test-results-real",
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
