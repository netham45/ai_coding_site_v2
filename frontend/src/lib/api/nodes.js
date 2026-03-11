import { apiClient } from "./client.js";

export function getNodeOverview(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/summary`);
}

export function getNodeLineage(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/lineage`);
}

export function getNodeSources(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/sources`);
}

export function getNodeRationale(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/rationale`);
}
