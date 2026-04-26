---
name: get-test-token
description: Generate an access token (JWT) for testing — exchange a username + password for a real auth token from the project's auth provider, then print it so the engineer can paste it into curl, Postman, or shell env vars. Knows how to talk to Supabase, Auth0, Cognito, and any standard OAuth2 password-grant endpoint. Use whenever the user says "get me a test token", "I need a JWT to test the API", "exchange these credentials for a token", "generate an auth token for testing", or whenever you're about to run an authenticated API call against a staging/dev environment and the user hasn't already pasted a token. Also use when a Story file's Test plan references this skill by name.
allowed-tools:
  - Read
  - Write
  - Bash
  - WebFetch
  - AskUserQuestion
  - mcp__workspace__bash
  - mcp__workspace__web_fetch
---

# Get Test Token

A small utility skill — given a username and password (and the project's auth
provider details), exchange them for an access token (JWT) and print the
token so the engineer can use it in `curl`, Postman, or `export` it as a
shell variable. Optionally decode the token to show the claims and the
expiry, so the engineer can sanity-check what they got.

## Why this skill exists

Every Story's Test plan section ends up with the same boilerplate "here's
how to grab a JWT with `curl`": the auth provider URL, the request shape,
where to find the access token in the response, what to do with the
refresh token. Copying that boilerplate into every Story file is noise
that obscures the actual test plan. Worse, it bit-rots: when the auth
provider URL changes or the response shape moves, every Story is wrong.

This skill solves that by being the **one** place that knows how to
exchange credentials for a token. Story Test plans say "use the
**get-test-token** skill with email `vendor-test@example.com`"; the
skill handles the rest.

## Hard preconditions

1. **Username and password must be supplied** by the user. The skill never
   reads them from a file, env var, or secret store on its own — credentials
   are sensitive and the user must hand them over explicitly each run.
2. **The auth provider must be identifiable.** Either the user names it
   ("Supabase", "Auth0", "Cognito", "OAuth2 password grant") or the skill
   asks via `AskUserQuestion`. If the project has a config file at
   `get-test-token.config.json` (see "Per-project config" below), the
   skill reads provider defaults from it.
3. **The environment must be specified** (typically `local`, `staging`,
   `dev`, `prod`). The skill never defaults to prod silently — it asks if
   the answer isn't obvious from context.

## Workflow

### Step 1 — Identify the auth provider and environment

If the user already named the provider and env (e.g. "get a vendor token
for staging Supabase"), proceed. Otherwise ask via `AskUserQuestion`:

- **Provider:** Supabase / Auth0 / Cognito / OAuth2 password grant /
  Other (custom URL).
- **Environment:** local / staging / dev / prod (with a strong
  recommendation against prod unless the user explicitly confirms).

### Step 2 — Locate provider details

Look for `get-test-token.config.json` in the user's mounted directory or
in the active repo. Schema:

```json
{
  "providers": {
    "supabase": {
      "staging": {
        "authUrl": "https://abcdefg.supabase.co",
        "anonKey": "eyJ..."
      },
      "local": {
        "authUrl": "http://localhost:54321",
        "anonKey": "eyJ..."
      }
    },
    "auth0": {
      "staging": {
        "domain": "your-tenant.auth0.com",
        "clientId": "...",
        "audience": "https://api.example.com"
      }
    }
  }
}
```

If no config file exists, ask the user for the URL and any secrets needed
(API key for Supabase anon, client_id for Auth0). Offer to save the
non-sensitive parts to `get-test-token.config.json` for next time.

**Anon keys / public client IDs are safe to persist.** Service-role keys,
client secrets, and other secrets are never persisted to the config file
— always read fresh from a secrets manager or prompt.

### Step 3 — Exchange credentials for a token

Run the exchange via `Bash` (using `curl`). Provider-specific recipes:

#### Supabase (password grant)

```bash
curl -sS -X POST "${AUTH_URL}/auth/v1/token?grant_type=password" \
  -H "apikey: ${ANON_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${USER_NAME}\",\"password\":\"${USER_PASSWORD}\"}"
```

Successful response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiI...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "user": { "id": "...", "email": "..." }
}
```

#### Auth0 (resource owner password grant)

```bash
curl -sS -X POST "https://${AUTH0_DOMAIN}/oauth/token" \
  -H "Content-Type: application/json" \
  -d "{
    \"grant_type\":\"password\",
    \"username\":\"${USER_NAME}\",
    \"password\":\"${USER_PASSWORD}\",
    \"audience\":\"${AUDIENCE}\",
    \"client_id\":\"${CLIENT_ID}\",
    \"scope\":\"openid profile email\"
  }"
