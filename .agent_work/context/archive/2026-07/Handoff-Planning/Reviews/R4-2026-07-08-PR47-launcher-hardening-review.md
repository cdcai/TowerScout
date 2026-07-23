# TowerScout External Review — R4 (PR #47: release-package launcher hardening)

> **HISTORICAL REVIEW**: Preserve as evidence. Current pilot/adoption action is
> defined in `../PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`.

| | |
|---|---|
| **Review round** | R4 (follows R3, 2026-07-08; next round will be R5) |
| **Date** | 2026-07-08 |
| **Reviewed state** | PR #47 `fix/task-088-v011-release-hardening` @ `44b94db` (draft), base `main` @ `dfe9e6b` (current tip — no drift), 3 commits, `mergeable_state: clean`; both PR workflows green at the head SHA |
| **Scope** | Line-level review of the launcher env-sync and engine-level image-identity check against the R3 §5.1 review checklist; merge-readiness verdict |
| **Method** | Full diff review; call-graph tracing of every entry point; package-root gating verified against the dev repo's own manifest; behavior comparison of `status.ps1` old vs new on the stopped-app path; CI/API checks |

---

## 1 · Verdict

**The two fixes are implemented correctly at their core — the design is exactly right — but the PR is not ready to merge as-is.** Two blocking items: ~25,700 lines of accidentally committed CI/test debris (including a binary ZIP), and a behavior regression in `scripts/status.ps1` that turns the routine "status while the app is stopped" case into a false **"image does not match pinned identity"** failure. Both are small, contained fixes. With B1 and B2 addressed (and ideally the three cheap S-items), this PR is ready to undraft and merge, and the `v0.1.1` flow in R3 §5.3 can proceed.

What is **not** in question: the env-sync semantics, its scoping, its call sites, the managed-variable list, the identity-check mechanics, and the test approach are all verified correct (§2).

---

## 2 · R3 §5.1 checklist — verification results

| Checklist item | Result | Evidence |
|---|---|---|
| Precedence semantics incl. absent-key handling | **PASS — stronger than asked** | `Sync-TowerScoutPackageEnvToProcess` sets each managed var from `.env` when present, and **removes it from the process environment when `.env` omits or blanks it** — host residue for a managed name can never win. |
| Scope: release-package roots only | **PASS** | Gated by `Test-TowerScoutReleasePackageRoot` = `release-manifest.v1.json` present with `release_version != "template"`. Verified the dev repo's own manifest says `"template"`, so developer checkouts keep normal env-override workflows. |
| Managed set completeness | **PASS (one optional gap, S3)** | All 14 `compose.yaml`-interpolated vars plus 7 launcher-read vars (`COMPOSE_PROJECT_NAME`, `PODMAN_COMPOSE_PROVIDER`, `PYTORCH_INDEX_URL`, GPU overlay flags, `TOWERSCOUT_PODMAN_MACHINE`, `TOWERSCOUT_PYTORCH_FLAVOR`). `COMPOSE_PROJECT_NAME` removal is safe — verified nothing in `scripts/` ever sets it programmatically. Missing only the GPU-overlay `NVIDIA_*` pair (S3). |
| Engine coverage / call sites | **PASS for launch paths** | Sync runs in both branches of `Initialize-TowerScoutEnvFile`, which is called by `launch.ps1:248` (before `compose up` at :271), `start.ps1:17` (before up at :19), `import-assets.ps1:29`, `import-tls-ca.ps1:27`. Both engines share these paths. `status`/`stop`/`logs` do **not** sync — see S1. |
| TLS-repair interaction | **PASS** | Repair writes the bundle path into `.env`; the next `start`/`launch` syncs it into the process. `import-tls-ca` itself syncs. `.env` remains the source of truth throughout. |
| WinPS 5.1 compatibility | **PASS (one style hazard, S2)** | No pwsh-only syntax (no ternary/`??`/`?.`); `[pscustomobject]`, `ConvertFrom-Json`, `Env:` provider all 5.1-safe. The `$matches` automatic-variable collision (S2) is behaviorally benign but fragile. |
| Engine-level identity check (R3 §5.2) | **PASS — implemented in-product** | `Get-TowerScoutRunningImageIdentity` inspects the running container (`.Image`, `.Config.Image`) and its image `RepoDigests` on both engines with graceful nulls; `Test-TowerScoutRunningImageMatchesPackage` matches the pinned digest against RepoDigests. The host-override spoof scenario (`towerscout:local`, no RepoDigests) is caught and fails `status` with exit 1 — precisely the R3 hole, closed. |
| No test weakening; CI green | **PASS** | Zero deletions in any code or test file (the −13 are `.agent_work` tracker edits). Both workflows green at `44b94db`. New coverage: a CI-executed source-contract test on `status.ps1`, plus Windows-only behavioral tests that reproduce the exact attack values (`towerscout:local`, bogus digest, `C:/bad/certs.pem`, engine override) and assert both the override and the remove paths. Windows-only skipping matches the repo's documented validation model (HANDOFF.md) — noted, not objected to. |
| Records updated | **PASS** | TASK-088/TASK-089/current-tasks record the v0.1.1 path; the decision memo and R2/R3 review docs are committed per the established pattern. |

