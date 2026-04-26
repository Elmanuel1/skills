---
name: synthesize-tech-docs
description: Write the engineering technical documentation for a new feature by synthesizing three required sources together — the PRD, the design doc, and the actual code. The PRD supplies the why, scope, and success metrics; the design doc supplies the UX intent and user flows; the code supplies ground truth on what's built. Produces a README, an architecture/system overview, and/or an API reference, saved as markdown locally with optional Confluence publishing. Use whenever a user is documenting a new feature and needs tech docs that carry full context, mentions "tech docs for a new feature", "engineering docs from the PRD, design, and code", "document this new feature using all our sources", "write engineering docs that match what we built and explain why", or shares a PRD + design + repo and asks for tech docs. The skill refuses to proceed with all three sources missing — a tech doc for a new feature without the PRD has no why, without the design has no UX intent, without the code has no truth. It also surfaces mismatches between PRD/design intent and code reality as explicit findings.
---

# Synthesize Tech Docs

Write the engineering documentation for a **new feature** by reading three sources together — the PRD, the design doc, and the actual code — and synthesizing them into docs that carry full context.

Produces up to three artifacts: a **README**, an **architecture / system overview**, and an **API reference**.

The unique value of this skill (vs. PRD-only or code-only doc generators) is **synthesis** for a new-feature doc: each section weaves the right level of context from the right source, and the skill surfaces where intent (PRD/design) and reality (code) disagree.

## When this skill applies

The user is documenting a **new feature** and has all three sources: a PRD, a design doc, and a codebase (local folder or GitHub repo).

Strong triggers:
- "Tech docs for a new feature"
- "Engineering docs from the PRD, design, and code"
- "Document this new feature using the PRD, design, and the code"
- "Write tech docs that match what we built and explain why"

## All three sources are required — don't proceed without them

A tech doc for a new feature without the PRD has no *why*. Without the design it has no *UX intent*. Without the code it has no *truth* — only aspiration. If any of the three is missing, **stop and ask the user for it before drafting**.

Acceptable phrasings if a source is missing:

- "I need the PRD before drafting — for a new-feature doc, the why and the scope have to come from the PRD, not from me. Where can I find it?"
- "I need the design doc — engineers reading this will want the UX intent, and that's not extractable from the code. Where is it?"
- "I need access to the code — without it, the doc is speculation. Local folder path or GitHub repo?"

If the user genuinely doesn't have one of them (e.g., the design lives only in Figma and there's no written design doc), ask them to capture the relevant intent in a few sentences before proceeding. A short written design summary is enough — a tech doc on a new feature can't fairly skip UX intent.

If the user pushes ahead without one, comply but flag clearly at the top of every produced doc:

> ⚠️ **Drafted without [PRD / design doc / code access].** Sections that depend on the missing source are marked TBD. This doc should be revised once that source is available.

## How the three sources fit together

Each source carries a different kind of truth, and each section of each doc uses them differently.

| Source | What it provides | What it's *not* good for |
|---|---|---|
| **PRD** | Why we built it, scope/non-goals, success metrics, target users, dependencies | The implementation reality (might be stale, aspirational, or wrong) |
| **Design doc** | User flows, UX intent, accessibility considerations, screen-by-screen behavior | Backend architecture, API shape, infrastructure |
| **Code** | What's actually built — endpoints, schemas, components, config, deps | Why it was built, what was deliberately left out, business framing |

The hard rule: **code is ground truth**. When the PRD says "we support .docx uploads" but the code only handles `.csv`, the doc says ".csv only — PRD references .docx but no code path was found" and flags it. Don't paper over the gap.

## Workflow

### 1. Confirm all three inputs are available before anything else

Ask once, briefly:

1. **PRD** — file path or link. *Required.*
2. **Design doc** — file path or link. *Required.*
3. **Code** — local folder path or GitHub repo (org/name + branch). *Required.*
4. **Which docs do you want?** README, architecture overview, API reference — any subset. Default: ask.
5. **Where should output land?** Markdown local. Plus Confluence? If yes, which space and parent page.

