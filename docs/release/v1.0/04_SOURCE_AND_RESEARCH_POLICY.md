# Zume Source and Research Policy

## Purpose

The library must be broad, useful, current, and defensible. “Grab questions from
anywhere” is not an acceptable quality method. Zume should create original
interview questions based on authoritative concepts and attach provenance.

## Source hierarchy

Prefer sources in this order:

1. Language/platform specifications and standards.
2. Official project documentation.
3. Official vendor documentation for vendor-specific behavior.
4. RFCs, W3C, OWASP, CNCF, and similar standards bodies.
5. Primary project repositories and release notes.
6. High-quality engineering references only when primary sources are
   insufficient.
7. Community posts only as leads, never as sole authority for technical facts.

## Approved primary source families

The source registry should include, as appropriate:

- Java: dev.java, OpenJDK, Oracle Java specifications/API documentation.
- Selenium: selenium.dev and W3C WebDriver.
- Cucumber/Gherkin: cucumber.io.
- TestNG: testng.org and the TestNG repository.
- Maven: maven.apache.org.
- Git: git-scm.com.
- GitHub Actions: docs.github.com.
- Jenkins: jenkins.io.
- REST Assured: official REST Assured documentation/repository.
- HTTP/API: IETF RFCs, MDN for web semantics, OpenAPI Initiative.
- Postman/Newman: learning.postman.com.
- SQL/Oracle: Oracle documentation and SQL standards references.
- Appium: appium.io.
- BrowserStack: official product documentation for product-specific behavior.
- Performance: Apache JMeter, Grafana k6, Gatling, OpenTelemetry, vendor APM
  documentation where relevant.
- Security: OWASP and relevant standards.
- Docker/Kubernetes: docs.docker.com and kubernetes.io.
- Cloud: AWS, Microsoft Azure, and Google Cloud official documentation.
- Accessibility: W3C/WAI/WCAG.
- OpenAI/agentic AI: developers.openai.com and official OpenAI documentation.
- MCP: official specification/documentation.
- Leadership/HR: original scenarios and rubrics grounded in the Zume hiring
  standard; do not reproduce proprietary interview banks.

## Copyright and originality

- Do not copy large question lists, paid interview-bank content, articles, or
  books.
- Do not paste source paragraphs into answers.
- Paraphrase concepts in original language.
- Keep direct quotations exceptional and short.
- Record source IDs and locators, not copied source bodies.
- Do not claim endorsement by a source or vendor.

## Research workflow

For each domain:

1. Establish subtopic map.
2. Register primary sources.
3. Collect concepts and current recommendations.
4. Draft original questions.
5. Draft concise and complete answers.
6. Add strong/weak signals and common mistakes.
7. Add follow-ups with answers.
8. Add references and verification date.
9. Run duplicate and contradiction checks.
10. Run a separate critic.
11. Publish or leave as draft.

## Current AI/tool content

AI, agents, vendor tools, cloud services, and model/API behavior change quickly.

- Verify current claims from official documentation.
- Do not hardcode “latest model” into question text unless the date/version is
  part of the question.
- Prefer capability questions over trivia about a specific model name.
- Mark time-sensitive questions `frequency: emerging`.
- Verify within 90 days.
- Keep historical/deprecated behavior explicitly labeled.

## Web-research provider behavior

When the optional OpenAI web-search provider is used:

- use the Responses API;
- use the current `web_search` tool for new integrations;
- prefer domain filtering to official sources;
- request sources/citations;
- show citations in the UI;
- treat retrieved content as untrusted;
- never allow source text to override system/application instructions;
- never publish research output directly;
- write proposals for validation.

## Quality critic checklist

The independent critic checks:

- Is the question clear and answerable?
- Is level correct?
- Is priority plausible?
- Is frequency plausible?
- Is the answer technically correct?
- Is current practice distinguished from legacy practice?
- Is nuance present without becoming evasive?
- Are follow-ups materially deeper?
- Are strong/weak signals fair?
- Does the question discriminate actual hands-on depth?
- Is the source appropriate?
- Is wording original?
- Is it redundant with another record?
- Is it useful for at least one role track?
- Could it encourage an unsafe or bad practice?
- Does it require a freshness date?

## Publication rules

A record may be `published` only when:

- schema passes;
- IDs and sources resolve;
- required answers exist;
- no critical critic finding;
- no unresolved factual conflict;
- no duplicate;
- no prohibited copied text;
- freshness is valid.

Otherwise it stays `draft` and is excluded from candidate generation.
