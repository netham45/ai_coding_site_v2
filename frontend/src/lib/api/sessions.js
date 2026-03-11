import { apiClient } from "./client.js";

export function getSessions(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/sessions`);
}
