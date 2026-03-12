# Original Starting Idea

Preserve the user-requested future direction:

- support arbitrary CLI coding tools as session providers
- specifically plan for Gemini and Claude in addition to Codex
- improve session tracking so Codex recovery uses a durable captured session UUID rather than `codex resume --last`
- figure out what Gemini and Claude expose for similar direct resume or attach behavior before deciding on the final abstraction

The current request is planning-only.

Nothing in this note should be read as active implementation.
