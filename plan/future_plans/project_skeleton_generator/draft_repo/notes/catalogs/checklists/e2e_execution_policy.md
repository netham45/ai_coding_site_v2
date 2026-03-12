# E2E Execution Policy

## Purpose

Explain how the repository treats real end-to-end proof.

## Starter Policy

- bounded tests are required during initial implementation
- real E2E tests are required before final completion claims for real runtime behavior
- E2E targets must be mapped explicitly from feature or flow docs
- capability-gated E2E tests are acceptable when the capability requirement is explicit
- serial-only test behavior caused by shared mutable state is a defect

## Initial Expectation

The starter repo should name at least one real runtime narrative early, even if the E2E itself is still future work.
