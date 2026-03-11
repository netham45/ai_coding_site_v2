# Frontend Website UI Final Verification Checklist

## Purpose

Define the final verification questions that should be answered before the website effort is considered fully planned for implementation or later considered flow-proven.

This is a working note, not an implementation plan.

## Verification Questions

### 1. Routes

- Which routes exist?
- Which routes have bounded tests?
- Which routes have Playwright coverage?

### 2. Views

- Which major views exist?
- Which views have loading-state tests?
- Which views have empty-state tests?
- Which views have error-state tests?

### 3. Shared component families

- Are `LoadingState`, `EmptyState`, `ErrorState`, and `StatusBadge` used consistently?
- Do they have bounded tests?

### 4. Actions

- Which v1 actions exist?
- Does each action have a rubric entry?
- Does each action have daemon/API proof?
- Does each action have browser proof when appropriate?

### 5. Tabs

- Does each detail tab have rendering proof?
- Does each meaningful tab have route/deep-link proof?

### 6. Mutation invalidation

- Do create, prompt, action, and session mutations refresh the correct surfaces?
- Are these covered by tests?

### 7. Selector stability

- Are stable `data-testid` conventions used on tested surfaces?
- Are Playwright tests relying on semantic selectors instead of incidental DOM?

### 8. Visual review

- Are screenshot targets defined?
- Are screenshot artifacts retained?
- Are complex screens visually reviewed where assertion-only tests are insufficient?

## Explicit Untested-Flow Audit

The final verification pass should produce an explicit list for:

- untested routes
- untested views
- untested action flows
- untested error or blocked flows
- unreviewed visual states

Goal:

- no unknown gaps

If gaps remain, they should be named explicitly rather than hidden behind broad "tested enough" language.

## Suggested Final Checklist

- project selector covered
- top-level creation covered
- tree rendering covered
- tree navigation covered
- overview covered
- workflow covered
- runs covered
- prompts/regenerate covered
- summaries covered
- sessions covered
- provenance covered
- actions covered
- blocked/error flows covered
- route refresh/back-forward covered
- screenshot review targets captured
- missing-test audit performed

## Rule

This checklist is not satisfied by general confidence.

It is satisfied only by explicit mapping from implemented surfaces to real proof.
