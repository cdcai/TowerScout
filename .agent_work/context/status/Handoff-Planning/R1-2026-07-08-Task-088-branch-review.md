# TowerScout External Review — R1

| | |
|---|---|
| **Review round** | R1 (first of a recurring series; findings are numbered `R1-nn` and future rounds will continue as `R2-nn`, …) |
| **Date** | 2026-07-08 |
| **Reviewed state** | `main` @ `d148727` (PR #46 squash merge); branch `docs/task-088-stable-handoff` @ `b5fc8da`; upstream `cdcai/main` @ `3e2c65d`; live GitHub state (branches, tags, Actions runs, repo metadata) |
| **Scope** | Quality check of all changes since `main` @ `229f59f` against the two canonical planning docs, plus a close review of the TASK-088 and TASK-089 plans themselves |
| **Method** | Commit-by-commit diff review; independent verification of every "done" claim in the TASK-088 log against the actual tree (not the log); GitHub API checks; local execution of the new frontend CI gates at the branch head |
| **Canonical docs** | `.agent_work/context/status/Handoff-Planning/TowerScout-Implementation-Strategy.md` (workstream IDs A–H referenced below) and `…/TowerScout-Handoff-Review-Comprehensive-Analysis.md` (finding IDs) |

**How to use this document:** each finding has a Status line. When you address one, flip its Status to `RESOLVED` (or `ACCEPTED` with a one-line rationale) and add a line of evidence (command output, commit SHA). The next review round will re-verify from this table.

---

## 1 · Verdict

The work reviewed is high quality and faithful to the plan. PR #46 cleanup and merge (Workstream B) is done correctly and completely except for B2; the pre-tag source pass (Workstream C) is largely done, with the C2 namespace deferral recorded as an explicit, defensible decision; the TASK-088 execution log is exemplary — every decision has context, rationale, and validation evidence.

**However, the tag is not safe to cut yet.** One sequencing hazard (R1-01) would silently break the cdcai migration if handled with the repo's habitual squash-merge, one deferred decision (R1-04) becomes irreversible the moment the tag exists, and the security-hygiene items A2/A3 (R1-02, R1-03) remain fully open — with the newly committed planning documents making A3 slightly larger than it was.

Nothing found requires re-doing completed work. All findings are additive fixes, decisions to record, or sequencing constraints.

---

## 2 · Verified done — no rework needed

Each item below was checked in the tree / live GitHub state, not taken from the log.

| Plan item | Verification |
|---|---|
| **B1** CI log-publishing residue | Both "Publish … logs as repo issue" steps gone from `task-087-frontend-puppeteer.yml`; `scripts/ci_publish_issue.py` deleted; `git grep ci_publish_issue` matches only historical docs |
| **B3** all three coverage guards | Bundle-freshness step at `ci.yml:36-39`; setup-wizard contract step at `ci.yml:41-42`; bundle-side dark-gate assertion at `tests/unit/test_frontend_provider_tls.py:35-36` |
| **B3 guards pass at branch head** | Reviewer ran all three locally at `b5fc8da`: setup-wizard contract PASSED; `node webapp/build.js && git diff --exit-code -I "Build Date"` clean (bundle fresh); ProviderStateManager regression PASSED. The merge to `main` will not trip the new gates |
| **B4** simulated helper removed | No `TOWERSCOUT_SIMULATED_HELPER` anywhere under `webapp/`; the Node CI helper (`tests/helpers/simulated_helper.js`) correctly retained |
| **B5** merge + CI green | PR #46 squash-merged as `d148727`; both workflows `conclusion: success` at that SHA (Actions API) |
| **Dark gates still off** | `webapp/ts_provider_http.py:120-121` returns `False`; `PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false` at `webapp/js/src/setup-wizard.js:17` and bundle `webapp/js/towerscout.js:7852` |
| **C1** upstream merge | `d40816e` is a true merge with second parent `3e2c65d` = current cdcai/main tip; README resolution matches the reviewed recipe exactly (Enterprise line verbatim, single About section, LA County bullet kept, stale weights block dropped) |
| **C3** docs pass | `HANDOFF.md` covers all six specified sections (a–f); `docs/support/host-helper.md` accurate (gate locations, security model, enabling gates); README Provenance added; `DATA_LICENSES.md` and `docs/support/oci-runtime-contract.md` cross-refs fixed and targets exist; `.github/copilot-instructions.md` genuinely refreshed to Sprint 07 state; settings-linked docs (quick-start / user-guide / project-overview, .md+.html) correctly moved from RC wording to stable-closeout wording while preserving the route-tested compatibility stubs |
| **C3 SBOM posture** | `SBOM.txt`, `release-manifest.v1.json` `sbom.status`, and the generated-SBOM text in `scripts/package-release.ps1` all moved to the honest deferred posture; the script diff is message-strings only (no behavior change) |
| **C5** stale tag | `v0.1.0` gone from origin tags; no `--tags` push occurred (origin tag set otherwise unchanged) |
| **C4** dead-code deferral | Explicitly dispositioned in the TASK-088 log rather than silently skipped — correct handling of an optional item |
| **Task split quality** | TASK-088 as active fork-side execution tracker + TASK-089 as blocked, owner-gated migration wrapper that defers to the runbook instead of re-interpreting it is the right structure; EARS requirements capture the no-force/no-squash/no-`--tags` guardrails |
| **Packaging mechanics** | `-Version v0.1.0-cpu` auto-derives asset-bundle version `v0.1.0` (suffix strip, `package-release.ps1:148-166`), so the expected assets filename is exactly `towerscout-v0.1.0-assets-towerscout-v1-assets-2026-05-05.zip` — consistent with the planned rename. Readiness `version.app` comes from the `TOWERSCOUT_RELEASE_VERSION` build arg (Dockerfile:17,27), so images built from ref `v0.1.0` with `tag=v0.1.0` will satisfy the D4 `app v0.1.0` gate |

---

## 3 · Findings

### R1-01 · BLOCKER (sequencing) — Tag must be cut from post-merge `main`, and the branch must NOT be squash-merged

**Status:** OPEN

**What:** All pre-tag work (C1 upstream merge, HANDOFF.md, host-helper.md, SBOM posture, doc fixes) exists only on `docs/task-088-stable-handoff`. `main` is still at `d148727`. Two failure modes for the stated next step ("create and push the fresh v0.1.0 tag"):

1. Tagging current `main` ships none of the branch work inside the tag — violating the plan's rule that the entire pre-tag pass lands before `git tag v0.1.0` (the packaged ZIPs embed seven of these docs).
2. **Squash-merging the branch into `main` breaks the migration.** The branch contains the true merge of `cdcai/main` (`d40816e`, parents incl. `3e2c65d`). A squash produces a new single commit and cdcai's commits (`f828b34`, `3e2c65d`) never become ancestors of fork `main` — so the Phase-2 `git push cdcai main` stops being a fast-forward and will be rejected, forcing a second upstream merge *after* the tag already exists. PR #46 was (correctly) squash-merged, so squash is the repo's recent habit — this branch is the exception.

**Also:** the branch has had **zero CI runs** (no PR exists, and both workflows trigger only on `push: main` / `pull_request: main`). The merge push will be the first time CI exercises these commits. The local reviewer runs above de-risk the frontend gates, but the Python suite has only been run on the branch locally.

**Action (exact sequence):**
```
git checkout main && git pull --ff-only
git merge --no-ff docs/task-088-stable-handoff     # or plain `git merge` — it fast-forwards if main hasn't moved; either preserves d40816e
git push origin main
# wait for BOTH workflows green at the new main SHA:
#   https://api.github.com/repos/J-Schulein/TowerScout/actions/runs?head_sha=<sha>
# only then:
git tag -a v0.1.0 -m "TowerScout v0.1.0" <that-sha>
git push origin v0.1.0                              # by name — never `git push --tags`
```
If you prefer a PR for the merge, set the merge method to **"Create a merge commit"** for this one PR (not squash, not rebase).

**Verify:** after merging, `git merge-base --is-ancestor 3e2c65d main` must succeed. That single check proves the cdcai fast-forward property survived.

---

### R1-02 · HIGH (security hygiene / disclosure decision) — A3 redactions not done, and the committed planning docs enlarged the exposure surface

**Status:** RESOLVED — tip-level `.agent_work` redaction pass applied on `docs/task-088-stable-handoff`; support-handoff note added to the pilot packet

**Evidence:** Verified current branch text no longer carries the raw CA name or full thumbprint in the targeted `.agent_work` task/pilot files. The pilot packet now includes the cdcai support-handoff note.

**What:** Strategy item A3 (redact the org CA name and thumbprint from `.agent_work`) has not been executed. Additionally, commit `5625577` committed the two Handoff-Planning documents into the repo at `.agent_work/context/status/Handoff-Planning/`. Because the fork is public, the following are now publicly browsable in **four** tracked files (and will be republished to cdcai with the migration push):

- recorded local TLS-inspection CA name and/or full thumbprint:
  - `.agent_work/tasks/completed/TASK-025-docker-containerization.md` (CA name lines 659, 664, 665, 669, 688; thumbprint lines 665, 688, 690, 1064)
  - `.agent_work/tasks/completed/TASK-080-uat-user-guide-process-simplification.md` (line 632)
  - `.agent_work/context/status/Handoff-Planning/TowerScout-Handoff-Review-Comprehensive-Analysis.md` (5 matching lines)
  - `.agent_work/context/status/Handoff-Planning/TowerScout-Implementation-Strategy.md` (1 matching line — the A3 instruction itself)
- The analysis document also contained a step-by-step key re-derivation recipe tied to the historical Azure Maps exposure. The key was rotated on 2026-07-08 and is dead, so this is not a live-credential issue — but it still amplified historical credential and internal TLS-inspection infrastructure detail.

To be clear about severity: the reviewer's scan found **no live secrets** in any committed document (the key appears as the `7G19…` prefix only, per the documents' own redaction rule). This finding is about hygiene and about making the publication of the internal security review a *deliberate* decision rather than a side effect.

