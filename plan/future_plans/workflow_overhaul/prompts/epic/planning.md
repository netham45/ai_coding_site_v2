Overlay Role Delta
- Use with `epic/base.md`.
- This overlay turns the epic into a planning root rather than an execution root.
- Keep downstream implementation waiting on explicit planning closure.

Overlay Objective Delta
- Turn rough intent into explicit planning phases that leave downstream implementation ready to begin.

Profile-Specific Inputs
- `required_child_roles` should usually include:
  - `requirements`
  - `architecture`
  - `planning`
  - `verification_mapping`

Additional Forbidden Actions
- Do not create implementation-heavy phases as the default.
- Do not produce phase names that merely restate the user prompt.
- Do not skip note, checklist, or command-definition obligations.
- Do not satisfy unresolved delivery bands by performing downstream execution at the epic tier.

Profile-Specific Expected Result
- A phase child set whose usual roles include:
  - `requirements`
  - `architecture`
  - `planning`
  - `verification_mapping`

Profile-Specific Completion Conditions
- Each phase resolves a distinct planning need.
- Outputs and acceptance criteria are concrete enough to know when planning is done.
- Downstream implementation should not need to rediscover core architecture or verification assumptions.
