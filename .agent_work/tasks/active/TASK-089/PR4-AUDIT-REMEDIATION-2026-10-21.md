# PR #4 audit remediation - October 21, 2026

## Scope and authority

The outgoing lead authorized addressing audit findings 1, 2, 3, and 5,
one item at a time, on October 21. Finding 4 (licensing and explicit approval
of the development-history transfer) and Chris's final merge approval remain
pending. This work does not authorize an adoption merge, credential/account
changes, image/release publication, or a readiness claim
for official packages.

The lead subsequently directed that historical `contents.txt` be excluded
from cdcai Git history. This authorizes preparing and verifying that bounded
exclusion in isolation; preserve original fork/release references and obtain
separate authorization before replacing the remote PR branch.

Starting PR head: `1d9c6d72413bc1b06b1450cfe21b244976bffbc9`.
Starting cdcai base: `87ca90089473e1855f98968f75a17b5f8d0dd1cd`.
Use an isolated filtered clone of the clean adoption worktree; preserve the
unrelated dirty primary checkout. Keep the commit topology, immutable releases, deferred
launcher work, ML dependencies/models, and 396-key security baseline intact.

## Acceptance and implementation sequence

1. WHEN historical credentials or investigation data are being adopted, THE
   PROJECT SHALL record specific credential unusability and data disposition
   before declaring the history acceptable. Redacted fingerprints identify
   findings; never copy credential values, locations, or raw datasets here.
2. WHEN a temporary security residual is applied, THE COMPARATOR SHALL verify
   its approved package location as well as its existing identity constraints,
   reject absent/mixed/unapproved locations, and preserve expiry and fail-closed
   publication behavior. Extend focused tests before changing the matcher.
3. WHEN CSV/KML contains special characters, THE EXPORT SHALL preserve field
   text through a standard parser without changing selection, geometry,
   provenance, download actions, filenames, or dataset ZIP behavior. Add
   reproductions, correct only serialization, and regenerate the bundle.
4. WHEN reporting PR checks and review readiness, THE PROJECT SHALL distinguish
   blocking checks, advisory failures, unresolved conversations, and real
   runtime qualification. Investigate the five integration failures before
   choosing bounded corrections; never hide failures or weaken required gates.

Validate and review each bounded change before moving to the next. Record
remaining owner decisions explicitly. Final verification must identify the
actual updated head/base; earlier green checks cannot qualify later commits.

## Finding 1 - historical credential and data disposition

**Status: local exclusion verified; remote PR replacement and final approval pending.**

The July 8 rotation record identifies the old 86-character Azure Maps key
from historical TASK-024. SHA-256 prefix: `18f45c5be251`. See the archived
[implementation strategy](../../../context/archive/2026-07/Handoff-Planning/TowerScout-Implementation-Strategy.md),
section A1. That record does not identify the separate value below.

Historical `contents.txt` in commit
`314a05df183da68596e0c96d9ca46811efa9643d` contains a different credential-like
value in eight Azure URL query parameters. Its SHA-256 is
`9af831074bba65da8237f993bba56a8a4ab55fb529bd3f7f5265b04eb3b70741`.
The file also contains saved location/detection data and local paths. No
credential or location is reproduced in this record. The file is absent from
the current tree but remained reachable through the original PR history.

A read-only rescan of all 2,674 new-to-cdcai blobs found that exact value only
in blob `12426b689e2ba62b721b397fa20e021ffdc59d85` (`contents.txt`, eight
occurrences). This bounded result does not establish that the value is active,
revoked, synthetic, or that no other possible secret exists. No provider
request was made with it, and no history or account was changed.

The preceding scan describes the pre-remediation state. Following the lead's
direction below, only the isolated incoming history was subsequently filtered.

The outgoing lead directed: "We should remove/exclude that file from being
included in cdcai's Git history." Prepare a bounded exclusion of historical
root `contents.txt`, with per-commit tree comparisons and a reachable-object
scan, while preserving original fork and release references. No revocation is
asserted for this value. The cdcai merge hold remains until the filtered
history is verified and the final PR source is approved.

