# Zume Knowledge Taxonomy

## Classification dimensions

Every record may be filtered by:

- domain;
- subdomain;
- level: basic, intermediate, advanced;
- priority: P0-P3;
- frequency;
- role track;
- years range;
- question type;
- skill tags;
- source;
- freshness;
- status.

## Role tracks

- Senior SDET
- Lead SDET
- Test Automation Architect
- Quality Engineering Lead
- QA Manager
- Quality Engineering Manager
- Test/Quality Architect
- Solution Architect
- Technical Architect
- Engineering Manager
- AI QA Engineer
- AI Test Engineer
- AI Engineer
- LLM/Agent Engineer
- Quality Platform Engineer
- DevOps/CI Quality Engineer
- Mobile Automation Engineer
- Performance Engineer

## Question types

- concept
- compare/contrast
- coding
- debugging
- framework design
- system design
- scenario
- troubleshooting
- code review
- test strategy
- leadership
- behavioral
- estimation/planning
- incident/postmortem
- current/emerging
- hands-on exercise

## Tier A domains

Target: at least 24 quality questions per level and at least 12 exercises per
domain when content quality supports the target.

### 1. Testing fundamentals and quality engineering

Subtopics:

- testing principles;
- test levels/types;
- risk-based testing;
- test design techniques;
- SDLC/STLC;
- shift-left/shift-right;
- test pyramid/honeycomb/trophy;
- exploratory testing;
- defect lifecycle;
- quality gates;
- requirements traceability;
- metrics and coverage;
- release readiness;
- production validation.

### 2. Java

Subtopics:

- language basics;
- OOP;
- Strings and immutability;
- equals/hashCode;
- collections;
- generics;
- exceptions;
- streams/lambdas;
- records/sealed classes/pattern matching;
- concurrency;
- virtual threads;
- JVM/memory/GC;
- I/O/NIO;
- reflection/annotations;
- design patterns;
- clean code;
- testing Java code;
- debugging/performance.

### 3. Selenium WebDriver

Subtopics:

- WebDriver architecture;
- browser/driver management;
- locators;
- waits and synchronization;
- elements/interactions;
- frames/windows/alerts;
- actions;
- JavaScript use;
- file upload/download constraints;
- Page Objects/component objects;
- Grid/parallel execution;
- BiDi/CDP distinctions;
- observability;
- flaky-test diagnosis;
- anti-patterns;
- accessibility/browser concerns.

### 4. TestNG and Java test execution

Subtopics:

- annotations/lifecycle;
- assertions;
- data providers;
- parameters;
- groups/dependencies;
- listeners;
- retries;
- parallelism;
- factories;
- suites/XML;
- reporting;
- integration with Maven/CI;
- thread safety;
- anti-patterns.

### 5. Cucumber, Gherkin, and BDD

Subtopics:

- BDD purpose;
- discovery/collaboration/examples;
- Gherkin syntax;
- scenarios/outlines/tables;
- hooks;
- tags;
- step definitions;
- parameter types;
- dependency injection;
- state/context;
- maintainability;
- living documentation;
- reporting;
- parallelism;
- when not to use Cucumber.

### 6. API testing fundamentals and OpenAPI

Subtopics:

- HTTP;
- REST constraints;
- methods/idempotency;
- status codes;
- headers/content negotiation;
- authentication/authorization;
- JSON/XML;
- pagination/filtering/sorting;
- error contracts;
- schema validation;
- OpenAPI;
- contract testing;
- negative/security testing;
- resiliency/retries/rate limits;
- async/event APIs;
- observability;
- test data.

### 7. REST Assured

Subtopics:

- request/response specifications;
- assertions;
- serialization/deserialization;
- authentication;
- filters/logging;
- JSON path/XML path;
- schema validation;
- chaining/correlation;
- parameterization;
- reusable clients;
- error handling;
- parallel execution;
- integration with TestNG/Cucumber;
- reporting;
- framework design.

### 8. SQL, Oracle, and database testing

Subtopics:

- SELECT/filter/sort;
- joins;
- aggregation;
- subqueries/CTEs;
- window functions;
- set operations;
- constraints;
- transactions/ACID/isolation;
- indexes/execution plans;
- normalization;
- latest-record patterns;
- duplicates/data quality;
- Oracle functions;
- sequences;
- PL/SQL fundamentals;
- database test design;
- reconciliation;
- performance and locking.

### 9. Automation framework architecture

Subtopics:

- layers/responsibilities;
- driver/client factories;
- configuration;
- dependency injection;
- data management;
- page/component/service objects;
- API/UI/mobile integration;
- logging/reporting;
- retries;
- parallelism/thread safety;
- environment handling;
- extensibility;
- packaging;
- testability;
- governance;
- migration;
- cost/maintenance trade-offs.

### 10. Debugging, reliability, and flaky-test engineering

Subtopics:

- reproduce/isolate;
- logs/artifacts;
- synchronization;
- environment/test data;
- race conditions;
- nondeterminism;
- retries vs repair;
- quarantines;
- failure classification;
- root cause;
- observability;
- CI-only failures;
- browser/network/database failures;
- incident handling;
- reliability metrics.

