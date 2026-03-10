# Multilanguage Provenance Expansion Decisions

## Summary

Feature `73_F30_multilanguage_provenance_expansion` broadens provenance refresh beyond the earlier Python-only slice while keeping the existing database model intact.

## Decisions

1. Provenance extraction now supports:
   - Python: `.py`
   - JavaScript: `.js`, `.jsx`
   - TypeScript: `.ts`, `.tsx`

2. This slice intentionally keeps the existing durable entity model:
   - entity types remain `module`, `class`, `function`, and `method`
   - relation types remain `contains` and `calls`

3. No database migration was required.
   Existing provenance tables already accept the broader extractor surface. Language is now carried in `node_entity_changes.metadata_json.language` rather than introducing a new `code_entities.language` column in this slice.

4. Matching semantics remain layered and confidence-aware.
   Exact matches still require type/name/path/signature continuity. Heuristic rename-or-move matches still rely on compatible type plus stable hash and signature continuity. The same `high` and `medium` confidence categories continue to apply across Python and JS/TS.

5. The relation `source` field remains on the current canonical values `ast_exact` and `ast_inferred` for compatibility with the existing DB constraint, even when the non-Python extractor is text-structured rather than AST-backed.

6. The current multilanguage slice is intentionally still bounded.
   It does not yet add first-class provenance for:
   - variables
   - types/interfaces
   - endpoints/routes
   - tests
   - cross-file import graphs

## Testing

This slice is covered by:

- existing Python provenance tests
- new TypeScript entity/relation coverage
- new JavaScript rename-or-move heuristic coverage
- mixed-language provenance performance coverage

## Performance

The extractor still defaults to the repository `src/` tree when present. This slice adds a mixed-language provenance refresh benchmark so the widened scan path remains bounded.
