# Design Rules And Enforcement

## Purpose

Capture the stricter design-system layer that should accompany the collaborative-design workflow if it is meant to help operators who do not have strong UI-design instincts.

This note is still exploratory.

## Core Recommendation

The future feature should not rely on the AI "having taste."

It should rely on:

- global design rules
- explicit page-level requirements
- narrow override rules
- strict verification that catches drift

The design workflow is safer if it behaves like a constrained system rather than a free-form aesthetic conversation.

## Why This Matters

Without design rules, collaborative design can degrade into:

- inconsistent spacing
- inconsistent typography
- random component variants
- pages that individually look acceptable but do not belong to one product
- revisions that satisfy one review round while breaking earlier conventions

For an operator with little design experience, the system should reduce the number of subjective decisions that must be made manually.

## Proposed Design Policy Layers

### Layer 1: Global Design Rules

Project-level rules that should apply by default across pages and components.

Examples:

- spacing scale
- typography scale
- color tokens
- radius and shadow rules
- button, input, form, and card variants
- breakpoint model
- density posture
- accessibility floor
- forbidden patterns

### Layer 2: Page Or Task Requirements

Requirements specific to the page or component currently under design.

Examples:

- required sections
- required fields
- required actions
- information priority
- special visual emphasis
- device priority

### Layer 3: Explicit Overrides

If a page needs to break a global rule, that should be visible and intentional.

The future system should require:

- an explicit override declaration
- a reason
- inspection surfaces that show the override
- tests that fail when an override is implicit rather than declared

## Where These Rules Would Live

### YAML

This layer should likely remain primarily declarative.

Possible future assets:

- project design-rule definitions
- allowed component variant catalogs
- forbidden-pattern declarations
- responsive breakpoint policies
- page-level override declarations

### Daemon And Compiler

Code should own:

- inheritance resolution
- override legality
- compile-time freezing of effective design policy
- completion gating when required design artifacts are missing
- operator-visible reporting of effective rules and overrides

### Prompts

Prompts should consume the effective rules.

They should not be the sole place where the rules exist.

The AI should be told:

- which rules are global defaults
- which page-specific requirements are mandatory
- which overrides are approved
- which patterns are forbidden

### CLI And Operator Surfaces

Operators should be able to inspect:

- current effective design rules
- page-specific requirements
- approved overrides
- failed verification checks
- reasons a design task cannot claim completion

## Suggested Verification Layers

The real feature should be tested at multiple layers.

### Document Or Config Validation

Validate:

- required design-rule fields exist
- allowed values use approved vocabulary
- references to tokens, components, and variants are valid

### Static Or Source Checks

Validate:

- approved tokens or component APIs are used
- forbidden classes or inline styles are rejected where policy forbids them
- undeclared overrides are rejected

### Rendered UI Checks

Validate:

- required fields and sections exist
- breakpoint behavior matches policy
- accessibility attributes are present
- important layout conventions hold in the rendered output

### E2E Or Browser Checks

Validate:

- flows remain usable
- required actions are reachable
- responsive behavior survives real interaction
- visual regressions or major layout drift are detectable

### Drift Checks

Validate:

- page-level deviations from the global rules are declared
- deviations are justified
- silent design drift does not accumulate over time

## Implications For The Collaborative Design Profile

If this stricter layer is adopted, `task.collaborative_design` should eventually include awareness of:

- inherited design rules
- required page-specific requirement artifacts
- explicit override artifacts
- mandatory verification categories beyond generic bounded tests

That may mean the final profile grows additional fields such as:

- `required_design_policy_inputs`
- `allowed_override_categories`
- `required_design_verification`

## Relationship To Workflow Overhaul

This note reinforces why collaborative design belongs after `workflow_overhaul/`.

The workflow-overhaul model is what makes it possible to express:

- profile-specific required artifacts
- profile-specific required verification
- runtime-visible completion restrictions
- richer inspection surfaces for operators and AI contributors

Without that machinery, design rules would likely collapse back into undocumented prompt advice.

## Relationship To Frontend Website UI

If the future browser UI becomes real, it could become a useful review surface for these rules.

Examples:

- showing the effective design policy for the current page
- showing override warnings
- showing pending review gates
- showing design-verification failures

But the browser UI is not the source of truth.

The source of truth should remain declarative rules plus daemon-enforced runtime behavior.

## Recommended Next Planning Step

The next useful planning artifact after this note would be a draft schema for:

- global design rules
- page-level design requirements
- explicit override records
- design-verification categories