If any of the first three is missing, stop and ask for it. Do not start drafting against a missing source — the resulting doc will mislead the engineers reading it.

The only exception: if the user has explicitly accepted the trade-off and asked you to proceed without one, comply but stamp the warning callout from the top of this skill on every produced doc.

### 2. Read the PRD and design doc first

Read these *before* surveying the code. They tell you what the feature is supposed to do and give you the vocabulary the team uses. Skipping this step and going straight to the code is a common failure mode — without the product framing, the resulting docs read like reverse-engineered notes.

From the **PRD**, extract:
- The product goal and one-line summary
- Target users and primary persona
- Success metrics (carry verbatim — eng wants the same numbers as PM)
- Functional requirements (these become the spine of "what the system does")
- Out-of-scope items (these become explicit non-goals in tech docs)
- Dependencies and risks (carry verbatim)

From the **design doc**, extract:
- Key user flows (these inform the API reference's "example call sequence" and the architecture overview's "request paths")
- UX intent / decisions designers want preserved (e.g., "always show file size limit before upload")
- Accessibility, locale, or platform constraints

Use the `pdf` skill for PDF inputs and read markdown directly.

### 3. Survey the codebase

Don't draft until you've built a structural map. Use the survey checklist in `references/codebase-survey.md`. The high-level steps:

