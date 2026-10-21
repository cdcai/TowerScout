# TowerScout External Review — R2 (pre-tag verification)

> **HISTORICAL REVIEW**: Preserve as evidence; `v0.1.2` is the final validated
> pilot baseline. See `../PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`.

| | |
|---|---|
| **Review round** | R2 (follows R1, 2026-07-08; next round will be R3) |
| **Date** | 2026-07-08 |
| **Reviewed state** | `main` @ `dfe9e6b` (current origin tip); merge commit `71d17d1`; fix commits `12a88cf`, `0f1e337`, `9a5d8be`, `dfe9e6b`; live GitHub state (Actions runs, branches, tags, repo metadata) |
| **Scope** | Independent verification of every R1 finding the Developer marked resolved (in the in-repo copy of the R1 doc), tag-safety assessment of `main` @ `dfe9e6b`, hidden package-surface/docs-route regression sweep, and the updated preflight for tag → image builds → packages → D4 validation |
| **Method** | Every "RESOLVED" claim re-verified against the tree or live GitHub state, not the log; CI runs inspected at all three new `main` SHAs including the failing run's job/step detail; packaging-script diffs checked semantically (whitespace-insensitive) |

---

## 1 · Verdict

**`main` @ `dfe9e6b` is safe to tag as `v0.1.0`.** Specifically:

- Both workflows are **green at `dfe9e6b`** (verified via the Actions API).
- **Zero product-code drift**: `git diff d148727..dfe9e6b` touches nothing under `webapp/`, no compose file, and not the `Dockerfile` — the runtime that CI validated at the PR #46 merge is byte-identical at the tag candidate. `tests/`, `ci.yml`, and `container-publish.yml` are also untouched; the entire delta is docs, task trackers, the reviewed workflow trim, and the packaged-file-list addition.
- The **cdcai fast-forward property is intact**: the branch was merged with a true merge commit (`71d17d1`), and `git merge-base --is-ancestor 3e2c65d main` passes. `git push cdcai main` will fast-forward when Task-089 unblocks.
- The redaction pass is in (zero tracked occurrences of the CA name, thumbprint, or key re-derivation recipe), and the two key-bearing branches are gone from origin.
- All R1 ownership gaps between Task-088 and Task-089 are closed (see §3).

One process note requires a change to the tag step itself (R2-01 below): `main` had a **red-CI window** today between the merge push and `dfe9e6b`. The Developer handled it correctly (fixed forward, did not tag), but the preflight must now say "tag the current green tip `dfe9e6b`", not R1's "tag the merge SHA" — and `main` should be frozen until the tag exists.

---

## 2 · R1 findings — independent verification of claimed resolutions

Every status below was re-verified by this review. The Developer's in-repo status claims were accurate in all twelve cases — no claimed resolution failed verification.

| ID | Claimed | R2-verified | Evidence |
|---|---|---|---|
| R1-01 (merge/tag sequencing) | OPEN (tag pending) | **Merge portion VERIFIED; tag step remains — superseded by §4 preflight** | True merge `71d17d1` (not squash); ancestor check passes; CI green at tip `dfe9e6b`. Note the merge push itself went red — see R2-01 |
| R1-02 (redactions) | RESOLVED | **CONFIRMED** | `git grep` for the CA name, full thumbprint, and the `git show 1c51c7a` recipe each return zero tracked matches; pilot packet now carries the support-transfer line (line 16). Tip-level scope as agreed (history retains the strings — accepted in R1) |
| R1-03 (key-bearing branches) | RESOLVED | **CONFIRMED** | `improvements` and `feature/geocoding-system-integration` deleted from origin (observed in fetch; absent from `ls-remote`) |
| R1-04 (namespace ownership) | RESOLVED | **CONFIRMED** | TASK-089 gained an EARS requirement, an acceptance criterion, and a recorded decision: fork-facing URLs/image defaults in a tag-tree rebuild are **accepted with mandatory cdcai release-note disclosure**; post-tag rewrite or point release preserved as documented alternatives; "must not silently redefine what the v0.1.0 tag means" captured verbatim |
| R1-05 (package-guide link) | RESOLVED | **CONFIRMED** (one accepted limitation → R2-02) | Link corrected to `support/host-helper.md`; "rc7" reworded to "current"; `docs\support\host-helper.md` added to `$releaseFiles` (joins the two `docs\support\oci-*` files already packaged there) |
| R1-06 (B2 workflow trim) | RESOLVED | **CONFIRMED** | `pull_request` scoped to `main`; dead push trigger removed; `permissions: contents: read` added; both diagnostics steps now `if: failure()`; `workflow_dispatch` kept. (Optional file rename not taken — was explicitly optional) |
| R1-07 (.gitignore) | RESOLVED | **CONFIRMED** | Root `.gitignore` adds `.env.*` with `!.env.example` ordered after it (negation wins — correct) |
| R1-08 (owner checks) | RESOLVED | **CONFIRMED** | Homepage now `https://www.ischool.berkeley.edu/projects/2020/towerscout` (verified via API); TASK-088 log records the logged-in Releases check: `Pre-release` badges only, no `Draft` entries |
| R1-09 (rotated-key prereq) | RESOLVED | **CONFIRMED** | TASK-088 "Validation Prerequisite" checklist item added (unchecked — to be checked at D4 time, which is correct) |
| R1-10 (Workstream F tracking) | RESOLVED | **CONFIRMED** | TASK-088 "External Guide Tracking" item added for F1–F9 including out-of-repo ownership. The work itself remains open (see §3) — the finding was about tracking, which now exists |
| R1-11 (AssetBundleVersion) | RESOLVED (info) | **CONFIRMED** | No action needed; §4 preflight retains the correct value |
| R1-12 (Last-reviewed dates) | RESOLVED | **CONFIRMED** | All six settings-linked docs (md + html) show `2026-07-08` |