Local preparation used pinned git-filter-repo 2.47.0 in a non-hardlinked,
single-branch clone without tags. Only root `contents.txt` was excluded from
commits after cdcai base `87ca900`. Empty commits, merge parent order, commit
messages, author/committer identities and timestamps were preserved. Verification
against the original local checkpoint `79f00bd` found:

- All 260 incoming commits retained; 213 commit IDs necessarily changed.
- Four commit trees changed solely by removing `contents.txt`; every other
  file's content and mode matched. Final working tree content was identical.
- The 98 signatures on rewritten commit copies were removed, because they
  cannot authenticate the rewritten content/ancestry. The original signed
  commits and release tags remain untouched in the original fork/repositories.
- Original cdcai base remains unchanged and is an ancestor of filtered
  checkpoint `120c6bdc630103355e193813a74dfd82fc7cefe1`.
- No root `contents.txt` history or excluded blob is reachable from that head.
  All 2,690 incoming blobs and other new reachable Git objects were scanned;
  the exact credential-like value had zero occurrences.
- Original repository refs were byte-for-byte unchanged. The isolated clone's
  local origin was removed to prevent an accidental push to the original checkout.

The sanitized verification JSON and original-to-filtered commit map are retained
under `output/handoff/pr4-remediation-security/` in the primary checkout.
Commit-map SHA-256:
`d55fdb9b02e746c01ad542548e10f9b510f8752398f03946320225d3e12ef5f0`.
Historical release/source references in documentation continue to identify the
original fork commits; do not relabel their evidence as filtered-source builds.

The existing required `frontend-test` job now fetches complete history and runs
`scripts/check_adoption_history.py` in cdcai. It rejects shallow evidence, any
root `contents.txt` history, and the known blob even under another name. The
original fork is intentionally excluded from this receiving-repository rule.
Never merge the original fork's unfiltered ancestry back into cdcai; use reviewed
patches/cherry-picks for later changes and keep this guard blocking. Fork PR #114
cannot establish the receiving repository's history exclusion; PR #4 must run
its own checks on the updated proposed merge.

