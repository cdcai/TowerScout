# TowerScout v0.1.0 Stable Release & cdcai Migration — Implementation Strategy

| | |
|---|---|
| **Audience** | The Developer executing the release + handoff work |
| **Prepared** | 2026-07-07 (from a two-pass, 35-agent adversarially-verified repo review) |
| **Deadlines** | Stable release package + migration plan: **2026-07-10** (hard stop **2026-07-13**); project ends 2026-07-15 |
| **Repo** | `c:\Users\Jonat\Documents\TowerScout\TowerScout` — fork `J-Schulein/TowerScout` of `cdcai/TowerScout` |
| **Starting state** | Branch `pr-46` @ `533e18b` = head of open **draft PR #46** into `main`; CI genuinely green; `main` @ `229f59f` |
| **Companion doc** | `TowerScout-Handoff-Review-Comprehensive-Analysis.md` (same folder) — every finding ID referenced below (e.g. *secrets-1*, *p2-runbook-4*) is fully evidenced there. Read a finding's entry before deviating from an instruction. |

Execution tracking for this plan now lives in `TASK-088` (fork-side stable
release and handoff closeout) and `TASK-089` (cdcai migration execution).

Every command in this document was validated against the actual scripts, workflows, and live GitHub state — most in a scratch-clone dry run. Where a command depends on a value produced earlier (a digest, a SHA), it is written as `<placeholder>`.

---

## 0 · The decision this plan implements

**Stable v0.1.0 is cut from `main` after merging PR #46 — not by promoting rc7.1, and without attempting to finish Task-087.**

Why (each verified): the rc7.1 tag contains two real bugs fixed on PR #46 — F4 (Google key validation accepts an empty 2xx body → invalid key saved as valid, `ts_provider_http.py:336` at rc7.1) and F5 (geocoding fail-fasts on TLS errors with no fallback to the second provider, `ts_geocoding.py:480` at rc7.1). PR #46's new control plane ships **dark** behind two hardcoded gates (`provider_helper_available()` → `False` at `ts_provider_http.py:120`; `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false` at `setup-wizard.js:17` and bundle line 7852) — no env/config can flip them, and tests pin them. Finishing Task-087 (rest of Gate 3 + Gate 4 managed-network package validation on CPU and CUDA) is not achievable by the deadline **and wouldn't remove the manual TLS commands from the User Guidance anyway** — so the guides document the manual `repair-provider-tls.cmd` flow regardless (they already do; see §F).

---

## 1 · Critical-path dependencies — raise on 07-08, they gate everything in §G

Send these asks to the cdcai owner (Chris Edens) **on 07-08**, because a dry run proved they are not currently satisfied:

1. **Write access to `cdcai/TowerScout` for Jonathan** — a dry-run push returned `403 Permission to cdcai/TowerScout.git denied to Jschulein`. No credential on this machine can push to cdcai today (*p2-runbook-5*). Fallback if refused: the PR route in §G Phase 1.
2. **Enable Issues on `cdcai/TowerScout`** — Issues are disabled on *both* repos; the backlog export (§H) has nowhere to go until this is flipped (*completeness-4 / p2-critic-4*).
3. **Confirm GitHub Actions is enabled for the org/repo and org policy allows `workflow_dispatch` + `GITHUB_TOKEN` `packages: write`** — cdcai currently has zero workflows; they arrive with the code push (*migration-6*).
4. **Agree who holds `ghcr.io/cdcai` package-write** and that they will flip package visibility to **Public** after first publish (GHCR defaults to private) (*migration-3*).

Also on 07-08, on this machine: **`gh auth login`** (gh 2.92.0 is installed but logged out — needed for release publishing). ~~Rotate the Azure Maps key~~ — **✅ done 2026-07-08** (§A1).

---

## 2 · Guardrails — prohibited actions (each has bitten someone or provably would)

