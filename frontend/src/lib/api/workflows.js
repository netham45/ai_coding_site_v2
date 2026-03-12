import { apiClient } from "./client.js";

export function getCurrentWorkflow(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/workflow/current`);
}

export function getCurrentSubtask(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/subtasks/current`);
}

export function getCurrentSubtaskPrompt(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/subtasks/current/prompt`);
}

export function getCurrentSubtaskContext(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/subtasks/current/context`);
}

export function getSubtaskAttempts(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/subtask-attempts`);
}

export function getSubtaskAttempt(attemptId) {
  return apiClient.get(`/subtask-attempts/${attemptId}`);
}

export function getRunProgress(nodeId) {
  return apiClient.get(`/node-runs/${nodeId}`);
}

export function getRuns(nodeId) {
  return apiClient.get(`/nodes/${nodeId}/runs`);
}
