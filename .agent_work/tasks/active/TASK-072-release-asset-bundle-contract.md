# TASK-072: Release Asset Bundle Contract

**Status**: COMPLETED
**Priority**: CRITICAL  
**Type**: C (Release Engineering / Asset Governance)  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  

## Objective

Define the release asset bundle contract for TowerScout's out-of-repo runtime assets so a non-technical pilot user can obtain, place, import, and verify the model weights and ZIP-code data required for V1 RC1.

This task must settle the asset bundle before end-user package documentation and clean-machine validation are finalized.

## Requirements (EARS Notation)

**R-072-001**: WHEN a V1 RC1 release package is prepared, THE PROJECT SHALL define the exact asset bundle layout expected next to or inside the release-candidate package.

**R-072-002**: WHEN model weights are distributed for V1 RC1, THE PROJECT SHALL document the expected filenames, relative paths, sizes, checksums, and source/provenance for each required model file.

**R-072-003**: WHEN ZIP-code boundary data is distributed for V1 RC1, THE PROJECT SHALL document the expected folder name, required shapefile components, sizes, checksums, and source/provenance.

**R-072-004**: WHEN an asset bundle is matched to a TowerScout release, THE PROJECT SHALL provide a versioning or naming convention that lets support identify whether the bundle belongs to the release package.

**R-072-005**: WHEN assets are imported with `scripts/import-assets.cmd`, THE PROJECT SHALL define which verification mode is required for release-candidate validation and which mode is normal for end users.

**R-072-006**: IF asset redistribution rights or source ownership are unclear, THEN THE PROJECT SHALL record the uncertainty and route it to release policy review before external distribution.

**R-072-011**: WHEN the AGPL-compliant YOLO release path is selected, THE PROJECT SHALL label YOLO detector weights as YOLO-derived/AGPL-governed unless separate written model terms say otherwise.

**R-072-007**: WHEN restricted-network or offline support is considered, THE PROJECT SHALL either keep it explicitly out of this task and route it to `TASK-070`, or document the limited fallback that V1 RC1 will support.

**R-072-008**: WHEN the V1 RC1 asset ZIP is published, THE PROJECT SHALL define the ZIP root layout, the post-extraction staged source layout, and the container runtime destination layout without requiring an extra nested `assets/` directory inside the ZIP.

**R-072-009**: WHEN the asset ZIP is published, THE PROJECT SHALL include or explicitly account for an asset manifest copy that can be compared to the control ZIP manifest by `manifest_version` and, during release/support validation, manifest file hash.

**R-072-010**: WHEN the asset ZIP checksum is published, THE PROJECT SHALL define the sidecar checksum filename and line format so release automation and support can verify the complete ZIP consistently.

## Acceptance Criteria

- [x] The V1 RC1 asset bundle layout is documented.
- [x] Required model assets are mapped to `webapp/asset_manifest.v1.json`.
- [x] Required ZIP-code data assets are mapped to `webapp/asset_manifest.v1.json`.
- [x] Asset naming/versioning rules are defined.
- [x] The asset ZIP root layout is defined as `model_params/`, `data/`, and `asset_manifest.v1.json`.
- [x] The post-extraction staged source layout is defined as `assets/model_params/...`, `assets/data/...`, and `assets/asset_manifest.v1.json`.
- [x] The runtime import destination is defined as `/app/webapp/model_params/...` and `/app/webapp/data/...`.
- [x] Asset checksum verification expectations are defined for release-candidate validation and normal end-user import.
- [x] The asset ZIP `.sha256` sidecar format is defined.
- [x] Asset/control manifest mismatch behavior is documented, including which checks are currently automated and which remain release-validation contract checks.
- [x] The relationship between GitHub Release control ZIP, GHCR image digest, and asset bundle is explicit.
- [x] Distribution/provenance notes are documented for each asset class.
- [x] External publication of the asset ZIP is conditioned on the accepted `agpl-yolo` release posture and documented model terms, with fallback to restricted pilot or bring-your-own-assets if reviewers reject AGPL.
- [x] Restricted-network handling is either deferred to `TASK-070` or explicitly scoped for V1 RC1.
- [x] Typed import exit codes and direct-ZIP path traversal protections are recorded as follow-up scope unless importer behavior is intentionally expanded.
- [x] Public-release staged allowlist import, release manifest, and revocation mechanics are recorded as follow-up scope.
- [x] Follow-on documentation requirements are handed to `TASK-071`.

