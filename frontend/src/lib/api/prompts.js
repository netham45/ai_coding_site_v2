import { apiClient } from "./client.js";

export function getPromptHistory(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/prompt-history`);
}

export function getNodeVersion(versionId) {
  return apiClient.get(`/node-versions/${versionId}`);
}

export function supersedeNode(nodeId, payload) {
  return apiClient.post(`/nodes/${nodeId}/supersede`, payload);
}

export function regenerateNode(nodeId) {
  return apiClient.post(`/nodes/${nodeId}/regenerate`, {});
}
