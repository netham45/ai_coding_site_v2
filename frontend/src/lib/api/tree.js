import { apiClient } from "./client.js";

export function getTree(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/tree`);
}
