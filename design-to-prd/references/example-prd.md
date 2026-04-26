# [PRD] Upload step redesign

## TL;DR

First-time users abandon onboarding at the document upload step at a 42% rate, mostly because they don't understand which file types are accepted or why their file was rejected. We're redesigning the upload step with inline format guidance, drag-and-drop affordance, and clearer error states. We expect this to reduce upload-step abandonment by 15 points and lift 7-day activation by 6%, based on prior funnel improvements in the same area.

## Context & problem

Today, when a new user reaches the upload step in onboarding, they see a single "Upload file" button with no inline guidance about accepted formats or size limits. If their file fails to upload, the system shows a generic "Upload failed — please try again" message with no detail.

Funnel analytics from the last 90 days show 42% of users who reach the upload step never complete it. Of those, 60% bounce within 30 seconds — a strong signal they're confused, not stuck on a slow upload.

Support has logged 312 tickets in the last quarter referencing the upload step. The top three themes:
1. "I don't know what file to upload" (42% of tickets)
2. "It says upload failed but doesn't tell me why" (31%)
3. "My file is too big" — but the size limit wasn't visible until after attempting upload (18%)

User interviews with 8 SMB customers in Q1 surfaced the same patterns and added a clear ask: surface format and size requirements *before* the user attempts to upload.

## Goals & non-goals

**Goals**
- Reduce upload-step abandonment from 42% to 27% (measured 30 days post-launch)
- Lift 7-day activation rate by 6 percentage points
- Reduce upload-related support tickets by 50% within one quarter

**Non-goals**
- Redesigning the broader onboarding flow
- Supporting new file formats beyond what's currently accepted
- Changing pricing or plan-gating around file size limits
- Mobile web upload (handled separately)

## Target users

**Primary:** First-time users in the SMB segment completing initial setup. They typically have a CSV or Excel export from another tool and limited patience for friction at this step.

**Secondary:** Returning users uploading additional files post-onboarding. Same UX, lower stakes since they've successfully uploaded before.

**Edge cases the design considered:**
- Low-bandwidth users (progress indicator must be informative, not vanishing)
- Screen reader users (drop zone must be keyboard-accessible and announce state changes)
- Users on locales where drag-and-drop UX is less common (click-to-upload always available)

## Solution overview

The new upload step replaces the current single-button file picker with a drag-and-drop zone (see design pp. 3–5) that surfaces accepted file types and the size limit inline at all times. File format is validated client-side before upload begins, and validation failures show specific, actionable error states (design pp. 6–7) instead of the current generic message.

Three UX shifts from today:
1. **Format guidance is always visible**, not hidden behind a tooltip or surfaced only on failure.
2. **Drag-and-drop is the default affordance**, with click-to-upload preserved as a secondary path.
3. **Errors are specific.** "File too large (max 50MB)" replaces "Upload failed."

## Key user flows

### Flow 1: First-time user uploads a valid CSV

1. User lands on the upload step after creating their account.
2. User sees the drop zone with "CSV, XLSX up to 50MB" inline.
3. User drags a CSV onto the zone.
4. System validates format and size locally; on success, upload begins with a percent-complete indicator.
5. On completion, user is routed to the next onboarding step.

*Edge cases:* If the user navigates away mid-upload, draft state is preserved. The next visit resumes the upload step with the file still attached.

### Flow 2: User attempts to upload an unsupported format

1. User drops a `.docx` onto the zone.
2. System rejects locally before upload starts.
3. Inline error appears: "We can't read .docx files. Try CSV or XLSX."
4. The drop zone remains active; user can drop a different file without reloading the step.

### Flow 3: User attempts to upload a file over the size limit

1. User drops a 75MB CSV onto the zone.
2. System rejects locally.
3. Inline error: "That file is 75MB — our limit is 50MB. Try splitting it or removing unused columns."
4. Drop zone remains active.

## Functional requirements

### Drop zone
- Users can drag a file onto the zone or click it to open a file picker.
- The zone displays accepted formats and the size limit inline at all times.
- The zone changes visual state on drag-over to confirm the drop target.
- The zone is keyboard-focusable and accepts file selection via keyboard.

### Validation
- The system must validate file format and size client-side before initiating upload.
- The system must reject files larger than 50MB with an inline message naming the size limit.
- The system must reject unsupported formats with an inline message naming acceptable formats.
- On validation failure, the system must keep the user on the upload step (no navigation away).

### Upload progress
- The system must display a percent-complete indicator during upload.
- If upload fails after starting (e.g., network error), the system must show a retry affordance without losing the file selection.

### State preservation
- If the user navigates away mid-upload, draft state must persist for at least 24 hours.
- On returning to the upload step within that window, the previously selected file must still be attached.

## Success metrics

**Primary**
- Upload-step abandonment: 42% → 27% (measured 30 days post-launch)

**Secondary**
- 7-day activation rate: +6 percentage points
- Upload-related support tickets: −50% within one quarter

**Counter-metrics**
- Time-to-upload-success: should not increase by more than 1 second
- Overall onboarding funnel completion: should not decrease

## Dependencies & risks

**Dependencies**
- Updated upload service endpoint with size/format validation hooks (Platform team, ETA TBD)
- Localization of new copy strings (Loc team, ~2 weeks lead time)

**Risks**
- *Med:* Browser-side validation may not catch all malformed CSVs. *Mitigation:* server-side validation as backstop.
- *Low:* Drag-and-drop is unfamiliar to some users. *Mitigation:* click-to-upload remains available and equally prominent.
- *Low:* Draft state preservation across sessions adds complexity. *Mitigation:* feature-flag the persistence layer for staged rollout.

## Out of scope

- Mobile web upload — handled in a separate workstream
- New file format support — covered by a separate Q3 proposal
- Redesign of the post-upload preview screen — out of scope for this milestone

## Open questions

- Final target for the abandonment metric — 27% is the team's estimate but not yet confirmed. [Owner: PM]
- Whether to support `.tsv` in v1. [Owner: PM + Eng]
- Accessibility review pass on the drag-and-drop interaction. [Owner: Design + a11y reviewer]
- Confirmed ETA for the Platform team's endpoint update. [Owner: Eng lead]
