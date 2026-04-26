# Calendar Sync v2 — Design Notes

**Designer:** Priya R. **Last updated:** 2026-04-10

## What we're building

We're rebuilding our two-way Google Calendar sync. The current sync is one-way (our app → Google) and breaks silently when users change their Google password or revoke the OAuth scope. We're moving to two-way sync with proactive failure detection.

## Why now

Support has logged 580 sync-related tickets in Q1, up from 240 the prior quarter. The top complaints:

- "My events aren't showing up in Google Calendar" (silent OAuth expiry)
- "I edited an event in Google Calendar and it didn't update in your app" (one-way sync limitation)
- "I have duplicate events" (after manual user resync)

We also lost 3 deals in the last 60 days where prospects called out our sync as not enterprise-ready, citing the lack of two-way sync as the dealbreaker.

## Who it's for

Primary: knowledge workers in the 50–500 employee segment, the bulk of our paid base. They live in Google Calendar and expect any tool that touches their schedule to keep parity.

Secondary: admins who set up the team-level sync and get pinged when it breaks.

## Design

### Setup flow

The new setup uses Google's incremental authorization. We ask for read-only scope first (lets us read events for display), then prompt for write scope only when the user takes an action that requires it (creating an event, updating a Google event from our app). This reduces drop-off at the OAuth screen by avoiding upfront broad scope requests.

Screens (in design file pp. 2–4):

1. Settings → Integrations → Connect Google Calendar
2. Google OAuth consent (read-only scopes)
3. Confirmation: "We can now show your Google events. To create or edit events, we'll ask for additional permission later."
4. Done.

### Sync behavior

Two-way sync. When a user creates or edits an event in either system, the change replicates to the other within 60 seconds.

Conflict resolution: last-write-wins, with a 5-minute reconciliation window for near-simultaneous edits. If a true conflict is detected (both sides edited within 30 seconds), we surface a diff modal and let the user pick (design pp. 7–8).

### Failure detection

We poll Google's token-info endpoint every 6 hours to check token validity. If the token is invalid, we:
1. Mark the integration as "Needs reauth" in Settings
2. Email the user (and admin, if set up at the team level)
3. Show an inline banner in the app's calendar view

(Design pp. 10–11.)

### Removal

User can disconnect from Settings → Integrations. We don't delete events from either system on disconnect — we just stop syncing. Disconnect confirms with "We'll stop syncing. Existing events stay where they are."

## Open from design side

- Should we also support Outlook/Microsoft 365 in this version? (No — separate workstream)
- What's the right error message tone when token is invalid? (Working with copy)
- A11y review on the diff modal hasn't happened yet.

## Out of scope for v2

- Outlook/Microsoft 365
- Calendly-style external scheduling links
- Recurring event editing (still single-event only)

## Loose ends for PM

- Need a target for how much we expect this to reduce sync-related tickets.
- Do we want to gate two-way sync behind a paid plan, or ship it to all tiers? Currently undecided.
