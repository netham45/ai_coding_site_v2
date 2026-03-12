# Future Flow: Inspect Checklist State

## Purpose

Inspect checklist items, active item, blockers, and prior item results through operator surfaces.

## When Used

- operator wants to understand checklist progress
- AI session needs the current active item contract
- blocked-state diagnosis is required

## Main Runtime Steps

1. request checklist summary
2. inspect active item detail
3. inspect blockers or `not_applicable` reasons where relevant
4. inspect prior item results and evidence

## Invariants

- active item and persisted item statuses agree
- blocker reasons remain inspectable
- `not_applicable` decisions remain inspectable
- reads reflect daemon-owned truth rather than prompt memory

## Main Surfaces

- CLI inspection
- daemon read routes
- website checklist detail view

## Main Outcome

Operator or session can explain the current checklist state and next legal action.