## Dependencies

- `TASK-065`: Release packaging and runtime support follow-through.
- `webapp/asset_manifest.v1.json`: current manifest source of truth for required runtime assets.
- `docs/oci-quick-start.md`: current user-facing asset import guidance.
- `docs/oci-runtime-contract.md`: current container/runtime asset contract.
- `scripts/import-assets.cmd` and `scripts/import-assets.ps1`: current asset import mechanism.
- `TASK-069`: license/release policy review for the AGPL-compliant YOLO release posture and model/data publication terms.

## Implementation Plan

1. Inventory the current asset manifest and release package guidance.
2. Define the canonical V1 RC1 asset ZIP root as:
   ```text
   model_params/
   data/
   asset_manifest.v1.json
   ```
3. Define the user staging workflow: users extract the asset ZIP contents into the release package's `assets/` directory, producing:
   ```text
   assets/model_params/
   assets/data/
   assets/asset_manifest.v1.json
   ```
4. Preserve the current importer source-root contract: `scripts/import-assets.cmd -Source assets` treats `assets/` as the staged source directory and expects `model_params/` and `data/` directly below it.
5. Define the runtime import destination as the container asset layout under `/app/webapp/model_params/` and `/app/webapp/data/`; the importer copies from the staged source into container volumes, not into another local package directory.
6. Define the bundle naming/versioning convention and release matching rules:
   - Asset ZIP pattern: `towerscout-<release-version>-assets-<manifest-version>.zip`.
   - Example: `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip`.
   - The control ZIP release version and asset ZIP release version must match.
   - The control ZIP `webapp/asset_manifest.v1.json` remains authoritative.
   - The asset ZIP manifest copy is used for identity/provenance matching by `manifest_version` and, during release/support validation, manifest file hash.
7. Define checksum and manifest verification expectations:
   - Normal user import: `scripts/import-assets.cmd -Source assets`; required files and byte sizes are verified, hashes are not checked.
   - Release-candidate/support import: `scripts/import-assets.cmd -Source assets -VerifyHashes`; required files, byte sizes, and SHA-256 hashes are verified.
   - Runtime/readiness hash verification: `TOWERSCOUT_VERIFY_ASSET_HASHES=1` is validation/support-only and should not be routine first-run behavior because the ZIP-code geometry file is large.
   - Asset ZIP sidecar format: `<lowercase-sha256-hex>  towerscout-<release-version>-assets-<manifest-version>.zip`.
8. Document mismatch behavior as contract expectations while distinguishing currently automated checks from release-validation/manual checks:
   - Required asset missing: automated import/readiness failure.
   - Required asset size mismatch: automated import/readiness failure.
   - Required asset hash mismatch under `-VerifyHashes` or `TOWERSCOUT_VERIFY_ASSET_HASHES=1`: automated failure.
   - Optional asset missing: reported as `optional_missing` without blocking import when all required assets pass.
   - Release version mismatch, manifest version mismatch, and asset ZIP manifest differing from the control ZIP manifest: release/support validation failures unless importer behavior is intentionally expanded to enforce them directly.
