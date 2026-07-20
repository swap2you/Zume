# Ask Zume

Ask Zume is the local workspace question-and-answer feature. It retrieves
context from the local knowledge library before using the configured provider.

## Safe use

- Ask about technical concepts, practice, and the knowledge library.
- Do not provide candidate resumes, interview notes, contact details, or other
  personal data. Obvious emails, phone numbers, and candidate payload markers
  are rejected.
- Conversation history is local, under git-ignored `data/chat/`; clear it from
  the UI/API when no longer needed.

## Providers

Offline behavior is the default. Optional hosted AI and web search are disabled
unless explicitly configured. Web search also requires the runtime flag and an
available configured provider. Check readiness with `zume doctor`; it reports
state only, never secret values.

Use intake and finalize—not Ask Zume—for candidate operations.
