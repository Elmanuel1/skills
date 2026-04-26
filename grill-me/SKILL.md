---
name: grill-me
description: Builds a design by walking the user down a decision tree one question at a time, validating every assumption along the way (external dependencies AND design choices AND NFR targets AND failure-mode assumptions) until every branch resolves to evidence (citation, probe, or explicit accepted-risk). Output is `decisions.md` — the design itself, captured as a structured decision tree with a parallel Dependency Ledger that records every assumption and its evidence. Use when starting a new feature design, validating a plan before implementation, or any time you say "grill me". This is the design-capture step in the pipeline: verbal idea → grill-me → decisions.md → design-to-prd → PRD → prd-to-features → engineering tickets.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - WebFetch
  - WebSearch
  - AskUserQuestion
---

# Grill Me

Interview the user relentlessly about every aspect of their plan or design until
we reach a shared understanding. Walk down each branch of the design tree,
resolving decisions one at a time. Maintain a **Dependency Ledger** in parallel
— every assumption the design relies on (external dependencies, design choices,
NFR targets, failure-mode assumptions, persona assumptions) gets a row, and no
row may stay in `❌ ASSUMED` when the session closes.

## Where this skill sits in the pipeline

`grill-me` is the **design-capture** step. It produces `decisions.md` (the
design itself, expressed as a resolved decision tree) and `dependencies.md`
(the parallel ledger of every assumption with its evidence). These are the
**primary deliverable**, not supporting docs.

The full pipeline:

```
verbal idea  →  [grill-me]  →  decisions.md + dependencies.md
                                          ↓
                                  [design-to-prd]
                                          ↓
                                        PRD
                                          ↓
                                  [prd-to-features]
                                          ↓
                            engineering stories + Jira tickets
```

If the user comes to grill-me with a fully-written PRD already in hand, that's
fine — grill-me stress-tests it the same way and produces the same
`decisions.md` + `dependencies.md`. But if they come with just a verbal idea
or rough notes, grill-me is where the design actually gets built. Don't punt
to "we'll figure it out later" — the close artifact IS the design.

## Why the Ledger is broad — every assumption, not just external

Most "design bugs" aren't logic bugs — they're **assumed-behavior bugs**: facts
the design relies on without evidence. These come in several flavors:

- **External dependency assumptions** — the Supabase access token "lasts
  forever" until you read the docs and find it's 1 hour. The new Anthropic
  endpoint is "available" until you discover only allowlisted orgs can call it.
- **Design assumptions** — "non-tech users have terminal access" without
  surveying them. "The existing admin UI handles this case" without grepping
  the source.
- **NFR-target assumptions** — "we'll have ~50 users at 6 months" without
  baseline data. "p99 latency will be under 200ms" without load testing.
- **Failure-mode assumptions** — "the org-wide cap will catch a runaway
  agent" without verifying real-time spend tracking exists.
- **Persona assumptions** — "marketing folks will adopt this if we ship it"
  without user research.