**Action (choose one, record it in the TASK-088 log either way):**

1. **Redact (recommended):** replace the recorded local TLS-inspection CA name with `<org-ca-name>` and the full thumbprint with `<thumbprint>` in all four files above; trim or generalize the key re-derivation recipe in the committed analysis doc (the finding text works without the exact extraction command); land it on the branch before the R1-01 merge.
   Note: tip-level redaction is the agreed scope — these strings already exist in public git history and history rewrite was ruled out; redaction still has value because branch tips are what people browse and what the cdcai push showcases.
2. **Accept:** record in TASK-088 that the CA identifiers and the security-review documents are knowingly published, with rationale (key rotated; CA name/thumbprint identify but do not compromise the TLS-inspection root). If accepted, add it to the §G Phase 5 disclosure list so cdcai hears it from us first.

**Also in A3, still pending (small):**
- `.agent_work/user-testing/instructions/RC1-PILOT-HANDOFF-PACKET.md` — add the one line noting support ownership transfers to cdcai at handoff (verified absent).
- Optional cosmetic: 19 `filecite` LLM artifacts remain in `.agent_work/context/status/TASK-087-PR46-97b2d9a-start-contract-review.md`.

---

### R1-03 · HIGH (security hygiene) — A2 key-bearing branches still live on origin

