# Audio and Voice

The workspace supports local browser speech by default. Optional hosted TTS and
realtime voice are capability-gated and remain disabled until configured.

## Behavior

- Speech requests disclose whether generated audio was used.
- Candidate PII is rejected for narration by default.
- Realtime sessions never return a long-lived API key.
- `zume doctor` reports audio and realtime readiness without printing keys.

Enable optional capabilities only through the documented runtime environment
settings and an approved local secret source. Never place credentials in this
repository, browser code, logs, prompts, or release packages. See
`SECURITY_AND_SECRETS.md`.