All of these belong in the Dependency Ledger. The narrow reading ("dependency
= third-party API") leaves NFR + design + persona assumptions invisible, and
those are the assumptions that derail launches. Force every one into the
ledger, force every ledger row to point at evidence, and refuse to close until
each cell is resolved.

## Rules

1. **Always use the `AskUserQuestion` tool — never output questions as plain text.**
   Every question to the user MUST be delivered via `AskUserQuestion`. This is not
   optional. Plain text questions will be missed or ignored. The tool call IS the
   question — do not also print the question in your response.

2. **Ask one question at a time.** Never ask a list of questions in one turn —
   pick the most important unresolved branch and ask about that. Wait for the
   answer before moving on.

3. **Every `AskUserQuestion` call must include options AND a recommendation.**
   Structure every call exactly like this:

   ```
   AskUserQuestion(question="""
   [Branch: <branch name>]

   <The question — one sentence, clear>

   Options:
     A) <option one>
     B) <option two>
     C) <option three if applicable>
     D) Other (describe)

   My recommendation: <letter> — <concrete reason, 1–2 sentences>
   """)
   ```

   Never present a question without options. Never present options without a
   recommendation. The user must be able to reply with just a letter.

4. **The Dependency Ledger gates closing.** As soon as the user states the plan,
   open the ledger and enumerate every external surface the design touches —
   third-party APIs, SaaS, internal services owned by other teams, libraries /
   SDKs whose behavior matters, infra (DB, cache, queue, DNS, IAM), and any
   feature/endpoint whose **rollout or access** is gated. Add new rows the
   moment a new dependency surfaces in conversation. The ledger must reach zero
   `ASSUMED` rows before the closing summary is allowed. See "The Dependency
   Ledger" section below for format and evidence rules.

5. **Explore the codebase before asking, then always ask anyway.** Read existing
   code, grep for patterns, check configs — report what you found as context in
   the question. Then still ask via `AskUserQuestion`. What the codebase shows
   may be a bug, a legacy pattern, or intentionally wrong. Never treat codebase
   evidence as a resolved decision — only the user's answer resolves it.

   **Always ask which branch / ref before reading code.** Active feature work
   often lives on `dev`, a feature branch, or a fork — `main` may be months
   stale on the surface area being designed. A finding of "the file doesn't
   exist" or "the function isn't there" on `main` is meaningless if the work
   is on `feat/X`. Ask the user once, up front: "which branch is current for
   this design?" and use it for every subsequent read.

   **GitHub code search returns false negatives on private repos.** If
   `search_code` returns 0 hits for a term you have other evidence exists,
   don't trust it — read the directory listing and the file directly. Search
   indexing is incomplete for private content.

   **For API features specifically:** before proposing any new endpoint, grep
   the spec and controllers for existing routes that cover the same resource.
   Prefer extending over creating — add optional request fields, query params,
   or widen the response shape before adding a new path. Only propose a new
   path when the existing endpoint's semantics are fundamentally incompatible
   (different HTTP verb required, breaking response contract, different auth
   level). Ask yourself:
   - Can an **optional request field** achieve this?
   - Can a **query param** toggle the behaviour?
   - Can the **response be widened** without breaking existing consumers?
   - Is the new path a true sub-resource or a duplicate of existing logic?

6. **Resolve dependencies in order.** Some decisions gate others. Identify which
   decisions must be made first (foundational) and work top-down. Don't ask
   about details of a component until its existence is confirmed.

7. **Track open branches AND open ledger rows explicitly.** After each answer,
   state (a) what just resolved, (b) the next open branch, and (c) the current
   ledger state in shorthand: `Ledger: 4 verified, 1 accepted-risk, 2 assumed`.
   This keeps both trees visible.

8. **Challenge weak answers.** If an answer is vague, contradictory, or
   incomplete, push back before marking it resolved. "That assumes X — is X
   actually true?" For ledger rows, "we think it works that way" is never
   evidence. Push for the doc URL, the curl response, or an explicit
   "accept-risk" acknowledgment.

9. **Stop only when the tree is closed AND the ledger is clean.** The session
   ends when every branch of the design is resolved AND the Dependency Ledger
   has zero `ASSUMED` rows. Then produce the decision summary AND the final
   ledger.

## The Dependency Ledger

The ledger is a table the skill maintains throughout the session. It is the
single most important artifact this skill produces, because it captures the
class of bug that surprises teams in production — assumed third-party behavior.

### Format

```
| # | Dependency | Assumed behavior we're relying on | Evidence | Status |
|---|------------|-----------------------------------|----------|--------|
| 1 | Supabase access token | Session valid for 1 hour, refresh token rotates | https://supabase.com/docs/guides/auth/sessions — quoted: "Access tokens are JWTs with a default expiry of 3600 seconds" | ✅ VERIFIED |
| 2 | Anthropic /v1/agents API | Available to all paid orgs in production | NONE — user accepted risk: "we'll discover at rollout" | 🟡 ACCEPTED-RISK |
| 3 | Internal user-svc /v2/profile | Returns 200 within 50ms p99 | NONE | ❌ ASSUMED — BLOCKS CLOSE |
```

### Status meanings

- **✅ VERIFIED** — Evidence cell points at a doc URL with a quoted snippet, a
  probe (curl / WebFetch / script) actually run during the session with the
  output captured, or both. Inferred-from-other-docs is not VERIFIED.
- **🟡 ACCEPTED-RISK** — User has knowingly accepted shipping on assumption.
  The Evidence cell records the concrete acknowledgment words verbatim. Two
  acceptable input modes:
  1. **User types the words.** Free-text via `AskUserQuestion`'s "Other"
     option. Most direct, useful when you want the user to put it in their
     own framing.
  2. **User click-confirms a prepared concrete sentence.** You draft a
     plain-language acknowledgment (no jargon, no shorthand, dated, named,
     each risk spelled out in user-visible terms), present it in the
     question body — not buried in option text — and the user picks
     "Confirm draft as-is." The prepared sentence becomes the Evidence
     cell verbatim. This is the common path because typing long
     acknowledgments is high friction; the audit trail stays intact
     because the click captured a fully-specified sentence the user read
     and accepted.
  Either way, the row appears in the final summary so the team can
  revisit it later.
- **❌ ASSUMED** — Default state for any newly-added row. Blocks the close.

**There are exactly three statuses. Do not invent intermediate statuses.**
Common drift patterns to refuse:

- ❌ "PLANNED" — masquerades as resolution. If "we'll build this in the
  upcoming sprint" is the entire evidence, the row is still ❌. To convert
  to ✅, the row must name the **WHO**, **WHEN**, and **WHAT** (specific
  scope) of the commitment. Without all three, it stays ❌.
- ❌ "TBD" — same pattern. Either it's evidence-backed (✅), an explicit
  accepted risk (🟡), or unresolved (❌).
- ❌ "PARTIAL" / "PARTIALLY VERIFIED" — split the row into sub-rows
  (use the `Nx` numbering convention from "Forgotten sub-rows" below).
  Each sub-row is independently ✅ / 🟡 / ❌.

A row whose evidence cell would say "we'll figure it out during implementation"
is a row that should still be open. Close discipline depends on this.

### Per-row sub-interview

When a new dependency surfaces, run this mini-flow before returning to the
main design tree:

1. **Identify the assumed behaviors.** Don't ask "does this dependency work?"
   Ask the specific contract bits the design relies on. Examples:
   - **Behavior**: TTLs, rate limits, response shape, error semantics,
     idempotency, ordering guarantees, retry behavior, transaction semantics.
   - **Access / rollout**: Who can call this today? Is it gated by tier,
     region, beta flag, role, allowlist, paid plan? What's the path to roll
     out to all target users?
   - **Capacity**: Quotas, throughput caps, fair-use terms, per-key limits.
   - **Failure mode**: What does the API return on 5xx, on timeout, on 429?
     What's the blast radius when this dep is fully down?
   - **Version**: What version are we coding against? Deprecation timeline?
2. **Pick a verification method** via `AskUserQuestion`:
   - A) **Cite** — paste a doc URL and quoted snippet. The skill should
     `WebFetch` the URL during the session to confirm the quote actually
     appears at that URL.
   - B) **Probe** — the skill proposes the exact curl / one-line script /
     WebFetch / Grep and runs it now. Output goes into Evidence.
   - C) **Accept risk** — user types the explicit acknowledgment. Status
     becomes 🟡, not ❌. Cell records the user's exact words and the date.
   - D) Other (describe).
