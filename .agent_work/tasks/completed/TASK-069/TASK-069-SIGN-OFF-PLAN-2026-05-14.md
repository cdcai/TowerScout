# TASK-069 Sign-Off Plan

**Date**: 2026-05-14
**Status**: SIGN_OFF_RECORDED
**Release Track**: `agpl-yolo`
**Scope**: Controlled-distribution Sprint 06 RC/pilot release posture, not final public open-source approval.

## Recommended Sign-Off Phrasing

Task-069 sign-off is sufficient to merge PR #11 as the Sprint 06 controlled-distribution, AGPL-governed YOLO-enabled RC planning and compliance baseline. This approval is scoped to the near-term RC path and is not final public open-source release approval.

The RC package is not Apache-2.0-only because the current TowerScout detection path includes or depends on Ultralytics/YOLOv5 components and YOLO-derived detector weights.

Therefore, the release control package must carry AGPL-aware license text, third-party notices, model/data terms, provider terms, source-location/source-offer information, release manifest metadata, checksums, image/source identification, SBOM-reference information, and revocation notes. The container image must carry generic compliance notices and OCI labels sufficient to match it to the release control package by pinned digest.

ONNX or other non-Ultralytics runtime migration is not a pre-RC blocker under this sign-off.

Formal owner/legal/reviewer approval remains a later gate for broader distribution, model/data/provider publication, the clean curated public release line, and the final decision on whether the public release remains AGPL-governed with the YOLO path included or moves to a permissive Apache-compatible posture through runtime replacement or separately approved licensing.

## Public Release Line Plan

The longer-term public release plan should use a clean curated public release line rather than publishing the current working repository history as-is.

The current repository should remain the development/workshop repo. The public line should include only approved source code, public-safe documentation, tests, release scripts, license/notice files, and intentionally selected decision records.

Internal planning material, broad `.agent_work/` history, model weights, raw data assets, scratch artifacts, and ambiguous third-party or historical content should be excluded unless explicitly reviewed and approved.

This clean-line approach reduces public-release risk, makes the repository easier for outside developers to understand, and gives legal/owner reviewers a clear surface to approve before broader publication.

## Sign-Off Boundary

This sign-off plan authorizes the Sprint 06 team to keep moving toward a controlled AGPL-aware RC/pilot package without treating ONNX/runtime replacement as a pre-RC blocker. It does not authorize any of the following by itself:

- final public open-source release
- Apache-2.0-only claims for the YOLO-enabled package/image
- public publication of model weights or raw data assets without confirmed terms
- publication of the current development repository history as-is
- waiver of provider/API key terms or user-side provider obligations

## PR #11 Merge Boundary

- PR #11 may be merged as the internal Sprint 06 RC planning and compliance baseline after normal technical review and repository checks.
- Merging PR #11 does not approve final public open-source publication, broader distribution, model/data/provider publication, or Apache-2.0-only release claims.
- The release control package/image metadata split must remain clear:
  - release control ZIP is authoritative for release-specific source ref, image digest, checksums, manifest, SBOM reference, and revocation notes
  - container image carries generic compliance notices and OCI labels
- `TASK-071`, `TASK-066`, and `TASK-073` must use the `agpl-yolo` RC framing.
- Public-release planning must treat clean-line publication as a later release-governance task, not an implied result of merging PR #11.

## Later Release And Publication Gates

- Formal owner/legal/reviewer approval before broader distribution or public release.
- Model/data/provider approvals before publishing assets, expanding distribution, or opening the clean public release line.
- Clean-machine RC validation under `TASK-066`.
- Public release-line decision after RC evidence and rights review.
- Later permissive Apache-compatible runtime path only if the team chooses ONNX, another non-Ultralytics runtime, or separately approved licensing.
