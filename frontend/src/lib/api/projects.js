import { apiClient } from "./client.js";

export function listProjects() {
  return apiClient.get("/projects");
}

export function getProjectBootstrap(projectId) {
  return apiClient.get(`/projects/${projectId}/bootstrap`);
}

export function listNodeKinds() {
  return apiClient.get("/node-kinds");
}
