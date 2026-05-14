# TASK-069: AGPL YOLO Release Implementation Update

**Status**: SIGN_OFF_RECORDED
**Date**: 2026-05-13
**Release Track**: `agpl-yolo`
**Purpose**: Reviewer feedback package and Sprint 06 implementation alignment, not final legal approval.
**Sign-Off Plan**: `TASK-069-SIGN-OFF-PLAN-2026-05-14.md`

## Decision Update

Sprint 06 is now modeled as a YOLO-enabled AGPL-compliant RC/pilot path. The ONNX or other non-Ultralytics detector runtime migration is no longer a pre-RC blocker. It moves to a later permissive Apache-only release or runtime modernization track.

TowerScout-authored code may be Apache-2.0 where ownership and relicensing authority are confirmed, but the full YOLO-enabled package/image is not Apache-2.0-only because it includes Ultralytics YOLOv5 AGPL-3.0 source and YOLO-derived detector weights.

## Implementation Requirements

- Replace any current-release `YOLO | MIT` attribution with `Ultralytics YOLOv5 | AGPL-3.0`.
- Include corrected compliance files in the release control package, with generic notices and OCI labels in the image:
  - `LICENSE`
  - `NOTICE`
  - `THIRD_PARTY_NOTICES.md`
  - `MODEL_LICENSES.md`
  - `DATA_LICENSES.md`
  - `PROVIDER_TERMS.md`
  - `SOURCE.txt`
  - `SBOM.txt`
  - `release-manifest.v1.json`
  - `IMAGE.txt`
  - `SHA256SUMS.txt`
- Provide matching corresponding source for each release package/image, including TowerScout source, vendored YOLO source, local YOLO patches, Docker/Compose files, scripts, requirements, and build/run instructions. The generated release control ZIP is authoritative for release-specific source ref, image digest, checksums, manifest, and SBOM-reference metadata.
- Label YOLO detector weights as YOLO-derived/AGPL-governed unless separate written model terms say otherwise.
- Keep provider API/key terms separate from application and YOLO licensing.
- Expose source/license location in docs and the local web UI.

## Sprint 06 Path Change

- `TASK-069` is active Sprint 06 work.
- `TASK-071`, `TASK-066`, and `TASK-073` remain in the committed lane, but they now validate a YOLO-enabled AGPL-compliant package.
- `TASK-072` remains completed but its publication language is revised for the `agpl-yolo` posture.
- A narrow `TASK-077` slice is pulled forward for release manifest, source ref, checksums, image digest, SBOM reference, model/data terms, and revocation notes.
- `TASK-076` remains near-active because AGPL does not resolve browser-visible provider key/API terms.
- ONNX/non-Ultralytics runtime migration moves to a later permissive Apache-only release track.

## Validation Plan

- Inspect the generated release package for compliance files, release manifest, image digest, source notice, SBOM reference, model/data/provider terms, and checksums.
- Scan release docs and notices to confirm YOLO is not labeled MIT and vendored YOLO is listed as AGPL-3.0.
- Confirm the source ref in generated `SOURCE.txt` and `release-manifest.v1.json` matches the release ZIP and image digest, and confirm release packaging rejects missing source refs or dirty trees unless explicit local-validation overrides are used.
- Run the existing clean Windows package validation, asset import, setup wizard, restart persistence, and bounded detection smoke during `TASK-066`.
- Review UAT docs so testers understand the release is controlled/AGPL-compliant and provider/API terms remain separate.

## Fallback

If reviewers reject AGPL as the public release posture, revert to the prior plan: restricted pilot now, and ONNX or another non-Ultralytics runtime replacement before any public Apache-compatible release claim.

## Sign-Off Alignment - 2026-05-14

Task-069 sign-off is sufficient to merge PR #11 as the Sprint 06 controlled-distribution AGPL-governed YOLO-enabled RC planning and compliance baseline. It is not final public open-source release approval.

The release control ZIP is authoritative for release-specific source ref, image digest, checksums, release manifest, SBOM reference, and revocation notes. The container image carries generic compliance notices and OCI labels sufficient to match it to the control package by pinned digest.

The public release path should use a clean curated public release line rather than publishing the current development repository history as-is. The development/workshop repo can continue to carry internal planning material and historical context; the public line should include only reviewed source, public-safe documentation, tests, release scripts, license/notice files, and intentionally selected decision records.

Formal owner/legal/reviewer approval remains a later gate for broader distribution, model/data/provider publication, and the clean curated public release line.

## PR #11 Review Follow-Up - 2026-05-14

The first PR #11 review agreed with the `agpl-yolo` direction but requested consistency fixes before merge readiness. The follow-up implementation addresses those review comments without reintroducing ONNX as a Sprint 06 blocker:

- Removed the active root `LICENSE.TXT` conflict and replaced it with `docs/legacy/LEGACY-LICENSE-NOTICE.md`.
- Clarified that the generated release control ZIP is authoritative for release-specific source ref, image digest, checksums, SBOM-reference, and manifest metadata; the image carries generic notices and OCI labels.
- Expanded `/license` to include `SOURCE.txt`, `SBOM.txt`, `release-manifest.v1.json`, and the vendored YOLOv5 AGPL license text.
- Hardened `scripts/package-release.ps1` so normal release packaging requires a git source ref and clean working tree, with explicit local-validation overrides.
- Aligned the checked-in and generated `release-manifest.v1.json` structure and added schema/static tests for compliance payload drift.
- Updated `.github/workflows/container-publish.yml` so published images populate release-version and source-ref OCI labels from the workflow tag and `GITHUB_SHA`.

Validation for this follow-up should include the targeted unit tests, PowerShell package-script parser check, `.agent_work` validation, and `git diff --check`.
