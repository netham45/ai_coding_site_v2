You are receiving the compiled plan briefing for node `{{node_id}}`.

This briefing is a compiler-generated artifact derived from:
- the selected plan workflow profile
- the selected or generated `task` layout definition
- the plan goal, rationale, artifact targets, and acceptance criteria
- any repository-update, verification, or completion rules attached to the selected profile

Purpose:
- show the plan session the exact task work packets it is expected to create or use
- explain why each task exists
- expose artifact ownership, verification commands, and dependencies before task execution begins
- prevent the plan session from inventing a parallel interpretation that diverges from the selected layout

This briefing should include:
- plan profile name and purpose
- overall plan goal
- required child-role coverage if the selected plan profile defines any
- layout compatibility notes for the current plan mode
- one entry per selected task containing:
  - task id
  - task role
  - task title
  - task goal
  - task rationale
  - artifact targets
  - required updates
  - verification commands
  - dependencies
  - acceptance criteria
- any balance constraints or point-budget expectations that matter for the plan
- completion restrictions that matter at the plan layer

Compiler contract:
- this text should be rendered from the effective layout YAML and profile inputs
- it should not be maintained as a second hand-authored parallel summary
- it should be frozen into compiled workflow state for auditability and inspection

Session expectations after receiving this briefing:
- treat the task catalog as authoritative for the current compiled run
- do not silently invent, delete, or redefine tasks without the appropriate replan or layout-replacement path
- use the task artifact ownership and verification data when deciding whether execution is complete

If this briefing is inconsistent with the selected layout or profile, that is a compiler or source-definition problem, not a prompt-interpretation issue.