### 11. Git, Maven, and build engineering

Subtopics:

- Git object/branch model;
- merge/rebase;
- conflict resolution;
- reset/revert/restore;
- cherry-pick;
- tags/releases;
- hooks;
- branching strategies;
- Maven lifecycle;
- POM/dependencies/scopes;
- plugins/profiles;
- Surefire/Failsafe;
- multi-module builds;
- dependency convergence;
- reproducible builds;
- secrets/artifacts.

### 12. CI/CD and quality pipelines

Subtopics:

- pipeline stages;
- PR vs nightly vs release;
- GitHub Actions;
- Jenkins;
- Azure DevOps concepts;
- caching;
- matrices/sharding;
- artifacts/reports;
- secrets;
- environments;
- quality gates;
- flaky handling;
- reruns;
- test selection;
- parallelism;
- deployment validation;
- rollback;
- supply-chain/security;
- cost/throughput.

## Tier B domains

Target: at least 15 quality questions per level and at least 6 exercises per
domain.

### 13. Postman, Newman, and API tooling
### 14. Mobile testing and Appium
### 15. BrowserStack/device clouds and cross-browser strategy
### 16. Performance testing and APM/observability
### 17. Security testing and OWASP fundamentals
### 18. Docker, Kubernetes, and cloud fundamentals for quality engineers
### 19. Test data, environment management, mocks, and service virtualization
### 20. Accessibility testing
### 21. QA strategy, metrics, management, and governance
### 22. Technical leadership, mentoring, and stakeholder management
### 23. Solution/test architecture and system-design scenarios
### 24. Behavioral, HR, communication, conflict, and ownership

Required subtopic examples for Tier B:

- Appium architecture, capabilities/options, Android/iOS engines, gestures,
  synchronization, hybrid apps, device matrix, cloud execution.
- Performance types, workload models, percentiles, throughput, errors,
  bottlenecks, JMeter/Gatling/k6 concepts, APM traces/metrics/logs.
- Security auth/session/input/API/OWASP, secrets, dependency risk, safe testing.
- Cloud identity/network/storage/compute/serverless/containers/observability,
  with vendor-neutral questions plus selected AWS/Azure/GCP mappings.
- Management hiring plans, prioritization, metrics misuse, roadmap, budget,
  vendor selection, conflict, performance coaching, executive communication.

## AI domains

Treat current facts as freshness-sensitive.

### 25. AI and machine-learning fundamentals — Tier B

- supervised/unsupervised/reinforcement;
- training/validation/test;
- overfitting/bias/variance;
- metrics;
- data quality;
- inference;
- drift;
- explainability;
- responsible AI.

### 26. LLM and generative-AI engineering — Tier A

- tokens/context;
- prompting;
- structured output;
- function/tool calling;
- embeddings/retrieval;
- RAG;
- grounding/citations;
- evaluation;
- latency/cost;
- caching;
- safety;
- privacy;
- model selection;
- hallucination handling;
- multimodal systems.

### 27. Agentic AI, tools, MCP, and orchestration — Tier A

- agents vs workflows;
- planning/tool choice;
- state/memory;
- handoffs;
- tool schemas;
- MCP concepts;
- permissions;
- sandboxing;
- prompt injection;
- web search;
- computer/code tools;
- observability/tracing;
- evals;
- failure recovery;
- human approval;
- multi-agent trade-offs.

### 28. AI for quality engineering — Tier A

- test generation;
- requirements analysis;
- locator/self-healing claims;
- API/schema generation;
- failure triage;
- synthetic data;
- visual testing;
- risk-based selection;
- autonomous testing;
- AI system testing;
- nondeterminism;
- evals;
- prompt injection;
- model drift;
- safety/adversarial testing;
- governance;
- human review.

### 29. AI leadership, governance, and adoption — Tier B

- business case;
- build/buy;
- data/privacy;
- model/vendor risk;
- governance;
- ROI;
- change management;
- capability development;
- responsible use;
- evaluation standards;
- incident response;
- cost controls;
- workforce impact;
- executive communication.

## Tier C domains

Target: at least 9 quality questions per level and at least 3 exercises per
domain.

### 30. Python for automation
### 31. JavaScript/TypeScript for automation
### 32. Contract testing and event-driven systems
### 33. Data/ETL/warehouse testing
### 34. SRE, resilience, chaos, and production quality
### 35. Agile/product delivery and estimation
### 36. Vendor/tool evaluation and quality economics

## Exercise families

At minimum include:

- coding;
- debugging broken code;
- refactoring;
- test-design challenge;
- framework-design whiteboard;
- API request/assertion;
- SQL query;
- CI YAML review;
- log/root-cause analysis;
- test-strategy case;
- leadership scenario;
- AI evaluation/prompt-injection case;
- architecture trade-off;
- code review.

Exercises must have variants so the same candidate is not repeatedly assigned
the same primary problem.
