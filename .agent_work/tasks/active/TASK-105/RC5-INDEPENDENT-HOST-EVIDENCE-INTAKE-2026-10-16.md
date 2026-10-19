# RC5 Independent-Host Evidence Intake

**Recorded**: October 16, 2026
**Task**: TASK-105
**Host**: `INDEP-HOST-01`
**Status**: Four-profile operational results reviewed; owner clarification
received. Final qualification and finding dispositions remain under review.

## Evidence custody and integrity

- Report: `V013-RC5-INDEPENDENT-HOST-REPORT-2026-10-14.md`.
- Archive: `V013-RC5-INDEPENDENT-HOST-SANITIZED-EXTRACTS-2026-10-14.zip`.
- Archive SHA-256:
  `25f611f9b9918e54a84e4eea86b2113412c7a28612d5d5747ec5114e80fe94a4`.
- All 110 ZIP entries were readable with clean CRCs. All 108 extract-manifest
  rows matched their recorded sizes and SHA-256 values; all 61 JSON files parsed.
- The standalone report has two later Docker-autostart clarifications relative
  to the report embedded in the archive. This is a report-version difference;
  the extract manifest verified without mismatches.
- A redacting review found no matches for Google key patterns, GitHub tokens,
  private keys, unredacted Windows user paths, or key-bearing URL parameters.
  The source report includes a public test-area label; it is omitted here.
- Source files, raw exports, screenshots, logs, and credentials remain outside
  tracked repository evidence under the owner's custody.

## Bound candidate

- Candidate: immutable, non-Latest `v0.1.3-rc5`.
- Accepted source: `835cbb910573a931350c5b704d14496952d7ef87`.
- CPU control ZIP:
  `dfcc653eef4d0c9666604d6455797c123b757d92d4507ad1d451032f5cdd7a8f`.
- CUDA control ZIP:
  `c418e1948ed2719cd8c3678b612addccf468a139aafc97f99d3f4bd7676974d0`.
- Asset ZIP:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- CPU image:
  `sha256:833dbe0d0097ffcc9e52dcf39d64f25cf503c3c9ffc806f55c42b60e452845d5`.
- CUDA image:
  `sha256:df0f30ac1bed4514d50c5b11eeac4ea64e38e6575bb209448fea4c53e5347890`.

## Results credited

The reviewed extracts substantiate Docker CPU, Docker CUDA, Podman CPU, and
Podman CUDA operation on the separate Windows NVIDIA host. They bind exact
browser downloads, downloaded-file markers, internal checksums, intended
devices, positive YOLO and EfficientNet work, both configured providers,
real-browser searches and separate exports, cancellation/retry, controlled
errors, eight named volumes per profile, stop/relaunch, and reboot.

Repeated live searches used the same public NYC area. HTTP results consistently
reported 48 Azure detections and 40 Google detections with matching confidence
fingerprints across profiles and lifecycle checkpoints. Secondary scores were
present on all detections. This is substantive comparative application evidence.
The visible Edge driver also exercised both provider maps, real detections,
downloads, and cancellation; browser automation is recorded as the method.

**Owner clarification, October 16**: The owner confirms that dataset download
and restore were thoroughly tested on the independent host and worked as
expected. Credit this as an owner-confirmed functional pass, supplementing the
report's contrary "not covered" entry. Preserve that provenance rather than
asserting that the supplied archive contains restore-driver output.

The owner also confirms that the same NYC area was used for the model tests
to make the results comparable. Credit that method and the supporting live
results. The frozen-fixture combined probe and warm-median benchmark are a
distinct method; their independent-host reports are not present in this packet.
That evidence-method distinction does not negate the observed real-model work.
The clarification does not claim a new benchmark result or amend ADR-022/v2
acceptance. Reconcile any remaining formal evidence requirement in closeout;
do not infer that the live-model tests or dataset restore were unperformed.

## Findings retained for disposition

- **N9**: Podman provider installation failed at the original longer path and
  succeeded after copying verified downloads to a shorter path with spaces.
  The reported 86-character package-path limit is specific to that host and
  interpreter. A supported short-path restriction or a code correction still
  needs explicit disposition before a clean ordinary-installation claim.
- **N14**: Both hosts selected Python 3.12 through the existing `-Python` option;
  the shipped guides omit that selection procedure.
- **N1**: Geocoding-limit display text is in a function without an active
  workflow call. Record a known issue or correct it; do not call F8 fully
  exercised based on an unused message.
- Other reported UI, staging, and host-transport findings remain available in
  the source report. Large browser dataset downloads passed despite a separate
  connection-closing HTTP-client/WSL relay failure.
- Normal engine switches passed. The independent host's post-login collision
  recovery was not reproduced; first-host recovery evidence remains separate.

This intake credits completed functional testing while preserving the source
report, owner clarification, evidence methods, and unresolved dispositions.
It does not close Task-105 or authorize publication, stable/Latest promotion,
or expansion to CPU-only hardware or Podman without Docker Desktop installed.

**October 19 closeout**: The
[qualification record](RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md) consolidates
dispositions and the unchanged public-byte recheck.
[ADR-026](../../../decisions/026-rc5-bounded-candidate-acceptance.md) records
the explicit test-method exception and short-path/Python support boundary.
The owner approved reviewed commit `33bd3a3` on October 19; this intake's
measurements and owner-confirmation provenance are preserved. The approved
exception does not invent an independent-host benchmark result.
