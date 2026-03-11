export const queryKeys = {
  projects: () => ["projects"],
  nodeKinds: () => ["node-kinds"],
  projectBootstrap: (projectId) => ["project", projectId, "bootstrap"],
  projectTree: (projectId, rootNodeId) => ["project", projectId, "tree", rootNodeId],
  nodeOverview: (nodeId) => ["node", nodeId, "overview"],
  nodeWorkflow: (nodeId) => ["node", nodeId, "workflow"],
  nodeRuns: (nodeId) => ["node", nodeId, "runs"],
  nodePrompts: (nodeId) => ["node", nodeId, "prompts"],
  nodeSummaries: (nodeId) => ["node", nodeId, "summaries"],
  nodeSessions: (nodeId) => ["node", nodeId, "sessions"],
  nodeProvenance: (nodeId) => ["node", nodeId, "provenance"],
  nodeActions: (nodeId) => ["node", nodeId, "actions"],
};