9. Document model weight provenance and ZIP-code data provenance.
10. Treat external publication of the asset ZIP as allowed only when `TASK-069` confirms the `agpl-yolo` release posture and the model notices label YOLO weights as YOLO-derived/AGPL-governed unless separate written model terms say otherwise.
11. Keep typed importer exit codes and direct-ZIP path traversal protections as follow-up scope unless `TASK-072` is intentionally expanded into importer behavior. If future importer work accepts ZIP files directly, it must reject unsafe archive entries such as `..\`, absolute paths, and paths escaping the extraction root.
12. Keep public-release staged allowlist import as follow-up scope unless `TASK-066` shows it is release-critical. Pull the narrow release manifest, source notice, SBOM reference, checksums, image digest metadata, model/data terms, and revocation notes into the AGPL-compliant RC payload.
13. Decide whether this task covers any restricted-network fallback or routes that entirely to `TASK-070`.
14. Update or create the durable asset contract artifact under `.agent_work/context/guides/` or `docs/`, depending on whether it is user-facing release documentation or internal planning material.
15. Hand off doc requirements to `TASK-071`.

---

## Implementation Log

### 2026-05-11 - Durable Asset Contract Completed
**Objective**: Create the durable V1 RC1 asset bundle contract and make it available in the release control package.
**Context**: `TASK-071` needs a stable asset contract before package-based end-user docs can be written, and `TASK-066` needs explicit release-validation rules for matching the control ZIP, GHCR digest, asset ZIP, manifest, and checksums.
**Decision**: Add the contract under `docs/` so release packages include it with the quick start and runtime contract. Keep the asset ZIP as an extracted-directory workflow rather than changing importer behavior. Treat external asset ZIP publication as governed by the `TASK-069` controlled-RC sign-off for the Sprint 06 RC path, with broader/public asset publication still gated by model/data/provider approvals or a documented bring-your-own-assets alternative.
**Execution**: Added `docs/release-asset-bundle-contract.md`, updated `scripts/package-release.ps1` to include it, updated `docs/oci-quick-start.md` and `docs/oci-runtime-contract.md` to reference the corrected ZIP/staged/runtime layouts, and added a package-release test assertion that the contract doc is staged.
**Output**: The V1 RC1 contract now defines artifact names, asset ZIP root layout, staged `assets/` layout, runtime destination, manifest authority and mismatch policy, required/optional asset tables, normal versus validation import modes, `.sha256` sidecar format, distribution/provenance notes, restricted-network scope, and follow-up boundaries.
**Validation**: `python .agent_work/scripts/validate_agent_work.py`, `git diff --check`, and `.\.venv\Scripts\python.exe -m pytest tests\unit\test_release_package_script.py -q -p no:cacheprovider` passed after whitespace cleanup.
**Next**: Start `TASK-071` end-user release package documentation against `docs/release-asset-bundle-contract.md`.

### 2026-05-13 - Final Roadmap Alignment Pass
**Objective**: Align the completed Task-072 contract with the May 13 final roadmap review without expanding the task into public-release importer implementation.
**Context**: Final roadmap review confirmed the restricted pilot path can continue, but public release still needs separate governance, allowlist import, release manifest, and revocation work. Review also found a mismatch between the contract's normal import command and the generated package asset README.
**Decision**: Keep Task-072 scoped to the V1 RC1 restricted-pilot asset contract. Tighten the contract to say the asset ZIP is restricted-pilot/support-supplied unless redistribution is approved, fix normal user import guidance to omit `-VerifyHashes`, and record staged allowlist import plus release manifest/revocation mechanics as follow-up public-release scope.
**Execution**: Updated `docs/release-asset-bundle-contract.md`, `scripts/package-release.ps1`, and this task file.
**Output**: The contract now separates restricted-pilot asset packaging from public redistribution, the generated asset README matches the documented import policy, and public-release asset hardening is explicitly handed off.
**Validation**: `git diff --check`, `python .agent_work/scripts/validate_agent_work.py`, and `.\.venv\Scripts\python.exe -m pytest tests\unit\test_release_package_script.py -q -p no:cacheprovider` passed.
**Next**: Continue `TASK-071` package documentation using the tightened restricted-pilot/public-release boundary.

### 2026-05-11 - Assessment Feedback Incorporated Into Plan
**Objective**: Update the `TASK-072` task plan with the corrected asset ZIP layout, contract invariants, verification policy, and follow-up boundaries from assessment review.
**Context**: Follow-up review found that an earlier recommendation to put a top-level `assets/` directory inside the asset ZIP would conflict with the current `scripts/import-assets.ps1` source-root contract. The importer expects the `-Source` directory to contain `model_params/` and `data/` directly, and the package docs already instruct users to run `scripts/import-assets.cmd -Source assets`.
**Decision**: Preserve the current importer behavior and define the asset ZIP root as `model_params/`, `data/`, and `asset_manifest.v1.json`. Users extract those contents into the release package `assets/` directory, then import from that staged source. Retain the high-value assessment recommendations for manifest copy, checksum sidecar format, mismatch policy, and `TASK-069` redistribution gating. Keep typed exit codes and direct-ZIP extraction security as follow-up scope unless importer behavior is intentionally expanded.
**Execution**: Updated requirements, acceptance criteria, and implementation plan in this task file to distinguish asset ZIP root layout, staged source layout, runtime destination layout, automated verification behavior, release-validation contract checks, and follow-up boundaries.
**Output**: `TASK-072` now records the corrected contract baseline: asset ZIP root contains `model_params/`, `data/`, and `asset_manifest.v1.json`; staged release package source is `assets/model_params/...`, `assets/data/...`, and `assets/asset_manifest.v1.json`; runtime destination is `/app/webapp/model_params/...` and `/app/webapp/data/...`.
**Validation**: `python .agent_work/scripts/validate_agent_work.py` passed after this documentation update.
**Next**: Validate `.agent_work` structure, then draft the durable V1 RC1 asset contract artifact and hand off package-doc requirements to `TASK-071`.

### 2026-05-11 - Initial Asset And Import Inventory
**Objective**: Inventory the current manifest, package guidance, and import verification behavior before drafting the V1 RC1 asset bundle contract.
**Context**: `TASK-072` depends on the existing container release package shape from `TASK-065`, the manifest-backed runtime readiness checks, and the current `scripts/import-assets.*` helpers.
**Decision**: Treat `webapp/asset_manifest.v1.json` as the authoritative runtime asset list for the first contract draft, then use the docs/import helpers to define user-facing bundle placement and verification modes.
**Execution**: Reviewed `webapp/asset_manifest.v1.json`, `scripts/import-assets.cmd`, `scripts/import-assets.ps1`, `scripts/package-release.ps1`, `webapp/ts_assets.py`, `docs/oci-quick-start.md`, and `docs/oci-runtime-contract.md`.
**Output**: Current manifest `towerscout-v1-assets-2026-05-05` defines 9 assets: 2 required model assets totaling 293,651,732 bytes and 7 ZIP-code data assets totaling 825,737,459 bytes. ZIP-code data includes 5 required shapefile components (`.cpg`, `.dbf`, `.prj`, `.shp`, `.shx`) and 2 optional metadata XML files. The package script stages an empty `assets/README.txt`; the importer requires a source root containing `model_params/` and `data/`, copies those directories into the selected engine's named volumes, and verifies manifest status inside the container. Normal import verifies presence and byte size; `-VerifyHashes` enables SHA-256 checks for release-candidate/support validation.
**Validation**: `.agent_work/scripts/validate_agent_work.py` passed before this inventory log. Follow-up validation required after this log entry.
**Next**: Draft the durable V1 RC1 asset bundle contract, including bundle naming/versioning, release matching rules, provenance notes, and verification expectations.

### 2026-05-11 - Task Intake Started
**Objective**: Start `TASK-072` after `TASK-065` owner acceptance.
**Context**: `TASK-065` is complete, so the next Sprint 06 dependency is the release asset bundle contract. `TASK-071` end-user docs and `TASK-066` release-candidate validation both depend on this task defining the model/data bundle shape, checksums, provenance notes, and import verification expectations.
**Decision**: Begin with an inventory of `webapp/asset_manifest.v1.json`, existing OCI asset guidance, and `scripts/import-assets.*` behavior before writing or changing the durable asset contract.
**Execution**: Updated `TASK-072` status to `IN_PROGRESS` in this task file and `.agent_work/current-tasks.md`.
**Output**: `TASK-072` is formally started and ready for analysis/inventory work.
**Validation**: Documentation validation to be run after the intake update.
**Next**: Inventory the manifest, current package docs, and import helper behavior.

### 2026-05-11 - Task Created
**Objective**: Create detailed Sprint 06 task documentation for the release asset bundle contract.  
**Context**: Sprint 06 planning identified the asset bundle contract as the first committed-lane task because package docs and meaningful user testing depend on knowing exactly what external files users receive and where they go.  
**Decision**: Keep this task focused on defining the V1 RC1 asset contract and routing broader restricted-network enhancement work to `TASK-070` unless it becomes a launch requirement.  
**Execution**: Created `.agent_work/tasks/active/TASK-072-release-asset-bundle-contract.md` and synchronized the task with `current-tasks.md`.  
**Output**: Task file ready for intake.  
**Validation**: Pending `.agent_work` validation after all Sprint 06 task files are created.  
**Next**: Start inventory of `webapp/asset_manifest.v1.json`, current OCI docs, and import helper behavior.

---

## Validation Results

### Test Summary
**Test Date**: 2026-05-11; alignment validation updated 2026-05-13
**Test Environment**: Windows workspace, PowerShell, branch `feature/task-072-asset-bundle-contract`
**Test Status**: PASS after final validation

### Acceptance Criteria Validation
- [x] Asset layout documented - PASS: `docs/release-asset-bundle-contract.md`
- [x] Manifest mapping verified - PASS: required and optional assets are mapped from `webapp/asset_manifest.v1.json`
- [x] Versioning rules defined - PASS: asset ZIP naming and release/manifest matching rules are documented
- [x] Checksum policy defined - PASS: normal import, `-VerifyHashes`, runtime hash verification, and ZIP sidecar format are documented
- [x] Asset ZIP root layout documented - PASS: `model_params/`, `data/`, and `asset_manifest.v1.json`
- [x] Post-extraction staged source layout documented - PASS: `assets/model_params/...`, `assets/data/...`, and `assets/asset_manifest.v1.json`
- [x] Runtime destination layout documented - PASS: `/app/webapp/model_params/...` and `/app/webapp/data/...`
- [x] Manifest-copy rule documented - PASS: asset ZIP manifest copy is used for release/support identity checks while control manifest remains authoritative
- [x] Mismatch policy documented - PASS: automated checks versus release/support validation failures are separated
- [x] `.sha256` sidecar format documented - PASS
- [x] Redistribution release gate documented - PASS: controlled-RC publication follows the `TASK-069` sign-off boundary; broader/public publication remains gated by model/data/provider approvals or a bring-your-own-assets alternative
- [x] Follow-up boundaries for typed exit codes and direct-ZIP extraction recorded - PASS
- [x] Public-release staged allowlist import and release manifest/revocation follow-up boundaries recorded - PASS
- [x] Distribution/provenance notes documented - PASS

### Issues Identified

External asset ZIP publication is governed by the `TASK-069` sign-off boundary. This is no longer a PR #11 merge blocker for the controlled RC baseline, but broader/public asset publication remains a later model/data/provider approval gate.

### Remediation Actions

None yet.

### Sign-off

Completed for Sprint 06 asset-contract purposes. `TASK-071` should now write end-user package docs against `docs/release-asset-bundle-contract.md`.
