---
name: grill-me
description: Builds a design by walking the user down a decision tree one question at a time, validating every assumption along the way (external dependencies AND design choices AND NFR targets AND failure-mode assumptions) until every branch resolves to evidence (citation, probe, or explicit accepted-risk). Outputs are `decisions.md` (the design as a resolved decision tree) and `dependencies.md` (the assumption-and-evidence ledger), and from them grill-me produces the change's **ADR** — its Decision, the Alternatives considered, and the accepted-risk Consequences. Use when starting a new feature design, validating a plan before implementation, or any time you say "grill me". This is the design-capture step in Spec-Driven Development: idea → grill-me (decisions.md + dependencies.md + the ADR) → Spec + Plan by initiative (see the `sdd` skill).
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

> **SDD stage 1 — design capture, and it provides the ADR** (see the `sdd` skill for the full map). grill-me produces the ADR directly: the resolved decision and the alternatives considered in `decisions.md` are the ADR's Decision and Alternatives, and the accepted-risk rows in `dependencies.md` are its Consequences. `decisions.md` also seeds the Spec (Goal, Requirements, Non-Goals), and `dependencies.md` the Plan's Constraints + Resilience. All of them live under `.specs/<initiative>/` in the repo that carries most of the change (usually `tosspaper`); there is no separate specs repository.

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

What follows it is decided by the `sdd` skill: a Lightweight (one-repo) change
goes straight to its Local Spec and Plan; only a Cross-Service change gets a
PRD. Never ask the user whether they want a PRD.

If the user comes with a written design, grill-me stress-tests it and produces
the same files. If they come with a verbal idea, grill-me is where the design
gets built. Don't punt to "we'll figure it out later": the close artifact IS
the design.

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
   answer before moving on. Keep asking until the tree is closed: "continue"
   means the next question, never "decide the rest yourself".

2a. **Ask the user only what is theirs to decide.** Business rules, what users
   see, who may do what, money, and scope are always asked. Implementation
   details (bean wiring, index type, lock store, record format, PR packaging,
   whether to write a PRD) are not: pick the option that fits the repo's rules,
   record it in `decisions.md` as "Decided by Claude", and list those in the
   close summary for the user to veto in one pass.

2b. **Only ask about cases that can happen.** Before asking about an edge case,
   name the steps in today's system that produce it. If no path produces it (a
   merged-away id the user can no longer see, a retry after a lost response, a
   second row a unique key already forbids), drop it and do not design for it.

2c. **Stay inside the asked change.** When a question would redesign something
   next to the change (claim flow, auth, another module), note it as a
   follow-up and keep going. Ask before widening scope, once.