**Status:** RESOLVED — `improvements` and `feature/geocoding-system-integration` deleted from origin on 2026-07-08

**Evidence:** `git push origin :improvements :feature/geocoding-system-integration` succeeded; `git ls-remote --heads origin improvements feature/geocoding-system-integration` now returns no matches.

**What:** `improvements` and `feature/geocoding-system-integration` still exist on the fork (verified via `ls-remote` during this review). Their tips publicly expose the (now dead) Azure key and the pre-BFG log files. Their only unique content is three stale Dec-2025/Jan-2026 docs commits, proven superseded (*branches-7*).

**Action:**
```
git push origin :improvements :feature/geocoding-system-integration
```
Do this before the cdcai push at the latest; before the v0.1.0 tag is cleaner. Record in the TASK-088 log.

---

### R1-04 · HIGH (plan gap) — The deferred namespace flip is owned by neither task, and the tag freezes its consequences

**Status:** RESOLVED — Task-089 now owns the namespace carry-forward decision and disclosure requirement for later cdcai rebuilds

**Evidence:** `TASK-089` now includes a namespace carry-forward requirement, acceptance criterion, and implementation-log entry covering fork-facing package URLs and image defaults in later cdcai rebuilds.

**What:** TASK-088 recorded a deliberate reversal of strategy item C2: keep all release URLs and image defaults on `J-Schulein` for the fork's v0.1.0 cut, and "defer the cdcai rewrite to TASK-089." The review confirms this was applied consistently (all ~20 namespace references untouched) and accepts the rationale — pointing users at cdcai surfaces that don't exist yet would be worse, and migration is still owner-gated.

