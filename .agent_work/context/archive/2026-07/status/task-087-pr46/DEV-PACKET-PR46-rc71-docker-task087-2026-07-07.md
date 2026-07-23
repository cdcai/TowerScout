# TowerScout Developer Packet — PR #46 Verification, rc7.1 Docker QA, and Task-087 Completion Plan

**Date**: 2026-07-07
**Audience**: Task-087 developer / release owner
**Sources consolidated here**:
- `PR46-bca6341-quality-review-2026-07-07.md` (full findings report + Verification Addendum)
- `rc7.1-docker-qa-2026-07-07/RC7.1-DOCKER-CPU-GPU-QA-2026-07-07.md` (this evening's Docker CPU+GPU validation)
- `.agent_work/tasks/active/TASK-087-host-side-tls-repair-control-plane.md` (canonical task plan, implementation log)
- `.agent_work/tasks/active/TASK-087/live-wrapper-validation-2026-07-06.md` (Gate 1/2 live-wrapper evidence)

---

## 1. Executive summary

- **PR #46 fixes: all 10 quality-review findings verified correctly implemented at head `533e18b`.** No test weakening; CI green is now meaningful (pipefail active). Full re-review table in §2.
- **rc7.1 release packages re-validated tonight on Docker Desktop — CPU and CUDA both PASS end-to-end**, including CUDA device selection on the T1000 and a 12/12 fixed-fixture CPU↔GPU parity run (53 detections, identical per tile; confidences agree to 1.7e-06). Docker now matches this morning's Podman result, so rc7.1 is proven engine-agnostic. Summary in §3.
- **One new low-severity finding** from tonight's QA (shared per-IP rate-limit key across endpoints — §4.1) plus two small pre-enablement items carried from the review notes (§4.2, §4.3).
- **Task-087 status**: Gates 1–2 passed and merged (PR #45); the internal Docker CPU/off live-wrapper run PASSED at `c55814b`; Gate 3's non-mutating contract slices are complete on PR #46 and independently verified. The control plane still ships dark behind two hardcoded gates, by design. **Remaining work: merge PR #46, the enablement slice (real helper availability + browser mutation gate + live fetch/poll/reconnect wiring), then Gate 4 packaging + managed-network validation.** Plan with sequencing and sign-off checkpoints in §6.

---

## 2. PR #46 Verification Addendum (fixes reviewed at `533e18b`, 2026-07-07)

The developer's fixes (commits `2b67123`, `533e18b`) were independently re-reviewed line-by-line against the findings report. **Verdict: all 10 findings correctly implemented. No test weakening detected — assertions got stronger, not weaker. CI is green on `533e18b`, and that green is now meaningful (pipefail active).**

| # | Status | How verified |
|---|--------|--------------|
| F1 | PASS | `defaults.run.shell: bash` added at workflow level (the preferred form). All Puppeteer steps now inherit pipefail. |
| F2 | PASS | Both templates use `'TEST_TOKEN_' + 'X'.repeat(32)` (43 chars, matches the 32-128 rule). Explicit `postStatus !== 202` assertion added. The e2e job passes WITH pipefail active — empirical proof the flow now works. Bonus: fixed a latent injection-ordering bug (`evaluateOnNewDocument` now registered before `page.goto`, plus a post-goto `evaluate`), which is likely why the poll flow genuinely runs now. |
| F3 | PASS | Option 1 (the report's preferred choice): the helper-unavailable step was removed from the e2e job; the template still runs in the templates job where the shim produces the 503. |
| F4 | PASS | Guard implemented as specified: Google 2xx with empty or non-Mapping body returns PROVIDER_HTTP_ERROR (`ts_provider_http.py:346-348`; `Mapping` import confirmed present). Required regression test added: 200 + `{}` -> `valid=False`, category `provider_http_error`. |
| F5 | PASS | All four decided elements implemented: TLS failure recorded + `continue` to next provider; warning carried onto the successful fallback result (`warning_message/category/provider` + sanitized `logger.warning`); all-fail path returns the TLS-categorized error (preferred over generic, as decided); per-run skip via an instance-level cache with a 60s TTL. Lifetime constraint verified: the service is instantiated once per detection run's address-lookup phase (`towerscout.py:715`), so the marking is naturally run-scoped and cannot permanently blocklist a recovered provider. All three required acceptance tests present, plus a fourth covering the skip behavior (`tests/unit/test_geocoding.py`). |
| F6 | PASS | `GET /health` added to the simulated helper; shape verified field-for-field against the real helper's `ConvertTo-TowerScoutHostHelperPublicRuntimeProfile` (`helper_version`, `state: "ready"`, `runtime{engine,gpu,app_port,package_flavor}`, `capabilities{...}`) — not an invented shape. `/health` exempted from the rate limiter (verified live: 35 rapid GETs, 35x HTTP 200). `ci_start_services.sh` probes `/health` read-only; the entire POST-probe/retry/backoff machinery was deleted, not left dormant (-52 lines). |
| F7 | PASS | All four rules implemented exactly: explicit-but-invalid default still 400s; omitted + one validated derives the default (persisted to env, `default_map_provider_derived: true` in the response); omitted + both validated uses the env preference; error message now names `default_map_provider`. Unit test covers the derivation path. |
| F8 | PASS | Implemented the sanctioned minimum: "N additional providers also need repair" notice in both the panel message and the status line (`getVisibleProviderTlsRepairViewModels` replaces first-only). New contract test drives BOTH providers repairable and asserts the notices. Bundle genuinely rebuilt (new build date 2026-07-07T21:54Z, auto-generated header intact, content parity with source confirmed). |
| F9 | PASS | `_allow_insecure_tls()` and `TRUTHY_ENV_VALUES` deleted from `ts_maps.py`; no references remain. (The `_allow_insecure_tls` in `ts_config.py` is a different, pre-existing function outside this finding's scope.) |
| F10 | PASS | New shared `scripts/lib/TowerScoutCertificateStore.ps1`; both `import-tls-ca.ps1` and `repair-provider-tls.ps1` dot-source it; duplicates deleted; `package-release.ps1` ships the new lib and `test_release_package_script.py` asserts it lands in the package. The JS half was also done: shared `fetchJson`/`providerFailureMessage`/`saveFailureMessage` extracted to `utils/apiHelpers.js` (`window.TowerScoutConfigApi`), consumed by both `settings.js` and `setup-wizard.js`. |

**Minor notes (no action required):**
1. Process deviation: two commits total rather than one per finding. Cosmetic; the work maps cleanly to findings.
2. The unified cert-store search order is LocalMachine-first, which changes `import-tls-ca.ps1`'s previous CurrentUser-first order. Functionally identical (lookup is by thumbprint; only the source store of the copy differs).
3. `setup-wizard.js` now uses the shared (settings-style) `providerFailureMessage`, dropping its normalize-based variant — a subtle message-precedence change; all contract tests still pass.
4. `TowerScoutCertificateStore.ps1` has no trailing newline and carries over the pre-existing unapproved "Normalize-" verb. Cosmetic.
5. As a consequence of F3 option 1, the e2e job no longer exercises a helper-unavailable scenario at all. If e2e coverage of that path is wanted later, implement the report's option 2 (an unavailability mode in the simulated helper). See §4.3.

---

## 3. rc7.1 Docker CPU + GPU QA (2026-07-07 evening) — PASS

Full report and raw artifacts: `Validation Evidence\rc7.1-docker-qa-2026-07-07\`. Highlights:

- **Host**: Windows 11, Docker Desktop (server 29.6.1, Compose v5.1.4, nvidia runtime), NVIDIA T1000 8GB.
- **Setup path** (both packages, fresh extractions, official commands): preflight OK; images pulled by pinned digests (cpu `14b6ef52…`, cuda121 `95f1f396…`); asset import with manifest hash verification clean; keys seeded via `POST /api/config/save-keys` (both providers validated live); `state=ready`.
  - CPU cell: `selected_device=cpu`, torch `2.2.1+cpu`.
  - GPU cell (`-Gpu on`): `device_policy=cuda`, `selected_device=cuda`, `pytorch_flavor=cuda121`, torch `2.2.1+cu121`, `cuda_device_name=NVIDIA T1000 8GB`.
- **Fixed-fixture CPU↔GPU parity (rc5 method, fresh 12-tile set)**: per-tile detection counts identical across CPU pass 1, CPU pass 2 (within-cell determinism), and GPU — total 53/53/53. Max |Δconf| CPU vs GPU = 1.7e-06 over 32 compared detections (pure float noise; byte-identical is not expected across CPU/CUDA numerics).
- **Live AOI (200 West St NYC, 200 m circle, engine=newest)**: google 67 (CPU) / 67 (GPU); azure 69 (CPU) / 34 (GPU). The Azure spread is the provider-imagery bimodality documented in the rc6 validation — not a device effect (fixture parity above proves the model path is identical).
- Combined with this morning's Podman run, rc7.1 is now validated **end-to-end on both engines, both device flavors**, on this hardware.

---

## 4. Open items for the developer (small, none block PR #46 merge)

### 4.1 NEW — Shared per-IP rate-limit key couples unrelated endpoints (Low)

Found during tonight's scripted QA; **still present at `533e18b`**. Most endpoints call `rate_limiter.is_allowed(client_ip, ...)` with the bare IP as the key — detection (`towerscout.py:863`, `:2616`), geocode (`:2191`, `:2241`), maps proxy (`:2350`), custom-image upload (`:2753`), upload dataset (`:3407`) — while each passes different max/window values against the same shared counter. Consequence observed live: 12 rapid `GET /api/maps/google/static` tile fetches consumed the upload endpoint's 10-per-60s budget, so the first `POST /getobjectscustom` returned `"Rate limit exceeded for image uploads"`.

Only `config-validate`/`config-save` use scoped keys (`f"config-validate:{client_ip}"` pattern). **Suggested fix**: apply the same per-endpoint key scoping everywhere (e.g. `f"detect:{ip}"`, `f"maps-proxy:{ip}"`, `f"upload:{ip}"`, `f"geocode:{ip}"`). Mechanical change + a unit test that two endpoints' budgets don't interfere. Mostly affects scripted/support use and map-heavy interactive sessions.

### 4.2 Simulated helper `GET /operations/:id` shape still diverges from the real helper

Carried from the review's "Intentional design notes" and re-verified today: `tests/helpers/simulated_helper.js` returns only `{operation_id, state, classification, terminal}` from `GET /operations/:id`, while the real helper also emits `provider` and `operation_type` (`TowerScoutHostHelper.ps1` public operation status), which the JS normalizer requires. Harmless today (nothing live feeds the simulated shape to the normalizer), but **this must be aligned before the live poll wiring is enabled** in the enablement slice, or the e2e proof will pass against a shape the real helper doesn't produce. Small fix: include `provider` (already tracked in `ops[opId]`) and a fixed `operation_type: 'provider-tls-repair'` in both poll responses.

### 4.3 Optional — e2e helper-unavailable coverage (review note 5)

Since F3 took option 1, the e2e job no longer exercises helper-unavailable at all. If that coverage is wanted, implement option 2: an unavailability mode in the simulated helper (e.g. `SIMULATE_UNAVAILABLE=1` returning 503s) and a dedicated e2e step. Reasonable to fold into the enablement slice's test work rather than doing separately.

### 4.4 TASK-088 start boundary

For Sprint 07 execution tracking, these items split into three groups:

- **Must be handled before active `TASK-088` execution starts**:
   - the PR #46 release-facing cleanup from the handoff strategy, especially the
      CI log-publishing removal and the reviewed coverage-gap fixes for the
      bundle/dark-gate checks
   - PR #46 merge to `main` with green workflows at the merge SHA
- **Can land immediately after merge without blocking `TASK-088` start**:
   - §4.1 rate-limiter key scoping and the non-interference test
- **Do not block `TASK-088` start; keep them in later `TASK-087` work**:
   - §4.2 simulated-helper operation-status shape alignment
   - §4.3 optional helper-unavailable e2e coverage
   - real helper availability, browser mutation-gate enablement, live fetch /
      poll / reconnect wiring, and Gate 4 helper-package validation

This boundary is now recorded in `TASK-088` so the stable-release and handoff
lane does not get blocked on work that only matters once the dark control plane
is intentionally enabled.

**2026-07-08 update**: the B4 disposition was taken in the preferred direction.
The `TOWERSCOUT_SIMULATED_HELPER`-gated simulated helper routes were removed
from `webapp/towerscout.py`, so they no longer remain as an accepted residual
risk for PR #46 merge readiness or TASK-088 entry.

---

## 5. Task-087 — where it stands

| Gate | Status | Evidence |
|---|---|---|
| Gate 1 — Helper transport proof | **PASSED** (merged via PR #45) | Loopback listener without admin ACL, origin/token checks, lifecycle/TTL/stop-cleanup, launch-profile capture; `.agent_work` log entries 2026-07-02 |
| Gate 2 — Security proof | **PASSED** (merged via PR #45) | Allowlist rejections, no arbitrary-command surface, controlled runner contract + hardening tests, operation locking/idempotency/timeout states |
| Internal live-wrapper validation (pre-Gate-3 checkpoint) | **PASSED** at `c55814b` (2026-07-06, Docker CPU/off, google, port 5000) | `TASK-087/live-wrapper-validation-2026-07-06.md`: terminal `ready`, `terminal_success`, readiness returned, no fallback needed. Required the `7177cc1` stop-cleanup fix (helper-controlled stop defers session invalidation via `TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION=1`). |
| Gate 3 — Product integration proof | **Non-mutating slices COMPLETE on PR #46 (`533e18b`), verified**; enablement not started | Structured validation metadata (`repairable`, `helper_available`), per-provider failure retention, repair panel + confirmation + disabled button + multi-provider notice (F8), start-contract preview, operation-status memory/busy states, redaction contract tests, genuinely green e2e (post F1–F3) |
| Gate 4 — Managed-network package validation | **NOT STARTED** | rc7.1 packages predate the helper (no `TowerScoutHostHelper.ps1`/`host-helper.ps1`/`TowerScoutCertificateStore.ps1` in the published `scripts/lib`); repo-side `package-release.ps1` already ships the new lib |

**Deliberately dark (unchanged, correct per staging decisions)**: `provider_helper_available()` returns `False` unconditionally (`ts_provider_http.py:120`); `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false` (`setup-wizard.js:17`); no live fetch path exists. Podman remediation product exposure remains blocked pending separate sign-off.

---

## 6. Task-087 completion plan

Ordering is load-bearing: each phase ends at a review/sign-off checkpoint that the task doc requires before the next may start.

### Phase A — Land the Gate 3 proof (≈0.5 day)

1. **Merge PR #46** (`feature/task-087-gate3-product-integration` @ `533e18b` → `main`). CI is green and trustworthy; the quality review verified all fixes; nothing further blocks it. This closes the non-mutating Gate 3 contract work.
2. **Small follow-up commit(s)** (can land right after merge, before the enablement branch):
   - Rate-limiter key scoping (§4.1) + non-interference unit test.
   - Simulated-helper operation-status field alignment (§4.2) — prerequisite for Phase B's e2e.
   - Optional: helper-unavailable e2e mode (§4.3).

### Phase B — Enablement slice: complete Gate 3 (≈2–3 days) — **requires release-owner sign-off to open the two gates**

3. **Backend — real helper availability.** Replace the hardcoded `provider_helper_available() -> False` with actual detection (helper `GET /health` via the captured runtime profile), and have the backend mediate the **short-lived operation authorization** so the durable helper token never reaches the frontend (design already specified in the task doc §Architecture 6/7; the Setup Wizard authorization plumbing and redaction tests from PR #46 are ready to consume it).
4. **Frontend — open the mutation gate and wire the live path.** Set `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = true` and add the live fetch path the start-contract preview already models: confirmed `POST /operations/provider-tls-repair` (provider enum + fixed confirmation + short-lived authorization only), operation polling across the restart window, reconnecting state, readiness poll, wizard resume with provider revalidation. Duplicate-click/reload must reuse the active operation id against the *real* helper (currently only proven against the contract shim).
5. **Test the newly-lit paths.** The review flagged that the JS status/next-action vocabularies are hand-maintained mirrors of the helper's — add a drift test against the real helper's emitted states if possible; verify F8's "N additional providers" notice against a real dual-repairable state; e2e with the simulated helper covering start→poll→terminal and busy/expired/rejected branches (fixture shape from §4.2 now aligned).
6. **Internal live browser-path validation (runbook re-run).** Repeat the internal live-wrapper runbook, this time triggered through the browser flow: Docker CPU/off + google first (same scope, port, timeout budget, sanitized-evidence rules as the 2026-07-06 run), then the **Docker CUDA variant** (still missing — the live proof so far is CPU/off only). Fresh explicit approval required per the runbook's rules; record sanitized evidence in `TASK-087/`.
   - Gate 3 exit check against the task doc's criteria: repair action only for repairable TLS + helper available; never for invalid-key/quota/provider-disabled/HTTP/generic-network; helper-unavailable is a normal fallback; no concurrent operations from duplicate clicks/reloads.

### Phase C — Gate 4: packaging + managed-network validation (≈1–2 days + validation window)

7. **Package integration.** Helper artifacts into CPU and CUDA packages (repo `package-release.ps1` already ships `TowerScoutCertificateStore.ps1`; extend/verify for `host-helper.ps1`, `TowerScoutHostHelper.ps1`, launcher runtime-profile integration in the packaged `launch.ps1`/`stop.ps1` paths). Package-generation tests must assert inclusion of helper scripts AND exclusion of runtime profiles, helper tokens, helper logs, `.env`, `.env.backup.*`, TLS bundle material (`test_release_package_script.py` is the existing home for these).
8. **Internal validation package** (rc8 candidate or a `task-087-validation` build): run the standard package matrix on this workstation (the harness + fixture set from tonight's QA in `rc7.1-docker-qa-2026-07-07/` is reusable for regression parity), then **managed TLS-inspected network validation**: guided button path works; documented manual fallback still works; restart preserves port and CPU/GPU mode; ambiguous-CA selection blocks one-click and directs to manual dry-run; sanitized evidence only.
9. **Release decision + docs.** Decide rc8 inclusion vs later release per the task's "Recommended Release Position" (rc7.1 + manual TASK-086 fallback remains the tester baseline until Gate 4 passes). Update the user guides' repair sections and release notes accordingly.

### Phase D — Deferred scope (explicitly out of the completion critical path)

- **Podman Compose provider remediation** (separate helper operation): still requires its own release-owner sign-off after the Docker proof; first slice may surface sanitized preflight status only. Do not bundle into Phases B/C.
- Multi-instance behavior polish beyond the current stale/wrong-package rejection, if pilot feedback demands it.

### Sign-off checkpoints summary

| Checkpoint | Who | Before |
|---|---|---|
| Merge PR #46 | release owner | Phase A.1 |
| Open `provider_helper_available` + browser mutation gate | release owner (documented Gate-3 staging decision) | Phase B.3/B.4 |
| Each mutating live validation run | release owner, fresh approval per runbook | Phase B.6 |
| Podman installer product exposure | release owner, separate sign-off | Phase D only |
| RC inclusion of guided repair | release owner after Gate 4 evidence | Phase C.9 |

**Estimate to Task-087 completion**: ~4–6 working days plus the managed-network validation window — consistent with the task's original 4–7 day estimate given Gates 1–2 and most of Gate 3 are done.

---

*Prepared 2026-07-07. Line references are to the working tree at `533e18b` (branch `pr-46`). Raw QA artifacts: `Validation Evidence\rc7.1-docker-qa-2026-07-07\`. Full findings report: `Validation Evidence\PR46-bca6341-quality-review-2026-07-07.md`.*
