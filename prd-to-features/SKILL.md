---
name: prd-to-features
description: Break a PRD into a structured engineering deliverable: per-Story markdown specs at .specs/features/NN_slug.md inside each affected repo, plus a matching Jira Epic with Stories and Tasks. Reads the PRD from Confluence, loads prior grill-me artifacts (decisions.md, dependencies.md), audits affected repos for impact, asks the user via AskUserQuestion for anything not yet decided, and applies grill-me's discipline (options + recommendation, refuse-on-fog) to surface and resolve new design gaps before writing any Story file. Use when the user says "break down a PRD", "create features from this design", "ticket this PRD", "decompose this design doc", "spec out the engineering work for", "make Jira tickets from", "create the engineering breakdown for", or shares a Confluence PRD link and asks for engineering scope. Refuses to start if the initiative's grill-me artifacts are missing; invoke grill-me first.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - mcp__01abfc93-c649-43ee-9fe0-12f5783b1432__getConfluencePage
  - mcp__01abfc93-c649-43ee-9fe0-12f5783b1432__updateConfluencePage
  - mcp__01abfc93-c649-43ee-9fe0-12f5783b1432__getAccessibleAtlassianResources
  - mcp__01abfc93-c649-43ee-9fe0-12f5783b1432__getVisibleJiraProjects
  - mcp__01abfc93-c649-43ee-9fe0-12f5783b1432__createJiraIssue
  - mcp__01abfc93-c649-43ee-9fe0-12f5783b1432__editJiraIssue
  - mcp__01abfc93-c649-43ee-9fe0-12f5783b1432__createIssueLink
  - mcp__01abfc93-c649-43ee-9fe0-12f5783b1432__searchJiraIssuesUsingJql
  - mcp__a9b002e8-c28d-43e1-afaf-1a7ea817b2fd__get_file_contents
  - mcp__a9b002e8-c28d-43e1-afaf-1a7ea817b2fd__search_code
---

# PRD → Features

Turn a PRD into something engineering can actually pick up: per-Story markdown
specs committed to the relevant code repo at `.specs/features/NN_slug.md`,
plus a matching Jira Epic with Stories and Tasks. The skill reads the source
PRD, the verified design decisions from a prior grill-me session, and **the
actual source code**, and refuses to write a single Story file until every
detail it needs to write that file precisely is settled — either by reading
it from the artifacts, asking the user via `AskUserQuestion`, or refusing
to proceed.

## Why this skill exists

Most PRD-to-tickets workflows fail in one of four ways:

1. **Premature decomposition.** The PRD is broken into stories before the
   design questions are resolved, so each story carries forward a fog of
   "we'll figure it out in implementation." That fog becomes scope creep at
   PR review time.
2. **PRD-text-grounded sizing.** Stories are sized by counting PRD sections
   instead of by reading the actual code. The PRD says "no new UI work"
   while the source says "8 new components needed" — and the wrong sizing
   sets a wrong release date.
3. **Stale PRD.** The source has moved on from what the PRD describes, but
   the PRD is treated as immutable truth. Stories get written that
   contradict the codebase, engineers discover the lie at implementation
   time, and the PRD never gets corrected — so the next person reading it
   inherits the same trap.
4. **Endless interview.** The breakdown agent asks dozens of questions to
   settle every detail, when most of those questions were already answered
   (and recorded) in the prior design review.

This skill resolves all four by:

- Making **grill-me artifacts a hard precondition** (decisions are settled
  before breakdown begins).
- **Sizing Stories from source code** rather than from PRD text.
- Treating the **PRD as a living document**: every discrepancy between PRD
  and source is surfaced via `AskUserQuestion`, resolved with the user,
  and **written back to the Confluence PRD** so the doc stays truthful.
- **Inlining grill-me's question discipline** (options + recommendation,
  refuse-on-fog, ledger tracking) for any new gap that surfaces during
  breakdown.

## Hard preconditions — the skill refuses to start if any are missing

1. **The input identifies a PRD.** A Confluence page link, page ID, tiny
   link ID, file path to a markdown PRD, or pasted PRD text. If unclear,
   ask via `AskUserQuestion`.