---

## 3 · Blocking findings

### R4-B1 · BLOCKER (hygiene) — ~25,700 lines of accidental CI/test debris are committed in the PR

**What:** 15 of the 27 changed files are not part of the fix:

- `artifacts/run-28827051189/test-results-3.11|3.12/{bandit-report.json, coverage.xml}` — 4 files, ~24,500 lines of downloaded CI output
- `artifacts/run-28828322075/run-logs-28828322075.zip` — a **binary** ZIP
- `artifacts/**/puppeteer-e2e-logs/ci_probe_*.{json,txt}` — 6 probe files
- `artifacts/**/image-metadata-v0.1.0-{cpu,cuda121}/image-metadata.json` — 2 files (useful *evidence*, wrong home)
- `test-artifacts/{ci_probe_last_request.json, ci_probe_resp_body_1.txt, ci_probe_response.json, helper_health.json}` — local Puppeteer run output at the repo root

**Why it matters:** this is exactly the debris class the B1/R1 cleanup spent effort removing from the repo's CI; merging it enshrines ~26k junk lines in `main` history right before the cdcai push, and the binary ZIP can never be meaningfully diffed.

**Action:** `git rm -r artifacts/ test-artifacts/` on the branch. Keep the two `image-metadata.json` files by moving them to the validation-evidence convention (outside the repo, alongside the packaging-workstation evidence) or `.agent_work/evidence/` if a tracked copy is wanted. **Also add `test-artifacts/` and `artifacts/` to `.gitignore` in this PR** — the root cause is that the Puppeteer suites write `test-artifacts/` into the working tree and nothing ignores it, so this will recur on every local e2e run otherwise.

### R4-B2 · BLOCKER (behavior regression) — `status.ps1` reports a false image mismatch when the app is simply not running

**What:** `Test-TowerScoutRunningImageMatchesPackage` returns `Checked=true, Matches=false, Reason="container_not_found"` when no service container exists. `status.ps1` treats every `Matches=false` identically:

- **Old behavior**, package root, app stopped: compose ps exits 0 (empty) → readiness probe fails → accurate `"TowerScout readiness endpoint is not reachable"` warning, **exit 2**.
- **New behavior**, same situation: `container_not_found` → **"Running container image does not match this package's pinned identity"**, **exit 1** — before the readiness probe ever runs.