3. **Update the ledger** before returning to the main tree.

### Worked examples (the kinds of misses to catch)

**Example 1 — Magic link session TTL.**
Plan mentions "user clicks magic link, then they're in." Add row:
"Supabase magic link → access token → session". Assumed behavior: "session
persists indefinitely / for the life of the project / until logout". This is
the failure mode you have seen before. Don't accept it. Run a `WebFetch` against
the Supabase auth docs and quote the actual TTL (3600s by default for access
tokens; refresh tokens are separate and rotate). The ledger row resolves to
VERIFIED with the URL + quote, and the design now has to handle silent token
refresh — which becomes its own branch in the main tree.

**Example 2 — Anthropic managed-agents rollout.**
Plan is "use the new managed-agents endpoint and ship to all users." Add row:
"Anthropic /v1/agents". Assumed behaviors are at least: (a) every target user's
org can call it today; (b) per-org rate limits accommodate our peak; (c) the
endpoint is GA, not preview. Each is its own ledger sub-row. Don't let any
resolve to "I'll find out when we ship." Either find the doc that confirms
GA + access tier, or run a probe call from a representative org, or mark
ACCEPTED-RISK with explicit words. Without this, "ship to all users" is a
launch-day surprise.

**Example 3 — Internal service quietly owned by another team.**
Plan mentions a call to `user-svc`. Even though it's internal, treat it as a
dependency. Ledger row: "user-svc /v2/profile". Assumed: latency, error
contract, deploy cadence (will they ship a breaking change next sprint?),
on-call ownership. Probe: ping the endpoint, read the OpenAPI spec, or
Slack-message the owning team's channel.