This prepares exclusion from future cdcai `main` ancestry. It does not revoke a
credential or erase existing fork objects, cached GitHub views, or old PR refs.
Those limits and signature consequences are described in GitHub's
[history-removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
Do not claim that the unverified credential is unusable. The remote PR still
has its original history until the narrowly scoped replacement is authorized.

History guard and existing CI-ratchet contracts: **15 tests passed**. The guard
also passed on the actual filtered clone and rejected the actual original
adoption checkout without printing data. Agent-work validation and diff
whitespace checks passed.

Existing provider URL redaction and structured-error tests: **13 passed**
using `tests/unit/test_provider_http.py` and
`tests/unit/test_error_sanitization.py` on Python 3.12.10. These synthetic tests
verify current redaction behavior, not historical credential revocation.

## Finding 2 - exact pip-private residual boundary

**Status: local correction and focused verification passed; updated remote
checks and official image qualification remain pending.**

The original comparator accepted an unapproved same-version urllib3 record
both alone and mixed with the expected record. Both regression reproductions
failed against the original implementation before correction.

Retained Trivy 0.69.3 reports show that the approved pip-private entry has no
`PkgPath`; it comes from pip's embedded CycloneDX inventory. See Trivy's
[embedded-SBOM documentation](https://trivy.dev/docs/v0.68/guide/supply-chain/sbom/#sbom-detection-inside-targets).
Requiring a path that the scanner does not supply would reject the known
qualified images. The correction therefore combines:

- Exact immutable-image filesystem inventory: only application urllib3 2.8.0,
  pip 26.2.1's private urllib3 2.7.0, and its license-only directory. An extra
  copy, distribution, ambiguous SBOM source, missing file, redirected path,
  changed version, or incomplete directory traversal fails closed.
- Matching Trivy package UID/PURL, SBOM analyzer, Python target, and observed
  package paths, in addition to existing version/class/type/severity checks.
  Missing identities in duplicate findings remain visible instead of being
  hidden by another populated record.
- Image/source/flavor binding and a retained inventory hash. The publish
  workflow collects evidence before registry login, and the exact-digest
  comparison uses it only after the existing same-config identity check.
  Standalone digest verification collects fresh evidence. The existing
  required Full Docker build also exercises collection on its new image.

Only the two existing urllib3 residuals gain a narrower location policy. No
package version, baseline finding, approved residual key, owner, or expiry is
changed. All five residuals still expire October 31, 2026 at 23:59:59 UTC.

Validation:

- Comparator, filesystem inventory, publish/verify workflow and CI ratchet:
  **81 tests passed** on Python 3.12.10.
- Actual retained RC5 CPU and CUDA images at source `835cbb9`: isolated,
  network-disabled, read-only inventory passed. Their existing application
  containers and named volumes were not mounted or modified.
- A disposable tmpfs containing an extra real urllib3 copy was rejected with
  exit 2 and no successful proof output.
- Both retained RC9 exact-digest reports replayed successfully with fresh
  inventory collected from their corresponding images: baseline 396,
  candidate 79, accepted baseline 74, accepted residuals 5, blocking 0,
  severity escalations 0, resolved 322. This is historical-report replay,
  not a fresh vulnerability scan or new official-image qualification.
- Inventory proof hashes: RC5 CPU
  `3e67342a4aef3fd300e9cae15d4605cef650a6305eeaeb542c5f6eae0a65b062`;
  RC5 CUDA `a45648c69467a9673a26928e880cb647042bd146b882a2c679c80e9df37e561a`;
  RC9 CPU `a8677c32c61c6e681f5081c8c1825d6f2605cebbc23f959431467bd68d263815`;
  RC9 CUDA `ec8ebcb2be2874f91fb57b294c9c42656e6534b708b8969c05994cd133099039`.
  Sanitized local outputs are retained under the primary checkout's
  `output/handoff/pr4-remediation-security/`.

Future Python/pip/urllib3 layout or scanner changes require a reviewed policy
update; they do not silently widen this exact, temporary exception.

## Finding 3 - CSV and KML serialization

**Status: local correction and focused verification passed; remote checks pending.**

Independent Python standard-library CSV and XML parsers reproduced both failures
against the original JavaScript download handlers. CSV now doubles embedded
quotes in address fields; KML escapes name and complete description text once,
preserving carriage returns with character references. No detection selection,
coordinate calculation, provenance label, download action, or dataset ZIP code
was changed. The generated bundle was rebuilt and its diff contains only these
source changes and the source fingerprint; build order remains unchanged.

Two parser tests now cover quotes, commas, ampersands, angle brackets, apostrophes,
CR/LF, Unicode, literal entity text, and `]]>`. They verify all six CSV rows,
the three eligible KML placemarks, ML/manual provenance, unknown-address fallbacks,
coordinates, and exclusion of unselected/below-threshold/outside-boundary KML
records. These tests also execute the existing explicit-download assertions and
are wired into the blocking frontend job.

Both parser tests and six maintained frontend contracts passed (exports, global
handlers, debug logging, setup wizard, cancel/recovery, provider-state manager).
Generated JavaScript syntax and source/bundle consistency checks passed. These
are synthetic serialization checks, not a replacement for official-package
browser and model qualification.

## Finding 5 - integration evidence and review conversations

**Status: local integration corrections passed; review replies, conversation
resolution, and checks of the updated remote PR remain pending.**

The same five integration failures were reproduced locally before correction.
The corrections are confined to two test modules:

- Route smoke now discovers synthetic catalog metadata in a temporary directory
  and checks both empty and populated catalogs. It no longer assumes untracked
  developer model weights exist in a CI checkout. The separate real-weight smoke
  still skips when assets are absent; synthetic catalog bytes are never loaded.
- Geocoding uses real Flask request contexts instead of patching the wrong
  session binding, and private temporary caches prevent cross-test state.
- Cache reads specify Azure, matching the existing provider-isolation contract;
  Google cannot reuse those entries. The radius fixture is about 50 m away,
  correctly between the tested 25 m and 100 m boundaries.
- The successful Azure response fixture uses the current `addresses` schema;
  exceptions can no longer silently make that success test pass.
- Failure tests cover both structured empty-address service failures and the
  actual application's coordinate-display fallback. Provider HTTP is mocked.

All integration tests plus existing geocoding unit tests: **52 passed, 3 skipped**.
The three skips are one real-model smoke without weights and two external host
helper templates without a running helper. No new skips or expected-failure
markers were introduced. The broader integration job remains advisory under
existing policy; formatting, mypy, and Bandit were not broadly changed or waived.
The ten deterministic route/geocoding regressions now also run as a separate
blocking step in both existing Python jobs. These contracts plus the CI-ratchet
tests passed: **21 tests**. This narrowly prevents the repaired failures from
being hidden again by the broader advisory step.

The full Windows Python 3.12 unit run reported **703 passed, 74 skipped,
19 failed** in 136.98 seconds. All 19 failures are in the existing Task-087
host-helper module: Windows antivirus rejects `TowerScoutHostHelper.ps1` with
`ScriptContainedMaliciousContent`, causing direct or downstream assertions to
fail. Its Git blob `8d6ba4ac3e0163efbbd5a741bc1f8f5a8b892fdc` is identical
to the original remote PR head; neither helper code nor its tests were changed.
No security protection was disabled and no workaround or launcher redesign was
attempted. This is an observed local execution block, not an established false
positive and not a passing full-suite result. The required Windows host-helper
CI job remains intact and must pass on the updated PR; this endpoint-specific
block remains disclosed for owner/IT assessment. The helper remains disabled
by default. Existing normal-launch and Windows runtime/TLS tests passed in the
same full run. Required fatal/syntax lint passed with zero findings.

The two unresolved [first](https://github.com/cdcai/TowerScout/pull/4#discussion_r4339751002)
and [second](https://github.com/cdcai/TowerScout/pull/4#discussion_r4341663108)
review threads describe the same torch LOW advisory. The updated
[dependency disposition](../TASK-103/DEPENDENCY-SECURITY-DISPOSITION.md) records
primary-source revalidation and current source-path evidence. No ML dependency
upgrade or alert dismissal is included.

Proposed reply for each thread, not yet sent:

> Reviewed CVE-2025-3000 against the current source and upstream advisory. It
> remains present in torch 2.10.0; the reported fix is 2.13.0. The affected
> operation is `torch.jit.script`. TowerScout has no call to that operation in
> its application or vendored source, and the shipped, hash-verified `.pt`
> model follows the PyTorch loader rather than the optional TorchScript branch.
> The existing Task-103 dependency disposition and ADR-022 retain this visible
> LOW finding as a time-limited compatibility-bridge risk. Reassess immediately
> if scripting, model format, trust, or runtime dependencies change; the existing
> review deadline and early-exit triggers remain in force. This is not a false
> positive or a claim that the dependency is fixed. No alert dismissal or
> vulnerability-gate relaxation is requested. See
> `.agent_work/tasks/active/TASK-103/DEPENDENCY-SECURITY-DISPOSITION.md` and
> `.agent_work/decisions/022-cuda128-blackwell-ml-runtime.md` in this PR.

Resolve the conversations only after the disposition is published and reviewed.
Retain the draft and final-approval hold. The old nine green required checks
identify remote head `1d9c6d7`; they cannot qualify the corrected filtered head.

## Remaining owner decision
- Finding 4: deliberately unchanged; Chris's specific approval remains pending.

## Follow-up: exclude deferred helper executables and re-review prepared update

The lead requested identification/exclusion of unused helper instances and a
second review of the prepared update before approving publication. The bounded
local correction excludes these four source files from the control ZIP list:

- `scripts/host-helper.cmd` (wrapper)
- `scripts/host-helper.ps1` (listener entrypoint)
- `scripts/host-helper-worker.ps1` (worker)
- `scripts/lib/TowerScoutHostHelper.ps1` (deferred execution/control module)

Their Git source, history, tests, deferred branches and reviews remain intact.
`TowerScoutHostHelperState.ps1` remains a required normal launch/stop dependency
for stale-session and bridge-environment cleanup. `TowerScoutCertificateStore.ps1`
and the manual repair/import scripts remain required by supported TLS repair.
The Dockerfile does not copy the Windows scripts directory, so no container
layer exclusion or ML runtime change is needed. Backend/frontend gates remain
disabled and continue to report the helper as unavailable.

The dependency review found one additional issue to correct: an inherited
`TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED=1` would otherwise make extracted launch
or stop dot-source the now-excluded module and fail. Both scripts now detect
the absent module, warn, and take the normal cleanup/Compose path. A stale
controlled-operation flag cannot suppress shutdown cleanup in that case.
Source checkouts containing the helper retain their existing review behavior;
this does not revive Task-087. Package guide, helper support reference and
example-environment comments now agree with this package boundary.

Validation of this bounded follow-up:

- **8 packaging tests passed**, including actual CPU/CUDA ZIP generation,
  outer SHA-256 sidecars, every internal file checksum, exact exclusions,
  retained manual TLS dependencies and archive manifests.
- Extracted ZIP scripts in a path containing spaces reached a fake Docker
  Compose engine for launch and stop with review flags both off and on. They
  preserved its deliberately nonzero exit code and cleared seeded stale state.
  These are synthetic behavior contracts, not successful live startup or
  downloaded release qualification. No real engine, provider or user state was
  touched. Fixture images use synthetic digests and allow dirty source explicitly.
- A new blocking step runs packaging contracts within the existing required
  Windows job; its name and original helper tests/self-test remain unchanged.
- The focused history, security, CI, TLS/launcher and helper run reported
  **103 passed, 5 failed, 18 deselected**. The five failures re-entered the
  unchanged helper module and reproduced `ScriptContainedMaliciousContent`.
  No new application failure was observed; this is not an all-green result.
  Earlier full-suite evidence (703/74/19) remains recorded above.
- The complete integration/geocoding rerun remained **52 passed, 3 skipped**.
  Both independent export parser tests and the explicit download contract
  passed again. The blocking history guard passed.

Second-review disposition:

| Finding | Local result | Remaining requirement |
| --- | --- | --- |
| 1: investigation history | Bounded exclusion and preserved original refs remain suitable. | Approve remote branch replacement; verify new cdcai merge ancestry. Old refs/caches and credential revocation are not addressed by this rewrite. |
| 2: security exceptions | Exact-image inventory and strict matcher remain suitable; baseline, five identities and expiry remain unchanged. | Fresh CI and later scans of the new official CPU/CUDA images. |
| 3: exports | Parser-verified serialization remains suitable; selection/model behavior unchanged. | Fresh required frontend checks and later official-package qualification. |
| 5: integration/review | Corrected tests and blocking regression gates remain suitable. Helper distribution issue now corrected locally. | Fresh required CI, published/reviewed security dispositions and resolved conversations. Retained helper source still has a local antivirus execution block. |

No further local correction was identified in this re-review. The prepared
update is suitable to publish **for review and fresh CI after authorization**;
it is not yet merge-ready. The remote draft source/base were rechecked and
remain the starting IDs recorded above. Earlier green checks cannot qualify
these changes. Chris's licensing/history and final merge approvals, fresh
required checks, and subsequent official-byte qualification remain separate.
No push, PR edit/reply, conversation resolution, merge, official build or
publication occurred during this follow-up.
