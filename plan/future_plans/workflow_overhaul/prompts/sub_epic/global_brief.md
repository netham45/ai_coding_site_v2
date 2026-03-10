You are receiving the compiled phase briefing for node `{{node_id}}`.

This briefing is a compiler-generated artifact derived from:
- the selected phase workflow profile
- the selected or generated `plan` layout definition
- the phase goal, rationale, and acceptance criteria
- any role-coverage, repository-update, verification, or completion rules attached to the selected profile

Purpose:
- show the phase session the exact execution slices it is expected to create or use
- explain why each plan exists
- expose dependencies, artifact targets, and proving expectations before plan work begins
- prevent phase-local reinterpretation from drifting away from the selected profile or layout

This briefing should include:
- phase profile name and purpose
- overall phase goal
- required child-role coverage
- layout compatibility notes for the current phase mode
- one entry per selected plan containing:
  - plan id
  - plan role
  - plan title
  - plan goal
  - plan rationale
  - artifact targets
  - required updates
  - verification targets
  - dependencies
  - acceptance criteria
- any balance constraints or point-budget expectations that matter for the phase
- completion restrictions that matter at the phase layer

Compiler contract:
- this text should be rendered from the effective layout YAML and profile inputs
- it should not be maintained as a second hand-authored parallel summary
- it should be frozen into compiled workflow state for auditability and inspection

Session expectations after receiving this briefing:
- treat the plan catalog as authoritative for the current compiled run
- do not silently invent, delete, or redefine plans without the appropriate replan or layout-replacement path
- use the artifact, dependency, and proving data when deciding whether local changes are legitimate

If this briefing is inconsistent with the selected layout or profile, that is a compiler or source-definition problem, not a prompt-interpretation issue.
