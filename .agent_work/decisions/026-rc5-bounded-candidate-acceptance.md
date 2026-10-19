# ADR-026: RC5 Bounded Candidate Acceptance

**Status**: Accepted
**Prepared**: October 19, 2026
**Accepted**: October 19, 2026, owner approval of reviewed commit `33bd3a3`
**Decision owner**: `J-Schulein`; official adoption remains with the project lead and cdcai owner
**Scope**: Exact fork candidate `v0.1.3-rc5` and its supplemental operating instructions

## Decision

Accept the completed first-host and independent-host functional testing for
the exact RC5 identities in the [closeout record](../tasks/active/TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md),
subject to the explicit restrictions and evidence substitutions below. Preserve
RC5's published images, ZIPs, sidecars, and tag. Supplement its shipped manuals
with the [RC5 operations addendum](../../docs/release/rc5-operations-addendum.md).

After confirming independent-host dataset restore and same-area NYC model
comparisons, the owner explicitly approved this decision in reviewed commit
`33bd3a3`: "Approve bounded RC5 acceptance." The stated method exceptions,
installation restrictions, and known-issue dispositions are therefore accepted
for this fork candidate. Task-105 continues through review, official adoption,
official-byte qualification, and handoff.

## Test-method reconciliation

1. Credit four actual Docker/Podman CPU/CUDA profiles on each of the two
   ADR-025 Windows NVIDIA hosts. Preserve exact downloads, devices, both
   models, providers, export/cancel/recovery, lifecycle, and reboot evidence.
2. Credit independent-host dataset download/restore as **owner-confirmed
   passed on October 16**. The report's "not covered" entry is supplemented
   by that confirmation; no restore-driver trace is claimed in its archive.
3. For this candidate, accept the first host's frozen 12-tile combined probe,
   expected outputs, both model devices, and warm measurements together with
   the independent host's real Google/Azure same-area comparisons and device
   evidence. Do not require a second frozen-fixture/warm-benchmark report on
   the independent host. This is a bounded exception to the v2 W10 per-profile
   probe requirement and ADR-022's qualification-method rule, not a claim that
   live imagery is frozen or that the retired HTTP harness is the formal probe.
4. Carry the first host's exact-image CUDA-unavailable negative and controlled
   classifier-failure/clean-follow-up proof forward. The independent host's
   recoverable HTTP/provider errors and next-request success remain separately
   credited. No independent classifier-injection report is claimed.
5. Carry first-host ZIP lookup and managed-TLS repair evidence forward;
   independent-host normal TLS and both providers were exercised. No separate
   independent ZIP-navigation trace, managed-network repair, or post-login
   pipe-collision reproduction is claimed. Normal engine switching passed on
   both hosts; the first host exercised volume-preserving machine recovery.
6. Accept visible Edge automation as real-browser observation for the changed
   export and late-cancel controls. Keep its method distinct from human
   observations. No additional manual-tower editing result is inferred.

This exception supplies no independent warmed-performance comparison, memory
benchmark, or numerical tolerance claim beyond the reports actually retained.
All other model correctness, fail-closed GPU, secret-safety, and security
requirements remain in force. A changed candidate needs a fresh delta review;
this exception does not automatically qualify official cdcai bytes.

## Installation and known-issue dispositions

- **N9, Podman path length**: Accept RC5 only with a short local extraction
  path. The independent installation passed at package-root lengths 57/61
  characters and failed at 108 with default Windows long-path settings. Use
  the addendum's conservative maximum of 80 characters and its short-layout
  examples; that is an operating restriction, not proof of a universal Windows
  limit. If the provider still fails, stop and obtain support. Do not claim the
  original longer-path install passed or change machine-wide policy to pass it.
- **N14, Python**: Support 64-bit Python 3.12 selected explicitly through the
  shipped `-Python` option. The addendum supplies the missing command. Other
  default Python versions remain outside the tested provider prerequisite.
- **N1/F8, display message**: Defer the inactive geocoding-limit display as a
  known issue. Addresses may be absent while coordinates remain available.
  Corrected imagery/geocoding wording is credited; the rate-limit display and
  corrected limit-log provider were not live-exercised.
- Defer the remaining UI, telemetry-label, staging, and host-transport findings
  with the [closeout dispositions](../tasks/active/TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md).
  These are recorded limitations, not assertions that the reported bugs were
  fixed. No unscoped stale-folder deletion is authorized.

## Distribution and ownership boundaries

The addendum and handoff are separately versioned supplemental documents;
they are not present in the immutable RC5 downloads or served Help pages.
They must accompany any newly authorized RC5 distribution. Future official
packages must incorporate equivalent guidance and receive new identities.

ADR-023 unsigned-wrapper exclusions, ADR-024's exact five-key residual policy
and October 31 expiry, and ADR-025's two-host scope remain unchanged. CPU-only
hardware, Podman without Docker Desktop installed, rootful Podman, and
signature-enforcing endpoints remain unqualified.

This decision does not authorize remote pushes, release-note edits, GHCR
publication, cdcai repository mutation, official publication, or Latest
promotion. Those actions retain their existing authorization boundaries.

## Approval record

Owner acceptance: **approved October 19, 2026**, for ADR-026 in reviewed commit
`33bd3a3`, followed by status-only updates recording that decision. The owner
also separately approved publishing the eleven-file documentation/evidence
branch to `J-Schulein/TowerScout` and opening a draft PR. Official adoption,
build/publication, and Latest remain separately authorized actions.
