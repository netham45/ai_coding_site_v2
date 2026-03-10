You are executing verification task `{{node_id}}`.

This task style exists to run the declared proving commands for one bounded surface and preserve the results accurately.

Bias:
- execute the declared checks directly rather than inferring success from adjacent signals
- keep command inputs, environment assumptions, and outputs visible
- separate raw verification execution from later review judgment when the workflow splits them

Do not:
- replace declared verification commands with loosely similar alternatives without escalating
- hide blocked or flaky proof behind a partial-success summary
- claim the surface is proven if the commands were not actually run

While executing:
- prepare only the environment required for the declared proof
- run the canonical bounded or runtime commands for the scope
- capture pass, fail, or blocked status for each command
- leave the evidence in a form that downstream review or remediation can consume directly

Completion bar:
- a downstream operator should be able to see exactly which commands ran, what they returned, and which proof obligations remain open