Running `status.cmd` while the app is stopped is a routine, documented flow (the setup deck's readiness step, support triage after `stop.cmd`). A false "pinned identity mismatch" is the worst possible message there — it sends support hunting a supply-chain-flavored problem that doesn't exist.

**Action:** special-case the reason. Reserve the mismatch warning + `exit 1` for `Reason -eq "mismatch"`; for `container_not_found`, print an informational "no running TowerScout container found for this package" (or nothing) and fall through to the readiness probe, preserving the old accurate down-state semantics. The Windows behavioral test should pin this: stopped-app status must not emit the mismatch warning.

---

## 4 · Should-fix (cheap; bundle with the blockers)

- **R4-S1 — run the sync in `status.ps1` too** (one line: `Initialize-TowerScoutEnvFile -RootPath $repoRoot` or the sync call directly after dot-sourcing). Without it, stale `COMPOSE_PROJECT_NAME`/`PODMAN_COMPOSE_PROVIDER` residue makes the container lookup miss on a *healthy* app → with B2 fixed this degrades to a wrong "not running" rather than a scary mismatch, but syncing makes `status` see the same world as `launch`. Consider the same for `stop.ps1`/`logs.ps1` (stale project-name residue can make `stop` target the wrong project — pre-existing, out of scope, but one line each while here).
- **R4-S2 — rename the `$matches` local** in `Test-TowerScoutRunningImageMatchesPackage` (e.g. `$isMatch`). PowerShell variable names are case-insensitive and `$Matches` is the automatic variable the `-match` operator assigns: on the digest-match path the function currently returns `Matches = <regex-match hashtable>` instead of `$true`. Behavior survives only because the hashtable is truthy — it will confuse the first person who serializes or strictly types the result.
- **R4-S3 (optional) — add `NVIDIA_VISIBLE_DEVICES` and `NVIDIA_DRIVER_CAPABILITIES`** to the managed set. The GPU overlays interpolate both from the host; remove-if-absent would pin packaged GPU launches to the compose defaults (`all` / `compute,utility`) regardless of workstation residue. Low likelihood, zero cost, GPU-cell-relevant.

---

## 5 · Merge checklist (undraft when all boxes tick)

1. B1: debris removed; `.gitignore` gains `test-artifacts/` + `artifacts/`; image-metadata files rehomed.
2. B2: `container_not_found` special-cased; behavioral test covers stopped-app status.
3. S1/S2 applied (S3 at the Developer's discretion — record either way).
4. Windows behavioral slices re-run locally **after** the above changes (`test_task_074_bootstrap`, `test_task_081_runtime_hardening`, `test_import_assets_script`, `test_release_package_script`) and results noted on the PR.
5. CI green at the new head; diff re-checked to be code + tests + `.gitignore` + `.agent_work` records only (target: roughly 27 files → ~12).
6. Merge normally (no special merge-commit requirement — this branch contains no upstream merge), freeze `main`, then proceed to the R3 §5.3 `v0.1.1` flow: tag the green tip, dispatch both builds from ref `v0.1.1`, packages, D4.

---

## 6 · What R5 will check

- The re-rolled PR head: blockers resolved, no debris, CI green, merge landed cleanly.
- `v0.1.1` tag/build/package flow per R3 §5.3–§5.5, including: new digests distinct from `0c1ea503…`/`9f1563eb…`; patched `TowerScoutCompose.ps1` inside both ZIPs; `status.cmd` on a running cell prints the running digest and passes; `status.cmd` on a stopped cell reports down-state without a mismatch warning.
- D4 evidence: the in-product identity line (`Running image digest: …`) captured per cell — this now supplements the readiness JSON as the anti-spoof record.

*Prepared by the external reviewer, 2026-07-08. Anchors: `Sync-TowerScoutPackageEnvToProcess` and `Get-TowerScoutPackageManagedEnvironmentNames` (TowerScoutCompose.ps1, PR head); `Test-TowerScoutRunningImageMatchesPackage` return paths incl. `container_not_found`; `status.ps1` gate at lines 18–38 (PR head) vs the readiness fallback at 40–74; call sites launch.ps1:248/start.ps1:17/import-assets.ps1:29/import-tls-ca.ps1:27.*
