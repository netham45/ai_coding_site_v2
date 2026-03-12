# Future Flow: Unblock Or Mark Not Applicable

## Purpose

Clear a blocked checklist item when its unblock conditions are met, or explicitly mark an item `not_applicable` through bounded authority surfaces.

## When Used

- a blocked item has become runnable
- an item is determined not to apply for this checklist instance

## Main Runtime Steps

1. inspect blocked or pending item
2. verify unblock conditions or `not_applicable` eligibility
3. persist the unblock or `not_applicable` decision
4. reevaluate legal next item selection

## Invariants

- blocked items retain structured blockers until cleared
- `not_applicable` requires an explicit reason
- illegal bypass of dependencies is not allowed
- orchestrator remains authoritative for next-item activation

## Main Surfaces

- daemon mutation validation
- CLI or website bounded item actions
- checklist persistence

## Main Outcome

Checklist state changes honestly and the next legal item becomes inspectable.
