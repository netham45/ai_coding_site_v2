import { apiClient } from "./client.js";

export function getNodeActions(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/actions`);
}

export function startNodeRun(nodeId) {
  return apiClient.post("/node-runs/start", { node_id: nodeId });
}

export function pauseNodeRun(nodeId) {
  return apiClient.post("/nodes/pause", { node_id: nodeId });
}

export function resumeNodeRun(nodeId) {
  return apiClient.post("/nodes/resume", { node_id: nodeId });
}

export function attachNodeSession(nodeId) {
  return apiClient.post("/sessions/attach", { node_id: nodeId });
}

export function resumeNodeSession(nodeId) {
  return apiClient.post("/sessions/resume", { node_id: nodeId });
}

export function providerResumeNodeSession(nodeId) {
  return apiClient.post("/sessions/provider-resume", { node_id: nodeId });
}

export function reconcileNodeChildren(nodeId, decision) {
  return apiClient.post(`/nodes/${nodeId}/children/reconcile`, { decision });
}