But two consequences are currently unowned:

1. **TASK-089's file never mentions the namespace rewrite.** No requirement, acceptance criterion, or plan step covers repointing release URLs (`README.md:24`, `docs/quick-start.md:149`, `docs/package-guide.md:142`, the four runtime user guides, `docs/quick-start.html:71`) and image defaults (`compose.yaml:3`, `scripts/package-release.ps1:37`, `scripts/lib/TowerScoutPodmanGpu.ps1:117`, contract docs, and the test assertions that pin them — find all with `git grep -in "j-schulein"`). TASK-088 says TASK-089 will do it; TASK-089 doesn't know. The work item has fallen between the two task files.
2. **The `v0.1.0` tag tree will permanently carry fork URLs.** The migration runbook (§G Phase 3) rebuilds the cdcai packages "from a fresh cdcai clone of tag `v0.1.0`" — those ZIPs would ship seven docs telling cdcai users to download releases from the fork's Releases page. This cannot be fixed after the tag without changing what `v0.1.0` means.

**Action:** before tagging, record the chosen resolution in TASK-089 (and cross-reference from TASK-088):

- **Option A (least machinery):** accept fork URLs inside the cdcai-rebuilt v0.1.0 packages; rely on the fork surviving with a "development has moved to cdcai/TowerScout" banner (§G Phase 5 already requires keeping the fork alive), and state the caveat in the cdcai release notes. Cheap, honest, slightly untidy.
- **Option B:** land the namespace-flip commit on `main` immediately after the fork release is published (still pre-migration), and have TASK-089 rebuild the cdcai packages from that post-flip commit instead of the tag — the package's `SOURCE.txt` records a commit SHA, so AGPL traceability is preserved; the digest-pinned image is unchanged.
- **Option C:** plan a `v0.1.0.1`/`v0.1.1` docs-only point release cut on cdcai after the flip. Cleanest end state, most process.

Whichever is chosen: add it as an explicit TASK-089 acceptance criterion (e.g., "package-facing release URLs and image defaults repointed to cdcai, or fork-URL carriage in v0.1.0 packages explicitly accepted in release notes").

---

### R1-05 · MEDIUM (shipped-doc defect) — Broken link and stale "rc7" wording in `docs/package-guide.md`, which ships in both package ZIPs

**Status:** RESOLVED — package guide wording/link corrected and `docs/support/host-helper.md` added to `$releaseFiles`

**Evidence:** `docs/package-guide.md` now says "current provider TLS repair path" and links to `support/host-helper.md`; `scripts/package-release.ps1` now stages `docs\support\host-helper.md`; `./.venv/Scripts/python -m pytest tests/unit/test_release_package_script.py -q` passed.

**What:** The C3 fix that replaced the stale "helper is not part of the rc7 package baseline" note introduced two defects at `docs/package-guide.md:819-822`:

