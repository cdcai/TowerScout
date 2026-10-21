# Code Review — PR #89 "Fix Task-103 W10 lifecycle recovery"

**Date:** 2026-09-28
**Branch:** `fix/task-103-w10-lifecycle` → `main` (head `31d3f3a`, diff base `afbe843`)
**Scope:** +849 / −87 across 31 files
**Verdict:** **NOT READY TO MERGE.** Fix the 4 blocking findings and wire the new contract test into CI first. Remaining items may ride in a follow-up.

All file paths below are relative to the repository root. Line numbers refer to the PR head commit `31d3f3a`.

## Review context

- CI at head is green: Trivy, security, test (3.11/3.12), frontend-test, Docker frontend stage, production controller contracts + e2e, Windows host-helper contracts all pass; `build` skipped. Merge state is clean.
- The PR's core ideas are sound: block detection retries while a cancellation is unresolved, and carry the host port through the TLS repair chain.
- All new tests in the PR pass as written (executed in a clean worktree).
- The `[Nullable[int]]` + `ValidateRange` PowerShell parameter pattern referenced below was empirically verified to work on Windows PowerShell 5.1.

## Blocking findings (fix before merge)

### B1. Repair wrapper silently rebinds live containers to port 5000
**File:** `scripts/repair-provider-tls.ps1:12`
The wrapper declares `-Port` as a non-nullable int with default `5000` and always forwards it to `import-tls-ca.ps1`. This defeats the importer's `$PSBoundParameters.ContainsKey('Port')` preserve-when-omitted design.
**Failure scenario:** Container running on port 5211; operator runs `repair-provider-tls.cmd -Provider google -Engine docker -Gpu on -Apply` without `-Port`. The importer receives an explicit `-Port 5000`, sets `TOWERSCOUT_PORT=5000`, and its `compose up -d towerscout` recreates the live container bound to `127.0.0.1:5000` — the deployment moves ports mid-repair and the previous URL goes dead.
**Fix:** Give the wrapper the same `[Nullable[int]]` parameter + `ContainsKey`-gated forwarding the importer uses, so an omitted port stays omitted through the whole chain.

### B2. Importer stomps custom ports in non-package (source) checkouts
**File:** `scripts/import-tls-ca.ps1:36`
The new unconditional `Set-TowerScoutPortEnvironment` call forces process `TOWERSCOUT_PORT=5000` when the env var is empty.
**Failure scenario:** In a source checkout, `release-manifest.v1.json` has `release_version: "template"`, so `Sync-TowerScoutPackageEnvToProcess` early-returns and never loads `.env` into the process env. With `TOWERSCOUT_PORT=5211` in `.env` and the container running on 5211, running the importer without `-Port` sees an empty `$env:TOWERSCOUT_PORT`, writes `5000` into the process environment, and process env takes precedence over the `.env` file during compose interpolation — `compose up -d towerscout` recreates the container on 5000. Before this PR the importer never touched the variable and compose correctly fell back to `.env`.
**Fix:** Only set the process variable when a port was actually resolved from an explicit parameter or an existing env value; otherwise leave it unset so compose falls through to `.env`.

### B3. `/abort` long-poll breaks the existing cancel smoke test contract
**File:** `webapp/towerscout.py:2734` (route change) vs `tests/frontend/test_detection_workflow_smoke.js:540,582` (un-updated consumer)
The route now blocks up to 60s while probing the detection lock and can return HTTP 202. The Puppeteer cancel smoke test still uses `waitForResponse({ timeout: 10000 })` and throws on any non-200 `/abort` response.
**Failure scenario:** A real mid-run cancel where the in-flight model/download step takes >10s to observe the exit event rejects with a Puppeteer timeout; a step >60s yields 202 → "Abort request returned status 202." The GPU/CPU browser validation runs flake or fail on slow cancels.
**Fix:** Update the smoke harness in this same PR to tolerate the new contract (longer wait, 202-as-pending handling), or bound the server-side wait below the harness timeout.

### B4. Stale `/abort` response can corrupt a subsequent detection's UI state
**File:** `webapp/js/src/ui/search.js:775` (`cancelRequest`)
The handler applies whatever `/abort` response arrives, with no request-generation guard. The race existed before, but the server's new up-to-60s hold makes it realistic.
**Failure scenario:** User double-clicks Cancel (two `/abort` requests in flight). The first returns `retryReady:true`, pending clears, the user starts a new detection and `enableProgress` runs. The second `/abort` response arrives seconds later (held server-side while probing the lock, which the NEW run now holds): the 200 branch calls `disableProgress(0,0)`, hiding the new run's overlay and killing its poll timer; the 202 branch sets `detectionCancellationPending = true` and overwrites the status with "Cancellation still pending", blocking further detections until another Cancel.
**Fix:** Capture a request sequence number (e.g. `detectionRequestSeq`) before the fetch and discard the response if it changed by the time it resolves.

