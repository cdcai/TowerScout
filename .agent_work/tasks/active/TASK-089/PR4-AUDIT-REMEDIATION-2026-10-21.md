# PR #4 audit remediation - October 21, 2026

## Scope and authority

The outgoing lead authorized addressing audit findings 1, 2, 3, and 5,
one item at a time, on October 21. Finding 4 (licensing and explicit approval
of the development-history transfer) and Chris's final merge approval remain
pending. This work does not authorize an adoption merge, credential/account
changes, history rewriting, image/release publication, or a readiness claim
for official packages.

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

**Status: OPEN - specific owner confirmation required before merge.**

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

The outgoing lead has been asked to confirm credential revocation/account
deletion (or documented synthetic provenance) and whether the saved data is
approved for transfer. Until evidence arrives, retain the merge hold. If the
history cannot be cleared, obtain a separate reviewed history-exclusion plan;
do not rewrite release/tag provenance as a routine cleanup.

Existing provider URL redaction and structured-error tests: **13 passed**
using `tests/unit/test_provider_http.py` and
`tests/unit/test_error_sanitization.py` on Python 3.12.10. These synthetic tests
verify current redaction behavior, not historical credential revocation.

## Remaining findings

- Finding 2: pending implementation and focused security regression proof.
- Finding 3: pending serialization corrections and source/bundle verification.
- Finding 5: pending advisory failure and review-conversation disposition,
  then final-head checks. Review replies/publication have not been sent.
- Finding 4: deliberately unchanged; Chris's specific approval remains pending.
