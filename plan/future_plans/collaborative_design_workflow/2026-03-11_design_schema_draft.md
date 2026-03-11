# Design Schema Draft

## Purpose

Sketch the future declarative document shapes that would make collaborative design and design-policy enforcement concrete enough to implement later.

This is a working draft, not an adopted schema.

## Main Schema Families

The strongest first-pass schema set is probably:

- `design_rule_definition`
- `design_requirement_capture`
- `design_override_record`
- `design_verification_definition`

These could remain distinct even if some are later embedded or compiled together.

## Family 1: `design_rule_definition`

Purpose:

- define project-level design defaults and forbidden patterns

Draft shape:

```yaml
kind: design_rule_definition
id: default_web_app_ui
name: Default Web App UI Rules
status: draft
scope: project
tokens:
  spacing_scale: [4, 8, 12, 16, 24, 32, 48]
  radius_scale: [4, 8, 12]
  shadow_tokens: [card_sm, popover_md]
  color_tokens:
    surface_primary: neutral_0
    surface_secondary: neutral_50
    text_primary: neutral_950
    accent_primary: blue_600
typography:
  families:
    heading: ui_heading
    body: ui_body
  scale:
    body_sm: 14
    body_md: 16
    heading_md: 24
components:
  button:
    allowed_variants: [primary, secondary, ghost]
    default_radius: 8
  input:
    allowed_variants: [default, inline]
responsive_policy:
  breakpoints:
    sm: 640
    md: 768
    lg: 1024
accessibility:
  min_contrast: "AA"
  require_visible_labels: true
forbidden_patterns:
  - generic unlabeled icon buttons
  - text smaller than body_sm for primary content
```

Required concepts:

- token vocabulary
- typography and spacing posture
- allowed component families and variants
- responsive policy
- accessibility floor
- forbidden patterns

## Family 2: `design_requirement_capture`

Purpose:

- store page- or task-specific design requirements derived from operator review

Draft shape:

```yaml
kind: design_requirement_capture
id: node_123_round_2
status: draft
node_id: 123
target:
  type: page
  name: account_settings
required_sections:
  - profile_summary
  - password_update
required_fields:
  - display_name
  - email
  - current_password
required_actions:
  - save_changes
  - cancel
priority_content:
  - save button above fold
style_direction:
  adjectives: [professional, calm, clean]
references:
  - type: url
    value: https://example.test/reference
avoidances:
  - overly playful illustration
  - dense table-like forms
device_priority:
  - mobile
  - desktop
open_questions:
  - should avatar upload be in scope
approval_state: pending_revision
```

Required concepts:

- target surface
- required UI obligations
- style direction
- references and avoidances
- unresolved questions
- approval state

## Family 3: `design_override_record`

Purpose:

- document exceptions to global design rules

Draft shape:

```yaml
kind: design_override_record
id: page_account_settings_override_1
status: approved
target:
  type: page
  name: account_settings
rule_ref: default_web_app_ui.components.button.allowed_variants
override_category: component_variant_exception
reason: Danger-zone actions need a distinct destructive variant not present globally.
approved_by: operator
linked_requirement_capture: node_123_round_2
expiry: until_global_rule_update
```

Required concepts:

- target
- referenced rule
- override category
- reason
- approval state
- linkage to the triggering requirement or review round

## Family 4: `design_verification_definition`

Purpose:

- define the categories of proof required for a design task or project policy

Draft shape:

```yaml
kind: design_verification_definition
id: collaborative_design_default_checks
status: draft
required_checks:
  - category: document_validation
  - category: token_usage_static_check
  - category: required_fields_render_check
  - category: responsive_render_check
  - category: accessibility_check
  - category: e2e_flow_check
allow_exceptions_only_with_override_record: true
```

## Likely Compilation Model

The compiler would probably freeze an effective design context per node or task:

- inherited global rule set
- current requirement capture
- approved overrides
- required verification categories

That compiled context should become the real execution input.

## Recommended Next Step

If this bundle keeps growing, the next schema note should probably map which of these families should be standalone YAML versus durable database records versus compiled snapshots.
