# Role Policy Validation

Source: `config/role-policies.yaml`

| Policy | Role tracks | Knockout domains | Exercises | Notes |
|---|---|---|---|---|
| senior-sdet | Senior SDET | java, selenium, sql-oracle, api-openapi | sql, api, java, selenium | Default |
| lead-sdet | Lead SDET, Quality Engineering Lead | java, selenium, framework-architecture, debugging-reliability | sql, api, java | Leadership medium |
| mobile-automation | Mobile Automation Engineer | mobile-appium, java, api-openapi | api, java, sql | Not a Selenium-only knockout |
| performance | Performance Engineer | performance-observability, sql-oracle, api-openapi | sql, api | Not Java/Selenium knockout |
| ai-qa | AI QA / AI Test / AI / LLM Engineer | ai-quality, llm-engineering, agentic-ai, api-openapi | api, sql | Not Java/Selenium knockout |
| automation-architect | Test Automation Architect (+ aliases) | framework-architecture, solution-architecture, java, selenium | java, api, sql | Architecture high |
| qa-manager | QA Manager / QE Manager / Eng Manager | qa-strategy-governance, technical-leadership, debugging-reliability | sql | Explicitly not Java/Selenium |

## Verified behaviors

- Plans for Senior SDET, QA Manager and Performance Engineer produce distinct
  knockout ID tuples (Phase 0 regression).
- When reviewed role coverage is insufficient, `plan.role_coverage.warning` is set
  and `sufficient` is false — the UI surfaces the warning banner.
- Agenda remains 180 minutes; knockout 20 minutes when applicable.

## Coverage honesty

With 66 reviewed gold-core questions, specialty roles (mobile, performance, AI,
manager) can still report limited depth. That warning is intentional and must not
be silenced.