2. **The PRD names its initiative** (the `.specs/<initiative>/` folder grill-me
   wrote). If it does not, ask via `AskUserQuestion`. If there is no such
   folder, the PRD has not been grilled: STOP and tell the user to invoke the
   **grill-me** skill on the PRD first, then return.
3. **Both `decisions.md` and `dependencies.md` exist** at
   `<repo>/.specs/<initiative>/`, where grill-me saves them. If either is missing, STOP
   and tell the user the same thing.

These preconditions are not optional. Breakdown without resolved decisions
is exactly the failure mode this skill exists to prevent. State the missing
input clearly and stop.

## Workflow

### Step 1 — Confirm inputs (AskUserQuestion)

Read the PRD body via Confluence (or the file path / pasted text). Resolve
`<repo>/.specs/<initiative>/` and read `decisions.md` and `dependencies.md` there. From `decisions.md`
plus the dependencies ledger, identify which code repos are likely affected
(repos are usually named in the resolution column or the related-files
lines).

Then use a single `AskUserQuestion` call to confirm:

- **PRD title and initiative**: one-line confirmation.
- **Affected repos** — multi-select if multiple plausible repos surfaced.
- **Branch/ref to read against per repo** — usually `dev` or a feature
  branch, not `main`. Active feature work typically lives off `main`. A
  finding of "the file doesn't exist" on `main` is meaningless if the work
  is on `feat/X`.
- **Jira project** — auto-detect from the PRD's Confluence space using the
  `prd-to-features.config.json` mapping (see "Confluence → Jira mapping"
  below). If unmapped, ask the user once and persist the mapping.
- **Epic title** — propose `[{ProductArea}] {PRD Title}` and let the user
  edit.

Don't proceed without explicit confirmation. Downstream actions (file
writes, Jira creation) are not idempotent enough to recover from a wrong
project guess silently.

### Step 2 — Read source (the most important step)

For each affected repo on the chosen ref:

- **Prefer the locally mounted directory** (use `Glob`, `Grep`, `Read`).
- **Fall back to GitHub MCP** (`get_file_contents`, `search_code`) if the
  directory is not mounted.
- **GitHub code search returns false negatives on private repos.** If
  `search_code` returns 0 hits for a term you have other evidence exists,
  don't trust it — read the directory listing and the file directly.

For each functional area named in the PRD + each `❌ FALSIFIED` /
`❌ MISSED-REUSE` row in `dependencies.md`, build a concrete file-level
inventory:

- **Files that exist today** that the work touches.
- **Files that need to be NEW.**
- **Files that need to be MODIFIED.**

