import axios from "axios";
import { normalizeApiError } from "./errors.js";

const DEFAULT_TIMEOUT_MS = 15_000;
const DEFAULT_API_BASE_URL = "/api";
const API_BASE_URL_STORAGE_KEY = "aicoding.apiBaseUrl";
const API_TOKEN_STORAGE_KEY = "aicoding.apiToken";
const DAEMON_BOOTSTRAP_GLOBAL = "__AICODING_DAEMON_BOOTSTRAP__";

function readBrowserStorage(key) {
  if (typeof window === "undefined" || !window.localStorage) {
    return null;
  }
  return window.localStorage.getItem(key);
}

function readDaemonBootstrap() {
  if (typeof window === "undefined") {
    return null;
  }
  return window[DAEMON_BOOTSTRAP_GLOBAL] ?? null;
}

export function getRuntimeApiConfig() {
  const env = typeof import.meta !== "undefined" ? (import.meta.env ?? {}) : {};
  const bootstrap = readDaemonBootstrap();
  const baseURL = bootstrap?.apiBaseUrl ?? readBrowserStorage(API_BASE_URL_STORAGE_KEY) ?? env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;
  const token = bootstrap?.apiToken ?? readBrowserStorage(API_TOKEN_STORAGE_KEY) ?? env.VITE_API_TOKEN ?? null;
  return {
    baseURL,
    token,
  };
}

export function createApiClient(options = {}) {
  const client = axios.create({
    baseURL: options.baseURL ?? getRuntimeApiConfig().baseURL,
    timeout: options.timeout ?? DEFAULT_TIMEOUT_MS,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  client.interceptors.request.use((config) => {
    const runtime = getRuntimeApiConfig();
    const token = options.token ?? runtime.token ?? null;
    config.baseURL = options.baseURL ?? runtime.baseURL;

    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    (error) => Promise.reject(normalizeApiError(error)),
  );

  return client;
}

export const apiClient = createApiClient();
export const apiStorageKeys = {
  baseURL: API_BASE_URL_STORAGE_KEY,
  token: API_TOKEN_STORAGE_KEY,
};
