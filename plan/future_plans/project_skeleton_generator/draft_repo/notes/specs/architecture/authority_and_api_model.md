# Authority And API Model

## Purpose

Define which subsystem is authoritative for live decisions and how other surfaces should inspect or request changes.

## Starter Invariants

- durable state should have one clear source of truth
- operator and AI surfaces should not mutate critical state by bypassing the authority layer
- browser or CLI surfaces should expose bounded actions rather than reimplementing authority logic
- recovery-critical decisions should be inspectable after failure

## Questions To Resolve Early

- what owns live state transitions
- what may request versus decide a mutation
- what audit records must exist before and after sensitive actions
