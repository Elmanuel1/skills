---
name: no-em-dashes
description: A house writing-style rule that strictly prohibits em dashes (—) in any document, prose, or written content produced for the user. Use this skill on every writing or editing task — drafting documents, emails, Slack messages, blog posts, reports, technical writing, presentations, marketing copy, README files, PRDs, code comments, and any other written output. The skill catches em dashes before they ship, replaces them with the appropriate alternative punctuation (comma, parentheses, semicolon, colon, or period for a new sentence), and explains why each substitution is the right one. It also covers a final sweep pass after writing is done. Trigger this skill at the start of any writing task to set the constraint, again before delivering written content as a check, and whenever the user asks to fix em dashes, remove em dashes, edit for style, or apply a writing correction pass.
---

# No Em Dashes

A house writing-style rule. **Never use em dashes (`—`) in writing produced for this user.** Apply this rule to every written deliverable — documents, emails, messages, code comments, PRDs, READMEs, presentations, anything.

## Why this rule exists

Em dashes are overused, particularly in machine-generated writing where they've become a stylistic tell. Removing them forces tighter sentence structure, fewer parenthetical asides, and prose that reads less like an AI default and more like a human voice. The user has decided em dashes don't appear in their written output. That decision is final — no exceptions for "but it really fits here" or "just one".

## What counts as an em dash

The character `—` (Unicode U+2014). Watch for these too:

| Character | Name | Treatment |
|---|---|---|
| `—` | em dash (U+2014) | **Forbidden.** Replace. |
| `–` | en dash (U+2013) | **Allowed only for number ranges** (e.g., `pages 4–7`, `2020–2024`). Never as a punctuation dash. |
| `--` | double hyphen | **Forbidden.** Some autoformatters render this as an em dash. Replace. |
| ` - ` | spaced hyphen used as a dash | **Forbidden.** This is a stylistic em-dash substitute. Replace. |
| `-` | hyphen | **Allowed** in compound words (`well-known`, `state-of-the-art`) and code/identifier contexts. |

If you're not sure whether a dash is an em dash, run `grep -n '—' <file>` (or the equivalent search) on the document before delivering.

## How to replace em dashes

Em dashes do four jobs in prose. Each job has a specific replacement.

### 1. Em dash signaling a parenthetical aside

Replace with **commas** (light aside) or **parentheses** (more clearly an aside).

| Before | After |
|---|---|
| The new feature — released last week — covers most edge cases. | The new feature, released last week, covers most edge cases. |
| The team — eight engineers and a PM — owns the migration. | The team (eight engineers and a PM) owns the migration. |

Prefer commas for short asides that belong in the sentence's flow. Prefer parentheses when the aside is genuinely tangential.

### 2. Em dash joining two related independent clauses

Replace with a **semicolon** (closely related clauses) or a **period** (split into two sentences).

| Before | After |
|---|---|
| The migration finished overnight — there were no errors. | The migration finished overnight; there were no errors. |
| The deploy went out at 3pm — and the team celebrated. | The deploy went out at 3pm. The team celebrated. |

If the clauses feel too distinct for a semicolon, just split them. Two short sentences are usually clearer than one long one.

### 3. Em dash introducing a list or explanation

Replace with a **colon**.

| Before | After |
|---|---|
| Three things broke in the deploy — the cache, the queue, and the auth service. | Three things broke in the deploy: the cache, the queue, and the auth service. |
| There's one rule — never push directly to main. | There's one rule: never push directly to main. |

### 4. Em dash for emphasis or interruption

Restructure the sentence. Em dashes used purely for dramatic effect almost always indicate the sentence can be tightened.

| Before | After |
|---|---|
| The fix is simple — but only if you have admin access. | The fix is simple, but only if you have admin access. |
| She knew the answer — finally. | She finally knew the answer. |

If the only thing the em dash adds is a beat of dramatic emphasis, cut it. Strong prose carries its own emphasis without typographic theatrics.

## Workflow when writing for this user

1. **At the start of any writing task,** remind yourself of the rule. Don't draft with em dashes intending to remove them later — that creates rework and risks misses.
2. **While drafting,** when you'd reach for an em dash, pick from the four-replacement table above instead. The choice is rarely close once you identify the job the dash was doing.
3. **Before delivering written content,** run a search for `—`, `--`, and ` - ` (spaced hyphen) across the document. Fix any hits.
4. **If editing existing content for the user** (their writing or someone else's), do a sweep pass for em dashes as part of the edit — that's the most common reason this skill is invoked.

## Edge cases

- **Code blocks and string literals.** Don't touch dashes inside code, command-line examples, identifiers, or string contents. The rule is about prose, not code.
- **Quoted material from third parties.** If you're quoting someone else's text verbatim, preserve their punctuation. The rule applies to writing *produced* for the user, not text being faithfully cited. If you'd like to paraphrase a quote, that's prose and the rule applies.
- **URLs and file paths.** Dashes there are part of the identifier — leave them.
- **Pre-existing user content.** If the user shares their own document and asks for help, only remove em dashes if asked. Otherwise respect their text. New content you write follows the rule.

## What to avoid

- **Treating this as a soft preference.** It's a hard rule. Even one em dash is a miss.
- **Replacing every em dash with a comma.** Not all dashes do the same job. Use the four-replacement table.
- **Loading replacements with subordinate clauses to compensate.** If the original sentence had an em dash because it was carrying too much, removing the dash and adding "however" / "moreover" / "in addition" is worse. Restructure instead.
- **Sneaking dashes back in via Unicode lookalikes.** No `—`, no `―` (horizontal bar), no decorative variants. The rule covers the family.

## A quick check before delivery

Before handing back any written content, do this final pass:

1. Search for `—` in the text. There should be zero hits.
2. Search for `--` (double hyphen). Zero hits.
3. Read the first paragraph aloud. If you'd naturally pause where there *was* a dash and the prose reads stiff or rushed, restructure that sentence — the replacement isn't pulling the dash's weight.

That's the whole skill. One rule, applied everywhere, with deliberate substitutions instead of mechanical ones.
