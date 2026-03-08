# Checklist C11: Auth And Local Magic-Cookie Verification

## Goal

Verify that daemon auth follows the intended local magic-cookie bearer-token model.

## Verify

- daemon creates or loads the auth token correctly
- token file path and permissions follow the intended local-access model
- CLI discovers and uses the token correctly
- authenticated and unauthenticated request behavior matches expectations

## Tests

- exhaustive auth lifecycle and failure tests
- performance checks for auth overhead on common request paths

## Notes

- update auth notes if token lifecycle, path, or semantics change
