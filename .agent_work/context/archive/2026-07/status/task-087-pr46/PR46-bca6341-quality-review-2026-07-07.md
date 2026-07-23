# PR #46 Quality Review — Findings Report

| | |
|---|---|
| **PR** | [#46 — [codex] Task-087 Gate 3 repair integration proof](https://github.com/J-Schulein/TowerScout/pull/46) |
| **Commit reviewed** | `bca6341d2dcd1b007a9543ce89365552e53c1bae` (PR head) |
| **Base** | `main` @ `12daa55` |
| **Diff size** | 105 files, +15,538 / −1,486 (approx. 11.5k lines of reviewable code after excluding `.agent_work/` and generated HTML docs) |
| **Review date** | 2026-07-07 |
| **Method** | 8 independent finder passes (line-by-line, removed-behavior, cross-file contract tracing, reuse, simplification, efficiency, altitude, conventions), followed by independent adversarial verification of every candidate against the actual source. Every finding below survived verification; refuted candidates are listed at the end so they are not re-litigated. |
| **CI status at review time** | All checks green on `bca6341`: `test (3.11)`, `test (3.12)`, `security`, `Trivy`, `frontend-test`, both Puppeteer jobs. **See F1 — the Puppeteer green is not trustworthy.** |

**Severity scale:** High — undermines the PR's stated purpose or accepts invalid state; Medium — real behavior regression or reliability risk; Low — latent bug, dead code, or maintenance debt.

---

## Summary

| # | Sev | Verdict | Location | One-liner |
|---|-----|---------|----------|-----------|
| F1 | High | CONFIRMED | `.github/workflows/task-087-frontend-puppeteer.yml:88,93,181,188` | `node ... \| tee` without pipefail — test failures can never fail CI |
| F2 | High | CONFIRMED | `tests/frontend/test_provider_tls_live_post_poll_template.js:90` | 27-char test token rejected by helper's 32-char minimum -> e2e poll flow never runs |
| F3 | High | CONFIRMED | `tests/frontend/test_provider_tls_helper_unavailable_template.js:150` | e2e variant asserts a 503 the live simulated helper can never return |
| F4 | Medium | CONFIRMED | `webapp/ts_provider_http.py:346` | Google 2xx + empty JSON body classified TLS_OK -> invalid key persisted as valid |
| F5 | Medium | PLAUSIBLE | `webapp/ts_geocoding.py:480` | TLS-categorized error aborts geocoding instead of falling back to second provider |
| F6 | Medium | CONFIRMED/PLAUSIBLE | `scripts/ci_start_services.sh:39` + `tests/helpers/simulated_helper.js` | CI liveness check is a state-mutating POST; missing `/health` in simulated helper; rate-limit flakiness window |
| F7 | Low | CONFIRMED | `webapp/towerscout.py:2085` | `save-keys` 400s when `default_map_provider` omitted and env default didn't validate (API callers only) |
| F8 | Low | CONFIRMED (latent) | `webapp/js/src/setup-wizard.js:481–504` | Repair panel renders only the first repairable provider; second is silently dropped |
| F9 | Low | CONFIRMED | `webapp/ts_maps.py:39–43` | Dead code: `_allow_insecure_tls()` + `TRUTHY_ENV_VALUES` unreferenced after connector refactor |
| F10 | Low | CONFIRMED | `scripts/repair-provider-tls.ps1:70` (+ JS pairs) | Cert-store scan/normalization duplicated across scripts; `fetchJson`/failure-message helpers byte-identical in two JS modules |

---

## F1 — CI cannot fail: `node ... | tee` masks test exit codes (Severity: High)

**Files:** `.github/workflows/task-087-frontend-puppeteer.yml` lines 88, 93 (templates job) and 181, 188 (e2e job)

**Problem.** All four Puppeteer test steps are of the form:

```yaml
run: node tests/frontend/test_provider_tls_live_post_poll_template.js 2>&1 | tee test-artifacts/....log
```

No step declares `shell:`, and the workflow has no `defaults.run` block. GitHub Actions' *implicit* shell on Linux is `bash -e {0}` — **pipefail is only enabled when `shell: bash` is written explicitly**. The pipeline's exit status is therefore `tee`'s (always 0), so a node process exiting with `process.exitCode = 2` still produces a green step.

**Why this matters here specifically.** This PR's purpose is the Gate 3 integration proof, and both e2e steps invoked by this workflow *currently do fail* (F2, F3) — the failures are invisible. The green `Run Puppeteer e2e (simulated helper)` checks on `bca6341` are not evidence the flow works. The commit history ("stabilize Puppeteer e2e tests", "fix probe timeout") suggests time was already lost debugging around this blind spot.

Note the irony: the only two run blocks in this workflow that *do* set `set -euo pipefail` are the log-publishing steps (lines 105, 200), which don't pipe node.

**Fix.**
```yaml
defaults:
  run:
    shell: bash        # explicit bash -> bash --noprofile --norc -eo pipefail {0}
```
at workflow (or both-jobs) level — or add `set -o pipefail` as the first line of each piped run block. After fixing, expect the e2e steps to fail until F2/F3 are also fixed.

---

## F2 — e2e POST is always rejected: test token is 27 chars, helper requires 32 (Severity: High)

**File:** `tests/frontend/test_provider_tls_live_post_poll_template.js:90` (token), consumed at lines 209–224, failure exit at 270–274
**Contract side:** `tests/helpers/simulated_helper.js:103`

**Problem.** The template injects `operation_token: 'TEST_TOKEN_XXXXXXXXXXXXXXXX'` — 27 characters. The simulated helper validates:

```js
if (typeof op_auth !== 'string' || !/^[A-Za-z0-9_-]{32,128}$/.test(op_auth)) {
  // -> HTTP 400 { state: 'rejected_operation_authorization' }
```

In e2e mode (`E2E_USE_SERVER=1`, fetch wrapper forwards to the live helper), the POST returns 400 with no `operation_id`; `if (postResp && postResp.operation_id)` (line 214) is false, so the poll loop (216–224) never executes, `pollCalls` stays empty, and the script hits:

```js
console.error('No poll calls captured for operation status');
process.exitCode = 2;
```

The script does **not** tolerate the 400 (the "accept 200/202" logic from commit `bca6341` applies to the startup probe in `ci_start_services.sh`, not to this template). The failure is then swallowed by F1.

**Fix.** Use a compliant token, e.g. `'TEST_TOKEN_' + 'X'.repeat(32)` (43 chars, matches `[A-Za-z0-9_-]{32,128}`) in both templates, or generate one per run. Consider asserting the POST status explicitly (`202` expected) so a contract regression fails loudly at the POST step instead of downstream at the poll check.

---

## F3 — Helper-unavailable template is incompatible with the e2e job that runs it (Severity: High)

**File:** `tests/frontend/test_provider_tls_helper_unavailable_template.js:150–154` (assertion), line 78 (shim-only 503), line 56 (token)

**Problem.** The template asserts:

```js
if (outcome.status !== 503) {
  console.error('Expected helper POST to return 503 in this simulation, got', outcome.status);
  process.exitCode = 2;
  return;
}
```

The 503 is produced only by the **non-e2e fetch shim** (line 78, the `!useReal` branch). The workflow's e2e job runs this same file with `E2E_USE_SERVER=1` against the live `simulated_helper.js`, which has no unavailability mode — it returns 400 (the 27-char token, F2), 202, or 429, never 503. So the e2e variant of this test always fails, masked by F1.

**Fix options** (pick one):
1. Don't run this template in the e2e job — it tests the shim scenario by design.
2. Give `simulated_helper.js` an unavailability mode (e.g. `SIMULATE_UNAVAILABLE=1` env or a `/admin/unavailable` toggle) and have the e2e job exercise it.
3. Branch the expected status on `useReal` inside the template.

Option 1 or 2 is preferred; option 3 makes the e2e run assert nothing meaningful.

---

## F4 — Google key validation: 2xx + empty JSON body -> key accepted without authorization check (Severity: Medium)

**File:** `webapp/ts_provider_http.py:345–359`; trusted caller at `webapp/ts_config.py:309–328`

**Problem.** In `classify_provider_response`, a 2xx response enters the success block, then:

```python
if provider == "google" and body_json:   # falsy {} / [] skips this
    ...check body_json["status"] (REQUEST_DENIED etc.)...
return TLS_OK                            # <- reached for empty body
```

`{}` and `[]` are falsy, so the Google `status` validation is skipped entirely and `TLS_OK` is returned. In `_validate_google_key` (`ts_config.py`), only an *unparseable* body is caught (`ValueError` -> `PROVIDER_HTTP_ERROR`); a successfully parsed empty body flows to `classify_provider_response`, and `if category == TLS_OK:` (line 321) returns `valid=True` — "validated successfully for map and geocoding access" — without ever seeing a Geocoding `status: OK`.

**Failure scenario.** A corporate proxy, gateway, edge cache, or captive portal returns HTTP 200 with an empty/stripped JSON body during key validation -> an unauthorized or wrong key is persisted as valid. The user then hits opaque failures at detection time instead of at setup time — precisely the failure mode this PR's TLS/setup-triage work is trying to eliminate.

**Fix.** Treat a Google 2xx with a missing/empty/non-`OK` `status` as **unverified** rather than falling through to `TLS_OK`:

```python
if provider == "google":
    if not body_json or not isinstance(body_json, dict):
        return PROVIDER_HTTP_ERROR   # or a dedicated "unverifiable response" category
    ...existing status checks...
```

---

## F5 — Geocoding no longer falls back to the second provider on TLS errors (Severity: Medium)

**File:** `webapp/ts_geocoding.py:480–488`; categorization source `webapp/ts_provider_http.py:297–300`

**Problem.** Old behavior (`main`): a live TLS failure (`requests.SSLError`) surfaced as an *uncategorized* `NetworkError`, the provider loop's `tls_ca_bundle` check didn't match, and the loop `continue`d to the next provider — so a provider-specific TLS fault still produced an address via the other provider.

New behavior: `SSLError` is categorized `tls_ca_untrusted` (`ts_provider_http.py:297–300`), and the loop now returns immediately:

```python
if e.details.get("category") in {"tls_bundle_missing", "tls_bundle_unusable", "tls_ca_untrusted"}:
    return GeocodingResult(..., success=False)   # provider 2 never tried
```

**Assessment.** Early-abort is defensible when TLS interception is network-wide (both providers would fail identically, and one clear TLS error message beats two). But for a provider-specific certificate fault (regional endpoint issue, one provider's chain newly distrusted, SNI-specific interception rules), this is a regression: detections silently lose addresses even though the second provider works. Verdict PLAUSIBLE — the mechanism is proven; whether it bites depends on how often single-provider TLS faults occur in your pilot fleet.

**DECIDED direction (product owner, 2026-07-07) — restore the fallback, keep the signal.** Pilot deployments run on managed networks and address geocoding is mission-critical, so fail-fast is the wrong trade. Implement the hybrid:

1. On a TLS-categorized error from the first provider, **record the failure (provider + category) and `continue` to the next configured provider** instead of returning.
2. If the backup provider succeeds, return the address as normal, but **carry the TLS warning forward** — at minimum a sanitized log line, ideally a flag the readiness/status surface can show — so support still learns provider A is broken and the repair helper is still recommended. The failure must not be silently masked just because the backup saved the run (that visibility is the point of Task-086).
3. Only when **all** configured providers fail should a failure be returned — and prefer the TLS-categorized error over a generic one, so the Setup Wizard/Settings repair guidance appears.
4. **Per-run short-circuit:** geocoding runs once per detection, and a TLS-broken provider fails by ~5s timeout. After the first TLS-categorized failure, mark that provider unhealthy for the remainder of the run (or a short TTL) and go straight to the backup — otherwise a 50-tower run wastes minutes re-timing-out against a dead endpoint through the proxy.

Note this strictly dominates the current fail-fast: in the common managed-network case (both providers intercepted) all providers fail and the user gets the same TLS-categorized repair guidance as today; in the provider-specific case, addresses are preserved. Single-provider configs are unchanged (no backup exists; categorized failure -> repair guidance).

---

## F6 — CI readiness probe: state-mutating POST as liveness check; no `/health` on the simulated helper; rate-limit flakiness (Severity: Medium)

**Files:** `scripts/ci_start_services.sh:39–121`; `tests/helpers/simulated_helper.js:42–61, 64–139`; real helper contrast: `scripts/lib/TowerScoutHostHelper.ps1:2053–2062`

Three related sub-issues:

1. **Mutating probe.** The readiness loop POSTs to `/operations/provider-tls-repair` with a fresh random 32-hex token per attempt just to decide the helper is up. Each probe mints a real operation in the simulated helper (`tokenToOp[op_auth] = operation_id; ops[operation_id] = {...}` at `simulated_helper.js:113–115`), so the `ops`/`tokenToOp` maps grow unboundedly across probes and the "liveness check" has side effects. If the helper ever treats repair POSTs as truly side-effecting (the real one does — it restarts things), this pattern would trigger real operations from CI.
2. **Root cause.** The probe resorts to POST because `simulated_helper.js` implements no `GET /health` — its only routes are OPTIONS, `POST /operations/provider-tls-repair`, and `GET /operations/:id`; everything else 404s (line 139). The **real** helper *does* expose `GET /health` (`TowerScoutHostHelper.ps1:2053`). The test double diverged from the contract, and the workaround (POST probe + retries/backoff, commits `3b1aae4`/`6c05b09`/`bca6341`) papers over that divergence.
3. **Rate-limit interaction (PLAUSIBLE).** The loop issues ~2 helper requests/second while waiting for the webserver; the helper rate-limits at 30/min/IP (`simulated_helper.js:42–52`). If the webserver takes >~16s to come up, probes start drawing 429s, and only 200/202 count as helper success (`ci_start_services.sh:76`), so the loop burns its up-to-10 retries per iteration against 429s. The 60s window reset means it usually recovers within the 300s timeout, but it's a built-in flakiness and noise source.

**Fix.** Add `GET /health` to `simulated_helper.js` mirroring the real helper's response shape; switch `ci_start_services.sh` to probe it read-only (the retry/backoff machinery and the rate-limit pressure then largely disappear). Exempt `/health` from the rate limiter.

---

## F7 — `save-keys` rejects Google-only saves from API callers that omit `default_map_provider` (Severity: Low)

**File:** `webapp/towerscout.py` — fallback at ~line 1932 (`os.getenv('DEFAULT_MAP_PROVIDER', 'azure')`), new gate at ~2085 ("selected default provider did not validate" -> 400)

**Problem.** New in this PR: the endpoint 400s when the effective default provider isn't among the providers that validated. When the request omits `default_map_provider`, the default falls back to the env default (`azure`). A POST supplying only a valid Google key then computes `valid_providers={'google'}` -> 400 — a configuration the old code accepted and persisted.

**Scope.** Both shipping frontends always send the field (`settings.js:205`, `setup-wizard.js:845`), so the UI is unaffected. Affected: curl/scripted setup, support tooling, or any older/external client. Low severity, but the error message ("The selected default provider (azure) did not validate") is confusing to a caller who never *selected* azure.

**DECIDED direction (product owner, 2026-07-07) — derive the default when omitted; reject only explicit bad choices.** The guard's intent is good (never persist a default pointing at a provider that didn't validate); the bug is only that an *implicit* env fallback is treated like a user's choice. Implement this rule set:

1. `default_map_provider` **explicitly provided** and it didn't validate -> keep the new 400. That's a genuine caller error and the guard doing its job.
2. **Omitted**, exactly one provider validated -> default to that provider, save, and state the derived default in the response payload.
3. **Omitted**, both validated -> use the env/default preference as now (it is in the validated set, so the guard passes).
4. Fix the error message to name the field, e.g. *"default_map_provider was not provided and the fallback default ('azure') did not validate"* — the current wording ("the selected default provider") is confusing for a caller who selected nothing.

The "make the field required" alternative was considered and **rejected**: it breaks existing automation/support tooling for no reliability gain. This rule set restores the pre-PR behavior for scripts (a valid Google-only save works again) while keeping the integrity guarantee the PR was after.

---

## F8 — Repair panel surfaces only the first repairable provider (latent) (Severity: Low)

**File:** `webapp/js/src/setup-wizard.js:481–489` (`firstVisibleProviderTlsRepairViewModel`), consumed at :504 (`renderProviderTlsRepairState`); mirrored in built `webapp/js/towerscout.js`

**Problem.** The renderer takes exactly one view model — the first visible one in `providerNames = ['google', 'azure']` order — and writes it into the single `wizard_provider_tls_repair_*` panel. If both providers have repairable TLS failures, Azure's repair state is never rendered until Google's is resolved, with no indication a second repair is pending.

**Why latent.** Today `visible` can't be true (the control plane is gated off — see "Intentional design notes" below), so nothing is user-visible yet. It becomes real the moment `provider_helper_available` starts returning true. Flagging now so it doesn't ship inside the enablement PR.

**Fix.** Render per-provider (loop or a queued "next repair" affordance), or at minimum show a "N providers need repair" indicator sourced from all visible view models.

---

## F9 — Dead code: `_allow_insecure_tls` / `TRUTHY_ENV_VALUES` in `ts_maps.py` (Severity: Low)

**File:** `webapp/ts_maps.py:39–43`

**Problem.** After this PR routes tile-download TLS through `create_provider_ssl_context(provider)` (`ts_maps.py:55` -> `ts_provider_http.py` -> `ts_tls.allow_insecure_tls()`), the local `_allow_insecure_tls()` helper and its `TRUTHY_ENV_VALUES` set have zero call sites (whole-repo grep: definition only). It's a second, driftable copy of the `TOWERSCOUT_ALLOW_INSECURE_TLS` parsing that `ts_tls` owns.

**Fix.** Delete both.

---

## F10 — Duplicated logic that will drift (Severity: Low)

**Locations:**
- `scripts/repair-provider-tls.ps1:37, 70–93` (`Normalize-TowerScoutThumbprint`, `Get-TowerScoutCertificateStoreMatches`) vs `scripts/import-tls-ca.ps1:52–76` (`Get-CertificateFromStore` + inline normalization) — same four `Cert:\{LocalMachine,CurrentUser}\{Root,CA}` stores, same `-replace '[^A-Fa-f0-9]'` normalization, **already ordered differently** between the two scripts, no shared module.
- `webapp/js/src/settings.js:11–25` vs `setup-wizard.js:98–112` — `fetchJson` byte-identical; `saveFailureMessage` byte-identical (`settings.js:59–72` vs `setup-wizard.js:648–661`); `providerFailureMessage` near-identical.

**Cost.** A store-path fix, a message-wording change, or a fetch-error-shape change must be applied in 2+ places by hand; the differing store order shows drift has effectively already begun. Package scripts ship to end users, where drift becomes a support burden.

**Fix.** PowerShell: extract the cert-store helpers into `scripts/lib/` (the packaging already ships a `scripts/lib/`). JS: extract one shared module (e.g. alongside the existing manager modules) for `fetchJson` and the failure-message formatters.

---

## Intentional design notes (not defects — for awareness)

- **The control plane ships dark, and that's documented.** Two independent hardcoded gates keep the browser repair flow inert: `provider_helper_available()` returns `False` unconditionally (`ts_provider_http.py:120`), and `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false` (`setup-wizard.js:17`). No env/config can flip either. The TASK-087 doc records this as an explicit Gate-3 decision ("Keep ... false and do not add any live fetch path..." pending release-owner sign-off), and a unit test pins the flag. Two consequences worth weighing for the enablement PR: (a) a large body of code merges un-exercisable (see F2/F3 — its only e2e exercise is currently broken and masked), and (b) the JS mirrors the helper's status/next-action vocabularies as hand-maintained Sets, which can drift until something real runs against them. The simulated helper's `GET /operations/:id` responses also omit `provider`/`operation_type`, which the real helper includes and the JS normalizer requires — align the fixture before the poll wiring is enabled.
- **Minor efficiency notes (no action required now).** `resolve_provider_tls_config` re-reads env + stats the CA bundle per `provider_get` call (tile cache-miss path — micro-cost vs the network call, cache if convenient). `/api/config/tls-status` with no `provider` param probes Google then Azure sequentially (worst case ~2x5s in the Flask worker) — currently a manual diagnostic endpoint with no frontend caller, so it only matters if something starts polling it. The host helper's accept loop polls `listener.Pending()` every 200 ms with a `Test-Path` per tick — fine for a short-lived support tool.

## Refuted candidates (verified non-issues — don't spend time on these)

1. **"save-keys silently discards a rotated key that failed validation."** Refuted: the 200 response carries per-provider `validation_results`, and both UIs surface the failure ("Settings saved. Google Maps: ..." via `showUserNotification`) — `settings.js:214–222`, `setup-wizard.js:861–871`.
2. **"Azure proxy lost its 429/401/403-specific user guidance."** Refuted: in `main`, those specific messages were raised as bare `Exception`s and swallowed by a generic `except -> 500 'Internal map proxy error'`; they never reached users. The new path returns 502 with structured `category` + `status_code` in `details` — strictly more information than before.
3. **"Operation-status normalizer requires fields the helper omits, breaking the duplicate-operation guard."** Refuted for the real helper: `New-TowerScoutHostHelperPublicOperationStatus` emits both `provider` and `operation_type` (`TowerScoutHostHelper.ps1:509–518`, populated on GET at :602–606). Only the *simulated* helper omits them (see fixture-alignment note above); no live path feeds its shape to the normalizer today.
4. **No CLAUDE.md/instructions violations** — checked against `.github/copilot-instructions.md` and `.github/instructions/*`: `ts_*.py` naming, no hardcoded secrets, sanitized logging, validation surface, and the generated-bundle rule (the `towerscout.js` changes are a genuine rebuild, header/date intact) all comply.

---

## Suggested fix order

1. **F1** (pipefail) — 3-line workflow change; do first so the CI stops lying.
2. **F2 + F3** (token length, 503 template) — makes the e2e jobs actually prove Gate 3; expect red until both land.
3. **F6** (simulated `/health` + read-only probe) — deletes the retry/backoff complexity added in the last three commits of this PR.
4. **F4** (falsy-body TLS_OK) — small guard, closes the invalid-key-accepted hole.
5. **F5, F7** (geocode fallback, save-keys default) — directions decided by the product owner 2026-07-07; implement per the "Decided direction" blocks in each section (F5: fallback + surfaced TLS warning + per-run unhealthy marking; F7: derive omitted default from the validated set).
6. **F8–F10** (panel loop, dead code, dedup) — fold into the enablement PR or a cleanup commit.

*Review artifacts: verification was performed against the working tree at `bca6341` on branch `pr-46` (local checkout `c:\Users\Jonat\Documents\TowerScout\TowerScout`). Line numbers reference that commit.*

---

## Implementation notes for the assigned agent

These instructions govern how the fixes above are to be implemented. Read this section fully before writing any code.

### Scope and order

1. Implement the findings in the order given in "Suggested fix order" (F1 first, then F2+F3, F6, F4, F5+F7, then F8-F10). The order is load-bearing: F1 restores CI's ability to report failure, and everything after it depends on that signal being real.
2. One commit per finding (F2+F3 may share a commit since they make the same jobs pass). Reference the finding ID in each commit message, e.g. `fix(ci): enable pipefail on piped test steps (F1)`.
3. F10 is deferrable. If the packaging implications (below) cannot be verified, stop and flag it rather than guessing.
4. Do NOT enable the gated control plane. `provider_helper_available()` returning `False` and `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false` are documented Gate-3 staging decisions and stay as they are. Nothing in this report authorizes flipping them.
5. Do NOT re-investigate or "fix" anything in the "Refuted candidates" section. Those were verified as non-issues; the report explains why.

### The red-CI rule (critical)

After F1 lands, the two Puppeteer e2e steps WILL fail. This is expected and correct: they have always been failing (F2, F3); F1 merely makes the failure visible. The failures resolve when F2 and F3 land.

Under no circumstances may you get these jobs green by weakening them. Specifically prohibited: re-introducing a pipe that masks exit codes, adding `continue-on-error`, `|| true`, or try/catch-and-exit-0 around test invocations; loosening an assertion (e.g. accepting 400 where 202 is expected, or "any status" where 503 is expected); deleting or skipping a test to avoid its failure; marking a template "non-runnable" to dodge the e2e job. If a test cannot pass for a reason not described in this report, stop and report the discrepancy instead of adapting the test to the observed behavior. The tee-masking bug, the POST-probe retry stack, and the assertion-free templates in the current PR are all artifacts of iterating against a green-but-meaningless signal; do not repeat that pattern.

### Verification requirements

- Frontend/e2e: run locally before pushing. The stack is plain Node: start `tests/helpers/simulated_helper.js` and a static server per `.github/workflows/task-087-frontend-puppeteer.yml`, then run both templates with `E2E_USE_SERVER=1` and confirm exit code 0 AND that the assertions actually executed (check the logged poll sequence is non-empty for the live-poll template).
- Python: the suite requires Python 3.11 or 3.12 (`webapp/requirements.txt` pins numpy 1.26.4 / torch 2.2.1, which do not install on 3.13). Run `pytest tests/unit/` in a 3.11/3.12 environment or container. Do not "fix" the pins to make 3.13 work; that is out of scope.
- A finding is done when: the fix is implemented, the relevant tests pass locally, CI is green for real (post-F1 semantics), and no test was weakened to achieve it.

### Per-finding constraints

- **F1:** prefer the workflow-level `defaults.run.shell: bash` form so future steps inherit pipefail. Verify by temporarily forcing a template to exit non-zero and confirming the step fails (then revert the probe).
- **F2:** use a token matching `[A-Za-z0-9_-]{32,128}` in BOTH templates. Also add the explicit POST status assertion (expect 202) so contract regressions fail at the POST, not downstream.
- **F3:** implement option 1 or option 2 from the finding. Option 3 (branching the expected status on `useReal`) is rejected: it makes the e2e run assert nothing.
- **F4:** the guard must treat a Google 2xx with missing/empty/non-dict JSON as unverified (PROVIDER_HTTP_ERROR or a dedicated category), while leaving the existing non-empty-body status checks untouched. Add a regression test: 200 + `{}` must NOT validate the key.
- **F5:** implement exactly the DECIDED direction block (fallback + surfaced warning + all-fail TLS-categorized error + per-run unhealthy marking). State-lifetime constraint: the "provider unhealthy" mark must be scoped to the current detection run (or a short TTL) and must not persist indefinitely, leak across runs, or permanently blocklist a provider that has recovered. Acceptance tests (all three required):
  1. Provider A fails with a TLS-categorized error, provider B succeeds: an address is returned AND the TLS warning for provider A is recorded/surfaced.
  2. Both providers fail with TLS-categorized errors: the returned failure is TLS-categorized (not generic), so repair guidance appears.
  3. Single-provider configuration: behavior identical to current (categorized failure, repair guidance).
- **F6:** mirror the REAL helper's `/health` response shape (`scripts/lib/TowerScoutHostHelper.ps1:2053-2062`), not an invented one. Exempt `/health` from the rate limiter. After switching `ci_start_services.sh` to the read-only probe, delete the POST-probe retry/backoff machinery rather than leaving it dormant.
- **F7:** implement the four rules in the DECIDED direction block verbatim. Making `default_map_provider` required was considered and rejected; do not implement that instead.
- **F8:** edit `webapp/js/src/setup-wizard.js` (source), then rebuild the bundle. NEVER hand-edit `webapp/js/towerscout.js`; it is generated build output (see the repo's CI "Rebuild frontend bundle" step for the build command). A diff to `towerscout.js` without a corresponding source change is a defect.
- **F9:** delete `_allow_insecure_tls()` and `TRUTHY_ENV_VALUES` from `webapp/ts_maps.py`. Confirm zero references remain repo-wide before and after.
- **F10:** the PowerShell extraction target is `scripts/lib/`. Before committing, confirm the new module is included by `scripts/package-release.ps1` and lands in the built package (check against `tests/unit/test_release_package_script.py`), and that both consuming scripts still run under Windows PowerShell 5.1 (the `.cmd` wrappers launch WinPS, not pwsh). If any of this cannot be verified, defer this finding and say so.

### Reporting back

For each finding, report: what changed (files), how it was verified (exact commands and results), and any deviation from this document with justification. If any finding's description does not match what you observe in the code, stop work on that finding and report the mismatch — do not improvise a different fix.
