---
name: tech-writing-style
description: A writing style guide for technical documentation. Apply on every technical writing or editing task — READMEs, architecture overviews, API references, runbooks, ADRs, design docs, PRDs, code comments, onboarding guides, and any other engineering-facing prose. Covers voice, structure, sentence-level rules, citation discipline, and patterns to avoid (marketing fluff, hedge words, passive voice, jargon without definition, paraphrasing the code). Trigger this skill at the start of any technical writing task to set the conventions, again before delivering for a final pass, and whenever the user asks to improve, edit, polish, tighten, or apply a style pass to technical content. Pair with the no-em-dashes skill — they apply together.
---

# Technical Writing Style

A writing style guide for engineering-facing documentation. Apply it on every technical writing or editing task. Pair it with the no-em-dashes skill — they apply together.

## The five things this skill is really about

1. **Concrete beats abstract.** Show real commands, real schemas, real file paths.
2. **Verifiable beats authoritative-sounding.** Cite the source. Anything that can't be cited is a claim, not a fact.
3. **Tight beats thorough.** One topic per paragraph. Cut filler.
4. **Direct beats hedged.** Imperative mood for instructions. Active voice. No "it is recommended that you might consider".
5. **Specific beats generic.** "Use semantic versioning" is noise. "We tag releases as `vMAJOR.MINOR.PATCH` and bump MAJOR on schema changes" is a doc.

If a sentence isn't doing one of those five things, it's probably cuttable.

## Voice and tense

**Use active voice.** Active voice names the actor, which technical readers need.

| Avoid | Prefer |
|---|---|
| The migration is run by the deploy script. | The deploy script runs the migration. |
| Errors are logged to Datadog. | The service logs errors to Datadog. |
| Authentication is required for all endpoints. | All endpoints require authentication. |

Passive voice is acceptable when the actor is unknown or genuinely irrelevant ("The file was created in 2018"), but that's rare in technical writing.

**Use the imperative mood for instructions.** Instructions tell the reader what to do; address them directly.

| Avoid | Prefer |
|---|---|
| Users can run `make dev` to start the server. | Run `make dev` to start the server. |
| It is recommended to set `LOG_LEVEL=debug`. | Set `LOG_LEVEL=debug`. |
| One should ensure the database is migrated. | Migrate the database. |

**Use second person ("you") sparingly.** Imperative covers most instructions without needing it. Reserve "you" for explicitly addressing the reader's situation: "you'll see this error if your token expired".

**Stay in present tense.** "The service handles 1,000 requests per second" is a present-tense fact about the system. "The service will handle…" is a promise; reserve future tense for genuinely future things (planned work, deprecation timelines).

## Structure

**Lead with the most important thing.** First sentence of every doc and every section: state the headline. Don't bury the lede in setup.

**One topic per paragraph.** If a paragraph covers two topics, split it. Readers skim — give them clean handholds.

**Heading hierarchy reflects the reader's mental model, not the writer's outline.** A reader scanning for "how do I deploy this?" should find a heading that says some version of that, not "Deployment considerations and operational concerns".

**Length follows the work, not a target.** A README for a simple library is shorter than one for a multi-service platform. Don't pad. Don't clip.

**Cross-link instead of repeating.** If two docs cover overlapping ground, the second one links to the first and adds only its delta. Repeated content drifts out of sync.

## Sentences

**Vary length, but lean short.** A run of 25-word sentences exhausts the reader. Mix short declarative sentences with the occasional longer one that carries an idea through. If a sentence has more than one comma in the middle, see if it should be two sentences.

**Cut filler words.** "In order to" → "to". "At this point in time" → "now" or "currently". "Due to the fact that" → "because". "It should be noted that" → just say it.

**Avoid hedge words when you know.** "Might", "perhaps", "possibly", "generally", "typically" — only when there's genuine uncertainty. If you know the service runs on Kubernetes, write "the service runs on Kubernetes", not "the service typically runs on a container orchestrator".

**Avoid intensifiers.** "Very fast", "extremely important", "really powerful". Either give the number or trust the word to do its job.

| Avoid | Prefer |
|---|---|
| The cache is very fast. | The cache returns 99% of requests in under 5ms. |
| It's extremely important to set this flag. | Set this flag. (Or: This flag controls X. Without it, Y breaks.) |

## Word choice

**Define jargon on first use.** If a doc uses a term not every reader will know — `JWT`, `circuit breaker`, `idempotency key` — define it once at first appearance, then use it freely. If the term is ubiquitous in the team's vocabulary, link to a glossary instead of defining inline.