3. **Every `AskUserQuestion` call must use structured fields — never stuff everything into the `question` string.**
   Map the content to the tool's fields like this:

   - **`question`** — the question only. One sentence, clear and unambiguous, nothing else. No
     branch name, no ledger state, no preamble, those go in the chat message you send immediately
     before the tool call, never inside the `question` string itself.
   - **`header`** — ≤12 chars, the branch name abbreviated (e.g. `"Auth method"`, `"Storage"`, `"Rollout"`)
   - **`options`** — array of objects. Each option gets:
     - `label`: short name for the choice (3–5 words, e.g. `"Directory bundle"`)
     - `description`: one sentence explaining what this choice means, including the recommendation signal. Mark the recommended option: `"(Recommended) <reason>"`

   State the branch and ledger shorthand as plain text in your message, right before the tool
   call, e.g. `Branch: Upload strategy | Ledger: 0 verified, 0 risk, 2 assumed`. Then call the tool:

   Example:
   ```
   AskUserQuestion(questions=[{
     question: "How should skill source files be packaged for upload?",
     header: "Upload",
     multiSelect: false,
     options: [
       { label: "Single file", description: "Point to one markdown file. Simple but limits structure." },
       { label: "Directory bundle", description: "(Recommended) Upload a whole directory. Matches how the Python SDK works and supports multi-file skills." },
       { label: "Zip archive", description: "Pre-zip locally and upload. More control but more friction." }
     ]
   }])
   ```

   Never put option text inside the `question` string. Never skip `description` on an option.
   Always mark one option as `(Recommended)` with a concrete reason.
   The user must be able to pick without reading anything beyond the question and its options.

   **Give context before every question.** The chat message before the tool call must
   carry, in this order and in plain words: (1) **Where we are:** the earlier decisions
   this question builds on, one line each; (2) **What the code or system does today:**
   the relevant fact with a file path or source; (3) **Why it matters:** what breaks or
   changes depending on the answer. Never ask a cold question. If the user dismisses
   a question, the context was probably too thin: add more, do not just re-send it.

   **Ground every question in a real-life example.** Abstract questions get dismissed
   or misread. In the chat message right before the tool call, state a short concrete
   scenario with named people, companies and amounts (e.g. "Ann and Bob both work at
   BuildCo; Acme invites both; Ann accepts. Does Bob's invitation become BuildCo's?"),
   then ask the question about that scenario. Use everyday nouns from the user's
   domain, not internal names or jargon. Make each option's `description` say what
   happens to the people in the example. If the user dismisses or says "ask this
   clearer", re-ask with a fresh example before anything else.

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

   **Trace today's flow before the first question about it.** For every flow the
   design touches, read the code path end to end (entry point, guards, state
   changes, who writes which row, events, what the frontend sends) and state it
   in plain words with file paths. A question built on a wrong picture of
   today's flow wastes the answer. Pay most attention to guards and invariants
   the change could break (uniqueness rules, "only one active" checks,
   operations that are all-or-nothing).

   **For API features specifically:** before proposing any new endpoint, grep
   the spec and controllers for existing routes that cover the same resource.
   Prefer extending over creating. Then check the shape against RFC 9110 and
   the spec's own conventions before asking about it:
   - resources are nouns, no verb paths (`/restore`, `/respond`, `/accept`);
   - create is `POST` → `201` + `Location`; a state change is `PATCH`
     (merge-patch) → `204`; moving or replacing a member set is `PUT`; async
     work is `202`;
   - `If-Match` (`412` stale, `428` missing, `ETag` returned) only where
     collaboration could alter previous information: two people editing the
     same fields, where a later write would overwrite what someone else
     changed. A status move whose rules already settle every race in the
     UPDATE's guard (accept is final, a second accept changes nothing) needs
     no `If-Match`;
   - every `POST` declares the spec's `Idempotency-Key` header, and one that
     costs money per call is called out in the ledger;
   - a resource the caller may not see is `404`.
   - no `canX` ability flags in a response: the client derives them from the
     caller's role (`company_roles`, `GET /v1/permissions`) and the resource's state.

6. **Resolve dependencies in order.** Some decisions gate others. Identify which
   decisions must be made first (foundational) and work top-down. Don't ask
   about details of a component until its existence is confirmed.

7. **Track open branches AND open ledger rows explicitly.** After each answer,
   state (a) what just resolved, (b) the next open branch, and (c) the current
   ledger state in shorthand: `Ledger: 4 verified, 1 accepted-risk, 2 assumed`.
   This keeps both trees visible.

8. **Challenge weak answers, and argue against the plan.** If an answer is
   vague, contradictory, or incomplete, push back before marking it resolved.
   "That assumes X — is X actually true?" For ledger rows, "we think it works
   that way" is never evidence. Push for the doc URL, the curl response, or an
   explicit "accept-risk" acknowledgment. Before closing, play devil's advocate
   on the whole design: name the three ways it most likely fails in stage or
   prod, and ask about each.

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

- ❌ "PLANNED" — masquerades as resolution. "We'll build this later" is
  still ❌. A row about work this change itself builds is ✅ once it names the
  plan task that builds it and the test that proves it; don't ask the user
  who or when.
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
   - **Plan, limits and price**: which plan the account is on today (Free,
     Hobby, Paid), each cap that plan sets (requests a day, calls per
     request, rows written, metric series, log lines, runner minutes) and
     the price per unit past it. Multiply by the expected use (say 1,000
     active users) and write down the number of users at which the first
     cap is hit. Quote the vendor's limits page; never use remembered
     numbers.
   - **Platform mechanics**: how the change reaches stage and prod through
     this vendor: which identity a push or deploy must come from, which
     events start which workflows, what a migration tool can and cannot run
     inside its transaction, which revision or version a deploy pins.
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

**Example 1 — Session lifetime.**
Plan mentions "the user signs in, then they're in." Add a row for the auth
provider's session. Assumed behavior: "the session lasts until logout". Don't
accept it. Fetch the provider's docs and quote the actual access-token and
refresh-token lifetimes. The row resolves to VERIFIED with the URL and quote,
and the design now has to handle silent refresh, which becomes its own branch.

**Example 2 — The plan the account is on.**
Plan moves a feature onto a managed platform. Add rows for the plan the
account is on today, each cap it sets (requests a day, writes, calls per
request) and the price past it. Multiply by the expected use and find the
number of users at which the first cap stops the feature. Do the same for
every other paid service the change leans on (metrics, logs, CI minutes).
Resolve with the numbers, an upgrade trigger, or ACCEPTED-RISK in the user's
words.

**Example 3 — A guard in our own code.**
Plan adds a new kind of record that existing code already checks for. Add a
row for every existing check that reads that record type and trace each path
the change touches: a guard written for the old shape can refuse the new one.
Our own code is a dependency like any vendor's.

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
- **An invariant** ("one X per Y", "a record has exactly one owner"). The row
  resolves only when it names the unique key, foreign key or check that
  enforces it, existing or added by this change.
- **What a field means** (whether we may generate an id, whether a value is
  a fixed set). Read real rows on stage or prod (read-only) before choosing a
  type or who fills it.
- **A stored value that can be derived** (a total, a count). Default to
  computing it on read; storing it needs a reason in `decisions.md`.
- **Who owns a row** (which account creates it, which account it belongs to
  after a transfer or a signup). Trace the insert, not the name.

If you're unsure whether something is an assumption worth a row, add it.
Removing a verified row is cheap; missing one is expensive.

### Reuse audit (run at opening, before the first design question)

Grep for what already does part of the job, on the current branch and in
shared modules and published packages: repositories and finders, validators,
HTTP clients, the outbox, locking and scheduling, idempotency, rate limiters,
caches, domain and email helpers, mappers, generated API clients (Java and
npm). List what you found in the opening message with paths. A design that
names a new class, table, module or endpoint must say which existing one it
looked at and why that one doesn't fit.

When the design describes behavior that would be more reliable, cheaper or
more observable on existing infrastructure than on the path it chose, add a
**missed-reuse row**:

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

1. **Read what was already decided.** Search memory, the initiative's ADRs and
   `.specs/`, and earlier sessions for decisions and known limits on this
   area. Build on them; never re-ask a settled question or reverse one without
   saying so.
2. **Trace today's flow and run the reuse audit** (rule 5 and "Reuse audit").
3. Identify and announce the **top-level branches** of the decision tree,
   including the mandatory branches below that apply.
4. Identify and announce the **initial Dependency Ledger** — every external
   surface you can already see in the plan, even if details are unknown. State
   the ledger out loud (in the message body, not via the tool) so the user can
   correct or add to it before you start drilling.
5. Fire the first `AskUserQuestion`, choosing whichever blocks the most other
   work — usually a foundational design branch OR the first ledger row whose
   resolution would change the rest of the design.

### Mandatory branches

Open each branch that the change touches. Each one has been where late
findings came from.

- **Audit history (ask first, before states and concurrency).** For every record
  the change creates, updates or deletes: does anyone need an earlier version?
  Keep history when a rollback is possible (a value someone may need to restore
  or see again); then a state change keeps the old version instead of an
  overwrite or a hard delete. How to keep it depends on the context: pick the
  easier option, a new status or new row in the **same** table, or a history
  table, and say why in `decisions.md`. Trace every `UPDATE` that replaces a
  value someone may need later, every `DELETE`, and every primary key that
  forces one row per pair (a re-send that overwrites the first send); a
  same-table design keeps one open row with a partial unique index
  (`WHERE status = 'open'`) instead of a key that allows only one row ever.
  Name who did each change and when.
- **Reads per screen and endpoint.** For each read, the queries it runs and
  the tables each joins. Target 2–3 database calls; no rollup or join query
  the list doesn't need; a design screen only shows data one call returns.
- **API shape.** The RFC checklist in rule 5, against the existing spec.
- **Caches and staleness.** For each cache: what it holds, its key, TTL, which
  event evicts it, and what a user sees until then (a removed user keeps
  access for how long; an `ETag` or `304` hides which change; a new response
  field needs a version bump or browsers keep the old copy).
- **Identity and access.** Who the actor is, which company context applies,
  what a token carries and for how long, how a removal or role change takes
  effect, and what another company can see.
- **States and columns.** Every status the change adds or reads, which are
  final, and every place that lists them (unique indexes, finders, rollups);
  for every new column, the code that writes it on every insert and update
  path, and the backfill for existing rows.
- **Concurrency.** The race (two sends at once, two reviewers on one item),
  the unique key or lock that settles it, and the per-key ordering a queue
  must keep.
- **Rollout and deploy.** The order of spec, migration, backfill, backend and
  frontend so nothing breaks in between; how each piece reaches stage and
  prod (migration workflow, CI path filters, the revision a deploy pins, who
  may trigger a deploy); every new config key, secret and webhook, and where
  it is set in stage and in prod; the backfill for rows that exist today; how
  to turn it off.
- **Hosting and ownership.** For every deployable piece the change adds: the
  account or org it runs in, the repository it lives in, who owns each, and
  who pays. Ask this even for a prototype; "where does it live" is a design
  decision, not a deploy detail.
  - BAD: design the Worker and Durable Object, never ask which Cloudflare
    account or GitHub org and repo hold them.
  - GOOD: "Which Cloudflare account runs the Worker, which GitHub org and
    repo hold it, and who owns the bill?"
- **Cost and limits.** The plan-and-limits sub-rows for every vendor row, and
  for anything that spends money per call, who starts it.
  When comparing vendors, price the load the user fears, not the entry tier:
  cost at 10x and 100x the expected use, including idle held connections.
  - BAD: "Vendor A starts at $5 a month", recommended on starting price alone.
  - GOOD: "At 10,000 concurrent connections A costs $X a month and B costs
    $Y; A's cap is hit at N users."


### Per question — ALWAYS use AskUserQuestion with structured fields

State the branch and ledger shorthand as a plain-text line in your chat message
first (e.g. `Branch: <branch name> | Ledger: <N> verified, <N> risk, <N> assumed`),
then immediately call the tool with just the question itself:

```
AskUserQuestion(questions=[{
  question: "<The question — one sentence, unambiguous>",
  header: "<≤12 char branch label>",
  multiSelect: false,
  options: [
    { label: "<short choice name>", description: "<one sentence — what this means and its tradeoff>" },
    { label: "<short choice name>", description: "(Recommended) <one sentence — why this is the right default>" },
    { label: "<short choice name>", description: "<one sentence — when you'd pick this instead>" }
  ]
}])
```

Rules:
- Chat message before the tool call: context (where we are, what exists today, why it matters), then a 1 to 3 sentence real-life example (named people, concrete numbers) that the question is about.
- `question` field: the question only, nothing else. No branch/ledger prefix inside it, that
  clutters the question and makes it harder to read at a glance, it belongs in the chat message.
- `header`: abbreviated branch name, ≤12 chars.
- `options[].label`: 3–5 words, the choice name only.
- `options[].description`: one sentence. Mark one option `(Recommended)` with a concrete reason.
- Never put the options list inside the `question` string.
- Never omit `description` on any option.

After the user replies, state what is now resolved, the next open branch, and
the current ledger shorthand. Then fire the next `AskUserQuestion`.

### Closing

Closing is allowed only when both conditions are true:
- Every design branch is resolved.
- The Dependency Ledger has zero ❌ ASSUMED rows (and zero ❌ FALSIFIED,
  ❌ MISSED-REUSE rows that haven't been resolved into a design decision).

**Simplicity challenge (before the close).** List every moving part the
design adds: tables, columns, endpoints, modules, queues, jobs, flags, states,
caches, background processes. Then write the smallest design that still meets
the user's stated goal, in plain words, and say what it gives up. Ask the user
to choose via `AskUserQuestion`, with the smaller design as one option. Do
this again whenever a single branch adds a new subsystem (a verification
flow, a second store, a migration mechanism).

**Accepted risk needs a trigger.** Every 🟡 row names the observable signal
that reopens it (a usage percentage, a query time, a count on stage). If 3 or
more rows resolve to 🟡 in one session, run the simplicity challenge again
before closing: many accepted risks usually mean the design is bigger than
the problem.

If a ledger row is still ❌, you must run its sub-interview before closing,
even if the user signals they want to wrap up. If they push back, ask via
`AskUserQuestion` whether they want to convert the row to 🟡 ACCEPTED-RISK
(with explicit words) or supply evidence. Never close on ❌.

#### Output style — prefer bullet points

Write every produced artifact (the ADR, the Spec, the Plan, the
architecture/ux docs) and the chat close summary for fast scanning, not
for prose reading:

- **Lead with bullets, not paragraphs.** A reader should grasp each section
  by skimming the bullets. Reserve prose for the one or two places that
  genuinely need a narrative (e.g. an ADR `Context` that explains the forces).
- **One claim per bullet.** Break a dense multi-clause sentence into separate
  bullets rather than stacking clauses with commas and semicolons.
- **Bold the lead phrase** of a bullet when it names the thing the bullet is
  about (`- **Write order:** Postgres commit first, then Redis publish.`),
  so the eye lands on the key term.
- **Keep ADR `Decision` and `Consequences` as bullet lists**, not flowing
  paragraphs. `Alternatives considered` is already one-bullet-per-option —
  keep it that way.
- Tables stay tables (Decision Summary, Dependency Ledger). Don't convert a
  table to bullets or vice versa.

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

Then **save all three to disk** — this is mandatory. `decisions.md` and
`dependencies.md` go in the change's folder per the `sdd` skill
(`<repo>/.specs/<initiative>/`), next to the ADR below. Add a "Decided by Claude" section to
`decisions.md` (rule 2a).

**Produce the ADR.** grill-me is the source of the change's Architecture Decision Record. Derive it directly from what you just resolved:

- **Decision** = the resolved choice (from the Decision Summary).
- **Alternatives** = the options weighed and why each was rejected (from the decision tree's branches).
- **Consequences** = the positive outcomes plus the `ACCEPTED-RISK` rows (from the Dependency Ledger).
- **Status** = `Accepted` (or `Proposed` if not yet ratified).

Write it to the change's ADR location per the `sdd` skill, scoped and grouped by initiative:

- `<repo>/.specs/<initiative>/adr/NNNN-<slug>.md`, in the same repo as `decisions.md`.

ADR sections: Status, Date, Deciders, Scope, Context, Decision, Consequences, Alternatives considered (see `.specs/vendor-jobs/adr/` for examples).

`decisions.md` and `dependencies.md` are the authoritative record for the plan,
the code-writer and the reviewer: decisions say what to build, dependencies say
which assumptions are evidence-backed and which are risks the team agreed to
ship with. When a later conversation changes a decision, update these files
and the ADR in the same turn, so nothing downstream plans from a stale copy.

## Failure Modes to Always Probe

These are runtime / system failure modes — distinct from dependency assumption
bugs (which the ledger handles). Probe each before closing, only for paths that
can happen (rule 2b):

- **Partial failure**: what happens if step N succeeds but step N+1 fails? (An
  email sent for an invitation whose insert rolled back.)
- **Concurrent execution**: is this safe if two instances run at once? Name the
  key or lock (see "Concurrency" under Mandatory branches).
- **Rollback**: how do you undo this if it goes wrong in prod?
- **Observability**: how will you know it's working after deploy? Name the
  metric or log line, check what the metric type does across a restart, and
  check that it fits the observability plan's limits.
- **Edge cases**: empty input, duplicate input, missing data, large volume.
- **Dependency outage**: for each ledger row, what breaks if that dep is down,
  rate-limited, or returning stale data?

## Non-Functional Requirements to Always Probe

Probe each category before closing. Skip one only if it is genuinely N/A, and
say why. Performance, scale, cost and rollout are covered by the mandatory
branches above; this pass covers what they don't.

### Performance and scale
- Latency target for the new endpoints (the API target is p95 under 250 ms)?
- Data volume now and in 12 months; any unbounded list or per-item loop?

### Reliability
- Blast radius if this component fails completely?
- Retry, ordering and give-up behaviour for background work?

### Security
- What data is touched — PII, sensitive, regulated?
- Access control enforced at the right layer (not just UI)?
- Injection risks (SQL, command, path traversal) in the new code path?
- Secrets in SOPS / the secrets store — none hardcoded?
- Cross-tenant isolation preserved, including ids and names in responses?
- **Auth lifetime**: every auth-related row in the ledger has its TTLs
  verified against the provider's docs, not assumed. Capture the URL and
  snippet.

### Data retention
- Data created, copied or deleted by this change, and its deletion path?
- Is the audit history kept where a rollback is possible (see the "Audit
  history" mandatory branch)? A hard delete or an overwrite of such a value
  needs the user's explicit words in `decisions.md`.

### Rollout & Access (the "ship to all users" question)
- For every ledger row representing a third-party endpoint or feature: does
  every target user / org / region have access to it today?
- If gated (beta, allowlist, paid tier, region, role): what's the path to
  ungate, and what's the user-visible failure if we ship without it?