## Should-fix (before merge, or immediately after in a follow-up)

### S1. `/abort` pins a WSGI worker for up to 60s with nothing to cancel
**File:** `webapp/towerscout.py:2730`
When the session has no run (`_mark_detection_run_cancel_requested` returns `None`) — including stray GETs, which the route still allows — the request still parks on the lock for up to 60s, then reports `cancelled`/`retryReady` for work it never signalled. Repeated Cancel clicks (which the UI explicitly instructs) each pin another worker, starving fixed-size thread pools that also serve `/api/detection/progress`.
**Fix:** Short-circuit when `run_state is None`; report slot readiness via the existing progress tracker instead of holding the request. Consider restricting the route to POST.

### S2. New cancel-recovery contract test is not enforced anywhere
**File:** `tests/frontend/test_detection_cancel_recovery_contract.js`
Neither `.github/workflows/ci.yml` nor any npm script runs it, so the contract it defines cannot catch regressions (same hollow-CI pattern previously found and fixed for the e2e suite in an earlier PR).
**Fix:** Add it to the CI workflow next to the other frontend contract tests and/or an npm script CI invokes.

### S3. Readiness probe by lock acquisition causes spurious 429s and stale readiness
**File:** `webapp/towerscout.py:2734`
The abort route probes readiness by transiently acquiring `detection_job_lock`. A concurrent legitimate `/getobjects` doing `acquire(blocking=False)` during that window gets 429 `DETECTION_BUSY` when nothing is running. Conversely, between the probe's release and the client's retry, another queued client can take the slot, making `retryReady:true` immediately stale.
**Fix:** Don't probe by acquisition; consult run/tracker state instead, and treat `retryReady` as advisory on the client.

### S4. Unparseable 200 `/abort` body permanently locks out detections
**File:** `webapp/js/src/ui/search.js:770`
If `response.ok` is true but `response.json()` throws (version skew against an older backend that returns plain text, or a proxy rewriting the body), `result` stays null, the `retryReady` check fails, and `detectionCancellationPending` stays true — `getObjects`/`getObjectsV2` refuse to start any detection even though the server slot is free. The removed code unlocked the UI on any completed `/abort`.
**Fix:** Treat an OK response with an unparseable body as terminal (clear pending), or fall back to polling the progress endpoint to resolve state.

## Minor / cleanup

### M1. Three divergent port-resolution implementations
`scripts/launch.ps1:5` binds `$Port` from the pre-sync process env and stomps `$env:TOWERSCOUT_PORT` after `Initialize-TowerScoutEnvFile` (line ~423), the importer preserves the synced value, and the wrapper forces 5000. With `TOWERSCOUT_PORT=5211` in a package `.env`, a fresh-shell `start.bat` still starts the container on 5000 unless `-Port` is retyped every launch. Route all three entry points through `Set-TowerScoutPortEnvironment` after env sync; this also removes the docs' "append `-Port` to every start.bat command" workaround.

### M2. Progress bar keeps advancing under a stale "still pending" banner
`webapp/js/src/ui/search.js:783` — after a 202, `activeDetectionRequest` is nulled so live progress polling stops, but the estimate-based timer keeps firing: the bar fills to 100% under "Cancellation still pending" indefinitely, and the user is never told when the slot actually frees. Polling `/api/detection/progress` here would clear `detectionCancellationPending` automatically instead of requiring a blind second Cancel.

### M3. Redundant `-Port` / `-PortWasSpecified` two-parameter protocol
`scripts/lib/TowerScoutCompose.ps1:651` — `Set-TowerScoutPortEnvironment` silently ignores `-Port` unless `-PortWasSpecified` is also passed; a future caller writing `-Port 5300` alone gets the env/default value with no error. `if ($null -ne $Port)` inside the function expresses intent by nullability alone and removes the switch, its guard throw, and the caller-side if/else duplication in `import-tls-ca.ps1:32-37`.

### M4. Cancellation guard duplicated into unreachable legacy code
`webapp/js/src/ui/search.js:186` — `window.getObjects` is assigned `getObjectsV2` (~line 910), so legacy `getObjects(estimate)` is dead code, yet the PR patches it too, leaving the identical multi-line warning string in four places (v1 + v2, doubled again in the generated `webapp/js/towerscout.js` bundle). Delete the legacy function or extract a shared guard helper.

## Acceptance criteria for merge

1. B1–B4 fixed; S2 (CI wiring) done.
2. Port-preservation verified end-to-end in both directions: a package deployment on a non-default port survives `repair-provider-tls` without `-Port` (B1), and a source checkout with a custom `.env` port survives `import-tls-ca` without `-Port` (B2).
3. Cancel smoke test passes against the new `/abort` contract, including a slow-cancel case (B3).
4. New and existing frontend contract tests run green in CI, not just locally.
