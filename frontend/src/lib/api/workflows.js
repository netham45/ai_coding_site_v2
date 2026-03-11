import { apiClient } from "./client.js";

export function getCurrentWorkflow(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/workflow/current`);
}

export function getRunProgress(nodeId) {
  return apiClient.get(`/node-runs/${nodeId}`);
}

export function getRuns(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/runs`);
}
