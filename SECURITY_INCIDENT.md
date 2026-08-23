# Security Incident — Exposed Firebase Service-Account Key

## Status: Credentials rotated (per user confirmation). Repository remediation in progress.

## Exposed files

| File | Actually a secret? | Details |
|---|---|---|
| `firebase-credentials.json` | **Yes — real, severe.** | Firebase/Google Cloud service-account JSON, including a private key. |
| `prodenv.yml` | **No — correction.** | Direct inspection shows this is a Conda environment export (`name`/`channels`/`dependencies`/`prefix`), 106 lines of package pins plus the standard public Anaconda channel URLs. No API key, token, password, or credential pattern anywhere in it (verified by direct grep for key/secret/token/password/credential and for embedded `user:pass@` URLs — none found). The only mildly sensitive content is a local Windows path (`C:\Code\Support\miniconda3\envs\routerprod`), which is low-severity information disclosure, not a rotatable secret. Removed from the repo anyway per instruction and because it reveals internal environment structure, but it should not be treated as equivalent in severity to the Firebase key. |

## Affected provider / project

- **Provider:** Google Cloud / Firebase (service account)
- **Project ID:** `omnilabs-43460`
- **Service account email:** `firebase-adminsdk-fbsvc@omnilabs-43460.iam.gserviceaccount.com`
- **Client ID:** `102503205344409048923`
- Private key value: **never printed, never copied out of the original file**, per instruction.

## Exposure scope — this is public, not private

- **Repository visibility: PUBLIC.** Verified via an unauthenticated GitHub API call
  (`api.github.com/repos/omnilabs-ai/OmniRouter` → HTTP 200; private repos return 404 without
  auth). This means the key was not just "committed" — it was openly readable by anyone,
  including automated secret-scanners and scrapers, for the entire time it was in the default
  branches. **Treat as fully compromised regardless of whether any misuse is observed** — this
  is why rotation (already done, per your confirmation) was the correct first step, not
  optional.
- **Present in git history on 9 of 12 checked branches** (verified by checking each branch tip
  directly, not assumed): `dev`, `main`, `claude-3-7-models`, `claude-reason-hotfix`,
  `deepai-image`, `function-xai`, `kimia-new-test`, `kimia-xai`, `smart-router-v2`. **Not**
  present on `ayush-adding_image_routing`, `ayush-image_models`, `kimia-smartrouter`.
- Commits that touched `firebase-credentials.json`: `b2135ff` ("fixed cred"), `6bd6a00` (merge
  commit). `prodenv.yml` was touched in `bbcc40d` ("test streaming times") and the same merge
  `6bd6a00`.
- **`prodenv.yml`'s branch distribution is identical** to `firebase-credentials.json`'s: present
  on the same 9 branches (`dev`, `main`, `claude-3-7-models`, `claude-reason-hotfix`,
  `deepai-image`, `function-xai`, `kimia-new-test`, `kimia-xai`, `smart-router-v2`), absent from
  the same 3 (`ayush-adding_image_routing`, `ayush-image_models`, `kimia-smartrouter`) — verified
  directly, not assumed from the first file's result. Both files can be purged from history in a
  single pass.

## Code paths that read the file

**Exactly one:** `serverRouter/core/config.py`, line 5 (before this fix):
`credentials.Certificate('firebase-credentials.json')`, executed at module import time —
meaning any process that imports this module immediately tried to load the file and connect to
Firestore. No other file in the repository referenced `firebase-credentials.json`.

## Other secrets — audit result

Scanned the full working tree (excluding `.git/`) for common secret signatures — OpenAI
(`sk-…`), Google API keys (`AIza…`), Google OAuth tokens (`ya29….`), AWS access keys (`AKIA…`),
Slack tokens (`xox…`), and PEM private-key headers. **The only match was the known Firebase
private key inside `firebase-credentials.json` itself — no other secret was found anywhere else
in the repository.** All other providers (OpenAI, Anthropic, Gemini, DeepSeek, Together,
Stability) already load their keys from environment variables via `python-dotenv` —
`config.py`'s file-based Firebase loading was the one inconsistent pattern in the codebase, now
fixed to match the rest.

## Remediation completed this pass (working tree only — nothing committed or pushed)

1. `firebase-credentials.json` and `prodenv.yml` removed from disk and unstaged from git
   (`git rm --cached`).
2. `.gitignore` updated with explicit patterns: `firebase-credentials.json`,
   `*firebase-credentials*.json`, `*serviceAccount*.json`, `*service-account*.json`,
   `*credentials*.json`, `*.pem`, `*.key`, `prodenv.yml`.
3. `serverRouter/core/config.py` rewritten to load the credential JSON from a
   `FIREBASE_CREDENTIALS_JSON` environment variable (via `python-dotenv`, matching every other
   provider's existing pattern) instead of a file, and to fail fast with a clear error at
   startup if that variable is missing, instead of a confusing SDK-level failure deep in
   Firebase's own code.
4. `.env.example` created with placeholder values only for every credential this codebase uses
   (Firebase + the 6 LLM/image provider keys) — no real values.

**Not yet done, per explicit instruction:** git history rewrite, force-push, and anything that
touches the remote. See the plan below.

## Process error to disclose

While running the secret-scan referenced above, one grep invocation matched inside
`firebase-credentials.json` itself and echoed a truncated fragment of the real private key into
this tool's own command output for a moment, before the file was removed. It was not repeated,
quoted, or written into any report, including this one. Since the key is already being treated
as fully compromised (public repo exposure) and has been rotated per your confirmation, this
doesn't change the required remediation — but it was a process violation of the "never print the
key" instruction and you should know it happened.

## Git history rewrite plan — NOT YET EXECUTED, awaiting approval

**Branches requiring rewrite (9):** `dev`, `main`, `claude-3-7-models`, `claude-reason-hotfix`,
`deepai-image`, `function-xai`, `kimia-new-test`, `kimia-xai`, `smart-router-v2`.
**Branches unaffected (3):** `ayush-adding_image_routing`, `ayush-image_models`,
`kimia-smartrouter`. **Tags:** none exist in this repo.

**Exact command to run (once approved), from a fresh clone of the repo:**

```bash
git clone --no-local --mirror <repo-url> omnirouter-filter.git
cd omnirouter-filter.git
git-filter-repo --invert-paths \
  --path firebase-credentials.json \
  --path prodenv.yml
```

`--invert-paths` with `--path` removes exactly those two paths from every commit on every ref in
the mirror clone (this naturally covers all 9 affected branches without needing to name them
individually; the 3 unaffected branches pass through untouched since the files were never in
their history). Running it against a mirror clone — not your working copy — is
`git-filter-repo`'s required safety model; it refuses to run on a repo with a normal remote
configured, by design, so it can't accidentally push anywhere by itself.

**Force-push: yes, required.** Every commit hash on the 9 affected branches changes once history
is rewritten, so updating the real remote requires a force-push to each of those 9 branches
(`git push --force origin <branch>` for each, from the filtered mirror). This does not touch the
3 unaffected branches. **Not run yet — waiting for your explicit approval, as instructed.**

**Before force-pushing, once approved, everyone with a local clone (all contributors) will need
to either re-clone or hard-reset their local branches to the new history** — a force-push that
rewrites shared branches breaks anyone's existing clone/PRs based on the old commits. Worth a
heads-up to the team before it happens, not just to me.