1. The link `[docs/support/host-helper.md](../support/host-helper.md)` is wrong relative to the file's own location: from `docs/package-guide.md`, `../support/…` resolves to a nonexistent repo-root `support/` directory. Broken on GitHub rendering **and** inside the extracted package. Correct relative target: `support/host-helper.md`.
2. Even with the path fixed, `docs/support/host-helper.md` is **not** in `$releaseFiles` (`scripts/package-release.ps1:229-…`), so inside the shipped package the link has no target at all.
3. The replacement sentence still reads "The **rc7** provider TLS repair path…" — stale for a stable v0.1.0 package.

**Action (pick one for the link):**
- Add `"docs\support\host-helper.md"` to `$releaseFiles` and fix the href to `support/host-helper.md` (nested copy works — `scripts\lib\…` files already package correctly), **or**
- Keep the doc unpackaged and make the reference non-relative (plain text "see `docs/support/host-helper.md` in the repository", or the GitHub URL).

Reword "rc7" to "current release" / "v0.1.0". Then re-run `./.venv/Scripts/python -m pytest tests/unit/test_release_package_script.py -q` if `$releaseFiles` changed.

---

### R1-06 · MEDIUM (process) — B2 workflow trim neither done nor dispositioned

**Status:** RESOLVED — workflow trimmed on branch; dead push trigger removed, `pull_request` scoped to `main`, diagnostics gated to failure, and `permissions: contents: read` added

**Evidence:** `.github/workflows/task-087-frontend-puppeteer.yml` now has `pull_request: [ main ]`, no feature-branch push trigger, `if: failure()` on both diagnostics steps, and an explicit `permissions: contents: read` block.

**What:** Strategy item B2 (Puppeteer workflow trim) was silently scoped out: the TASK-088 pre-entry checklist item reads "completed **or explicitly dispositioned**, with emphasis on [B1, B3]" and is checked — but no disposition for B2 was recorded anywhere. At the branch head, `.github/workflows/task-087-frontend-puppeteer.yml` still has:

- `pull_request: branches: ['**']` (lines 4–5) → double-runs on every PR (once for the PR, once via ci.yml)
- push trigger for `feature/task-087-gate3-product-integration` (line 8) — branch already deleted from origin; dead trigger
- two "Diagnostics" steps at `if: always()` (lines 80–87, 162–171) instead of `if: failure()`
- no `permissions:` block (ci.yml has `contents: read`; this workflow runs with the repo default token permissions)
- the optional rename to a durable name (`frontend-contract.yml`) is still free — no branch-protection check names pin it yet; after cdcai adds protections it stops being free

**Action:** either apply the trim (10 minutes, lowest-risk on the branch before the R1-01 merge so it rides the same CI run), or add an explicit "B2 deferred to cdcai-era cleanup, rationale: …" entry to the TASK-088 log. The review's concern is the undocumented skip, not the residue itself — though note the `['**']` trigger and missing permissions block migrate to cdcai as-is.

---

### R1-07 · MEDIUM (repo hardening) — A4's tracked `.gitignore` hardening never landed

**Status:** RESOLVED — root `.gitignore` now includes `.env.*` with `!.env.example` preserved

**Evidence:** `.gitignore` now contains `.env.*` and still preserves `!.env.example`.

