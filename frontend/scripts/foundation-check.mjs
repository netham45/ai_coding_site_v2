import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import QueryProvider from "../src/lib/query/QueryProvider.js";
import { createApiClient, getRuntimeApiConfig } from "../src/lib/api/client.js";
import { queryKeys } from "../src/lib/query/keys.js";

function FoundationProbe() {
  return createElement("div", { "data-testid": "query-provider-probe" }, "query-ready");
}

const markup = renderToStaticMarkup(
  createElement(
    QueryProvider,
    null,
    createElement(FoundationProbe),
  ),
);

if (!markup.includes('data-testid="query-provider-probe"')) {
  throw new Error("Expected the query provider probe to render.");
}

const mockClient = createApiClient({
  baseURL: "http://example.invalid",
  token: "test-token",
  timeout: 1234,
});

if (mockClient.defaults.baseURL !== "http://example.invalid") {
  throw new Error("Expected the central Axios client to preserve baseURL.");
}

if (mockClient.defaults.timeout !== 1234) {
  throw new Error("Expected the central Axios client to preserve timeout.");
}

const authHeader = queryKeys.nodeOverview("node-123");
if (JSON.stringify(authHeader) !== JSON.stringify(["node", "node-123", "overview"])) {
  throw new Error("Expected stable query-key conventions for node overview.");
}

globalThis.window = {
  localStorage: {
    getItem(key) {
      if (key === "aicoding.apiBaseUrl") {
        return "http://storage.invalid/api";
      }
      if (key === "aicoding.apiToken") {
        return "storage-token";
      }
      return null;
    },
  },
  __AICODING_DAEMON_BOOTSTRAP__: {
    apiBaseUrl: "/api",
    apiToken: "daemon-token",
  },
};

const runtimeConfig = getRuntimeApiConfig();
if (runtimeConfig.baseURL !== "/api" || runtimeConfig.token !== "daemon-token") {
  throw new Error("Expected daemon-served bootstrap config to override browser storage defaults.");
}

console.log("foundation-check: ok");
