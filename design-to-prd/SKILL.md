---
name: design-to-prd
description: Turn a design document (PDF design spec, Figma export, or markdown design notes) into a high-level Product Requirements Document (PRD) and publish it to Confluence. Use whenever the user mentions writing a PRD, drafting product requirements, "PRD from design", "high-level requirements doc", "spec from this design", or shares a design file and asks for a requirements doc. Also trigger when the user has a design ready and needs a written artifact for leadership and engineering — even if they don't say the word "PRD". The skill produces a structured PRD aimed at both executive readers (TL;DR, problem, success metrics) and engineering readers (functional requirements, key flows, dependencies), then publishes the result as a Confluence page.
---

# Design-to-PRD

Turn a design document into a high-level Product Requirements Document (PRD) and publish it as a Confluence page.

## When this skill applies

The user has a design artifact (PDF, markdown, or design notes) and needs a written PRD. The PRD is high-level — it captures the *why*, *who*, *what*, and *how we'll measure it*, not detailed engineering tasks. The audience is mixed: leadership skims the top, engineering reads the requirements and flows.

## Inputs you'll typically receive

- A **PDF** design spec (exported from Figma, Sketch, or written as a design doc)
- A **markdown / plain text** file with design notes, flows, and rationale
- Sometimes both, or a design plus a short verbal brief

If neither the design nor the user supplies a piece of information that the PRD needs (e.g., success metrics, target launch date), don't invent it. Mark the section `**TBD — needs input from PM/leadership**` and list the open question at the bottom. A PRD that admits its gaps is more useful than one that bluffs.

## Workflow

Follow these steps in order.

### 1. Read the design fully before writing anything

Use the `pdf` skill (or its scripts) for PDFs, and read markdown files directly. Don't skim — extract:

- The user problem the design addresses
- Who the design is for (personas, segments, roles)
- The flows being designed (entry points, key screens, success states, edge cases)
- Anything the designer explicitly called out (e.g., "this is for low-data environments", "we're optimizing for first-time users")
- Dependencies the design implies (auth, payments, third-party APIs, existing components)

If the design is image-only and you can't read text from it, tell the user what you need (a written brief, or an annotated version) before proceeding.

### 2. Confirm the basics with the user

Before writing the full PRD, confirm or fill in three things if they aren't obvious from the design:

1. **Project / feature name** — what's this called?
2. **Target audience for the PRD** — leadership + engineering by default, but ask if there are other readers (legal, marketing, support).
3. **Confluence space and parent page** — where should it be published? Use `getConfluenceSpaces` and `getPagesInConfluenceSpace` if you need to look these up.

Keep this short. One round of questions, not an interrogation.

### 3. Draft the PRD using the standard structure

Use the section template in `references/prd-structure.md`. Read it before drafting — it has guidance on what each section should and shouldn't contain, plus example phrasings.

The structure (in order) is:

1. **TL;DR** — 3–5 sentences a busy exec can read in 30 seconds
2. **Context & Problem** — what's broken/missing today, evidence
3. **Goals & Non-Goals** — what success looks like, and explicitly what we're not doing
4. **Target Users** — personas or segments, with the primary one called out
5. **Solution Overview** — high-level description of what we're building, with references to the design
6. **Key User Flows** — the 2–4 most important journeys, narrated
7. **Functional Requirements** — grouped, high-level (not engineering tasks); each requirement starts with "The system must…" or "Users can…"
8. **Success Metrics** — how we'll know it worked, with target numbers if known
9. **Dependencies & Risks** — what we rely on, what could derail us
10. **Out of Scope** — explicitly excluded, with brief reason
11. **Open Questions** — anything unresolved, tagged with who needs to answer

### 4. Write for two audiences in one document

A high-level PRD has to work for both leadership and engineering. The way to do this is structural, not by writing two versions:

- **TL;DR, Problem, Goals, Success Metrics** are the leadership read. Lead with business framing — user pain, opportunity size, what success looks like in numbers. No implementation detail here.
- **Solution Overview, User Flows, Functional Requirements, Dependencies** are the engineering read. Be specific about behavior, edge cases, and what the design implies technically — but stay at the requirements level, not the implementation level. "The system must persist draft state across sessions" is a requirement; "use IndexedDB with a 7-day TTL" is implementation.

If you find yourself writing implementation details (specific libraries, schema fields, API endpoints), pull back. That belongs in a tech design doc, not a PRD.

### 5. Reference the design, don't re-describe it

Every PRD section that talks about the user experience should link to or cite the relevant design artifact rather than trying to reproduce it in prose. If the design is a PDF on disk, mention the page number. If the user gave you a Figma link, use it. The PRD's job is to say *why* and *what*, not to re-render the design.

### 6. Publish to Confluence

Once the draft is ready, show it to the user as markdown for a quick review. Ask: "Anything you want to change before I publish it to Confluence?" Then use `createConfluencePage` to publish:

- Pass the markdown content as the page body — Confluence accepts a Wiki-style format. If the connector requires Atlassian Document Format (ADF) or storage format, convert from markdown first using the conventions in `references/confluence-publishing.md`.
- Set a clear title: `[PRD] <Feature Name>` is a good default unless the user has a different convention.
- Place it in the space and under the parent page the user specified.

After publishing, share the Confluence URL with the user. Don't paraphrase what's in the doc — they can read it.

## Style notes

- **High-level means high-level.** Resist the urge to fill space. A great high-level PRD is often 1–2 pages of dense prose plus a flows section, not an exhaustive document.
- **Use plain language.** No "leveraging synergies". Write the way you'd brief a smart colleague who's new to the project.
- **Bullet sparingly.** Use prose for context and rationale; reserve bullets for genuinely list-shaped content (requirements, non-goals, open questions).
- **Mark gaps explicitly.** `**TBD — needs input from <role>**` is better than vague hand-waving.
- **Numbers earn their keep.** If you cite a metric or impact, name the source (analytics dashboard, user research, support ticket volume) or mark it as an estimate.

## What to avoid

- Inventing personas, metrics, or business context that aren't in the design or confirmed by the user.
- Padding sections to look thorough. Empty sections marked TBD are more useful than fabricated ones.
- Writing implementation specifics (libraries, schemas, API design) — that belongs in a tech design doc.
- Restating the design in prose. Reference and link instead.
- Skipping the open-questions list. Even a polished PRD has unresolved things; surfacing them makes the doc more useful, not less.

## Reference files

- `references/prd-structure.md` — Section-by-section template with what to include, what to avoid, and example phrasings. **Read this before drafting.**
- `references/confluence-publishing.md` — How to format and publish to Confluence, including markdown→ADF conversion notes and title conventions.
- `references/example-prd.md` — A complete example PRD generated from a design doc, for tone and structure reference.
