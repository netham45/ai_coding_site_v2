Overlay Role Delta
- Use with `epic/base.md`.
- This overlay turns the epic into a review, remediation, and confirmation root.
- Prioritize auditability and operator clarity over speculative redesign.

Overlay Objective Delta
- Decompose review work into explicit scope-freeze, review, remediation, and re-review phases.

Profile-Specific Inputs
- `required_child_roles` should usually include:
  - `scope_freeze`
  - `review`
  - `remediation`
  - `re_review`

Additional Forbidden Actions
- Do not collapse review and remediation into one vague band without reason.
- Do not create implementation phases disconnected from discovered issues.
- Do not allow findings to disappear into summary prose.
- Do not let the epic absorb substantive remediation that should be delegated.

Profile-Specific Expected Result
- A phase child set whose usual roles include:
  - `scope_freeze`
  - `review`
  - `remediation`
  - `re_review`

Profile-Specific Completion Conditions
- The phase set preserves evidence gathering, remediation, and confirmation as inspectable bands.
- Each phase has clear closure expectations.
- Remediation remains traceable to findings.
