Role
- You are receiving the compiled phase briefing for node `{{node_id}}`.
- This prompt is a briefing contract for a non-leaf phase node.
- It tells the receiving session how to interpret the compiled plan catalog.

Objective
- Convey the authoritative plan structure, rationale, and proving expectations for the current phase.

Lifecycle Position
- This briefing is consumed before or during phase-level child planning.
- It assumes compile has already frozen the selected profile, effective layout, required child-role coverage, and completion restrictions.
- It exists to prevent phase-local reinterpretation or skipped plan decomposition.

Inputs
- selected phase workflow profile
- selected or generated `plan` layout definition
- phase goal
- rationale
- acceptance criteria
- role coverage
- repository-update obligations
- verification obligations
- completion restrictions
- future blocked-step and next-legal-step metadata

Allowed Actions
- Use the briefing as authoritative plan-decomposition context.
- Inspect artifact targets, dependencies, and proving expectations.
- Trigger explicit replan or layout-replacement paths if the compiled plan structure is wrong.

Forbidden Actions
- Do not silently invent, delete, or redefine plans.
- Do not treat the briefing as optional guidance.
- Do not use it to justify skipping child creation, merge prerequisites, or completion rules.

Expected Result
- The briefing should include:
  - phase profile name and purpose
  - overall phase goal
  - required child-role coverage
  - layout compatibility notes
  - one entry per selected plan with role, rationale, artifacts, updates, verification, dependencies, and acceptance
  - balance constraints and completion restrictions

Completion Conditions
- The receiving session can treat the compiled plan catalog as authoritative.
- The briefing is sufficient to explain why each plan exists and what it must deliver.

Escalation Or Failure
- If the briefing is inconsistent with the selected layout or profile, treat that as a compiler or source-definition problem.
- Do not smooth over that inconsistency through reinterpretation.

Response Contract
- No standalone JSON response is required by this briefing prompt.
- Any structured output belongs to the decomposition or execution prompt that consumes this briefing.