### Ledger heuristics — when to add a row

The Ledger covers every assumption, not just external surface area. Add a row
whenever the design references any of:

**External-surface assumptions** (the easy ones to spot):
- A vendor name (Stripe, Supabase, OpenAI, Anthropic, Slack, Twilio, etc.)
- A protocol/spec the team didn't author (OAuth, OIDC, SAML, WebRTC, gRPC)
- A managed infra component (RDS, Aurora, ElastiCache, S3, SQS, SNS,
  CloudFront, Lambda concurrency, IAM permissions)
- A library whose semantics matter to correctness (HTTP retry behavior, ORM
  lazy-loading, concurrency primitives, JSON parsers, date/time libs)
- An internal service owned by another team
- A feature flag, beta program, allowlist, paid tier, or region gate

**Linguistic tells** (assumptions hiding behind hand-waves):
- "The X just works that way", "X handles that for us", "we pass it through
  to X"
- "No new UI work required", "the existing X already handles this", "we just
  reuse Y" — *internal-dependency* assumptions hiding scope creep. Grep the
  named component on the current branch.

**Design assumptions** (the harder, easier-to-miss class):
- A target user persona ("non-tech users will be comfortable with terminal")
- A scale or volume target ("we'll have ~50 users at 6 months")
- A latency or throughput target ("p99 < 200ms")
- A failure-mode assertion ("the org-wide cap will catch a runaway agent")
- A behavioral claim about a downstream system ("Sentinel can express this
  policy", "TF Cloud's run triggers fire fast enough")
- A claim about your own org's capabilities ("the platform team has Go
  expertise to write a custom TF provider")

If you're unsure whether something is an assumption worth a row, add it.
Removing a verified row is cheap; missing one is expensive — and the design
assumptions are the ones that derail launches without anyone noticing they
weren't validated.

If you're unsure whether something is a dependency, add it. Removing a
verified row is cheap; missing one is expensive.

### Missed-reuse rows

When you audit the codebase to verify a dependency claim, you will sometimes
discover infrastructure the team already runs but the PRD didn't reference
(a Temporal workflow engine, an existing blocklist file, a feature-flag
service, a queue, a cron framework). When the PRD describes behavior that
would be more reliable / cheaper / more observable on that existing infra
than on the path the PRD chose, add a **missed-reuse row**:

```
| 15 | Temporal workflow engine (existing) | PRD chose log-and-forget for addenda fan-out; existing infra would give retries + observability for free | Source: backend /temporal/ dir + build.gradle | ❌ MISSED-REUSE — design decision needed |
```

These are not dependency-assumption bugs (the team isn't depending on
something they assumed); they are scope-and-architecture misses. They still
gate close because the choice of "build new vs. reuse existing" is a
first-class design decision. Resolve by either: (a) PRD updates to use the
existing infra, (b) explicit decision documented in `decisions.md` for why
the new path is right despite the existing option, or (c) ACCEPTED-RISK with
typed words.

### Forgotten sub-rows

When a probe falsifies a row, it often opens new sub-rows (e.g. probing
"refresh-token never expires" surfaces a separate "max-lifetime time-box
setting" sub-row that the original PRD didn't mention). These sub-rows are
easy to lose because they weren't on the initial enumeration. Two rules
prevent this:

1. **Number every sub-row immediately.** When a probe surfaces a new
   contract bit, add it to the ledger as `Nx` (e.g. 2a, 2b, 2c) before
   asking the next question, even if its resolution will come later.
2. **At every status update, scan for `❌ ASSUMED` rows and name them.**
   Don't just say "ledger: 5 verified, 2 assumed" — enumerate which two.
   This forces visibility on rows that have drifted out of focus.

## Session Structure

### Opening

When the skill starts, use `AskUserQuestion` to ask the user to state the plan
or paste the design. Then in this exact order, before any other questions:

1. Identify and announce the **top-level branches** of the decision tree.
2. Identify and announce the **initial Dependency Ledger** — every external
   surface you can already see in the plan, even if details are unknown. State
   the ledger out loud (in the message body, not via the tool) so the user can
   correct or add to it before you start drilling.
3. Fire the first `AskUserQuestion`, choosing whichever blocks the most other
   work — usually a foundational design branch OR the first ledger row whose
   resolution would change the rest of the design.

### Per question — ALWAYS use AskUserQuestion

```python
AskUserQuestion(question="""
[Branch: <name of branch being explored>]
[Ledger: <verified> verified, <risk> accepted-risk, <assumed> assumed]

<The question — one sentence, unambiguous>

Options:
  A) <first option with brief description>
  B) <second option with brief description>
  C) <third option if applicable>
  D) Other (describe)

My recommendation: <letter> — <1–2 sentence rationale grounded in the codebase or known tradeoffs>
""")
```

After the user replies, state what is now resolved, the next open branch, and
the current ledger shorthand. Then fire the next `AskUserQuestion`.

### Closing

Closing is allowed only when both conditions are true:
- Every design branch is resolved.
- The Dependency Ledger has zero ❌ ASSUMED rows (and zero ❌ FALSIFIED,
  ❌ MISSED-REUSE rows that haven't been resolved into a design decision).

**Multi-accept-risk meta-warning.** If 2 or more rows resolve to
🟡 ACCEPTED-RISK in the same session, surface this pattern explicitly
before producing the close summary: "You've accepted risk on N independent
dependencies in this design — that's a design-level signal, not just N
individual choices. Want to reconsider whether the current rollout is too
aggressive, or commit to ship as-is?" Use `AskUserQuestion` to gate the
close on a deliberate answer. The point is not to block the team — it's
to make sure that "shipping on faith" was a chosen posture, not the
accumulated default of clicking past three different gate questions.

If a ledger row is still ❌, you must run its sub-interview before closing,
even if the user signals they want to wrap up. If they push back, ask via
`AskUserQuestion` whether they want to convert the row to 🟡 ACCEPTED-RISK
(with explicit words) or supply evidence. Never close on ❌.

When both conditions are met, output:

```
## Decision Summary

| Decision | Resolved To |
|----------|-------------|
| ...      | ...         |

## Dependency Ledger

| # | Dependency | Assumed behavior | Evidence | Status |
|---|------------|------------------|----------|--------|
| ...

All design branches resolved. All dependency rows verified or explicitly accepted as risk.
```

Then **save both to disk** — this is mandatory:

```bash
cd /Users/macbook/devloop
python3 orchestrator/state_cli.py summary  # find the relevant design ID

DESIGN_DIR=".orchestrator/designs/{designId}/design"
mkdir -p "$DESIGN_DIR"
# Write decisions.md with the full Decision Summary table
# Write dependencies.md with the full Dependency Ledger
```

`decisions.md` and `dependencies.md` together become the authoritative record
for downstream agents. The architect reads both before designing — decisions
tell them what to build, dependencies tell them which assumptions are evidence-
backed and which are explicit risks the team agreed to ship with. The reviewer
checks both to catch fields and behaviors that were never agreed. The
code-writer uses them to avoid implementing scope or relying on contracts that
were never confirmed.

## Failure Modes to Always Probe

These are runtime / system failure modes — distinct from dependency assumption
bugs (which the ledger handles). Probe each before closing:

- **Partial failure**: what happens if step N succeeds but step N+1 fails?
- **Concurrent execution**: is this safe if two instances run at once?
- **Rollback**: how do you undo this if it goes wrong in prod?
- **Observability**: how will you know it's working correctly after deploy?
- **Edge cases**: empty input, duplicate input, missing data, large volume
- **Dependency outage**: for each ledger row, what breaks if that dep is down,
  rate-limited, or returning stale data? (The ledger captures the contract;
  this question captures what your code does when the contract is violated.)

## Non-Functional Requirements to Always Probe

Probe every NFR category below before closing. Skip a category only if it is
genuinely N/A — and state why. Many of these will surface new ledger rows;
add them as they appear.

### Performance
- p50 / p99 latency target under normal load?
- Throughput target (requests/sec, records/sec, bytes/sec)?
- Synchronous hot paths that could become bottlenecks?
- Caching layer, TTL, invalidation strategy? (Cache provider becomes a ledger row.)

### Scalability
- Expected data volume now vs. in 12 months?
- Horizontal scaling — what shared state must be coordinated?
- Any O(N²) or unbounded operations on growing datasets?
- DB query plan at 10× current row count?

### Reliability & Availability
- SLA / uptime target?
- Blast radius if this component fails completely?
- Circuit breaker, retry policy, graceful degradation path?
- Recovery time if the service crashes mid-operation?

### Security
- What data is touched — PII, sensitive, regulated?
- Access control enforced at the right layer (not just UI)?
- Injection risks (SQL, command, path traversal) in the new code path?
- Secrets in SSM / secrets manager — none hardcoded?
- Cross-tenant isolation preserved?
- **Auth lifetime**: every auth-related row in the ledger must have its TTLs
  verified against the provider's docs, not assumed. The Supabase access-token
  default is 3600s; refresh tokens rotate; "magic link session = forever" is a
  red flag that has bitten teams before. Confirm and capture the URL + snippet.

### Maintainability
- Will the next engineer understand this without asking the author?
- Magic numbers, hardcoded IDs, env-specific assumptions that will rot?
- Documented runbook for operating this in production?
- Feature flag / kill switch if it needs to be disabled quickly?

### Cost
- New AWS API calls, S3 ops, or DB queries per request?
- Unbounded loop that could amplify cost under adversarial input?
- Cost per unit acceptable at projected scale?

### Compliance & Data Retention
- Data subject to retention policies — created, copied, transformed?
- Audit trails or logging requirements affected?
- Data deletion path if a user requests it?

### Rollout & Access (the "ship to all users" question)
This is the category that the Anthropic managed-agents miss falls under, and
it deserves its own probe pass before closing:
- For every ledger row representing a third-party endpoint or feature: does
  every target user / org / region have access to it today?
- If gated (beta, allowlist, paid tier, region, role): what's the path to
  ungate? Who owns it? What's the timeline?
- If we ship without ungating, what's the user-visible failure?
- Are there per-org / per-tenant rate limits we'd hit at full rollout?