**Pick a name and stick to it.** If the system is a "service", call it a "service" everywhere. Don't switch to "app", "system", "platform", "backend" within the same doc. Same for nouns like "user" / "customer" / "account holder". Inconsistency makes readers wonder if you mean different things.

**Avoid marketing language.** "Powerful", "robust", "scalable", "intuitive", "best-in-class", "enterprise-grade". These don't carry information. If something is scalable, say what it scales to. If it's robust, say what it survives.

**Avoid generic best-practice boilerplate.** Lines like "follow REST conventions", "use semantic versioning", "implement proper error handling" are noise unless you say something specific to the project. Either name the convention precisely (with a link), or omit.

## Concrete patterns for tech docs

**Show, don't paraphrase.** When documenting commands, schemas, or configs, paste the real thing in a code block. Don't describe it in prose.

| Avoid | Prefer |
|---|---|
| You can configure the service using a JSON config file with various options. | The service reads config from `config.json`:<br><br>```json<br>{<br>  "port": 8080,<br>  "log_level": "info"<br>}<br>``` |
| The login endpoint returns a token. | `POST /auth/login` returns:<br><br>```json<br>{<br>  "token": "eyJhbGc…",<br>  "expires_in": 3600<br>}<br>``` |

**Cite the code on every concrete claim.** "The service uses JWT" → "The service uses JWT (issued at `POST /auth/login`, see `src/auth/routes.ts:42`)." Citations make claims verifiable.

**Show command output when it helps.** If running a command produces output the reader can sanity-check against, show it.

```
$ make dev
Building...
Server listening on :8080
```

**Use diagrams when text would take more space.** A simple ASCII boxes-and-arrows diagram in a code block carries a lot:

```
[Client] --> [API Gateway] --> [Service A]
                          \--> [Service B] --> [DB]
```

If a richer diagram is needed, leave a placeholder and note that a Mermaid or draw.io version should follow.

## Lists

**Use bullets for genuinely list-shaped content.** Requirements. Steps. Options. Items that share structure.

**Don't bullet narrative.** A paragraph of three sentences is clearer than three bulleted half-sentences.

**Bullets should be parallel.** Each item should start the same way grammatically — all imperative verbs, or all noun phrases, not a mix.

| Avoid | Prefer |
|---|---|
| - Run the migration<br>- Logs are written to Datadog<br>- You should set the env var | - Run the migration<br>- Set the env var<br>- Confirm logs are flowing to Datadog |

**Numbered lists for ordered steps. Bulleted lists for unordered items.** If the order matters (do A, then B, then C), number them. If it doesn't (the service depends on Redis, Postgres, and Kafka), bullet them.

## What to avoid

- **Marketing fluff.** "Powerful", "robust", "best-in-class", "industry-leading". Cut.
- **Hedge words when you know.** "Might", "typically", "generally" — only with genuine uncertainty.
- **Passive voice for actions with a clear actor.** "Errors are logged" → "The service logs errors".
- **Restating code in prose.** A function that takes an int and returns a bool doesn't need a paragraph; show the signature.
- **Generic best-practice lines.** Either be specific to the project or omit.
- **Unsourced claims.** "It's faster than X" without a benchmark or citation is opinion masquerading as fact.
- **Inconsistent terminology.** Pick one name per concept and stick to it.
- **Burying the lede.** First sentence of every section should carry the headline.
- **Em dashes.** See the no-em-dashes skill.

## Final pass before delivery

Before handing back any technical document, run this checklist:

1. **First sentence of every section names the topic.** If not, rewrite.
2. **Every concrete claim cites its source.** File path, line number, link, or name.
3. **No marketing words.** Search for "powerful", "robust", "scalable", "intuitive", "enterprise-grade", "best-in-class". Cut or replace.
4. **No hedge words where you know.** Search for "might", "typically", "generally", "perhaps", "possibly".
5. **No filler phrases.** Search for "in order to", "at this point in time", "due to the fact that", "it should be noted that".
6. **Code blocks for code, not prose.** Spot-check.
7. **Em dash check.** Search for `—` and `--`. Zero hits.
8. **Read the first and last paragraph aloud.** If anything trips you up, rewrite.

## When this style applies and when it doesn't

This skill targets *engineering-facing* prose: docs and comments meant for developers and operators. The same rules don't always serve marketing copy, end-user help articles, or executive summaries — those have different audiences and conventions. If the user asks for content in one of those genres, adjust the style to fit while keeping the universal rules (concrete over abstract, no marketing fluff, no em dashes).
