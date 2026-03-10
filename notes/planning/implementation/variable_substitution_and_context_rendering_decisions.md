# Variable Substitution And Context Rendering Decisions

## Scope implemented in this phase

- added a shared daemon-owned template renderer for compile-time prompt and command rendering
- canonical placeholder syntax is `{{variable}}`
- legacy `<variable>` placeholders remain supported for packaged compatibility
- rendered prompt and command text are frozen into compiled subtasks
- rendered-versus-source details are exposed through `compiled_workflows.resolved_yaml.rendering`

## Current precedence

Unqualified variable lookup is deterministic and last-scope-wins.

Current scope order:

1. `node`
2. `task`
3. `subtask`
4. `prompt`
5. `command`
6. `compat`
7. `hook`
8. `invoker`

Practical meaning:

- explicit `render_context.variables` win over built-in compile context aliases
- dotted references such as `{{node.id}}` or `{{task.key}}` stay stable regardless of alias collisions

## Current renderable fields

The current implementation intentionally allows rendering only in:

- `subtask_definition.prompt`
- `subtask_definition.command`
- `subtask_definition.pause_summary_prompt`
- hook `run[].prompt`
- hook `run[].command`

The compiler now rejects render syntax in:

- `args`
- `env`
- `checks`
- `outputs`
- `retry_policy`

That boundary is deliberate for this slice so workflow freeze semantics stay simple and auditable.

## Escaping

- `{{{{` renders as literal `{{`
- `}}}}` renders as literal `}}`
- `<<` renders as literal `<`
- `>>` renders as literal `>`

## Auditability decision

No new tables were added in this slice.

Existing durable surfaces were sufficient:

- source prompt templates already remain in source lineage
- rendered prompt and command text are frozen in compiled subtasks
- prompt delivery history already persists the rendered prompt content and template identity
- render diagnostics now live under `compiled_workflows.resolved_yaml.rendering`

## Deferred

- field-by-field rendering outside prompt/command surfaces
- runtime-time rerendering
- automatic availability of late-bound values such as the durable compiled-subtask UUID inside compile-time prompt bodies
- project-authored conditional render expressions or custom rendering functions
