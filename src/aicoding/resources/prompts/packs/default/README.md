# Default Prompt Pack

This directory contains the packaged default prompt assets used by the built-in
YAML library.

Authoring rules for this pack:

- prompts describe one exact stage or recovery situation
- prompts state the expected output or status contract explicitly
- prompts prefer canonical `{{variable}}` placeholders
- prompts align with daemon-owned workflow, CLI, and history surfaces
- prompts avoid placeholder filler and ad hoc runtime-only wording

The pack is intentionally reusable: one prompt may support multiple YAML tasks
or hooks when their durable input and completion contract are the same.
