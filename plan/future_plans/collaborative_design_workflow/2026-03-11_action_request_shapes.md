# Action Request Shapes

## Purpose

Define draft mutation/request shapes for the future collaborative-design action surfaces.

This is a working draft.

## Covered Actions

This note covers likely request bodies for:

- review submission
- requirement confirmation
- revision request
- approval
- stop with known gaps
- escalation

## Design Rule

Every significant human decision should become an explicit structured action, not an ambiguous blob of chat text.

## Draft `submit review` Request

### Purpose

Record operator answers to the review questionnaire for the current round.

### Suggested shape

```json
{
  "round": 2,
  "answers": {
    "page_purpose": "Allow users to update their profile and password.",
    "required_sections": [
      "profile summary",
      "password update"
    ],
    "required_fields": [
      "display_name",
      "email",
      "current_password"
    ],
    "style_direction": [
      "professional",
      "clean"
    ],
    "avoidances": [
      "dense form layout"
    ],
    "device_priority": [
      "mobile",
      "desktop"
    ]
  },
  "freeform_notes": "Keep the save button easy to find."
}
```

## Draft `confirm requirements` Request

### Purpose

Record whether the synthesized requirement summary is accepted.

### Suggested shape

```json
{
  "round": 2,
  "requirement_capture_id": "node_123_round_2",
  "decision": "confirm",
  "corrections": []
}
```

Possible `decision` values:

- `confirm`
- `correct`
- `reject`

## Draft `request revision` Request

### Purpose

Ask for another revision after reviewing the updated draft.

### Suggested shape

```json
{
  "round": 2,
  "reason_summary": "The structure is close but the password section still feels too cramped.",
  "updated_constraints": {
    "priority_content": [
      "save button above fold"
    ],
    "avoidances": [
      "cramped password section"
    ]
  }
}
```

## Draft `approve` Request

### Purpose

Record operator approval of the current design round.

### Suggested shape

```json
{
  "round": 2,
  "decision": "approve",
  "approval_summary": "Approved for the current scope."
}
```

## Draft `stop with known gaps` Request

### Purpose

Stop the loop while recording what remains imperfect.

### Suggested shape

```json
{
  "round": 2,
  "decision": "stop_with_known_gaps",
  "remaining_gaps": [
    "Mobile spacing still needs polish later.",
    "Avatar upload is intentionally deferred."
  ]
}
```

## Draft `escalate` Request

### Purpose

Move the work out of the simple task-level loop into a larger redesign or planning effort.

### Suggested shape

```json
{
  "round": 2,
  "decision": "escalate",
  "reason": "Requirements conflict across rounds and need a wider redesign."
}
```

## Recommended Next Step

The next useful companion note would be an artifact taxonomy note so these actions and responses point to a stable set of artifact kinds.