**What:** The root `.gitignore` gained no `.env.*` pattern. The existing `*.env` glob (line 53) does **not** match backup-style names like `.env.uat-backup-20260615` (gitignore `*` matches the whole name; that filename doesn't end in `.env`) — demonstrated by such a file showing as untracked-and-visible in `git status` on the reviewer's clone. `webapp/config/.env.backup.*` (line 51) covers only that subdirectory. One `git add -A` with a root-level env backup present would stage it; that's exactly the accident A4 was designed to prevent, and env backups have historically been created at the repo root during validation runs.

**Action:** add to root `.gitignore`:
```
.env.*
!.env.example
```
(Keep the existing `!.env.example` semantics — order the negation after the new pattern.) Also delete any stray root-level `.env.*` backup files present in working clones used for validation. Land the `.gitignore` change on the branch before the R1-01 merge.

---

### R1-08 · LOW (fork repo settings) — A5 owner-account checks not recorded

**Status:** RESOLVED — repo homepage updated to the correct live site location and no owner-visible draft releases remain

**Evidence:** Repo owner updated the GitHub homepage field to the correct live site location and reviewed the Releases page while logged in on 2026-07-08; visible release entries carried `Pre-release` badges only, and no entries were marked `Draft`.

**What:**
- The fork's homepage field still points at the dead URL `https://groups.ischool.berkeley.edu/TowerScout/` (404) — verified via the public API during this review.
- The logged-in check for **draft releases** (invisible to the unauthenticated API; a forgotten draft could hold pre-rotation notes) has not been recorded as done anywhere.

**Action:** on github.com while logged in as the repo owner: clear/replace the homepage; open the Releases page and confirm no drafts exist. One line in the TASK-088 log for each.

---

### R1-09 · LOW (validation prerequisite) — Rotated-key follow-up is owned by neither task

**Status:** RESOLVED — Task-088 now carries the validation `.env` prerequisite for the post-rotation Azure key

**Evidence:** `TASK-088` now contains a dedicated "Validation Prerequisite" item requiring the validation `.env` to carry the post-rotation Azure key before the D4 live-smoke and setup-wizard checks.

**What:** The Azure key rotation (A1, done 2026-07-08) has a follow-up the plan calls out: the `.env` used for the stable validation pass must contain the **new** key. Neither TASK-088's checklists nor its log carries this. Risk: the D4 live-smoke and S1/S2 wizard steps fail with a dead key, which looks exactly like an F4-style validation defect and burns triage time inside the 07-10 window.

**Action:** add a checklist item to TASK-088's validation slice: "validation cell `.env` verified to contain the post-rotation Azure key (validate via the wizard/API key check before starting the harness)".

---

### R1-10 · LOW (coverage) — Workstream F (User Guidance deck, F1–F9) has no concrete tracking

**Status:** RESOLVED — Task-088 now explicitly tracks Workstream F guide/deck follow-through as an external guide checklist item

**Evidence:** `TASK-088` now contains an "External Guide Tracking" checklist item for Workstream F (F1-F9) ownership and completion.

**What:** TASK-088's acceptance criteria cover guides only generically ("User/support guides … reflect the actual stable release path"). The nine reviewed deck/docx edits (F1–F9) — including **F1, a genuine regression** (slide 16 lost the readiness command `.\scripts\status.cmd -Engine docker`) — live outside the repo and are otherwise easy to lose. Deadlines: guides final by 07-09 PM per the day plan.

**Action:** add the F1–F9 table (or a pointer to strategy §F) as an explicit TASK-088 sub-checklist, and record who executes it (the deck edits may be user-side work rather than Developer work — deciding that is the point of tracking it). F5's screenshot retake depends on D3 package filenames existing, so schedule it after packaging.

---

### R1-11 · INFO (discrepancy resolved in the canonical docs) — Use the strategy doc's `-AssetBundleVersion`, not the analysis doc's

**Status:** RESOLVED by this review — no action needed beyond awareness

**What:** The two canonical docs disagree on the packaging command. The **strategy doc (§D3) is correct**: `-AssetBundleVersion v0.1.0` (or simply omit it — `package-release.ps1:148-166` derives `v0.1.0` from `-Version v0.1.0-cpu` by stripping the flavor suffix). The **analysis doc's** verifier note (finding *p2-validation-1* precondition P5) says `-AssetBundleVersion towerscout-v1-assets-2026-05-05` — that is wrong: the script composes the expected assets filename as `towerscout-{AssetBundleVersion}-assets-{manifest_version}.zip` (line 375), so the analysis value would demand a doubled filename `towerscout-towerscout-v1-assets-2026-05-05-assets-towerscout-v1-assets-2026-05-05.zip` and setup would reject the correctly named bundle.

**Expected final filename (fixed point):** `towerscout-v0.1.0-assets-towerscout-v1-assets-2026-05-05.zip`, sidecar containing hash `00599cc4…` + two spaces + that exact filename + CRLF.

---

### R1-12 · INFO (cosmetic) — Stale "Last reviewed" dates in refreshed docs

**Status:** RESOLVED

**Evidence:** The Settings-linked docs now show `Last reviewed: 2026-07-08` in both their markdown sources and their served HTML twins.

**What:** The settings-linked docs edited on 2026-07-08 (`docs/quick-start.md`, `docs/user-guide.md`, `docs/project-overview.md` and their `.html` twins) still say `**Last reviewed**: 2026-06-29`. Trivial, but these ship in the package and the field exists to be trusted.

**Action:** bump to 2026-07-08 in the same commit as any other pre-tag doc touch-up.

---

## 4 · Preflight checklist for the imminent step (tag → builds → digests → packages)

Sequenced version of the next step with the review findings folded in. Items marked ⚑ come from findings above.

1. ⚑ Land on the branch: R1-05 link/wording fix, R1-07 `.gitignore`, R1-02 redactions (or recorded acceptance), R1-06 B2 trim (or recorded defer), R1-12 dates. Optionally R1-03 branch deletions (pure remote operation, can happen any time before the cdcai push).
2. ⚑ Record the R1-04 decision in TASK-089 before tagging.
3. ⚑ Merge `docs/task-088-stable-handoff` → `main` with a **merge commit or fast-forward — never squash** (R1-01). Push. Wait for **both** workflows green at the new `main` SHA.
4. Sanity: `git merge-base --is-ancestor 3e2c65d main` succeeds; `git tag -l v0.1.0` is empty locally on the machine that will tag (delete a stale local copy first if present — the origin-side deletion does not remove local tags on other clones).
5. Tag the merge SHA: `git tag -a v0.1.0 -m "TowerScout v0.1.0" <sha>`; push **by name** (`git push origin v0.1.0`). Never `git push --tags`.
6. Dispatch `container-publish.yml` twice **from ref `v0.1.0`** (`tag=v0.1.0`, `push_latest=false`, `pytorch_flavor=cpu` | `cuda121`) — Actions web UI works if `gh` isn't authenticated; if using `gh`, confirm `gh auth status` first on that machine. Record both `pinned=ghcr.io/…@sha256:<digest>` lines from the run step summaries. A full rebuild is expected and required (rc7.1 images predate the PR #46 webapp code).
7. Packages from a **fresh clone of tag `v0.1.0`** (`git clone -c core.longpaths=true`, extract/build under a space-free path), using `-Image ghcr.io/j-schulein/towerscout:v0.1.0-<flavor>` + `-ImageDigest sha256:<digest>` per §D3 — fork namespace is correct here per the recorded TASK-088 decision. Asset ZIP renamed per R1-11's fixed point, sidecar regenerated, hash `00599cc4…` re-verified.
8. Package integrity: each ZIP matches its `.sha256`; `scripts\lib\TowerScoutCertificateStore.ps1` present **inside both ZIPs**; if R1-05 added host-helper.md to `$releaseFiles`, confirm it's inside too.
9. ⚑ Before the D4 validation pass: validation `.env` carries the **post-rotation** Azure key (R1-09). Then run the D4 protocol as written (fixture parity 12/12 at 53; S1–S7; rate-limit rules; `-CaptureFixtures` never).

---

## 5 · Notes for the next review round (R2)

R2 will verify, in addition to re-checking the Status column above:

- The merge SHA on `main`, its CI runs, and the ancestor check (R1-01).
- The tag object: annotated, correct target, pushed by name; origin tag list shows no strays.
- Both image digests recorded; workflow runs dispatched from ref `v0.1.0`; `push_latest=false`.
- Package contents spot-check (docs set, certificate-store lib, manifest fields incl. `sbom.status`, `asset_bundle_release_version=v0.1.0`).
- TASK-089 acceptance criteria updated per R1-04; TASK-088 log entries for every ⚑ item.
- Validation evidence folder layout vs the rc7.1 QA precedent, once D4 runs.

*Prepared by the external reviewer, 2026-07-08. Questions about any finding: each cites the exact file/line and the canonical-doc item it traces to (workstream letters = Implementation Strategy; `p2-…`/named findings = Comprehensive Analysis).*