```

#### Cognito (USER_PASSWORD_AUTH)

```bash
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id "${CLIENT_ID}" \
  --auth-parameters USERNAME="${USER_NAME}",PASSWORD="${USER_PASSWORD}"
```

#### Generic OAuth2 password grant

```bash
curl -sS -X POST "${TOKEN_URL}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=${USER_NAME}&password=${USER_PASSWORD}&client_id=${CLIENT_ID}"
```

### Step 4 — Output the token (and optionally decode it)

Print the access token clearly so the user can copy it. Wrap it in a
fenced code block. Also offer:

- **Decode the JWT** — base64-decode the payload section, pretty-print the
  claims. Highlights `sub`, `email`, `exp`, `iat`, `iss`, `aud`, and any
  custom claims. Useful for sanity-checking the token belongs to the
  right user and isn't already expired.
- **Export as a shell var** — print `export ACCESS_TOKEN="..."` ready to
  paste.
- **Show the expiry in human time** — convert the `exp` Unix timestamp to
  the user's local time; show how long until it expires.

Suggested output template:

```
Got a token for ${USER_NAME} on ${PROVIDER} (${ENV}).

Access token (expires in ${MM} minutes, at ${LOCAL_TIME}):

eyJhbGciOiJIUzI1NiI...

Export it:
  export ACCESS_TOKEN="eyJhbGci..."

Use it:
  curl -H "Authorization: Bearer ${ACCESS_TOKEN}" https://staging-api.example.com/v1/...

Decoded claims:
  sub  : <user-id>
  email: vendor-test@example.com
  exp  : 2026-04-25T20:18:04Z (in 59m)
  iss  : https://abcdefg.supabase.co/auth/v1
  ...
```

### Step 5 — Handle the refresh token (optional)

If the response includes a refresh token, mention it briefly: print the
refresh token only if the user asked, and remind them refresh tokens are
typically single-use (they get a new pair on every refresh). Don't print
refresh tokens by default — they're more sensitive than access tokens.

## Per-project config

Projects can drop a `get-test-token.config.json` next to their other
config files (e.g., in the repo root or in `.specs/`). The skill reads
this on every invocation to avoid re-asking for the auth URL and anon key.

Schema:

```json
{
  "$schema": "https://example.com/get-test-token.schema.json",
  "default_provider": "supabase",
  "providers": {
    "supabase": {
      "staging": { "authUrl": "...", "anonKey": "..." },
      "local":   { "authUrl": "...", "anonKey": "..." }
    }
  }
}
```

The skill never persists secrets (service-role keys, client secrets) to
this file. If a secret is required and isn't in env, ask the user.

## Failure modes

- **HTTP 400 / `invalid_grant`** — usually wrong password. Tell the user
  plainly; do not retry on the user's behalf.
- **HTTP 429 / rate limited** — auth provider is throttling. Surface the
  `Retry-After` if present; do not retry without telling the user.
- **HTTP 422 / 401 / 403** — provider rejected the request. Print the
  full error body so the user can debug.
- **Network error** — print which URL we tried; ask the user whether the
  auth provider is reachable from their network.
- **User asked for prod but didn't confirm explicitly** — refuse. Ask via
  `AskUserQuestion`: "You asked for the prod environment. Are you sure?
  This will mint a real production token tied to a real user account."

## Examples of when this skill should fire

- "I need a JWT to test `POST /v1/vendor/invitations`."
- "Get me a vendor token for staging — email `vendor-test@example.com`."
- "Exchange these credentials for a token: `acme@example.com` /
  `correct-horse-battery-staple`."
- A Story file's Test plan section says "use the **get-test-token**
  skill with email `...`."

## What this skill is NOT

- Not a session manager — single-shot token mint, no refresh loop.
- Not a credential store — never reads or writes user credentials.
- Not a JWT signing utility — only exchanges credentials for tokens
  issued by the project's real auth provider.
- Not for prod use without explicit confirmation each run.
