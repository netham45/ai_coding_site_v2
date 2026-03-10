# Testing Framework Integration Decisions

## Phase

- `plan/features/28_F23_testing_framework_integration.md`

## Decisions

1. Testing results are persisted in a dedicated `test_results` table, while `subtask_attempts.testing_json` caches the latest per-attempt gate summary for current-run inspection and recovery.
2. The daemon interprets `run_tests` subtasks as first-class testing gates and routes outcomes through `workflow advance`, including retry-pending, fail-to-parent, and pause-for-user behavior.
3. Retry behavior is driven by testing-definition retry policy instead of ad hoc command heuristics; the current staged runtime does not yet implement a separate operator override mutation for `allow_override`, so that path pauses the run for explicit operator intervention.
4. Source lineage and compiled workflow source backfill now include testing definitions referenced by tasks, keeping testing-policy inputs audit-visible alongside review and validation inputs.
5. The packaged default node workflows remain unchanged in this phase. Testing is fully implemented for workflows that explicitly include `test_node` or otherwise compile `run_tests`, but default built-in node kinds are not silently expanded yet because that would change the shipped execution ladder before the later finalize/docs slices settle the broader default quality-gate sequence.
6. Performance guardrails were retained but recalibrated slightly for steady-state compile and inspection costs after adding persisted testing results and extra compile inputs; the phase keeps sub-second lookup expectations and low-single-digit-second orchestration/compilation ceilings rather than pretending the earlier cheaper envelope still reflects the actual runtime.
