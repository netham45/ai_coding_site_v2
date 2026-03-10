You are receiving the compiled epic briefing for node `{{node_id}}`.

This briefing is a compiler-generated artifact derived from:
- the selected epic workflow profile
- the selected or generated `phase` layout definition
- the epic goal and acceptance criteria
- any required role-coverage, balance, or closure rules attached to the profile

Purpose:
- show the epic session the exact delivery bands it is expected to create or use
- explain why each phase exists
- expose dependencies, required outputs, and proof expectations before downstream work starts
- prevent the epic session from inventing a parallel interpretation that diverges from the chosen layout

This briefing should include:
- epic profile name and purpose
- overall epic goal
- required child-role coverage
- layout compatibility notes, including why this layout is valid for the current epic mode
- one entry per selected phase containing:
  - phase id
  - phase role
  - phase title
  - phase goal
  - phase rationale
  - expected outputs
  - required updates
  - verification targets
  - dependencies
  - acceptance criteria
- any balance constraints or point-budget expectations if the profile uses them
- completion restrictions that matter at the epic layer

Compiler contract:
- this text should be rendered from the effective layout YAML and profile inputs
- it should not be maintained as a second hand-authored parallel summary
- it should be frozen into compiled workflow state for auditability and inspection

Session expectations after receiving this briefing:
- treat the phase catalog as authoritative for the current compiled run
- do not silently invent, delete, or redefine phases without going through the appropriate replan or layout-replacement path
- use the rationale, dependency data, and mode/layout compatibility data when deciding whether a proposed change is legitimate

If this briefing is inconsistent with the selected layout or profile, that is a compiler or source-definition problem, not a prompt-interpretation issue.