This inventory is the basis for Story sizing. **Do not size Stories from
PRD section counts.** The PRD might say "no new UI work required" while the
source audit reveals 8 new components are actually needed (the Vendor
Portal row #13 case). The source audit is the truth.

When the source audit reveals that PRD claims about existing UI / infra are
false, log the discrepancy. It will become a new Story (often the largest
one), and you'll surface it in the confirmation summary so the user knows
the breakdown deviates from the PRD body.

### Step 3 — Reconciliation pass (PRD ↔ source — write back)

This is the step that keeps the PRD truthful. After Step 2's source audit,
**enumerate every discrepancy** between what the PRD says and what the
source shows. Discrepancies fall into a small set of patterns:

- **PRD asserts existing behavior that doesn't exist.** Example: "the
  existing invitation list gains a Response column" when there is no
  existing invitation list component on the chosen branch.
- **PRD claims no new work is needed where new work is needed.** Example:
  "no new UI work required on the GC side" when the source shows the
  entire GC-side surface needs to be built.
- **PRD silent on a constraint the source enforces.** Example: a config
  cap, an existing rate limit, a foreign-key constraint that the PRD
  ignores.
- **PRD references infrastructure as if it doesn't exist.** Example:
  "log-and-forget" notification when a Temporal workflow engine is already
  running in the same backend.
- **PRD uses defaults that don't match real defaults.** Example: PRD says
  session is "infinite" when the auth provider's actual default is 1 hour
  (the magic-link case).

**Default reconciliation mode is "appended audit trail."** Don't try to
edit the PRD body in place by default — most teams find inline edits to
PRD prose too disruptive (they conflict with concurrent edits, they fight
the PRD author's voice, they're hard to undo). Instead, the default
output of the reconciliation pass is a single appended section at the
bottom of the PRD called "Design Review — Reconciliation Pass
({date})" containing a table of (Discrepancy → Resolution → Source).
The table grows over the lifetime of the PRD; readers cross-reference.

Surgical edits to the PRD body are **opt-in per discrepancy**. When the
user explicitly chooses "apply surgical edit," follow the inline-edit
workflow below. Otherwise the discrepancy goes into the appended table
and the PRD body stays untouched.

For each discrepancy, run **one** `AskUserQuestion` call following
grill-me's discipline. **Critical: when the question involves a
multi-paragraph diff, put the OLD/NEW text in the question body
(plainly, not in code blocks that may be hard to scan), not buried
inside option labels or descriptions.** A user who has to read 200
words of option text to understand what they're choosing will skip the
edit. Question body is for context; options are for the choice itself.

```
AskUserQuestion(question="""
[Reconciliation: <one-line discrepancy summary>]

<What the PRD says verbatim — quote it.>

<What the source actually shows — cite the file path and ref.>

How do we resolve?

Options:
  A) Update the PRD to match source — I edit the Confluence page now.
  B) Keep the PRD claim, treat as scope addition — new Story will exist.
  C) Keep the PRD claim, drop the work — note in decisions.md as
     deferred-to-V2 with the reason.
  D) Other (describe).

My recommendation: <letter> — <concrete reason, grounded in the source
audit, in dependencies.md, or in user-visible impact>.
""")
```

After the user resolves a discrepancy:

1. **Append the reconciliation to `decisions.md`.** Add a row with: the
   discrepancy, the chosen resolution, the date, and the user.
2. **If the chosen resolution is A or C**, build the corresponding edit to
   the PRD body. Edits to PRD prose should be small and surgical — replace
   the false sentence with the correct one, not rewrite the section. Add
   a Confluence panel-info block at the bottom of the section saying
   "Updated 2026-MM-DD via prd-to-features reconciliation: see
   decisions.md row N."
3. **Apply the PRD edit via `updateConfluencePage`.** Bump the version
   number, set `versionMessage` to "Reconciliation pass — source audit
   discrepancy resolved (decisions.md row N)". Use `contentFormat:
   markdown` and pass the full updated body.
4. **If the chosen resolution is B (scope addition)**, no PRD edit yet —
   the new Story will surface the addition explicitly in Step 5's
   confirmation summary, and the PRD body update can come later as part
   of the Epic's "delivered" close-out.

**Refuse to proceed to Step 4 (Story enumeration) until every discrepancy
is resolved AND every PRD write-back call has succeeded.** If a write-back
fails, retry once; if it fails twice, stop the skill and surface the
error so the user can fix the underlying Confluence issue.

If the source audit reveals **many** discrepancies (more than ~5), pause
and ask the user via `AskUserQuestion` whether to proceed
discrepancy-by-discrepancy (default) or whether the PRD is so out of date
that a fresh grill-me session is the right next step. The point is to
keep the PRD honest, not to hide a fundamental rewrite behind small
edits.

### Step 4 — Source-grounded Story enumeration

Stories come from grouping the file-level inventory into coherent
"changes-together" units. A Story is a set of files that:

- Implement one user-facing capability (one flow, one page, one feature
  toggle), AND
- Can be picked up by **one engineer on one stack** and shipped without
  coordinating mid-work with another engineer on a different Story.

**Always split FE and BE into separate Stories.** Most engineering teams
have specialised roles — a backend engineer ships the API, a frontend
engineer ships the UI that consumes it. Bundling both into one Story
forces sequential work and makes ownership ambiguous. Instead:

- The **BE Story** ships first, exposing a stable API contract. Its
  Success criteria are framed in terms of API behavior (correct status
  codes, response shapes, persisted DB state) — not in terms of UI.
- The **FE Story** is blocked-by the BE Story. Its Success criteria are
  framed in terms of user-visible behavior and what API calls happen
  under the hood. It can be developed against a stub of the API contract
  while the BE Story is in flight, but doesn't ship until the BE is in
  staging.
- Both Stories cite the **same API contract** in their respective Source
  files affected sections (typically a shared OpenAPI spec or a typed
  schema file).
- If a Story is purely BE (a migration, a workflow, an infra change) or
  purely FE (a UI-only change with no new API), it stays as one Story.

Stories that span infra changes (Terraform, Helm, WAF rules) are usually
their own third Story so the platform engineer can pick them up
independently.

Story sizing emerges from the inventory, not from a heuristic on PRD
length:

- Count NEW files + MODIFIED files in the Story's scope.
- A Story should fit roughly 5–15 file changes. Below 5 is usually too
  small and should be merged with an adjacent Story; above 15 is usually
  too big and should be split.
- For each Story, draft Tasks. Tasks are PR-sized — roughly half a day
  each, ~3–6 file changes — and each Task should be writable as a single
  PR title.

Sources of Stories beyond the PRD body:

- **Falsified-but-resolved rows in `dependencies.md`** that imply work the
  original PRD did not name (e.g., Vendor Portal row #13 → "GC-side
  invitation list inside Tender detail" became a whole Story the PRD
  claimed wasn't needed).
- **Missed-reuse rows.** Each becomes either a Task ("route the X flow
  through the existing Temporal workflow") or a separate Story if the
  reuse work is substantial.
- **Open follow-ups in `decisions.md`** that need a Story to land before
  the parent Story can ship.

### Step 5 — Gap surfacing (inline grill-me discipline)

For each draft Story, ask yourself: **can I write this Story file
precisely without inventing any new design decision?** The Story file has
to specify files affected, acceptance criteria, and tasks. If any of those
would require silently choosing between two plausible designs, the Story
has a gap.

When a gap surfaces, apply grill-me's discipline directly here — don't
write "TODO" or "open question" into the Story output:

1. **Phrase the question with options + recommendation.** Use the same
   pattern grill-me uses:

   ```
   AskUserQuestion(question="""
   [Story: <story name>] <The question — one sentence, clear>

   Options:
     A) <option one>
     B) <option two>
     C) <option three if applicable>
     D) Other (describe)

   My recommendation: <letter> — <concrete reason, 1–2 sentences,
   grounded in the source code or in dependencies.md if relevant>
   """)
   ```

2. **Append the resolution to `decisions.md`.** Add a new row to the
   Decision Summary table noting the new decision, who decided, and what
   Story it's for. This keeps the central design record complete.

3. **If the gap is a new external dependency** (third-party API, library,
   protocol), append a new row to `dependencies.md` with the same status
   discipline as grill-me (✅ VERIFIED / 🟡 ACCEPTED-RISK / ❌ ASSUMED).
   Refuse to write the Story file until that row resolves to ✅ or 🟡.

4. **If the gap is structural and large** (multiple Stories' worth of new
   design questions), STOP and tell the user: "this breakdown surfaced N
   design questions that warrant a fresh grill-me session, not inline
   resolution. Run grill-me on the following sub-questions, then return."
   List the questions. Don't try to absorb a major design re-think inside
   the breakdown.

The boundary between AskUserQuestion (for skill-mechanical questions) and
the gap-surfacing pattern above (for design questions): **AskUserQuestion
without options** is for filling in things the **skill** needs (which Jira
project, which repo, confirm before creating). The **options +
recommendation** pattern is for filling in things the **design** needs (what
should the user see, what state machine governs this, what's the contract
with this third party).

### Step 6 — Confirm before writing or creating

Present the full planned breakdown via `AskUserQuestion`:

- The Epic title.
- Each Story: title, repo, file count (NEW + MODIFIED), days estimate, task
  count.
- Total counts: N Stories, M Tasks.
- **Discrepancies surfaced**: any Story that exists because of a falsified
  PRD claim should be flagged here, with a one-line note.

Options:

- **Confirm and create** — proceed to write files + create Jira.
- **Revise sizing** — split or merge specific Stories.
- **Drop scope** — remove specific Stories (defer to V2 etc.).
- **Other** — free-text revision.

Don't write any files or create any tickets before this confirmation. File
and ticket creation are not free to undo.

### Step 7 — Write files and create Jira

Order matters because each Story file gets a Jira key back-written into its
header:

1. **Number the Story files.** For each affected repo, scan
   `<repo>/.specs/features/` for existing files. Find the highest existing
   numeric prefix. The first new Story gets the next integer. If the
   directory doesn't exist, create it.
2. **Create the Jira Epic.** Use the auto-detected project (Step 1). Title
   = the Epic title agreed in Step 5. Description = a short summary of the
   PRD plus the Confluence link plus the initiative.
3. **For each Story, in display order:**
   a. Write the Story file to `<repo>/.specs/features/NN_slug.md` (template
   below). Leave the `Jira:` line as `TBD` initially.
   b. Create the Story in Jira, linked to the Epic via "is part of" or the
   Epic Link field (depending on Jira project type). Use the Story title
   and a description that points at the Story file path.
   c. **Back-write the Jira Story key** into the .md file's header line.
   d. **For each Task** under the Story, create a Sub-task (or Task with
   "blocks" link to the Story, depending on project type).
   e. Back-write each Task's Jira key into the Story file's `## Tasks`
   section.
4. **Print a summary** with the Epic key, Story keys, file paths, and a
   one-line per-Story note about anything notable (e.g., "Story 3 was
   gap-resolved inline — see new dependencies.md row #16").

If any Jira create call fails, write the error inline into the Story file's
`Jira:` line as `Jira: CREATE-FAILED — {error}` so the file is still useful
and the failure is visible.

## Story file template (use verbatim)

The Story file's job is to make the work pickup-able by any engineer
without follow-up questions to the author. That means: clear language (no
shorthand), success criteria phrased as binary observable outcomes, and a
test plan concrete enough that the engineer can copy-paste commands to
verify their own work. If a Story file can't be handed to a stranger and
shipped end-to-end, it isn't done.

```markdown
# {Story Title — written as a sentence, not a label}

**Epic:** {EpicKey}: {EpicTitle}
**Jira:** {StoryKey}
**Repo:** {repo name}
**Branch base:** {branch this Story should be built off}
**File changes:** {N} new, {M} modified
**Estimated:** {N} days
**Status:** todo

## Goal
{One paragraph — what this Story accomplishes and why. Plain English, no
jargon. A new joiner should understand it without reading the PRD.}

## User-visible behavior
{What changes for the end user when this ships. If no user-visible change
(pure infra/migration), say "No user-visible change — infrastructure for
X" and explain what X enables.}

## Source files affected
- `relative/path/file.ts` — NEW — {what it does, why it's new}
- `relative/path/other.tsx` — MODIFIED — {what changes and why}
- `relative/path/migrations/V42__add_x.sql` — NEW — {what it migrates}

## Success criteria
Each criterion is a binary, observable outcome. If a human can't say
"yes/no, this is satisfied" by looking at the running system, the
criterion is too vague — rewrite it.

1. {Specific outcome 1, written as a complete sentence}
2. {Specific outcome 2}
3. {Specific outcome 3}

## Test plan
The engineer who builds this Story uses this section to verify their own
work end-to-end before opening a PR. Reviewer uses it to verify nothing
regressed.

### Automated tests
- `path/to/test_file.spec.ts` — {what the test asserts}
- `path/to/other_test.kt` — {what the test asserts}

### Manual API verification
Concrete steps with copy-pasteable commands. Replace `{ENV}` with `staging`
or `local` as appropriate.

**1. Get an auth token:**
Use the **get-test-token** skill — pass the test username/email and
password for the role you need (e.g. a vendor account, a GC account, an
admin account). The skill handles the provider-specific exchange and
prints the JWT plus an `export ACCESS_TOKEN=...` line you can paste.

Example invocation: "Use get-test-token with email
`vendor-test@example.com` for staging Supabase."

If get-test-token isn't installed, fall back to the project's auth flow
inline (Supabase example):
```bash
curl -X POST 'https://{ENV}.supabase.co/auth/v1/token?grant_type=password' \
  -H 'apikey: ${SUPABASE_ANON_KEY}' \
  -H 'Content-Type: application/json' \
  -d '{"email":"vendor@acme.com","password":"..."}'
```

**2. Call the new/changed endpoint:**
```bash
curl -X POST 'https://{ENV}.tosspaper.com/v1/{endpoint}' \
  -H 'Authorization: Bearer ${ACCESS_TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{"...example payload..."}'
# Expected: HTTP 200 with body { ... example response ... }
# Expected on failure path: HTTP 4xx with body { "error": "..." }
```

**3. Verify database state:**
```sql
-- Check the row was written as expected
SELECT id, vendor_email, status, supabase_user_id, viewed_at
  FROM invitations
  WHERE id = '<INVITATION_ID>';
-- Expected: status = 'viewed', supabase_user_id IS NOT NULL,
-- viewed_at within the last minute.
```

### Manual UI smoke test
Numbered steps a non-engineer could follow.

1. {Step 1 — exact action and expected result}
2. {Step 2}
3. {Step 3}

### Edge cases to verify
- {Edge case 1 + how to trigger it + expected behavior}
- {Edge case 2}

## Tasks
1. **{Task title written as the PR title}** ({TaskKey}) — ~{N}h
   - {one or two bullets describing what to do, what to test}
2. **{Task title}** ({TaskKey}) — ~{N}h
   - {one or two bullets}

## Definition of done
- [ ] All Success criteria above are observably satisfied in staging.
- [ ] Automated tests in the Test plan all pass in CI.
- [ ] Manual API + UI verification steps were run by the author and
  attached output (or screenshots) in the PR description.
- [ ] Reviewer ran at least one manual verification step independently.
- [ ] No new ACCEPTED-RISK rows added to `dependencies.md` without an
  explicit decision to ship anyway.

## Dependencies
- Blocks: {Story keys this enables}
- Blocked by: {Story keys that must land first}
- External (from PRD ledger): {row #s in dependencies.md this Story relies on}

## Related decisions (from decisions.md)
- {Decision row this Story implements, copied verbatim}

## Open risks (from dependencies.md)
- {ACCEPTED-RISK rows that affect this Story, if any — copied verbatim so
  the on-call engineer who picks up this Story knows what they're shipping}
```

## Confluence space → Jira project mapping

Maintain a small JSON config alongside the skill:

```json
{
  "spaceToProject": {
    "Tosspaper": "TOS"
  },
  "lastUpdated": "2026-04-25"
}
```

When the skill encounters a Confluence space not in the map, ask the user
once via `AskUserQuestion` for the matching Jira project key, then append
to the config. The skill uses `getVisibleJiraProjects` to validate the
project key exists before persisting.

If the config file doesn't exist on first run, create it with `{}`.

## Failure modes — what to refuse, not paper over

- **Missing grill-me artifacts** — refuse to start; tell the user to invoke
  grill-me on the PRD first. Do not try to grill from scratch inside this
  skill — that's grill-me's job. This is the most common failure mode and
  the most important one to enforce; without it the skill devolves into
  unstructured ticket-creation.
- **A Story can't be precisely written even after gap-surfacing** — write
  the unresolved question into the Epic description as a blocker, do NOT
  write that Story file or its Jira ticket. Print clearly which Stories
  were blocked.
- **Multiple unresolved gaps in one breakdown** — STOP and tell the user
  the breakdown surfaced enough new design questions that a fresh grill-me
  session is the right next step, not inline resolution.
- **Confluence/Jira API errors** — if the Confluence read fails, stop. If
  Jira creation fails partway, leave a clean failure trail (CREATE-FAILED
  in the Jira: line of each affected Story file) so the user can resume
  manually.
- **Repo is not mounted AND GitHub access also fails** — stop after Step 1.
  The skill cannot produce useful Stories without source access; faking it
  produces fictional file paths that send engineers on wild-goose chases.
- **Source audit reveals the PRD is heavily out of date.** Don't stop
  silently — that's exactly what Step 3's reconciliation pass exists to
  prevent. Walk every discrepancy, write resolutions back to Confluence,
  and only escalate to "stop and re-grill" if the user explicitly chooses
  that path during reconciliation (more than ~5 discrepancies should
  trigger that escalation prompt automatically).
- **PRD write-back fails** — if `updateConfluencePage` fails twice on the
  same edit, stop and surface the error. Don't write Stories whose
  reconciliation never landed in the source-of-truth doc.

## Heuristics that catch missed scope

- **PRD claims about existing UI / existing infra.** Phrases like "no new
  UI work required", "the existing X already handles this", "we just reuse
  Y" are an explicit signal to grep the named component on the current
  branch and verify. If the claim is false, a new Story is required and the
  PRD claim must be retracted in `decisions.md` (and ideally back-edited
  in the Confluence PRD body too).
- **Falsified PRD claims in `dependencies.md`.** Every `❌ FALSIFIED` row
  is a candidate for a new Story (the resolution to the falsification often
  IS the Story).
- **Missed-reuse rows in `dependencies.md`.** Every `❌ MISSED-REUSE` row
  either becomes a Task ("route the X flow through the existing Y") or is
  explicitly noted as "decision: do not reuse — see `decisions.md` row N."
- **Accepted-risk rows in `dependencies.md`.** Each ACCEPTED-RISK row
  should appear in the "Open risks" section of every Story it affects, so
  the on-call engineer who picks up that Story knows what they're
  shipping.

## Worked example — for the Vendor Portal PRD

Inputs:

- PRD: [PRD] Vendor Portal (Confluence page 13828097)
- Initiative: vendor-portal
- decisions.md, dependencies.md from the 2026-04-25 grill-me session

Affected repos (auto-detected from decisions.md + dependencies row sources):

- `tosspaper-frontend` on `dev` — vendor portal UI + GC-side invitation
  list (the scope expansion from row #13)
- `tosspaper` on `main` — Java API for vendor auth, invitation, RFI,
  addenda
- `tosspaper-flyway` on `main` — companies table migration

Source audit highlights:

- `tosspaper-frontend/components/tenders/tender-detail.tsx` exists, has 5
  tabs, **zero invitation/vendor/Resend references** → the PRD's "no new UI
  work required" claim is FALSE → new Story required for GC-side
  surface.
- `tosspaper/temporal/` directory exists → the PRD's "log on failure"
  notification model has a better alternative → Story 9 below.
- `tosspaper/disposable_email_blocklist.txt` exists (66KB) but is for a
  different policy goal than personal-email-blocking → adopt a maintained
  library that covers both classifications.
- `tosspaper/nginx/nginx.conf` confirms per-instance rate limiting → Story
  10 below moves it to WAF.

Stories the skill would propose (all sized from source-level file
inventory, not PRD text):

1. **Companies table foundation migration** (`tosspaper-flyway`) — adds
   `domain` + `domain_hash`, ships first. ~3 file changes. 1 day.
2. **Personal-domain blocklist library integration** (`tosspaper`) — adopt
   the chosen library, wire into sign-up. ~5 file changes. 1 day.
3. **Vendor authentication flow** (`tosspaper` + `tosspaper-frontend`) —
   `admin.getUserByEmail`, `admin.generateLink`, set-password page,
   sign-in page, hard-sign-out UX. ~12 file changes. 3 days.
4. **Vendor invitation dashboard + detail page** (`tosspaper-frontend`) —
   list, detail, intent-to-bid controls. ~10 file changes. 2 days.
5. **Document download with redownload affordance** (`tosspaper` +
   `tosspaper-frontend`) — pre-signed URL endpoint, list UI. ~6 file
   changes. 1 day.
6. **RFI question + reply flow** (`tosspaper` + `tosspaper-frontend`) —
   submit, list, GC reply, in-app + email notifications. ~10 file
   changes. 2 days.
7. **Vendor org auto-provisioning** (`tosspaper`) — sha256 lookup,
   create-or-join, race resolution. ~8 file changes. 2 days.
8. **GC-side invitation list inside Tender detail**
   (`tosspaper-frontend`) — the scope expansion from falsified row #13.
   New tab/section, response status column, Resend button (state-aware),
   Q&A modal. ~14 file changes. 4 days.
9. **Addenda fan-out via Temporal workflow** (`tosspaper`) — replaces the
   PRD's "log on failure" model per row #15 missed-reuse resolution. ~6
   file changes. 1 day.
10. **Rate limit moves from Nginx to WAF for vendor API** (`tosspaper` +
    infra) — verify-email zone + general vendor zones. ~4 file changes,
    plus terraform/WAF rules. 1 day.

Each Story file lands at the corresponding repo's
`.specs/features/NN_<slug>.md`. One Epic in the TOS Jira project, 10
Stories linked to it, ~30 Tasks under those Stories.

Stories 8, 9, and 10 didn't exist in the PRD body — they came from
falsified / missed-reuse ledger rows surfaced during the original
grill-me session. That's the value of requiring grill-me artifacts as
input AND of source-grounded sizing.
