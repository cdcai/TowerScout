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
Use the existing clean adoption worktree; preserve the unrelated dirty primary
checkout. Keep the history-preserving topology, immutable releases, deferred
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

**Status: OPEN - owner-selected history exclusion awaiting verification.**

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
the current tree but remains reachable through the proposed merge history.

A read-only rescan of all 2,674 new-to-cdcai blobs found that exact value only
in blob `12426b689e2ba62b721b397fa20e021ffdc59d85` (`contents.txt`, eight
occurrences). This bounded result does not establish that the value is active,
revoked, synthetic, or that no other possible secret exists. No provider
request was made with it, and no history or account was changed.

The outgoing lead directed: "We should remove/exclude that file from being
included in cdcai's Git history." Prepare a bounded exclusion of historical
root `contents.txt`, with per-commit tree comparisons and a reachable-object
scan, while preserving original fork and release references. No revocation is
asserted for this value. The cdcai merge hold remains until the filtered
history is verified and the final PR source is approved.

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

## Remaining findings
- Finding 3: pending serialization corrections and source/bundle verification.
- Finding 5: pending advisory failure and review-conversation disposition,
  then final-head checks. Review replies/publication have not been sent.
- Finding 4: deliberately unchanged; Chris's specific approval remains pending.
