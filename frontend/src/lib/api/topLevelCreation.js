import { apiClient } from "./client.js";

export function createTopLevelNode(projectId, payload) {
  return apiClient.post(`/projects/${projectId}/top-level-nodes`, payload);
}