- **Never force-push or squash-merge into `cdcai/TowerScout`.** Shipped packages embed exact commit SHAs in `SOURCE.txt` as the AGPL corresponding-source promise; a squash/force would orphan every release tag and break that promise (*migration-2*). If the PR fallback route is used, the owner must use **"Create a merge commit"** — put that in writing.
- **Never `git push --tags`** from this working copy. It would publish the stray local-only `uat-local-fix-2026-06-15` tag and (pre-cleanup) the stale `v0.1.0` tag, and would export throwaway validation tags to cdcai (*p2-github-1, migration-5*). Push tags by name only.
- **Do not enable the dark control plane.** `provider_helper_available()` and `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED` stay as they are. Nothing in this plan authorizes flipping them (Task-087 Gate 3/4 are the new owner's decision).
- **Do not weaken tests to get green.** No `continue-on-error`, `|| true`, loosened assertions, or deleted tests. If a test can't pass for a reason not described here, stop and report the discrepancy. (This repo has already been burned by a green-but-meaningless CI signal.)
- **Do not run the harness with `-CaptureFixtures`** — it overwrites the baseline fixture tiles in place (*p2-validation-2*).
- **Do not print secret values** anywhere (evidence, logs, commit messages). The Azure key is referenced only by prefix `7G19…` in all documents.
- **Do not upgrade torch/numpy or the Dockerfile base images this week** — a dependency bump invalidates the completed CPU/GPU parity validation. These are backlog items (§H).
- **Extract and run packages only from space-free paths** (rc6 lesson: Podman breaks under folders with spaces).
- **Use `git clone -c core.longpaths=true` for every fresh clone.** A default Windows clone fails checkout ("Filename too long") when the target directory prefix exceeds ~104 characters — verified on this machine (*p2-runbook-7*).

---

## A · Workstream A — Security remediation (start immediately; A1 is mandatory)

### A1. Rotate the Azure Maps subscription key — *(secrets-1, HIGH)* — ✅ **COMPLETED 2026-07-08**
A real 86-char Azure Maps key (prefix `7G19…`) was publicly browsable since 2026-01-05 at the tips of two branches and in deep `main` history. **The key was rotated (regenerated) in the Azure portal on 2026-07-08 — the exposed value is now inert.** Remaining follow-ups:
- Update the local `.env` used for validation runs with the new key before the §D4 validation pass (a stale key makes Azure key-validation and live-smoke steps fail and can masquerade as an F4-style defect).
- **A2 below is still required**: the branches still publish the dead credential and pre-cleanup log files — delete them for hygiene before handoff.
- The §G Phase 5 disclosure item stands (history contains a rotated key; rotation is the remediation of record).

### A2. Delete the two key-bearing branches — still pending
```
git push origin :improvements :feature/geocoding-system-integration
```
Their only unique content is 3 stale Dec-2025/Jan-2026 docs commits, proven superseded (*branches-7*). This also removes the leftover pre-BFG log files (*secrets-2*). The key they expose is dead as of the 2026-07-08 rotation, but a browsable (even dead) credential at a public branch tip is still a handoff blemish — delete before the cdcai push.

### A3. Redaction commit in `.agent_work`
- `.agent_work/tasks/completed/TASK-025-docker-containerization.md` lines 659, 664, 665, 669, 688, 690, 1064 — replace the recorded local TLS-inspection CA name and thumbprint with `<org-ca-name>` / `<thumbprint>` (*agent-work-1*).
- `.agent_work/tasks/completed/TASK-080-uat-user-guide-process-simplification.md` line 632 — same CA-name redaction.
- `.agent_work/user-testing/instructions/RC1-PILOT-HANDOFF-PACKET.md` — add one line: support ownership transfers to cdcai at handoff (*agent-work-3*).
- Optional cosmetic: strip the 19 `filecite` LLM-citation artifacts from `.agent_work/context/status/TASK-087-PR46-97b2d9a-start-contract-review.md` (*p2-pr46-8*).

### A4. Working-tree and local-ref hygiene
```
# untracked env backup: no secrets today, but one 'git add -A' from committing a real one
del .env.uat-backup-20260615
# add root-level backup pattern to .gitignore (tracked change, part of the pre-tag pass):
#   .env.*
#   !.env.example
```
Local-only refs (superseded by merged PR #33 work; archive first if you want retention — the tag's commit is reachable from nothing else):
```
git bundle create %USERPROFILE%\Documents\towerscout-local-refs-archive.bundle uat-local-fix-2026-06-15 feature/podman-gpu-cdi-enablement
git tag -d uat-local-fix-2026-06-15
git branch -D feature/podman-gpu-cdi-enablement
git branch -D feature/task-083-rc5-podman-independence-gpu-release
git checkout main && git pull --ff-only        # local main is 7 behind origin
```

### A5. One-minute logged-in checks on github.com (owner account)
- Releases page: confirm **no draft releases** exist (invisible to the unauthenticated API; a forgotten draft could hold pre-rotation notes) (*p2-github-3*).
- Repo settings: clear or replace the dead homepage URL `https://groups.ischool.berkeley.edu/TowerScout/` → 404 (*p2-github-2*).

---

## B · Workstream B — Finalize and merge PR #46 (07-08 morning)

PR #46 state (re-confirmed): head `533e18b`, draft, `mergeable_state: clean`, no new commits, all 10 check-runs green. All 10 quality-review findings (F1–F10) verified implemented; 4 of 10 independently re-verified again in pass 2.

### B1. Strip the CI log-publishing residue — *(ci-1/tests-1, HIGH; exact ranges verified at `533e18b`)*
On the PR branch, in `.github/workflows/task-087-frontend-puppeteer.yml`, **delete bottom-up so line numbers stay valid**:
1. Delete lines **192–198** ("Publish e2e logs as repo issue" step + preceding blank line; 198 is the last line of the file).
2. Delete lines **104–110** ("Publish test logs as repo issue" step + preceding blank line).
3. `git rm scripts/ci_publish_issue.py` (exactly two references repo-wide, both just deleted).

After deletion each job validly ends with its "Upload test artifacts" block. The logs are preserved as workflow artifacts — nothing is lost. This tool has already posted 11 bot comments on PR #46 and would spam cdcai after migration.

### B2. Trim the Puppeteer workflow — *(p2-pr46-6; minimum-viable set)*
Same file, same commit:
- Delete line **8** (dead push trigger `feature/task-087-gate3-product-integration` — dead the moment the PR merges).
- Scope `pull_request:` (lines 4–5) from `branches: ['**']` to `branches: [main]` (removes double-runs).
- Change the two "Diagnostics" process-dump steps (lines 80–87, 169–178) from `if: always()` to `if: failure()`.
- Keep `workflow_dispatch` (useful for manual re-validation).
- *If time allows:* collapse to a single job and rename the file/workflow to something durable (`frontend-contract.yml`) — no branch-protection check names are pinned anywhere yet, so renaming is free now and won't be after cdcai adds protections. Full residue inventory with line numbers: *p2-pr46-6*.

### B3. Close the two real coverage gaps found in pass 2 — *(p2-pr46-3, p2-pr46-4, HIGH)*
Small, high-value, and they protect the dark gates:
1. **Bundle-freshness CI step** — the served page loads the *bundle* (`webapp/js/towerscout.js`), but every gate test reads only the *source* copy. Demonstrated: flipping the gate **only in the bundle** leaves all tests green. Add to `ci.yml`'s `frontend-test` job, after "Rebuild frontend bundle":
   ```yaml
   - name: Verify committed bundle matches source
     run: |
       node webapp/build.js
       git diff --exit-code -I "Build Date" webapp/js/towerscout.js
   ```
2. **Pin the gate in the bundle too** — extend `tests/unit/test_frontend_provider_tls.py` to assert the literal `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false` string in `webapp/js/towerscout.js` as well as in `js/src/setup-wizard.js`.
3. **Run the behavioral gate test in CI** — `tests/frontend/test_setup_wizard_validation_contract.js` (the only behavioral test of the mutation gate) currently runs in **no** workflow. Add to `ci.yml` `frontend-test`:
   ```yaml
   - name: Setup wizard validation contract
     run: node tests/frontend/test_setup_wizard_validation_contract.js
   ```
   (Plain Node, no Puppeteer, ~1 s, passes at HEAD.)

### B4. Optional but recommended: remove the dead simulated-helper block — *(p2-pr46-5)*
`webapp/towerscout.py:1902–1987` (`TOWERSCOUT_SIMULATED_HELPER`): default-off, undocumented, set by nothing (CI uses the Node helper on :5001), unreachable through compose's fixed env allowlist — but when enabled it registers two **unauthenticated** endpoints with reflected-Origin CORS. Preferred: delete the block (pure dormant attack surface). If kept: one sentence in the release notes' security section ("never set `TOWERSCOUT_SIMULATED_HELPER` in production"). If you delete it, rerun `pytest tests/unit/` and the frontend contract tests locally first.

### B5. Merge
1. Push the cleanup commits; wait for CI green on the PR head (post-B1 the green is meaningful).
2. Mark PR #46 **ready for review** (undraft), then **squash-merge** into `main` (22 of the 30 commits are CI-debugging iterations; fork-internal squash is fine — the never-squash rule applies only to pushes *into cdcai*).
3. Confirm both workflows green at the merge SHA: `https://api.github.com/repos/J-Schulein/TowerScout/actions/runs?head_sha=<merge-sha>`.

---

## C · Workstream C — Pre-tag source pass (07-08, after the merge, before the tag)

**Everything in this workstream must land before `git tag v0.1.0`** — packaging requires a clean tree at the tag, and seven of these docs ship inside every package ZIP (*p2-runbook-8*).

### C1. Merge upstream cdcai/main — *(migration-1; resolution validated in a dry run, one conflicted file)*
```
git remote add cdcai https://github.com/cdcai/TowerScout.git
git fetch cdcai
git checkout main
git merge cdcai/main        # CONFLICT (content): README.md — expected, 2 hunks
```
Resolution recipe (validated to a clean merge in the dry run, *p2-runbook-1*):
- **Hunk 1** (top of file): keep **both** — first cdcai's line, verbatim: *"TowerScout Enterprise, a new program re-designed from the ground up to make better use of modern architectures and cloud computing resources, is now available: [TowerScout Enterprise](https://github.com/cdcai/TowerScout-Enterprise)"* — then a blank line, then the fork's `## Install The Release Package` heading. Drop cdcai's duplicate `## About TowerScout` heading (the fork already has that section).
- **Hunk 2** (~lines 50–61): take the fork's side (LA County bullet without trailing space); **drop** cdcai's stale `**Additional required files**` block (Google-Drive-era weights links) — the fork's `## Additional files` section supersedes it.
- Commit message: `Merge cdcai/main: graft TowerScout Enterprise announcement`.

### C2. Namespace sequencing and `J-Schulein` → `cdcai` pass — *(docs-1, migration-3, HIGH; full verified file list)*
**Important sequencing correction:** do not make the fork-published stable
`v0.1.0` package point users at a `cdcai` release or GHCR namespace that does
not exist yet. For `TASK-088`, the fork release must remain self-consistent
about its actual download home and image source. Perform the full `cdcai`
release/GHCR rewrite during `TASK-089` when the cdcai release is actually being
rebuilt and published, unless same-day cdcai publication is already guaranteed.

Use this split:
- **Fork-side stable release (`TASK-088`)**: keep package-facing release URLs
  and image defaults self-consistent with the fork release, or make them
  neutral enough that they do not misdirect users.
- **cdcai migration (`TASK-089`)**: apply the `J-Schulein` → `cdcai` release
  URL and GHCR default rewrite in the cdcai rebuild/release pass so the cdcai
  package and docs agree with the real cdcai artifacts.

The verified rewrite inventory remains the same and should be used in the
migration pass:
Release URLs (`https://github.com/J-Schulein/TowerScout/releases` → `https://github.com/cdcai/TowerScout/releases`):
`README.md:22` · `docs/quick-start.md:149` · `docs/quick-start.html:71` · `docs/package-guide.md:142` · `docs/docker-cpu-user-guide.md:64` · `docs/docker-gpu-user-guide.md:73` · `docs/podman-cpu-user-guide.md:86` · `docs/podman-gpu-user-guide.md:108`

GHCR defaults (`ghcr.io/j-schulein/towerscout` → `ghcr.io/cdcai/towerscout`):
`compose.yaml:3` · `scripts/lib/TowerScoutPodmanGpu.ps1:117` · `scripts/package-release.ps1:37` · plus contract docs `docs/support/oci-runtime-contract.md:131,137`, `docs/support/oci-quick-start.md:117–139`, `docs/release/release-asset-bundle-contract.md:44`, `docs/package-guide.md:288`

Test assertions (will fail CI if missed): `tests/unit/test_task_081_runtime_hardening.py:61-65,687-735` **+ 4 other test files** — find them all with `git grep -rn "j-schulein" -- tests/`.

Leave `.agent_work/` hits as-is (historical record). If the fork stable release
is published before the cdcai release exists, do not repoint its package-facing
defaults or download instructions to cdcai prematurely.

### C3. Documentation fixes (same commit or adjacent)
- `docs/package-guide.md:818-820` — remove/replace "the one-click repair helper is not part of the rc7 package baseline" (now contradicted: the helper scripts ship in the package, dark) (*docs-4 verifier note*).
- **New `docs/support/host-helper.md`** (*docs-4*): what the host helper is; that it ships **disabled** with the two gate locations (`webapp/ts_provider_http.py:120`, `webapp/js/src/setup-wizard.js:17` + bundle); the security model (loopback-only, token, allowlisted operations); that enabling requires the remaining Task-087 Gate 3 sign-off + Gate 4 managed-network validation per `.agent_work/tasks/active/TASK-087-…md`.
- Broken cross-refs: `DATA_LICENSES.md` → `docs/release/release-asset-bundle-contract.md` (path moved); `docs/support/oci-runtime-contract.md` → remove the dead `.agent_work/tasks/active/TASK-025/` pointer (*docs-6/-7*).
- `README.md`: add a short **Provenance** paragraph — this repo is a fork of `cdcai/TowerScout` (itself derived from `TowerScout/TowerScout`); the 2026 v0.1.0 packaging/validation work was done on the fork (*docs-2*).
- `.github/copilot-instructions.md`: refresh the "Sprint 06 is active / 2026-05-27" content or delete the file (*docs-3*).
- **New `HANDOFF.md`** at repo root, containing: (a) how to read `.agent_work/` (`current-tasks.md → task-backlog.md → tasks/completed/ → decisions/`); (b) the **CI gates note** — 8 `ci.yml` steps are `continue-on-error` (black, mypy, bandit, integration tests, codecov, Docker build, Trivy, SARIF): green ≠ those passed (*ci-5*); (c) the **automated-vs-manual verification map** (paste from analysis §6.7 `tests-12`: CI covers Python unit + contract shapes; everything Windows/package/GPU/live-provider is human-validated via the RC evidence); (d) asset-bundle custody: the 800 MB bundle is **not rebuildable from the repo** — sole source is the release assets, sha256 `00599cc4…`, weights pinned per-file in `webapp/asset_manifest.v1.json` (*packaging-1*); (e) known-accepted risks: torch 2.2.1 / CVE-2025-32434 with the sha256-pinned-asset mitigation and the note that the YOLO vendor path forces `weights_only=False` so a torch bump alone doesn't harden it (*p2-critic-2*); node:18 build stage EOL — bump to node:22, **not** node:20 (also EOL) (*p2-critic-3*); (f) the "what did not migrate" list (§G Phase 5).
- SBOM decision (*docs-5*): either generate a real SBOM for the stable release (`syft ghcr.io/...@<digest>` or `trivy sbom`, plus `webapp/requirements.txt` + `package-lock.json`) and attach it, or amend `SBOM.txt` + `release-manifest.v1.json`'s `sbom.status` to an honest deferred posture. Do not leave the unmet "must be generated for each release candidate" claim as-is.
- Optional community-health files (*p2-critic-1*): minimal `SECURITY.md` (reporting address decided with cdcai) and `.github/dependabot.yml` (pip + npm + github-actions) — 10-minute adds; Dependabot is what would have auto-surfaced the torch CVE.

### C4. Dead-code deletions — optional, timebox to 1 hour *(analysis §5.2)*
Safe deletions, each verified orphaned: `/debug-azure-maps` route (`webapp/towerscout.py:1826-31` — serves a file that has never existed; keep `webapp/js/azure_maps_debug.js` which is alive); 4 permanently-skipped legacy test modules (74 skips per CI run); `webapp/js/towerscout.original.js` (176 KB, ships in the Docker image); `webapp/static/phase1_validation.js`; `validate_stage_0.sh` + stage-0 test files + `package.json` metadata refresh; `scripts/validate_container_task052_smoke.py`; `tests/integration/test_task_041_stability.js`; templates `incompatible.html`/`unauthorized.html`. If time is short, skip — none blocks the release.

### C5. Fix the stale tag; push everything
```
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0     # removes the 2025-12-04 "15% complete" tag from origin
git push origin main
```

---

## D · Workstream D — Build and validate stable v0.1.0 (07-08 afternoon → 07-09)

### D1. Tag
```
git tag -a v0.1.0 -m "TowerScout v0.1.0" <final-main-sha>
git push origin v0.1.0
```

### D2. Build images (both flavors, in parallel) — *(p2-runbook-2, p2-validation-1)*
Dispatch `container-publish.yml` **from ref `v0.1.0`** via the Actions web UI ("Run workflow": ref `v0.1.0`, `tag=v0.1.0`, `push_latest=false`, `pytorch_flavor=cpu`, then again with `cuda121`), or once `gh auth login` is done:
```
gh workflow run container-publish.yml --repo J-Schulein/TowerScout --ref v0.1.0 -f tag=v0.1.0 -f push_latest=false -f pytorch_flavor=cpu
gh workflow run container-publish.yml --repo J-Schulein/TowerScout --ref v0.1.0 -f tag=v0.1.0 -f push_latest=false -f pytorch_flavor=cuda121
```
Record the two **`pinned=ghcr.io/…@sha256:<digest>`** lines from each run's step summary. A full rebuild is required — rc7.1 images predate the PR #46 code (webapp changes ship in the image).

### D3. Prepare the assets ZIP and build packages — *(p2-runbook-3; sidecar format verified byte-level)*
```powershell
$src='C:\Users\Jonat\Documents\TowerScout\rc7.1-testing\towerscout-v0.1.0-rc7.1-assets-towerscout-v1-assets-2026-05-05.zip'
$dstDir='C:\Users\Jonat\Documents\TowerScout\release-v0.1.0'
$dstName='towerscout-v0.1.0-assets-towerscout-v1-assets-2026-05-05.zip'
New-Item -ItemType Directory -Force $dstDir | Out-Null
Copy-Item -LiteralPath $src -Destination (Join-Path $dstDir $dstName)
$dst=Join-Path $dstDir $dstName
$hash=(Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLowerInvariant()
if($hash -ne '00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb'){throw "hash mismatch: $hash"}
[System.IO.File]::WriteAllText("$dst.sha256", "$hash  $dstName`r`n")
```
(The content hash is rename-invariant; the sidecar format is `<64 lowercase hex><two spaces><filename>` + CRLF — the setup flow enforces the exact filename for the release version.)

From a **clean checkout of tag `v0.1.0`** (fresh clone with `-c core.longpaths=true`, extract nowhere deep):
```
.\scripts\package-release.cmd -Version v0.1.0-cpu     -Image ghcr.io/j-schulein/towerscout:v0.1.0-cpu     -ImageDigest sha256:<cpu-digest>     -PytorchFlavor cpu     -AssetBundleVersion v0.1.0 -AssetBundleSha256 00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb -OutputDir dist
.\scripts\package-release.cmd -Version v0.1.0-cuda121 -Image ghcr.io/j-schulein/towerscout:v0.1.0-cuda121 -ImageDigest sha256:<cuda121-digest> -PytorchFlavor cuda121 -AssetBundleVersion v0.1.0 -AssetBundleSha256 00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb -OutputDir dist
```
Yes, `-Image ghcr.io/j-schulein/…` for the **fork** build even though source defaults now say cdcai: the parameter overrides the default, these images exist and are pullable now, and it keeps the fork release functional with zero owner dependency. The cdcai rebuild (§G Phase 3) passes the cdcai image instead.

Integrity checks: verify each ZIP against its `.sha256`; confirm `scripts\lib\TowerScoutCertificateStore.ps1` is **inside both ZIPs** (new in PR #46; a package missing it hard-fails `import-tls-ca.cmd`).

### D4. Validation protocol — *(p2-validation-1…11; baselines confirmed from artifacts, not memory)*

**Setup:** copy `Validation Evidence/rc7.1-docker-qa-2026-07-07/fixtures-20260707` to a scratch dir; re-verify the 12 SHA256 prefixes against the QA doc (`e3c97267, c7797de0, 10c624a7, 11ff18b7, eba2ba2c, ba356d01, ccfdba81, 94d4cfa5, 20d2ea30, 0921aa8d, 928df690, 6ebf7c0a`). Extract packages to space-free paths; launch `.cmd` wrappers with a clean Windows-PowerShell `PSModulePath` (QA doc finding 2). Cells are **port-5000-sequential** — stop one before starting the other.

**Per cell** (CPU cell: two passes; GPU cell: one pass):
```
pwsh -NoProfile -File ts-detect-harness.ps1 -Cell stable-cpu       -OutDir out-stable-cpu       -FixtureDir <fixtures-copy>
pwsh -NoProfile -File ts-detect-harness.ps1 -Cell stable-cpu-pass2 -OutDir out-stable-cpu-pass2 -FixtureDir <fixtures-copy>
pwsh -NoProfile -File ts-detect-harness.ps1 -Cell stable-gpu       -OutDir out-stable-gpu       -FixtureDir <fixtures-copy>
```
Compare against the rc7.1 baselines (`out-docker-cpu`, `out-docker-cpu-pass2`, `out-docker-gpu`):
```powershell
$b=(gc baseline\summary.json|ConvertFrom-Json).fixtures
$n=(gc new\summary.json|ConvertFrom-Json).fixtures
$b.PSObject.Properties.Name|%{ if($b.$_ -ne $n.$_){"MISMATCH $_ $($b.$_) -> $($n.$_)"} }
```

**PASS requires all of:**
1. **Readiness per cell**: `state=ready`, `app v0.1.0`, `image_digest` = the NEW pinned digest; CPU cell `selected_device=cpu`, torch `2.2.1+cpu`; GPU cell `selected_device=cuda`, torch `2.2.1+cu121`, `cuda_device_name=NVIDIA T1000 8GB`.
2. **Fixture parity (the gate)**: per-tile counts equal baseline on **every** tile — `tile_000..011 = 0,0,13,8,0,4,6,11,2,4,5,0`, totals **53** per cell; `stable-cpu` pass1 == pass2 (12/12); `stable-cpu` == `stable-gpu` (12/12). Any per-tile mismatch = hard FAIL (runtime drift in rebuilt images).
3. **Live smoke**: google AND azure return success with ≥1 detection per cell; counts recorded but **not compared** (documented same-day provider bimodality: azure 69 vs 34; rc7.1's CPU live baseline came from pass2 — pass1 live had a since-fixed harness bug).

**Setup-Wizard manual smoke S1–S7** (CPU cell; ~40 min; genuinely new coverage — rc7.1 QA seeded keys via API, never the wizard UI):
- **S1** (10m) wizard happy path: fresh setup, enter both keys in the UI, validate green, pick default provider, save, app reaches ready; **repair panel never visible**; no JS console errors.
- **S2** (5m, F4) plausible-but-bogus Google key → clean `valid=false` naming the category; progression blocked; no repair panel.
- **S3** (5m, F7) `POST /api/config/save-keys` with ONLY `google_api_key`, no `default_map_provider` → 200 with `default_map_provider=google`, `default_map_provider_derived=true`.
- **S4** (5m, F5) `POST /api/geocode/forward` → `results[0]` contains `warning_message/warning_category/warning_provider` keys (null on healthy TLS — presence proves the new schema shipped). *(Note: the reverse route drops these fields — forward only; p2-validation-6.)*
- **S5** (5m, F8) repair panel stayed `display:none` through S1/S2; no repair-command text on non-TLS failures.
- **S6** (5m) settings page: change default provider + re-save keys (settings.js changed in PR #46).
- **S7** (2m) from the extracted package: `scripts\lib\TowerScoutCertificateStore.ps1` exists and dot-sources cleanly in WinPS.

**Rate-limit rules** (the shared per-IP limiter is still present at HEAD; a 429-poisoned pass mimics a parity failure): don't touch the UI or issue API calls during a harness pass; keep S3/S4 ≥60 s clear of harness start; if any `fixture_tile_*.json` shows a 429, discard and re-run that pass after 60 s.

**Non-goals** (declare, don't do): no Podman revalidation — the 35-file PR #46 diff touches zero Podman/compose/setup paths (verified; optional 20-min podman-cpu setup-only smoke if time allows); no fixture recapture; no forced live TLS-failure simulation (CI-covered); no perf testing; no upstream validation (that's §G).

**Time budget:** ~3.5–5 h wall clock post-merge (images 20–45 min parallel; packages 10 min; CPU cell setup 15–25 min incl. 800 MB import; harness runs 3–6 min each; smoke 40 min; GPU cell 25–45 min; comparison + write-up 30 min). Record evidence in a new `Validation Evidence/stable-v0.1.0-qa-<date>/` folder mirroring the rc7.1 layout.

### D5. Abort criteria and fallback — *(p2-validation-9)*
- **G1 merge**: CI red at merge SHA → fix forward, don't tag.
- **G2 package**: sidecar mismatch / `TowerScoutCertificateStore.ps1` missing from a ZIP → rebuild packages (cheap; not a fallback trigger).
- **G3 readiness**: any cell fails ready/flavor/device → timebox investigation to half a day.
- **G4 fixture parity**: any mismatch → hard abort of the candidate.
- **G5 smoke**: S1/S2 blockers → hard abort; S3–S6 wrong-but-safe anomalies → document as known issues and proceed.
- **Timing rule:** fix-forward is allowed until **07-10 EOD**. After that, until the 07-13 hard stop, the only path is **rc7.1 promotion**: re-tag the existing rc7.1 ZIPs + digests as the stable release, attach the existing 2026-07-07 validation evidence, and document the absent PR-46 fixes as Known Issues — **lead with the F4 key-validation gap**. (Fallback feasibility verified: all rc7.1 artifacts + sidecars present and re-hashed locally; CI residue lives in the repo, not in the rc7.1 packages.)

If this fallback is taken, the release notes and user guidance must state
explicitly that the shipped fallback artifacts remain the validated `rc7.1`
artifact set adopted as the stable fallback baseline. Do not imply that a fresh
`v0.1.0` rebuild/package set exists if the fallback path was a direct `rc7.1`
promotion.

---

## E · Workstream E — Publish the fork release (07-09 → 07-10)

Release notes must include: what's new vs rc7.1 (F4/F5/F7 fixes, cert-store refactor, dark host-helper scaffolding); **the manual TLS repair procedure** (or a pointer to the packaged docs — the 4-command sequence); a note that the guided-repair control plane ships disabled and what enabling would require (link `docs/support/host-helper.md`); the security posture paragraph (torch CVE documented + mitigations, SBOM status per C3); image digests for both flavors; the asset table with sha256s; supported engines matrix.

```
gh release create v0.1.0 --repo J-Schulein/TowerScout --title "TowerScout v0.1.0" ^
  --notes-file release-notes-v0.1.0.md --latest --verify-tag ^
  dist\towerscout-v0.1.0-cpu.zip dist\towerscout-v0.1.0-cpu.zip.sha256 ^
  dist\towerscout-v0.1.0-cuda121.zip dist\towerscout-v0.1.0-cuda121.zip.sha256 ^
  release-v0.1.0\towerscout-v0.1.0-assets-towerscout-v1-assets-2026-05-05.zip ^
  release-v0.1.0\towerscout-v0.1.0-assets-towerscout-v1-assets-2026-05-05.zip.sha256
```
`--verify-tag` fails fast if the tag wasn't pushed (without it, gh silently creates the tag at the default-branch tip — a footgun). `prerelease` stays **off**: this is the first non-prerelease, and `--latest` makes it the badge release. The 800 MB upload takes ~2 min at 50 Mbps / ~11 min at 10 Mbps; if one asset fails mid-transfer: `gh release upload v0.1.0 <file> --repo J-Schulein/TowerScout --clobber`.

---

## F · Workstream F — User Guidance finalization (07-09 → 07-10; all edits slide-verified)

The near-final deck (`Setup Guide_Updated_2026.07.07.pptx`, 21 slides) is structurally sound: `<release-version>` placeholders throughout, no fork/ghcr URLs in text, TLS commands match shipped script parameters exactly, engine coverage complete. Required edits (*p2-guides-1…9*):

| # | Where | Edit |
|---|---|---|
| F1 | Deck slide 16 (Step 6) | **HIGH — regression:** re-insert the missing readiness command after "run:" — `.\scripts\status.cmd -Engine docker` + Podman note + "Expected result: readiness reports ready" (copy from Slides-1-18 twin, slide 14). |
| F2 | Deck slides 10, 14, 18 | Fix stale cross-refs after the +2 slide shift: slide 10 "see Slide 6"→"Slide 8"; slide 14 "see Slide 15"→"Slide 17"; slide 18 "from Slide 15"→"from Slide 17". Better: switch to section references. |
| F3 | Deck slide 18 + Slides-1-18 HTML (lines ~883, 993) + Setup-Guide.docx | `logs.ps1` has **no `-Port` parameter** — change "include the same -Port 5009 on all later status, logs, and import commands" to "…on all later **status and import** commands (the logs command does not take -Port)". |
| F4 | Deck slide 18 TLS row | Re-append the dropped clause: "Use `-Provider azure` for Azure keys; keep the same `-Engine` and `-Gpu` values you used at setup (e.g. `-Engine podman`)." Without it, Azure/Podman users copying verbatim repair the wrong provider/engine. |
| F5 | Deck slide 13 screenshot | The File-Explorer screenshot shows rc7.1 filenames (text uses placeholders; the leak is image-only). Retake with v0.1.0 files after D3, or caption "example shows an earlier release". |
| F6 | RC6 User Testing Guide (docx) | Global v0.1.0-rc6→v0.1.0 + retitle; fix "RC1" audience typo (body **and** docx core-properties title); fix the `>-assets` / doubled-hyphen filename mangling in the Step-2 table; replace the pre-Task-086 TLS appendix with the repair-provider-tls dry-run/-Apply/stop/start sequence (keep import-tls-ca as thumbprint fallback); plan the releases-hyperlink flip to cdcai. Or formally retire the doc if user testing is over. |
| F7 | Deck slides 5/8/10 + HTML + docx | "GitHub Change Release (GHCR)" is a misexpansion — rename the checklist item "GitHub Release page access" (GHCR = GitHub **Container Registry**; keep the acronym only in the network-requirements bullet where it's correct). Re-verify the "8 Assets" count against the actual v0.1.0 release before publishing. |
| F8 | Deck slides 2/3, 4, 9, 14, 21 | Placeholders: delete or fill slide 4 ("xx TowerScout Setup guide xx") and 21 ("xxxx"); keep one ToC (slide 2, delete 3); resolve the video/GIF placeholder stubs on 9 and 14. |
| F9 | Folder hygiene | Move `TowerScout Setup Guide.pptx/.pdf` and `Setup Guide_Updated.pptx` (superseded 17-slide drafts with empty sections) to an `archive/` subfolder; update the two "rc7.1 package documentation" attribution notes in the Slides-1-18 HTML (lines 290, 1010) to "v0.1.0" after the cut. |

---

## G · Workstream G — Migration to cdcai (07-10 → 07-13; commands dry-run-validated)

### Phase 0 — already done by workstreams A–E
Fork main = merged PR #46 + cdcai merge + namespace/docs pass; v0.1.0 tagged and released on the fork.

### Phase 1 — owner access *(CE; requested 07-08 per §1)*
If write access is refused: open PR `J-Schulein:main → cdcai:main` with written instruction to use **"Create a merge commit"** (never squash — see §2), then the owner pushes tags themselves or accepts a follow-up tags-only push.

### Phase 2 — push history *(JS or CE)*
```
git ls-remote cdcai        # sanity-check auth first
git push cdcai main        # guaranteed fast-forward after C1 (verified); ~30 MiB
git push cdcai tag v0.1.0
git push cdcai tag v0.1.0-rc7.1
# optional history: git push cdcai tag v0.1.0-rc1 … tag v0.1.0-rc7   (never --tags)
```
Leave behind: `tls-validation-*` ×3, `gpu-validation-2026-06-16`, `v0.1.0-rc5-candidate.3` (all point at commits off main), and anything local-only.

### Phase 3 — images and release in cdcai *(JS + CE)*
**Critical (dry-run proven, *p2-runbook-4*):** `docker pull → tag → push` does **NOT** preserve the pinned digest — the published images are OCI image indexes with buildx provenance attestations; a docker re-push mints a different digest and the digest baked into the packages would 404 under `ghcr.io/cdcai`. Two working options:

**Option 1 (preferred — preserves the validated digests, packages stay valid):**
```
curl -L -o regctl.exe https://github.com/regclient/regclient/releases/latest/download/regctl-windows-amd64.exe
.\regctl.exe registry login ghcr.io -u <cdcai-package-writer>     # PAT with write:packages
.\regctl.exe image copy ghcr.io/j-schulein/towerscout@sha256:<v0.1.0-cpu-digest>     ghcr.io/cdcai/towerscout:v0.1.0-cpu
.\regctl.exe image copy ghcr.io/j-schulein/towerscout@sha256:<v0.1.0-cuda121-digest> ghcr.io/cdcai/towerscout:v0.1.0-cuda121
```
Then rebuild the two packages from a fresh cdcai clone of tag `v0.1.0` with `-Image ghcr.io/cdcai/towerscout:v0.1.0-<flavor>` and the **same** digests — only the image *name* changes; validation evidence remains valid because the bytes are identical.

**Option 2 (no regctl):** dispatch `container-publish.yml` inside cdcai (it derives the image name from the owning repo automatically) — but this **rebuilds** (new digests), so repackage with the new digests and run at least readiness + one fixture pass to re-anchor the evidence.

Either way: **[CE]** flips `ghcr.io/cdcai/towerscout` visibility to **Public** and links it to the repo (first publish is private by default — user setup pulls fail until flipped).

Publish the cdcai release from the rebuilt artifacts:
```
gh release create v0.1.0 --repo cdcai/TowerScout --title "TowerScout v0.1.0" --notes-file release-notes-v0.1.0.md --latest --verify-tag <6 assets as in §E>
```

### Phase 4 — verification *(JS)*
- Fresh clone: `git clone -c core.longpaths=true https://github.com/cdcai/TowerScout ts-cdcai` — the `core.longpaths` flag is required (default clone fails checkout at Documents-depth paths; also put this in the cdcai README/handoff notes for future consumers).
- `git describe --tags` = `v0.1.0`; `git cat-file -t <source_ref SHA from a shipped SOURCE.txt>` succeeds (AGPL corresponding-source intact).
- Unzip cdcai-built vs fork-built package; hash-compare file-by-file — expect diffs **only** in `release-manifest.v1.json` / `IMAGE.txt` / `SOURCE.txt` / `SHA256SUMS.txt` lines carrying image ref + timestamps (byte-identical ZIPs are impossible; the manifest embeds a generation timestamp).
- Anonymous `docker pull ghcr.io/cdcai/towerscout@<digest>` from a logged-out session.
- Download cdcai release assets, verify sidecars; one `setup-towerscout.cmd` Docker-CPU smoke from the cdcai package on a clean, space-free path.

### Phase 5 — close out *(JS + CE)*
- Fork README banner: "Development has moved to cdcai/TowerScout"; clear/repoint the fork's dead homepage field too.
- **Keep the fork alive** (do not delete) at least until Phase 4 passes — it holds the PR/Actions history and the rc-release archive, and the AGPL SOURCE.txt SHAs of already-shipped rc packages.
- Owner optionally enables branch protection on cdcai main.
- **Disclose at handoff:** a rotated Azure Maps key (rotated 2026-07-08) exists in deep git history (rewrite impractical — it would invalidate every tag/release; the rotation neutralizes it). Also hand over: known-accepted risks list (HANDOFF.md §C3(e)), and the "what did not migrate" list — Actions run history, PR history #1–#46 (commit `(#NN)` links will mislink in cdcai; cosmetic), fork releases (rc archive stays on the fork), branch protections (none existed), collaborators, secrets (none custom).

---

## H · Workstream H — Backlog export & knowledge transfer (07-11 → 07-13, after Issues enabled or alternate destination approved)

File as GitHub Issues **on cdcai** (not the fork — fork issues would not migrate), each linking back to its `.agent_work/task-backlog.md` entry:

1–11. The ordered backlog: TASK-076 (provider API key restriction policy — release-policy item), TASK-068 (Windows test portability), TASK-077 (release manifest/asset-import hardening), TASK-070 (restricted-network packages), TASK-078 (Apache-only runtime migration off AGPL YOLO — release-policy item), TASK-058 (background detection jobs), TASK-059 (backend decomposition), TASK-027 (error handling), TASK-026 (CPU optimization), TASK-029 (multi-provider fallback), TASK-060 (frontend build modernization).
12–17. Parking lot: TASK-028 (mobile), TASK-061 (NumPy 2), Sprint-04 quick wins, advanced filtering, performance dashboard, user preferences.
18. **New:** torch/torchvision ≥ 2.6.0 upgrade (CVE-2025-32434; requires model-parity re-validation; note the YOLO vendor path needs an ultralytics/vendor change too since `torch_load` forces `weights_only=False`; consider `TOWERSCOUT_VERIFY_ASSET_HASHES=1` default as cheap defense-in-depth).
19. **New:** Dockerfile base refresh — node:18 → **node:22** (not 20; also EOL) + digest-pin both FROM lines.
20. **New:** Task-087 completion (Gate 3 enablement + Gate 4 managed-network validation) — link `docs/support/host-helper.md` and the task file.
21. **New:** e2e helper-unavailable coverage (quality-review note 5) + promote the Puppeteer contract job per *p2-pr46-6* if not done in B2.

If cdcai Issues are still disabled at execution time, use an explicitly approved
alternate durable destination instead of waiting indefinitely. Minimum fallback:
commit a repo-tracked backlog handoff appendix under `HANDOFF.md` or a dedicated
backlog-transfer markdown file and hand that to the cdcai owner as the pending
issue-creation source.

---

## Day-by-day schedule

| Date | Work | Output |
|---|---|---|
| **07-08 AM** | §1 owner asks sent · ~~A1 key rotation~~ ✅ done · A2 branch deletions · `gh auth login` · B1–B4 PR cleanup commits | PR #46 final, CI green |
| **07-08 PM** | B5 merge · C1 upstream merge · C2–C3 namespace/docs pass · A3 redactions · A4/A5 hygiene · C5 stale tag + push · D1 tag · D2 dispatch builds | `v0.1.0` tagged; images building |
| **07-09 AM** | D3 packages · D4 CPU cell validation (harness ×2 + S1–S7) | CPU cell PASS/FAIL |
| **07-09 PM** | D4 GPU cell · evidence write-up · **G4/G5 gate decision** (fallback call by EOD) · F guide edits | Validation verdict; guides final |
| **07-10** | E fork release published · migration plan doc delivered (this doc + analysis) · F9 archive pass | **Deliverables met** |
| **07-11 → 07-13** | G Phases 1–4 (owner-gated) · H backlog export · Phase 5 closeout | cdcai owns repo + release |
| **07-14 → 07-15** | Buffer; final handoff conversation walking the owner through HANDOFF.md | Project close |

If validation fails past 07-10 EOD → execute the D5 fallback (rc7.1 promotion) and continue the migration schedule unchanged; the migration mechanics are identical either way.

---

## Definition of done

- [x] Azure Maps key rotated (2026-07-08)
- [ ] `improvements` + `feature/geocoding-system-integration` deleted from origin; local `.env` updated with the new key
- [ ] PR #46 merged with CI residue stripped and the three B3 coverage guards added; CI green at merge SHA
- [ ] cdcai/main merged (Enterprise links preserved); namespace pass + docs pass + redactions landed **before** the tag
- [ ] Stale `v0.1.0` tag deleted; new `v0.1.0` tagged and pushed; no `--tags` push ever ran
- [ ] Both packages built from the tag, digest-pinned, `TowerScoutCertificateStore.ps1` present inside both ZIPs
- [ ] Validation: readiness criteria met on both cells; 12/12 fixture parity at 53 detections ×3 runs; S1–S7 pass; evidence folder written
- [ ] Fork release `v0.1.0` published, non-prerelease, marked Latest, 6 assets with valid sidecars
- [ ] Guides: F1–F9 edits applied; superseded drafts archived
- [ ] cdcai: main + selective tags pushed (fast-forward, no force); images available under `ghcr.io/cdcai` (digest-preserved or repackaged); release recreated; package visibility Public; Phase-4 verification checklist all green
- [ ] HANDOFF.md in repo; backlog exported to cdcai Issues; disclosure conversation held; fork banner up, fork retained

*Questions or contradictions: check the finding ID in the companion analysis first; if the code disagrees with this document, stop and report rather than improvising.*
