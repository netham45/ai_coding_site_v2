import { apiClient } from "./client.js";

export function getSummaryHistory(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/summary-history`);
}
