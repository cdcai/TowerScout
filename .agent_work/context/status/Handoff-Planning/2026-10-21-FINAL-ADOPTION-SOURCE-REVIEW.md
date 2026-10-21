# Final adoption source review - October 21, 2026

**Tasks:** TASK-089 / TASK-092. **Result:** Reviewed preparation changes pass the
bounded local checks below after corrections. Ready for a fork checkpoint push
and PR-based remote validation; not approved for merge or official release.

**Subsequent dependency review:** [PR #113 update](2026-10-21-PR113-DEPENDENCY-AND-ADOPTION-REVIEW.md) supersedes
this snapshot for current readiness. Its aiohttp/Pillow changes require
reviewed integration and affected qualification; the unchanged-runtime
statement below applies only to the earlier checkpoint.

## Scope and baselines

Refreshed upstream/main `3e2c65de3c1772ad67d5c14d5ff38eb5fa274631` and
origin/main `d21c3b207949b6a49f13acae84a451ef0c74cad6` with no tag fetch.
Both are ancestors of the preparation branch; no new cdcai-only commit was found.
Reviewed local changes on top of checkpoint `037974c`, including the outstanding
Tuesday status/audience corrections. The evidence receipt records the final
commit separately to avoid a self-referential document hash.

The 896-file tracked-tree inventory covers the accumulated adoption source.
Detailed semantic review targets the preparation delta from accepted fork main,
using accepted task/ADR evidence for inherited application work. This is not a
new line-by-line audit of all 248,000-plus historical additions, a full-history
secret scan, or a fresh runtime/security qualification of that history.

## Review results

| Area | Result |
| --- | --- |
| Source preservation | cdcai ancestry retained; application webapp/, Dockerfile and security-policy tree unchanged from accepted runtime source 835cbb9 |
| Runtime defaults | All four edits are exactly the fork-to-cdcai CPU namespace replacement; explicit/digest precedence retained |
| CI | Parsed workflow differs from accepted main only by removing the optional Codecov upload; coverage generation/archive remains |
| Agent guidance | All 12 skill names/descriptors validate; current candidate-versus-official boundary retained; deferred launcher work not resumed |
| User guidance | Manual/wiki changes cover short Podman paths and explicit 64-bit Python 3.12; Docker route remains host-Python-free; official destinations reviewed |
| Wiki navigation | 48 internal page references checked, including three heading anchors |
| Support destination | cdcai Issues enabled with Chris's approval; anonymous HTTP 200 verified |
| Distribution exclusions | No tracked output/, dist/, build/, real .env, debug.log or local browser fixture included in inventory |
| Focused credential patterns | 12 occurrences reviewed: 11 dummy/example occurrences and one 41-character literal in a mocked error-redaction test; no real credential established by this review |
| Remaining fork links in scanned maintained/runtime surfaces | README deliberately points to fork preview; accepted RC5 handoff points to immutable fork candidate. Preserve both |

The credential review printed locations/context without printing full matched
values and did not attempt to validate keys against any provider. It does not
rule out other secret formats or sensitive historic content.

## Findings corrected

1. **29 broken historical task-summary links:** repaired relative paths in the
   July pre-rebaseline completed-task snapshot. Confirmed non-link text is
   identical to the pre-repair commit, preserving historical task outcomes.
   Earlier checks of newly added handoff links did not cover these old links.
2. **Stale Issues wording:** updated current PR/coordination/build drafts after
   the approved setting change. Dated preflight evidence remains historical.
3. **CI trigger expectation:** documented that branch pushes do not trigger the
   workflow's main-only push event. Use a PR targeting main for remote checks;
   do not infer green CI from a pushed branch with zero check runs.
4. **Carried-forward review corrections:** separate manager leadership report
   from Chris's packet and retain precise Tuesday incomplete-substep wording.

## Executed checks

- 63 passed in 23.19 seconds: documentation, unsigned-support docs, publication
  workflow, release-manifest schema, release-package staging, mocked Podman GPU
  helper and runtime-hardening tests. No skips/failures were reported.
- Pytest used `--noconftest -o addopts= -p no:cacheprovider`; these modules do not
  need shared application bootstrap. Process-local Windows PowerShell module
  paths were supplied so Get-FileHash is available. No persistent policy changed.
- No containers were started and no official images/packages were published.
  Package staging tests create disposable local fixtures, not qualified ZIPs.
- Source inventory, parsed CI comparison, four-default exact comparison,
  skill metadata and changed-Markdown link checks pass.
- Strict agent-work validator and git whitespace checks pass at checkpoint.
- Original-checkout preservation and packet separation/hashes are rechecked;
  private outputs stay outside the public source checkpoint.

Local detailed evidence is in `output/handoff/final-adoption-review/` in the
original workspace. Remote CI and full real-package evidence remain separate.

## Next sequence

1. Push reviewed preparation branch to J-Schulein/TowerScout, preserving identity.
2. Run remote validation through a PR targeting main. A fork-side validation PR
   can establish checks before the cross-repository adoption PR; if using the
   cdcai PR directly, its final head must pass applicable checks before merge.
   Confirm which route is being executed and retain the exact head/results.
3. Review the concrete cdcai adoption PR, history-preserving merge and build plan.
   Recheck destination heads and identities immediately before execution.
4. After approved adoption, build/scan/verify official CPU/CUDA identities,
   package/download integrity, affected real-runtime profiles and public access.
   Package API 404 did not establish publishing rights or public image access.
5. Finish official wiki/video, owner practice, security action agreement and
   private evidence delivery. The manager report is a separate deliverable.

No remote source push, PR creation, merge, workflow dispatch, setting change,
image/release publication or wiki write occurred during this review slice.