---

## 3 · Answers to the standing review questions

**Is the Task-088 / Task-089 ownership split now complete enough?** Yes. Every gap R1 identified now has a named owner and a durable record: namespace carry-forward → Task-089 (decision recorded, disclosure required); validation `.env` key → Task-088 checklist; Workstream F → Task-088 checklist; owner-account checks → recorded with evidence. Correctly still open (tracked, not blocking the tag): F1–F9 execution and its out-of-repo ownership assignment, the optional rate-limiter hygiene item, and all validation/evidence work that can only happen after packages exist.

**Any hidden package-surface or docs-route regressions?** One occurred and was already caught and fixed; one accepted limitation and one fragility note remain (R2-02, R2-03). Verified clean: the `0f1e337` `package-release.ps1` change is **whitespace-only** (`git diff -w` = empty — key-alignment formatting, zero semantic change); the manifest content, `$releaseFiles` addition, and SBOM wording match intent; the regenerated HTML twins now satisfy every route-contract assertion (CI green proves it); the compatibility stubs (`v1-rc1-*`, `towerscout-user-guide.*`) are intact; no test was modified anywhere in the delta.

---

## 4 · New findings (none block the tag)

### R2-01 · PROCESS — `main` was CI-red from the merge push until `dfe9e6b`; tag the green tip, and freeze `main` until the tag exists

**Status:** RESOLVED by the Developer's fix — recorded here because it changes the preflight and because R3 will check the freeze held.

