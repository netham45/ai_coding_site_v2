You are defining child `plan` nodes for real-E2E-verification sub-epic `{{node_id}}`.

This delivery band exists to prove the intended runtime behavior through real boundaries rather than bounded-only or simulated proof.

Bias:
- prefer plans that map features or flows explicitly to real proof
- keep environment assumptions, command surfaces, and evidence visible

Do not:
- substitute bounded or mocked proof where real E2E is the contract
- write plans that say only "add tests"
- leave canonical commands or proving scope implicit

Each plan should make explicit:
- which real flow or feature scope it proves
- which boundaries are exercised
- which canonical commands it runs
- what evidence is produced if the proof passes or fails

Closure bar:
- the E2E band must leave explicit proof narratives rather than only raw test files

Return JSON only:
{"status":"OK","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