1. **Project type** — manifest files (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`). Note language(s), framework(s), declared scripts.
2. **Directory map** — top two or three levels with what each folder holds. Use `scripts/dir_summary.sh`.
3. **Entry points** — `main.*`, `index.*`, `app.py`, `cmd/*/main.go`, etc.
4. **API surface (if any)** — OpenAPI/Swagger files, GraphQL schemas, route registrations, gRPC `.proto`. Use `scripts/find_routes.sh`.
5. **Config surface** — env vars, config files, secrets schema. Use `scripts/list_env_vars.sh`.
6. **Data layer** — schemas, migrations, ORM models, DB clients.
7. **Build/deploy** — Dockerfile, CI configs, Helm/Terraform/k8s manifests.
8. **Existing docs** — partial READMEs, comments-as-docs, ADRs. Don't duplicate; extend or link.

For GitHub repos, use the connector tools (`get_file_contents`, `search_code`, `list_branches`). For local folders, work directly with the mounted path.

### 4. Cross-reference: PRD/design vs. code

For each major requirement in the PRD, find the code that implements it. Two things to capture:

- **Implementation citations** — "PRD requirement: 'system must validate file format before upload'. Code: client-side validation at `src/upload/validate.ts:23`, server-side backstop at `api/handlers/upload.go:91`."
- **Discrepancies** — anything in the PRD or design not visible in the code, or anything in the code not described in the PRD/design. Examples:
  - "PRD section 5.2 mentions email digest support; no scheduling code found. Either deferred or missing."
  - "Code includes a `/admin/feature-flags` endpoint not mentioned in the PRD or design. Likely an internal tool — confirm with engineering."
  - "Design pp. 7–8 specify a diff modal for sync conflicts; code resolves with last-write-wins silently."

Discrepancies aren't bugs in the doc — they're the most useful thing the doc can surface. They go in a "PRD/design vs. code" callout near the top of the architecture overview.

### 5. Decide which doc(s) make sense

Push back gently if a requested doc doesn't fit:

- **No API surface** in the code → skip the API reference (or document the CLI/library interface instead). Tell the user.
- **Tiny codebase** → fold architecture into the README rather than producing a separate doc.
- **Existing good docs** → extend rather than overwrite. Show the user what exists first.

### 6. Draft each doc, weaving the three sources

Read the relevant template in `references/`:

- `references/readme-template.md` — README structure
- `references/architecture-overview-template.md` — Architecture overview structure
- `references/api-reference-template.md` — API reference structure

Each template explains how to weave PRD context, design intent, and code reality into each section, with example phrasings.

**Audience and emphasis differ across the three docs:**

- **README → onboarding engineers.** What it is (one-line PRD summary) → how to run it locally (from code: scripts, env vars, docker) → where to look first (from code: directory map). Light on PRD/design, heavy on code.
- **Architecture overview → tech leads and reviewers.** Context (PRD's product scope) → user flows (design) → components and data flow (code) → integration points and deps (code, cross-checked with PRD) → trade-offs and decisions (code reality vs. PRD intent). All three sources, balanced.
- **API reference → cross-team integrators.** What the API does (PRD one-liner) → auth and conventions (code) → per-endpoint detail (code, with a request/response example pulled or extrapolated from real handler code). Heavy on code; PRD provides framing only.

**Cite the code on every concrete claim.** "The service uses JWT auth (issued at `POST /auth/login` — see `src/auth/routes.ts:42`)." Citations make the doc verifiable.

### 7. Save markdown locally, then optionally publish

Default local layout:

```
<service-name>-tech-docs/
├── README.md
├── architecture-overview.md
└── api-reference.md
```

For Confluence, follow `references/confluence-publishing.md`. Title format default:

- `[Eng] <Service Name> — README`
- `[Eng] <Service Name> — Architecture Overview`
- `[Eng] <Service Name> — API Reference`

Publish all three under the same parent page. Cross-link between them using the URLs returned from the create call. Also link back to the PRD and design doc in the architecture overview's "References" section.

### 8. Hand back

Return:

- Markdown paths (and Confluence URLs)
- A short list of TBDs the doc surfaced ("3 things flagged as not determinable: SLO target, on-call rotation, DR plan")
- The PRD/design vs. code discrepancies (these are the most consequential thing — call them out explicitly)

Don't paraphrase the docs.

## Style notes

- **Engineers, not executives.** Skip the marketing framing — that lives in the PRD. Open each doc with technical context.
- **Cite specific files.** `src/auth/routes.ts:42` beats "the auth module".
- **Show real commands and config.** If the README says "run `make dev`", that target must exist in the Makefile.
- **Diagrams as ASCII when small enough.** Boxes-and-arrows in monospace beat no diagram. For richer diagrams, leave a placeholder.
- **Code blocks for code, not prose.** Real commands, schemas, config — not narration.
- **Cross-link the three docs and back to PRD/design.** Engineers move between them; navigation should be obvious.
- **Make discrepancies visible, not buried.** A "PRD/design vs. code" callout near the top of the architecture overview is the single most useful addition this skill produces.

## What to avoid

- **Inventing facts.** No made-up endpoints, schemas, env vars, commands. If you didn't see it in the code, mark it TBD.
- **Letting the PRD override the code.** If the PRD says one thing and the code does another, the code wins for the doc — but the discrepancy gets surfaced.
- **Generic best-practice boilerplate.** "Use semantic versioning" / "Follow REST conventions" — noise. Either say something specific or omit.
- **Paraphrasing the code.** A doc that narrates every function is worse than one that names entry points and sends you to the source. Stay at *what does this system do*, not *what does this function do*.
- **Skipping citations.** Every concrete claim should be traceable.
- **Glossing over discrepancies.** They're the most valuable thing the doc surfaces — name them.

## Reference files

- `references/codebase-survey.md` — Survey checklist with patterns for popular stacks
- `references/readme-template.md` — README structure with PRD/design/code weaving notes
- `references/architecture-overview-template.md` — Architecture overview structure with cross-reference callout format
- `references/api-reference-template.md` — API reference structure with per-endpoint format
- `references/confluence-publishing.md` — Confluence publishing conventions

## Bundled scripts

- `scripts/find_routes.sh` — Find HTTP route declarations across common frameworks
- `scripts/list_env_vars.sh` — Find every env var reference in the code
- `scripts/dir_summary.sh` — Two-level directory tree with file counts
