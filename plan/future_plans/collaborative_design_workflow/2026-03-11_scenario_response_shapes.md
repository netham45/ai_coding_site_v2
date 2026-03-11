# Scenario Response Shapes

## Purpose

Define draft daemon/API response shapes for the future collaborative-design scenario surfaces so review-state reporting is concrete instead of hand-wavy.

This is a working draft.

## Covered Surfaces

This note covers likely future responses for:

- design status
- scenario status
- design artifacts
- design verification

## Design Rules

### Rule 1

Return operational state, not just static metadata.

Callers need to know:

- whether the app is actually running
- whether the target review state is ready
- whether human input is blocking progress

### Rule 2

Separate effective runtime mode from scenario definition.

The response should say both:

- what the scenario intends
- what mode is currently active

### Rule 3

Expose artifact references directly.

The caller should not need to infer where screenshots, traces, or logs live.

### Rule 4

Expose the next required action explicitly.

The design-review loop should always report what is blocking forward progress.

## Draft `design status` Response

### Purpose

Tell the caller the current collaborative-design state for one node.

### Suggested shape

```json
{
  "node_id": "123",
  "workflow_profile": {
    "id": "task.collaborative_design",
    "name": "Collaborative Design Task"
  },
  "review_state": "awaiting_review_input",
  "round": 2,
  "pending_operator_action": {
    "type": "submit_review_answers",
    "summary": "Operator answers are required before requirement synthesis can continue."
  },
  "effective_runtime_mode": {
    "id": "fixture_seeded",
    "name": "Fixture Seeded Backend"
  },
  "active_scenario": {
    "id": "account_settings_default",
    "name": "Account Settings Default"
  },
  "latest_requirement_capture_id": "node_123_round_2",
  "latest_verification_status": "pending",
  "latest_artifact_bundle_id": "artifact_bundle_456"
}
```

Required concepts:

- current review state
- current round
- pending human action
- effective runtime mode
- active scenario
- latest requirement and artifact references

## Draft `scenario status` Response

### Purpose

Tell the caller whether the local app and target UI state are actually ready for review.

### Suggested shape

```json
{
  "node_id": "123",
  "scenario": {
    "id": "account_settings_default",
    "name": "Account Settings Default",
    "entry_strategy": "direct_url"
  },
  "runtime_contract": {
    "id": "web_app_local_dev",
    "name": "Web App Local Dev"
  },
  "runtime_processes": [
    {
      "name": "frontend",
      "status": "ready",
      "base_url": "http://127.0.0.1:3000"
    },
    {
      "name": "backend",
      "status": "ready",
      "base_url": "http://127.0.0.1:4000"
    }
  ],
  "effective_mode": "fixture_seeded",
  "auth_state": "ready",
  "target_url": "http://127.0.0.1:3000/settings/account",
  "review_readiness": {
    "status": "ready",
    "summary": "App is running, auth is available, and the target page has been reached."
  }
}
```

Required concepts:

- scenario identity
- runtime contract identity
- process readiness
- effective mode
- auth readiness
- target URL
- review-readiness status

## Draft `design artifacts` Response

### Purpose

Tell the caller which review artifacts exist for the current round.

### Suggested shape

```json
{
  "node_id": "123",
  "round": 2,
  "artifacts": [
    {
      "kind": "screenshot_desktop",
      "path": "artifacts/design/node_123/round_2/desktop.png"
    },
    {
      "kind": "screenshot_mobile",
      "path": "artifacts/design/node_123/round_2/mobile.png"
    },
    {
      "kind": "playwright_trace",
      "path": "artifacts/design/node_123/round_2/trace.zip"
    },
    {
      "kind": "browser_console",
      "path": "artifacts/design/node_123/round_2/console.json"
    }
  ]
}
```

## Draft `design verification` Response

### Purpose

Tell the caller which design-policy and UI checks have passed or failed.

### Suggested shape

```json
{
  "node_id": "123",
  "round": 2,
  "verification": [
    {
      "category": "token_usage_static_check",
      "status": "passed"
    },
    {
      "category": "required_fields_render_check",
      "status": "failed",
      "summary": "The current_password field is missing from the rendered page."
    },
    {
      "category": "accessibility_check",
      "status": "pending"
    }
  ],
  "completion_gate": {
    "status": "blocked",
    "summary": "Required design verification has not completed successfully."
  }
}
```

## Recommended Next Step

The next useful companion note would be a mutation/request-shape draft for review submission, requirement confirmation, approval, stop, and escalation actions.
