# Document Schema Test Policy

## Purpose

Explain how and when authoritative document-family tests must run.

## Policy

- if an authoritative document changes, run the relevant document tests afterward
- if a new required field or status value is introduced, update the tests in the same change
- documentation work is not complete unless the relevant document-family tests exist and pass for the changed scope

## Starter Command Placeholder

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```
