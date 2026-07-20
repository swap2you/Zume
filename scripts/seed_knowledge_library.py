"""Generate the versioned, reviewable Zume knowledge-library seed corpus.

The generated YAML is intentionally deterministic.  Editorial changes belong in
this file or knowledge/taxonomy.yaml; never patch a generated record in place.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from zume.knowledge.models import ExerciseRecord, QuestionRecord  # noqa: E402

VERIFIED = "2026-07-15"
LEVELS = ("basic", "intermediate", "advanced")
COUNTS = {"A": (24, 12), "B": (15, 6), "C": (9, 3)}
AI_DOMAINS = {"llm-engineering", "agentic-ai", "ai-quality", "ml-fundamentals", "ai-governance"}

# Legacy ids are deliberately retained for the small set of concepts already
# curated in the v1 libraries.  New ids are stable because their construction
# depends only on the taxonomy ordering and template number.
LEGACY_IDS = {
    ("java", "basic"): ["java-b1", "java-b2", "java-b3"],
    ("java", "intermediate"): ["java-i1"],
    ("selenium", "basic"): ["sel-b1", "sel-b2", "sel-b3"],
    ("rest-assured", "basic"): ["rest_assured-b1"],
    ("sql-oracle", "basic"): ["sql_oracle-b1"],
}

# These adapted seed entries preserve legacy identifiers while replacing the
# old library's phrasing with original wording. They also give reviewers
# representative domain-specific records beside the broad concept banks.
HAND_AUTHORED = {
    "java-b1": {
        "subdomain": "equals-hashcode",
        "title": "Object equality and hash collections",
        "question": "A value object is used as a HashMap key. Explain identity versus logical equality, and the contract its equality methods must keep.",
        "concise_answer": "Reference identity answers whether two variables point to the same object; logical equality answers whether their values represent the same thing. Equal keys must produce the same hash code, otherwise a hash collection can place an equal key in a different bucket and fail to find it.",
        "recommended_answer": "Use identity only when object instance ownership matters. For a value object, implement equality from the stable fields that define its value and implement hashCode from the same fields. Verify behavior by inserting one equal instance into a HashMap or HashSet and retrieving it with another; do not mutate fields used by equality while the object is a key.",
        "key_points": ["identity differs from logical equality", "equal objects require equal hash codes", "key fields must remain stable"],
    },
    "java-b2": {
        "subdomain": "exceptions",
        "title": "Exception boundaries and context",
        "question": "How would you decide whether an API should expose a checked exception, an unchecked exception, or a domain-specific wrapper?",
        "concise_answer": "Choose an exception boundary based on what the caller can realistically recover from, not merely the exception's origin. A domain wrapper can preserve useful context while keeping low-level implementation details from leaking across the boundary.",
        "recommended_answer": "Identify the recovery action at the call site. Propagate or model a recoverable condition deliberately, use unchecked exceptions for violated programming contracts or unrecoverable invariants, and wrap infrastructure errors only when the wrapper adds domain context and retains the cause. Avoid broad catch blocks that erase evidence; log or translate at the boundary that owns the response.",
        "key_points": ["caller recovery drives the boundary", "preserve cause and context", "do not swallow exceptions"],
    },
    "java-b3": {
        "subdomain": "collections",
        "title": "Choosing collection semantics",
        "question": "A test needs ordered iteration, duplicate values, and frequent lookup by a business key. How would you choose and combine Java collections?",
        "concise_answer": "A List preserves sequence and permits duplicates, while a Map supports keyed lookup; neither is a universal substitute for the other. Model the required semantics explicitly, often using a list for ordered input and a map when fast keyed access is independently needed.",
        "recommended_answer": "Start from operations: ordered traversal, duplicate handling, and key lookup. Use an ArrayList for ordered records where indexed access is useful, and build a HashMap keyed by a stable unique identifier when average constant-time lookup matters. State duplicate-key behavior explicitly rather than silently overwriting it, and choose LinkedHashMap only when map iteration order is also a requirement.",
        "key_points": ["select by operations and semantics", "define duplicate-key behavior", "avoid linear search when a key is available"],
    },
    "sel-b1": {
        "subdomain": "locators",
        "title": "Stable WebDriver locators",
        "question": "How do you choose a locator for a control whose layout and CSS classes change often?",
        "concise_answer": "Prefer a unique, intentionally stable semantic or test attribute over structural position or styling. A locator should express the control's durable role or business identity, so it fails when behavior changes rather than when a layout refactor occurs.",
        "recommended_answer": "Work with the product team to expose a stable accessibility name, label relationship, or purpose-built data attribute. Use a concise CSS selector when it expresses that stable contract; use XPath only when its relationship or text capability is necessary and robust. Avoid copied absolute paths, indexes, and generated IDs, then verify uniqueness and behavior through the user interaction.",
        "key_points": ["prefer stable semantic attributes", "verify uniqueness", "avoid layout-coupled selectors"],
    },
    "sel-b2": {
        "subdomain": "waits-synchronization",
        "title": "Condition-based synchronization",
        "question": "Why should a WebDriver test wait for a specific condition instead of sleeping for a fixed duration?",
        "concise_answer": "A fixed sleep guesses timing and is either slow when the page is ready early or flaky when it is not ready in time. A condition-based wait polls for the state the next action actually needs and produces a focused timeout when that state never occurs.",
        "recommended_answer": "Identify the actionable condition: for example, an element is visible, enabled, detached after a refresh, or a request-driven status has completed. Apply an explicit wait around that condition and keep timeout ownership clear; do not mix unrelated global delays into the same reasoning. If it times out, inspect the locator, application state, overlay, and page event rather than immediately increasing the timeout.",
        "key_points": ["wait for the next action's condition", "fixed sleeps are guesses", "timeouts are diagnostic evidence"],
    },
    "sel-b3": {
        "subdomain": "page-components",
        "title": "Page and component object boundaries",
        "question": "What should a page or component object encapsulate, and what should remain in the test?",
        "concise_answer": "An object should encapsulate how the UI is located and operated, while the test states the business scenario and its assertions. This keeps UI changes local without making the object a hidden test script.",
        "recommended_answer": "Expose meaningful actions and state queries rather than leaking raw locators to tests. Keep navigation and synchronization close to the component that owns them, return the next page or observable state where useful, and let tests assert the scenario outcome. Avoid putting broad scenario assertions or unrelated workflow decisions inside page objects, because that reduces reuse and obscures failures.",
        "key_points": ["encapsulate UI mechanics", "tests own scenario assertions", "prefer meaningful actions over locator leakage"],
    },
}

SOURCE_BY_DOMAIN = {
    "testing-fundamentals": "istqb-glossary", "java": "java-oracle-docs",
    "selenium": "selenium-dev", "testng": "testng-docs", "cucumber": "cucumber-docs",
    "api-openapi": "openapi-spec", "rest-assured": "rest-assured", "sql-oracle": "oracle-sql",
    "framework-architecture": "selenium-dev", "debugging-reliability": "selenium-dev",
    "git-maven": "maven-docs", "cicd": "github-actions", "postman-newman": "postman-docs",
    "mobile-appium": "appium-docs", "browserstack": "browserstack-docs",
    "performance-observability": "opentelemetry", "security-owasp": "owasp",
    "containers-cloud": "kubernetes-docs", "accessibility": "w3c-wcag",
    "python-automation": "python-docs", "javascript-typescript": "typescript-docs",
    "contract-events": "pact-docs", "llm-engineering": "openai-docs",
    "agentic-ai": "mcp-spec", "ai-quality": "openai-docs", "ml-fundamentals": "nist-ai-rmf",
    "ai-governance": "nist-ai-rmf",
}

QUESTION_FRAMES = {
    "basic": [
        "What problem does {concept} address, and what is its practical boundary?",
        "Explain {concept} to a teammate who must use it safely tomorrow.",
        "What would you check first before relying on {concept} in a test or delivery workflow?",
        "Give a small example of {concept} and state the observable outcome.",
        "Which assumption about {concept} most often causes an avoidable defect?",
        "How would you recognize that {concept} is being used for the wrong purpose?",
        "What information must be known before choosing {concept}?",
        "What is the simplest useful validation for {concept}?",
        "Compare a sound use of {concept} with a superficially similar but unsafe use.",
        "What should a concise team convention say about {concept}?",
        "How does {concept} affect the reliability of a routine automated check?",
        "What evidence would make you trust a result produced through {concept}?",
        "What failure mode should be made visible when introducing {concept}?",
        "How would you explain the trade-off behind {concept} without relying on jargon?",
        "Which input or precondition matters most for {concept}?",
        "When should a team stop and clarify the intended use of {concept}?",
        "What would a useful acceptance criterion for {concept} look like?",
        "How would you test the negative path around {concept}?",
        "What is a reasonable first diagnostic when {concept} behaves unexpectedly?",
        "How can a team avoid turning {concept} into a brittle convention?",
        "Which outcome would show that {concept} has delivered value?",
        "What should be documented about {concept} for the next maintainer?",
        "How would you make {concept} understandable in a code review?",
        "What is a common scope mistake when applying {concept}?",
    ],
    "intermediate": [
        "How would you design {concept} for a changing product while preserving clear ownership?",
        "What trade-offs would you evaluate before scaling {concept} across multiple teams?",
        "A result involving {concept} is intermittent. How do you isolate cause from symptom?",
        "How would you make {concept} observable enough to support a production investigation?",
        "Where should the boundary around {concept} live, and why?",
        "How would you validate that {concept} remains correct when inputs are incomplete or delayed?",
        "What design choice makes {concept} easier to evolve without hiding failures?",
        "How would you separate deterministic checks from environmental uncertainty around {concept}?",
        "What data would you collect before tuning or optimizing {concept}?",
        "How would you review a proposal that centralizes {concept}?",
        "What are the consequences of retrying failures associated with {concept}?",
        "How would you build a representative test matrix for {concept} without testing every combination?",
        "What contract should adjacent components share when they use {concept}?",
        "How do you prevent a local optimization of {concept} from degrading system behavior?",
        "How would you introduce {concept} incrementally and measure whether it helped?",
        "What failure classification would you use for incidents involving {concept}?",
        "How would you decide whether {concept} belongs in a reusable abstraction?",
        "What is the difference between validating {concept} and merely exercising it?",
        "How would you debug a discrepancy between local and CI behavior involving {concept}?",
        "Which signals would trigger a review of the current {concept} design?",
        "How would you handle concurrency or shared-state risk around {concept}?",
        "What should a high-signal test report expose about {concept}?",
        "How would you make a change to {concept} reversible?",
        "Which shortcut around {concept} seems efficient but creates future maintenance cost?",
    ],
    "advanced": [
        "Design a policy for {concept} that balances correctness, delivery speed, and operational evidence.",
        "A large organization has inconsistent implementations of {concept}. How would you converge them safely?",
        "How would you evaluate competing architectures for {concept} under reliability and cost constraints?",
        "What governance and exception path would you establish for {concept}?",
        "How would you detect silent degradation of {concept} before users report it?",
        "Design an experiment that distinguishes whether {concept} improves outcomes or only activity metrics.",
        "How would you set risk-based quality gates for a change to {concept}?",
        "What must be true before delegating decisions about {concept} to automation?",
        "How would you model blast radius and rollback for a failure involving {concept}?",
        "How do you avoid Goodhart-style metric misuse when measuring {concept}?",
        "How would you establish ownership boundaries for {concept} across platform and product teams?",
        "What evidence would justify retiring or replacing a mature {concept} implementation?",
        "How would you design a post-incident review focused on {concept} without blaming individuals?",
        "What is the minimum observability design that makes {concept} auditable?",
        "How would you make {concept} resilient to partial failure and degraded dependencies?",
        "How would you review a vendor claim that automates {concept}?",
        "How would you protect sensitive data while operating {concept} at scale?",
        "What decision record would you require before changing a high-impact {concept}?",
        "How do you balance standardization with context-specific needs for {concept}?",
        "How would you test whether a proposed abstraction for {concept} hides important domain behavior?",
        "What leading and lagging indicators should inform investment in {concept}?",
        "How would you define a human-approval boundary for {concept}?",
        "How would you challenge a design that treats {concept} as a one-time project?",
        "What systemic failure patterns would you look for when {concept} repeatedly causes incidents?",
    ],
}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def dump_yaml(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(value, handle, allow_unicode=True, sort_keys=False, width=100)


def priority(index: int, total: int) -> str:
    # 17/33/33/17 percent; small domains use the nearest workable distribution.
    if total not in {9, 15, 24}:
        return "P1" if index == 0 else "P2"
    distribution = {9: (1, 3, 3, 2), 15: (2, 5, 5, 3), 24: (4, 8, 8, 4)}[total]
    p0, p1, p2, _ = distribution
    return "P0" if index < p0 else "P1" if index < p0 + p1 else "P2" if index < p0 + p1 + p2 else "P3"


def concept(domain: dict[str, Any], index: int) -> str:
    items = domain["subdomains"]
    return items[index % len(items)].replace("-", " ")


def answer_text(concept_name: str, level: str, domain_label: str) -> tuple[str, str]:
    concise = (
        f"{concept_name.title()} should be applied to a stated outcome, observable evidence, and known "
        f"constraints; using it as a ritual is not enough. In {domain_label}, validate both the intended "
        f"result and the meaningful negative or failure path before treating it as reliable."
    )
    recommended = (
        f"Start by naming the decision that {concept_name} supports and the invariant it must preserve. "
        f"Choose the smallest mechanism that exposes inputs, outputs, failures, and ownership; then test "
        f"representative normal, boundary, and failure cases. Explain the trade-off rather than claiming a "
        f"single universal pattern, and use telemetry or review evidence to revise the design when reality differs."
    )
    if level == "advanced":
        recommended += " At scale, define an exception path, measurable guardrails, and a rollback or containment plan."
    return concise, recommended


def make_question(domain: dict[str, Any], level: str, index: int) -> dict[str, Any]:
    concept_name = concept(domain, index)
    concise, recommended = answer_text(concept_name, level, domain["label"])
    legacy = LEGACY_IDS.get((domain["id"], level), [])
    record_id = legacy[index] if index < len(legacy) else f"{domain['id']}-{level[0]}-{index + 1:02d}"
    fresh = domain["id"] in AI_DOMAINS
    record = {
        "id": record_id, "domain": domain["id"], "subdomain": slug(concept_name),
        "title": f"{concept_name.title()}: {level} decision", "level": level,
        "priority": priority(index, COUNTS[domain["tier"]][0]),
        "frequency": "emerging" if fresh else ("very_common" if index < 4 else "common"),
        "question": QUESTION_FRAMES[level][index].format(concept=concept_name),
        "concise_answer": concise, "recommended_answer": recommended,
        "deep_dive": f"Probe for a concrete {domain['label']} example, competing constraints, and evidence that would change the candidate's decision.",
        "key_points": ["states an invariant", "uses evidence", "names trade-offs"],
        "strong_signals": ["distinguishes symptom from root cause", "defines a bounded validation strategy"],
        "weak_signals": ["recites a tool feature without a decision context"],
        "red_flags": ["claims a pattern is universally correct", "hides or ignores failure evidence"],
        "common_mistakes": ["testing only a happy path", "confusing activity with outcome"],
        "follow_ups": ([{
            "question": f"What evidence would make you revise your {concept_name} approach?",
            "recommended_answer": "A repeatable failure, a violated invariant, or telemetry showing the design misses its stated outcome should trigger review. Reproduce the evidence, classify the scope, and change the smallest responsible layer."
        }] if priority(index, COUNTS[domain["tier"]][0]) in {"P0", "P1"} else []),
        "examples": [f"Use a small, representative {concept_name} case before generalizing."],
        "role_tracks": list(domain["role_tracks"]), "years_range": [3, 15] if level != "basic" else [1, 8],
        "tags": [domain["id"], slug(concept_name), level], "estimated_minutes": 4 if level == "basic" else 6,
        "references": [{"source_id": SOURCE_BY_DOMAIN.get(domain["id"], "istqb-glossary"), "locator": concept_name}],
        "last_verified": VERIFIED, "freshness_days": 90 if fresh else 365, "status": "draft",
        "review_status": "unreviewed", "quality_origin": "generated_proposal",
        "question_type": "scenario" if level != "basic" else "concept",
    }
    record.update(HAND_AUTHORED.get(record_id, {}))
    return record


def runner_for(domain_id: str) -> str:
    if domain_id == "sql-oracle":
        return "sql"
    if domain_id in {"java", "testng", "selenium", "cucumber", "rest-assured"}:
        return "java"
    if domain_id in {"api-openapi", "postman-newman"}:
        return "api"
    return "none"


def make_exercise(domain: dict[str, Any], level: str, index: int, total: int) -> dict[str, Any]:
    concept_name = concept(domain, index)
    fresh = domain["id"] in AI_DOMAINS
    runner = runner_for(domain["id"])
    return {
        "id": f"{domain['id']}-exercise-{level[0]}-{index + 1:02d}", "domain": domain["id"],
        "subdomain": slug(concept_name), "title": f"{concept_name.title()} evidence exercise",
        "level": level, "priority": priority(index, total),
        "task": f"Given a small {domain['label']} scenario, propose and implement or describe a bounded approach for {concept_name}. State assumptions, cover a failure path, and show the evidence you would collect. Do not include interviewer answers in your submission.",
        "constraints": ["Keep the solution scoped to the stated scenario.", "Make failure handling observable.", "Explain a trade-off."],
        "starter_files": {}, "expected_reasoning": f"Identify the invariant for {concept_name}, choose a minimal approach, exercise normal and negative paths, and explain evidence, limits, and next diagnostic steps.",
        "reference_solution": f"A strong solution defines the intended outcome and a measurable invariant for {concept_name}. It implements the smallest clear mechanism, validates representative normal and failure cases, records evidence, and names a safe rollback or containment action.",
        "test_cases": [{"name": "normal-path", "expected": "The stated invariant is satisfied with observable evidence."}, {"name": "failure-path", "expected": "Failure is classified and reported without masking the cause."}],
        "scoring_rubric": ["Defines a relevant invariant (2)", "Covers normal and failure paths (3)", "Explains trade-offs and evidence (3)", "Keeps scope maintainable (2)"],
        "requirement_change_follow_up": f"How would you adapt the {concept_name} approach if the input volume or failure rate doubles?",
        "requirement_change_recommended_answer": "Re-evaluate the stated invariant and bottleneck before scaling. Add bounded capacity, observability, and prioritization; do not merely add retries or parallelism without evidence that they address the limiting factor.",
        "debugging_follow_up": f"The approach for {concept_name} passes locally but fails intermittently in CI. What do you inspect first?",
        "debugging_recommended_answer": "Start with the exact CI artifact, error, environment difference, and timing or shared-state evidence. Reproduce the smallest case under comparable conditions, classify the failure, then fix the cause rather than masking it with a blanket retry.",
        "independence_questions": [{"question": f"What would demonstrate that the {concept_name} solution is independently understood rather than copied?", "recommended_answer": "The candidate can explain its invariant, trade-offs, failure handling, and how a changed requirement alters the design; they can make a small justified modification without prompting."}],
        "hints": ["Write down the invariant before selecting a tool.", "Consider one meaningful negative path."],
        "runner_type": runner, "allowed_languages": ["Java"] if runner == "java" else (["SQL"] if runner == "sql" else []),
        "runtime_limits": {"minutes": 30 if level == "advanced" else 20},
        "references": [{"source_id": SOURCE_BY_DOMAIN.get(domain["id"], "istqb-glossary"), "locator": concept_name}],
        "last_verified": VERIFIED, "freshness_days": 90 if fresh else 365, "status": "draft",
        "review_status": "unreviewed", "quality_origin": "generated_proposal",
        "role_tracks": list(domain["role_tracks"]), "tags": [domain["id"], slug(concept_name), "exercise"],
        "variant_family": f"{domain['id']}-{slug(concept_name)}",
    }


def allocation(total: int) -> dict[str, int]:
    base, remainder = divmod(total, 3)
    return {level: base + (1 if position < remainder else 0) for position, level in enumerate(LEVELS)}


def validate(records: list[dict[str, Any]], model: type[QuestionRecord] | type[ExerciseRecord]) -> None:
    for record in records:
        model.model_validate(record)


def main() -> None:
    taxonomy = load_yaml(ROOT / "knowledge" / "taxonomy.yaml")
    sources = {item["id"] for item in load_yaml(ROOT / "knowledge" / "sources.yaml")["sources"]}
    all_questions: list[dict[str, Any]] = []
    all_exercises: list[dict[str, Any]] = []
    for domain in taxonomy["domains"]:
        question_count, exercise_count = COUNTS[domain["tier"]]
        exercise_counts = allocation(exercise_count)
        for level in LEVELS:
            questions = [make_question(domain, level, index) for index in range(question_count)]
            exercises = [make_exercise(domain, level, index, exercise_counts[level]) for index in range(exercise_counts[level])]
            for record in [*questions, *exercises]:
                missing = {ref["source_id"] for ref in record["references"]} - sources
                if missing:
                    raise ValueError(f"{record['id']} has unregistered sources: {sorted(missing)}")
            validate(questions, QuestionRecord)
            validate(exercises, ExerciseRecord)
            dump_yaml(ROOT / "knowledge" / "questions" / domain["id"] / f"{level}.yaml", {"version": 1, "records": questions})
            dump_yaml(ROOT / "knowledge" / "exercises" / domain["id"] / f"{level}.yaml", {"version": 1, "records": exercises})
            all_questions.extend(questions)
            all_exercises.extend(exercises)
    print(f"Draft questions: {len(all_questions)}")
    print(f"Draft exercises: {len(all_exercises)}")
    for domain_id, count in sorted(Counter(item["domain"] for item in all_questions).items()):
        levels = Counter(item["level"] for item in all_questions if item["domain"] == domain_id)
        exercise_total = sum(1 for item in all_exercises if item["domain"] == domain_id)
        print(f"{domain_id}: basic={levels['basic']}, intermediate={levels['intermediate']}, advanced={levels['advanced']}, exercises={exercise_total}")


if __name__ == "__main__":
    main()
