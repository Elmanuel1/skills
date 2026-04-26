# PRD Section Template

Use this as the structure for the PRD. Each section below describes what belongs in it, what does *not* belong in it, and shows example phrasings.

The PRD is high-level. It should answer:
- **Why** are we doing this? (Problem, Goals, Success Metrics)
- **For whom**? (Target Users)
- **What** are we building? (Solution Overview, User Flows, Functional Requirements)
- **What's in / out**? (Scope, Non-Goals, Out of Scope)
- **What could go wrong** or block us? (Dependencies, Risks, Open Questions)

It does *not* answer how we'll implement it — that's a tech design doc.

---

## 1. TL;DR

**Goal:** A busy exec reads this in 30 seconds and walks away with the gist.

**Length:** 3–5 sentences. One short paragraph. No bullets.

**Include:**
- The user problem in one sentence
- What we're building in one sentence
- The expected impact (with a metric if you have one)

**Avoid:** lists, jargon, anything you can't say in plain English.

**Example:**
> First-time users abandon onboarding at the document upload step at a 42% rate, mostly because they don't understand which file types are accepted. We're redesigning the upload step with inline format guidance, drag-and-drop affordance, and clearer error states. We expect this to reduce upload-step abandonment by 15 points and lift activation by 6%, based on prior funnel improvements in the same step.

---

## 2. Context & Problem

**Goal:** Make the reader feel the problem before you propose a solution.

**Include:**
- What's happening today (status quo)
- Who's affected and how
- Evidence: data, user research, support tickets, NPS comments
- Why now? (if relevant)

**Avoid:** describing the design or the proposed solution. Stay in the problem space.

**Example phrasings:**
- "Today, when a user first opens the app, they…"
- "Support has logged 312 tickets in the last quarter referencing…"
- "User interviews with 8 customers in the SMB segment surfaced…"

---

## 3. Goals & Non-Goals

**Goals:** 2–5 outcomes we're trying to achieve. Each goal is an outcome, not an output. "Reduce upload abandonment by 15 points" is a goal; "build a new upload component" is not.

**Non-Goals:** 2–5 things we're explicitly *not* trying to do, even though a reader might assume we are. This is one of the most-skipped, most-valuable sections — it prevents scope creep.

**Example:**
> **Goals**
> - Reduce upload-step abandonment from 42% to 27%
> - Activate 6% more new users (defined as: completed first import within 7 days)
> - Reduce upload-related support tickets by 50% within one quarter
>
> **Non-Goals**
> - Redesigning the broader onboarding flow
> - Supporting new file formats beyond what's currently accepted
> - Changing pricing or plan-gating around file size limits

---

## 4. Target Users

**Goal:** Be specific about who this is for. Vague answers ("our users") are a yellow flag.

**Include:**
- Primary persona (or segment) — the one whose problem this most centrally addresses
- Secondary persona(s) — who else benefits, in what way
- Edge cases the design considered (accessibility, low-bandwidth users, locale)

If personas exist in your org's research repo, link to them rather than redefining.

---

## 5. Solution Overview

**Goal:** In a few paragraphs, describe what we're building, anchored in the design.

**Include:**
- The core experience in one sentence
- Reference to the design artifact (link, file, or page numbers)
- The 2–3 most important UX changes from today

**Avoid:** screen-by-screen narration. The design itself does that. Don't reproduce it.

**Example:**
> The new upload step replaces the current single-button file picker with a drag-and-drop zone (see design pp. 3–5) that surfaces accepted file types inline and validates file format before upload completes. When validation fails, the error state explains *what* went wrong and *how to fix it*, replacing the current generic "upload failed" message.

---

## 6. Key User Flows

**Goal:** Narrate the 2–4 most important journeys end-to-end.

**Format:** Each flow is a numbered list of user actions and system responses, plus one or two callouts about edge cases.

**Example:**
> ### Flow 1: First-time user uploads a valid file
> 1. User lands on the upload step after creating their account
> 2. User sees the drop zone with three accepted formats listed inline
> 3. User drops a CSV file onto the zone
> 4. System validates locally; on success, file uploads with a progress indicator
> 5. On completion, user is routed to the next onboarding step
>
> *Edge cases:* If the user navigates away mid-upload, draft state is preserved and they can resume.

---

## 7. Functional Requirements

**Goal:** A grouped list of what the system must do. This is the section engineers will read most carefully.

**Format:** Group by area (e.g., "Upload zone behavior", "Validation", "Error handling"). Each requirement starts with "The system must…" or "Users can…". Stay at the level of behavior, not implementation.

**Example:**
> ### Upload zone
> - Users can drag a file onto the zone or click to open a file picker
> - The zone displays accepted file formats inline at all times
> - The zone changes visual state on drag-over to confirm the drop target
>
> ### Validation
> - The system must validate file format before initiating upload
> - The system must reject files larger than 50MB with an inline message naming the size limit
> - On validation failure, the system must keep the user on the upload step (no navigation away)

**Bad example (too implementation-specific):**
> - Use the `react-dropzone` library
> - Store files in S3 with a 7-day TTL

---

## 8. Success Metrics

**Goal:** Define how we'll know this worked. Numbers, not vibes.

**Include:**
- Primary metric (the one we're moving)
- Secondary metrics (supporting outcomes, guardrails)
- Counter-metrics (what we don't want to break)
- How long after launch we'll measure

If a target number isn't known, mark it `**TBD — needs input from PM**` rather than inventing one.

**Example:**
> **Primary**
> - Upload-step abandonment: 42% → 27% (measured 30 days post-launch)
>
> **Secondary**
> - 7-day activation rate: +6 percentage points
> - Upload-related support tickets: −50% within one quarter
>
> **Counter-metrics**
> - Time-to-upload-success: should not increase by more than 1 second
> - Overall onboarding funnel completion: should not decrease

---

## 9. Dependencies & Risks

**Dependencies:** What we rely on to ship this — other teams, services, design assets, third-party APIs, infra changes.

**Risks:** What could derail us, with a quick rating (low/med/high) and mitigation if known.

**Example:**
> **Dependencies**
> - Updated upload service endpoint (Platform team, expected by [date])
> - Localization of new copy strings (Loc team, ~2 weeks lead time)
>
> **Risks**
> - *Med:* Browser-side validation may not catch all malformed CSVs. *Mitigation:* server-side validation as backstop.
> - *Low:* Drag-and-drop UX is unfamiliar in some locales. *Mitigation:* click-to-upload remains available.

---

## 10. Out of Scope

**Goal:** Explicitly call out things readers might assume are included but aren't.

**Format:** Bulleted list with a brief reason for each.

**Example:**
> - Mobile web upload — being handled in a separate workstream (see [link])
> - New file format support — covered by a separate proposal in Q3
> - Redesign of the post-upload preview screen — out of scope for this milestone

---

## 11. Open Questions

**Goal:** A short list of unresolved things, each tagged with who needs to weigh in.

**Format:** Bulleted list. Tag with `[Owner: <role/name>]`.

**Example:**
> - Final target for upload-step abandonment metric — 27% is the team's estimate but not yet confirmed. [Owner: PM]
> - Whether to support .tsv files in v1. [Owner: PM + Eng]
> - Accessibility review pass on drag-and-drop interaction. [Owner: Design + a11y reviewer]
