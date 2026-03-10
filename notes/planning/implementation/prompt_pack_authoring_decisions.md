# Prompt Pack Authoring Decisions

## Phase

- `plan/features/43_F05_prompt_pack_authoring.md`

## Decision Summary

- The packaged default prompt pack under `src/aicoding/resources/prompts/packs/default/` is now treated as authored implementation content, not scaffold prose.
- Prompt-reference inventory in `prompts/default_prompt_refs.yaml` now covers the shipped recovery, pause, docs, and quality assets in addition to the previously referenced execution/runtime prompts.
- The default packaged prompts now prefer canonical `{{variable}}` placeholders and are validated for render compatibility with daemon-owned context.

## Boundary Clarification

- This phase does not change prompt delivery persistence or daemon prompt-history behavior.
- This phase also does not add a new prompt-loading API because the existing resource catalog and CLI prompt inspection surfaces were already sufficient.
- The implementation work is therefore centered on asset quality, prompt-reference coverage, tests, and note alignment rather than new runtime plumbing.

## Testing Expectations Frozen By This Phase

- every packaged default prompt asset must be real authored text rather than placeholder filler
- every built-in YAML prompt reference must resolve to an existing default-pack prompt asset
- every packaged default prompt asset must be render-compatible with the canonical prompt renderer
- prompt-pack load-and-render cost should stay bounded in the performance harness
