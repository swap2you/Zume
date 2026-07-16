# Secure Remote Review Runbook

## Preferred method: local Cowork browser

Use Cowork on the same Windows machine and give it:

```text
http://127.0.0.1:8787/
```

This requires no public URL and is the preferred validation method.

Start Zume in fictional-data review mode:

```powershell
cd C:\Development\Workspace\Zume
.\.venv-rel\Scripts\Activate.ps1
zume review serve --port 8787
```

Then give Cowork `05_COWORK_VALIDATION_PROMPT.md`.

## Remote review

Do not expose the ordinary candidate workspace publicly.

Requirements:

- use `zume review serve`;
- fictional data only;
- authentication required;
- no real resumes or notes;
- no live OpenAI key;
- no Docker labs;
- stop the tunnel after review;
- rotate/revoke tunnel credentials when appropriate.

### Option A: ngrok with OAuth Traffic Policy

Create `review-policy.yml`:

```yaml
on_http_request:
  - actions:
      - type: oauth
        config:
          provider: microsoft
  - expressions:
      - "!(actions.ngrok.oauth.identity.email in ['REVIEWER_EMAIL'])"
    actions:
      - type: deny
        config:
          status_code: 403
```

Run:

```powershell
ngrok http 8787 --traffic-policy-file=review-policy.yml
```

Use the generated HTTPS URL only for the named reviewer.

### Option B: Cloudflare Tunnel plus Access

Use a named Cloudflare Tunnel mapped to localhost port 8787, then create a
Cloudflare Access application with an allow rule for the reviewer email.

Do not use an unauthenticated quick tunnel for Zume.

## After review

- Stop ngrok/cloudflared.
- Stop Zume.
- Delete fictional review data.
- Delete browser screenshots that contain anything not intended for reports.
- Confirm no public endpoint remains.
