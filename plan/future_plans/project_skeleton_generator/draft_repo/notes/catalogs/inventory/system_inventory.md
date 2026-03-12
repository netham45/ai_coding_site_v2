# System Inventory

## Purpose

Name the repository's primary systems and their responsibilities.

## Starter Systems

- Database: durable source of truth for state, history, and recovery-critical records.
- CLI: human and AI operational command surface.
- Daemon or backend: live runtime authority and state transition enforcement.
- Config or YAML: declarative structure and policy, not hidden runtime authority.
- Prompts: first-class execution and review assets when AI behavior is part of the system.
- Website UI: browser operator surface when the product includes one.

## Project-Specific Decisions To Fill In

- which systems are in scope now
- which systems are planned later
- which systems are not applicable
- chosen stack decisions for each active system
- stack choices that remain undecided and must be resolved during genesis or architecture

Related note:

- `notes/specs/architecture/stack_decision_record.md`
