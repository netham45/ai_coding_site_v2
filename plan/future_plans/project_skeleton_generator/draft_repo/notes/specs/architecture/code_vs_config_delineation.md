# Code Vs Config Delineation

## Purpose

Define what belongs in code and what belongs in config or YAML.

## Starter Rule

Config or YAML should define declarative structure and policy.

Code should retain:

- live runtime authority
- safety checks
- state transitions
- recovery behavior
- concurrency control
- mutation legality

## Questions To Resolve Early

- what policy belongs in declarative assets
- what behavior must stay in code
- which runtime decisions are too dynamic or safety-critical for config ownership
