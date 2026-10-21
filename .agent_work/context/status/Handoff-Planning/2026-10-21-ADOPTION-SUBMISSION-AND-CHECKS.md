# Adoption submission and checks - October 21, 2026

**Tasks:** TASK-089 / TASK-104 / TASK-105. **State:** draft adoption PR open;
no cdcai source merge, official build, release or wiki publication.

## Completed sequence

1. The user explicitly approved PR #113 in the conversation. Its exact tested
   head `2980f96` was rechecked, squash-merged to the fork at `60ae1c9`, and
   verified tree-identical. The head branch and local evidence were preserved.
2. [Post-merge CI](https://github.com/J-Schulein/TowerScout/actions/runs/39640507007)
   and [controller checks](https://github.com/J-Schulein/TowerScout/actions/runs/39640507010)
   passed. The raw full-build log confirms an actual local Docker image was
   exported, with no error marker. No registry publication was performed.
3. Adoption integration `8b49f74` retains fork-main ancestry and the two
   rehearsed documentation resolutions. Runtime, tests, scripts, configuration
   and skills match the 144-test rehearsal; later changes are documentation.
4. Preparation checkpoint `25c2e86` was pushed to the fork and submitted as
   [draft validation PR #114](https://github.com/J-Schulein/TowerScout/pull/114).
   [Combined CI](https://github.com/J-Schulein/TowerScout/actions/runs/39641115622)
   and [controller checks](https://github.com/J-Schulein/TowerScout/actions/runs/39641115379)
   passed. Unit results are 586 passed, 162 skipped and five subtests passed
   per Python version. The extra Linux skip is the additional parametrized
   Windows package test; the corresponding local Windows test is exercised.
5. [cdcai adoption draft #4](https://github.com/cdcai/TowerScout/pull/4) was opened
   from the fork preparation branch against cdcai main `3e2c65de`. The initial
   head was `25c2e86`; cdcai reported it mergeable. The initial historical scope
   is 769 changed files, 249,375 additions and 2,193 deletions. This is not a
   new line-by-line audit of the whole inherited project. The next status-only
   checkpoint includes this receipt; its final head/checks are recorded in the
   PR descriptions and local execution receipt to avoid a self-referential hash.

## Review checks retained

- cdcai main is an ancestor, with no cdcai-only commits at submission.
- Application code matches approved fork main. Since accepted RC5 source,
  the new runtime delta is the aiohttp/Pillow pins and Pillow minimum only.
  Model assets, thresholds, Dockerfile and security policy remain unchanged.
- Four official CPU defaults are exact namespace replacements; existing
  explicit image/digest precedence tests remain intact.
- Parsed CI changes only remove the optional Codecov uploader; coverage
  generation and artifacts remain. All 32 direct Action references match the
  rechecked cdcai allowlist. No repository protection/settings were changed.
- The source inventory, changed relative links, 12 skill descriptors, strict
  task validator and whitespace checks pass. The same 12 credential-pattern
  matches remain the previously reviewed synthetic examples/test data.
- Eight preserved original local documents still match their recorded hashes.
  Current wiki sources match the published fork rehearsal at `ca24d6f`.

## Open checks and explicit limits

- At draft creation cdcai reports no check runs and no Actions runs. This is
  not a green cdcai CI result. Actions is enabled, but its workflow inventory
  is empty on the current destination. Monitor destination checks and record
  the actual result; source validation on the fork is separately linked above.
- The fork dependency graph/SBOM still lists aiohttp 3.14.3 and Pillow 12.3.0.
  Alerts 77/78/79 consequently remain open. Actual merged pins and blocking
  scans are corrected; alert closure has not been claimed or forced through
  dismissal. A separate existing Low torch alert remains. Reconcile the graph
  before final security handoff and verify cdcai's graph after adoption.
- Five advisory integration failures, including the radius subtest, match
  accepted-main results before either dependency update. Advisory formatting,
  typing and Bandit findings remain. The original local Waitress connection
  reset is retained even though the focused and complete reruns passed.
- The full CI build is a local image build on GitHub's runner, not a published
  cdcai image, two-flavor release scan or actual Windows package qualification.
  Local preprocessing tests use the older local torch pair; CI uses the
  maintained pair with mocked model loading. No real model/device acceptance
  is inferred from these source checks.

## Next decisions and work

Review draft #4, the final source/checks and the recommended history-preserving
merge commit. User approval of #113 does not approve the cdcai adoption merge.
Recheck the destination head and required reviews immediately before any merge.
Keep fork #114 as a validation checkpoint; no separate fork-main preparation
merge or branch deletion has been authorized by this submission.

After separately approved adoption, freeze the official source and build
identities, verify package permissions/public access, perform strict scans and
actual downloaded-package/model/provider/recovery/persistence checks, then
publish and verify wiki/video and complete owner practice/receipt. ADR-024's
five exact residuals and October 31 expiry remain binding. Preserve immutable
RC5 artifacts and deferred launcher work. Chris's packet and the manager's
leadership report remain separate; neither was sent or uploaded here.
