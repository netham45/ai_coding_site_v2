You are executing real-E2E task `{{node_id}}`.

This task style exists to prove one runtime flow or user-visible behavior through real boundaries rather than bounded-only or simulated checks.

Bias:
- keep the proving scope explicit
- make environment assumptions, canonical commands, and evidence visible
- treat the proof narrative as part of the deliverable, not an afterthought

Do not:
- substitute mocked or bounded-only proof where real E2E is the contract
- leave the runtime boundary or exercised flow implicit
- describe success without preserving the command and observed outcome

While executing:
- prepare only the environment needed for the declared real proof
- run the canonical E2E command set
- capture what flow was exercised and what evidence the run produced
- fail clearly if the environment or runtime behavior does not support the proof

Completion bar:
- the result should show exactly what real flow was proven, how it was proven, and what broke if the proof failed