**What happened:** the merge push (`71d17d1`) failed CI — `test (3.12)` › "Run unit tests": the HTML regeneration in `0f1e337` line-wrapped a paragraph in `docs/user-guide.html`, breaking the contiguous-string route assertion at `tests/unit/test_flask_routes.py:134` (`b"Docker Desktop is installed, approved, and running"`). `9a5d8be` was pushed while red; `dfe9e6b` re-joined the wrapped line — **content-identical, formatting-only, and the test was not touched** (verified: the fix commit's diff is 3 lines of HTML re-wrap in one file). Both workflows green at `dfe9e6b`.

**Assessment:** textbook fix-forward — nothing was weakened to get green. Two consequences:

1. **The tag target is `dfe9e6b`** (or a later green tip), not "the merge SHA" as R1's checklist phrased it. Tagging `71d17d1` would tag a commit whose CI run is red on record.
2. **Freeze `main` between now and the tag.** Any further push restarts the CI-green requirement and retargets the tag. If something must land, land it, wait for green, and retarget deliberately.

### R2-02 · INFO (accepted limitation) — the in-app docs route cannot serve `docs/support/host-helper.md`; no action recommended pre-tag

**What:** the `/docs/<path>` route rejects any path containing `/` by design (`webapp/towerscout.py:1630`) before the allowlist check, so the packaged `docs/support/*` files — including the newly packaged `host-helper.md` — are not reachable in-app. R1-05's fixed link therefore works in the two contexts that matter (extracted package folder, GitHub) and 404s only for someone hand-typing `/docs/support/host-helper.md` into the running app. This matches the pre-existing, accepted pattern for the two `docs\support\oci-*` files that have shipped in packages since before this cycle. Package-guide.md is served raw (unrendered markdown) in-app anyway, so there is no in-app click path to break.

**Action:** none before the tag. Do **not** try to fix by adding `support/host-helper.md` to `PUBLIC_DOC_FILES` — the route's subpath rejection means that alone would not work, and changing route logic pre-tag for a cosmetic path is the wrong trade. If in-app support-doc serving is ever wanted, that is a post-release/cdcai-era item.

### R2-03 · INFO (future-proofing) — the docs HTML twins carry byte-level contract strings; re-run the route tests after any regeneration

**What:** `tests/unit/test_flask_routes.py` asserts **contiguous multi-word strings** inside the served docs, so any future edit or regeneration that re-wraps lines can break CI even when the visible content is unchanged (exactly what R2-01 demonstrated). Current load-bearing strings include: quick-start index — `"You do not need Git, Python, Conda, Node.js, VS Code"`; project-overview — `"What Users Need Installed"`, `"source-code checkout"`; user-guide — `"Docker Desktop is installed, approved, and running"`, `"qualified Podman path"`; package-guide — `"CPU Application Package is the primary path"`, `"12.1 Application Package"`, `"support-assigned paths"`.

**Action:** before pushing any future docs/HTML touch-up (including Workstream-F-driven syncs), run `pytest tests/unit/test_flask_routes.py -q` locally. Worth a one-line note in the Task-088 Workstream F checklist item.

---

## 5 · Updated preflight — tag → image builds → packages → D4 validation

Supersedes R1 §4. Steps 1–2 of the R1 preflight (branch fixes, R1-04 decision) are done and removed. Changes from R1 are **bold**.

1. **Tagging-machine preflight:** `git fetch origin`; confirm `git rev-parse origin/main` = `dfe9e6b8286dd687ec837a0bebf56fa068596570` and local `main` matches; `git tag -l v0.1.0` must return nothing locally (the old tag was deleted from origin, but clones that had it keep the local copy — delete it locally first if present); confirm both workflows green at that SHA: `https://api.github.com/repos/J-Schulein/TowerScout/actions/runs?head_sha=dfe9e6b8286dd687ec837a0bebf56fa068596570`.
2. **Freeze `main`** — no further pushes until the tag is pushed (R2-01). If something must land, wait for green and consciously retarget the tag.
3. Tag **the green tip**: `git tag -a v0.1.0 -m "TowerScout v0.1.0" dfe9e6b` → `git push origin v0.1.0` (by name; never `git push --tags`).
4. Dispatch `container-publish.yml` twice **from ref `v0.1.0`** (`tag=v0.1.0`, `push_latest=false`; `pytorch_flavor=cpu`, then `cuda121`). Actions web UI works without `gh`; if using `gh`, check `gh auth status` on that machine first. Record both `pinned=ghcr.io/…@sha256:<digest>` lines from the run step summaries. Full rebuild is expected — rc7.1 images predate the PR #46 webapp code.
5. Fresh clone of tag `v0.1.0` (`git clone -c core.longpaths=true`, work under a **space-free path**). Prepare the assets ZIP: copy the verified `00599cc4…` bundle to `towerscout-v0.1.0-assets-towerscout-v1-assets-2026-05-05.zip`, regenerate the sidecar (`<hash><two spaces><filename>` + CRLF), re-verify the hash.
6. Build both packages per strategy §D3 (`-AssetBundleVersion v0.1.0` or omit — R1-11; `-Image ghcr.io/j-schulein/towerscout:v0.1.0-<flavor>` per the recorded fork-side decision; `-ImageDigest sha256:<digest>` from step 4).
7. Package integrity: each ZIP matches its sidecar; `scripts\lib\TowerScoutCertificateStore.ps1` inside both ZIPs; **`docs\support\host-helper.md` inside both ZIPs (newly packaged this cycle)**; spot-check `release-manifest.v1.json` in a ZIP — `sbom.status` shows the deferred posture, `asset_bundle_release_version` = `v0.1.0`, `image_digest` = the pinned digest.
8. Before D4: check the Task-088 "Validation Prerequisite" box only after confirming the validation cell `.env` carries the **post-rotation** Azure key. Then run D4 exactly as written (per-cell readiness gates incl. `app v0.1.0` + new digest; 12/12 fixture parity at 53 across the three runs; S1–S7; rate-limit rules; never `-CaptureFixtures`).
9. After validation passes: fork release per strategy §E (`gh auth status` on the publishing machine; `--verify-tag`; 6 assets; `--latest`; not prerelease).

---

## 6 · What R3 will check

- The tag object: annotated, targets `dfe9e6b` (or a deliberately retargeted later green tip), pushed by name, no stray tags appeared alongside it; `main` freeze held between R2 and the tag.
- Both dispatch runs: ref `v0.1.0`, `push_latest=false`, digests recorded; digests differ from rc7.1's (`14b6ef52…`/`95f1f396…`) as expected for a rebuild.
- Package contents per §5 step 7, including the new `docs\support\host-helper.md`.
- D4 evidence folder against the rc7.1 QA layout; the Task-088 validation-prerequisite box checked with evidence.
- Workstream F: ownership assigned and F1–F9 progressing (deck edits are on the critical path for the 07-09/07-10 guide deadline); R2-03's route-test habit applied to any HTML touch-ups.
- Release publication fields when reached (§E): `--verify-tag` used, 6 assets, sidecars valid.

*Prepared by the external reviewer, 2026-07-08. All twelve R1 dispositions were independently re-verified this round; none failed verification — see §2 for per-item evidence.*
