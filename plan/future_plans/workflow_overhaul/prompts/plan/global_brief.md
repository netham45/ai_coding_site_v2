Role
- You are receiving the compiled plan briefing for node `{{node_id}}`.
- This prompt is a briefing contract for a non-leaf plan node.
- It tells the receiving session how to interpret the compiled task catalog.

Objective
- Convey the authoritative task structure, artifact ownership, and proof expectations for the current plan.

Lifecycle Position
- This briefing is consumed before or during task planning and execution.
- It assumes compile has already frozen the selected profile, effective layout, required child-role coverage, and completion restrictions.
- It exists to prevent plan-level reinterpretation or skipped task decomposition.

Inputs
- selected plan workflow profile
- selected or generated `task` layout definition
- plan goal
- rationale
- artifact targets
- acceptance criteria
- repository-update obligations
- verification obligations
- completion restrictions
- future blocked-step and next-legal-step metadata

Allowed Actions
- Use the briefing as authoritative task-planning context.
- Inspect task rationale, artifact ownership, verification commands, and dependencies.
- Trigger explicit replan or layout-replacement paths if the task structure is wrong.

Forbidden Actions
- Do not silently invent, delete, or redefine tasks.
- Do not treat this briefing as optional guidance.
- Do not use it to justify skipping task creation or completion predicates.

Expected Result
- The briefing should include:
  - plan profile name and purpose
  - overall plan goal
  - required child-role coverage if applicable
  - layout compatibility notes
  - one entry per selected task with role, rationale, artifacts, updates, verification commands, dependencies, and acceptance
  - balance constraints and completion restrictions

Completion Conditions
- The receiving session can treat the compiled task catalog as authoritative.
- The briefing is sufficient to explain why each task exists and what it must prove or change.

Escalation Or Failure
- If the briefing is inconsistent with the selected layout or profile, treat that as a compiler or source-definition problem.
- Do not smooth over the inconsistency through reinterpretation.

Response Contract
- No standalone JSON response is required by this briefing prompt.
- Any structured output belongs to the decomposition or task-execution prompt that consumes this briefing.
