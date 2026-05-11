# TASK-072: Release Asset Bundle Contract

**Status**: NOT_STARTED  
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

**R-072-007**: WHEN restricted-network or offline support is considered, THE PROJECT SHALL either keep it explicitly out of this task and route it to `TASK-070`, or document the limited fallback that V1 RC1 will support.

## Acceptance Criteria

- [ ] The V1 RC1 asset bundle layout is documented.
- [ ] Required model assets are mapped to `webapp/asset_manifest.v1.json`.
- [ ] Required ZIP-code data assets are mapped to `webapp/asset_manifest.v1.json`.
- [ ] Asset naming/versioning rules are defined.
- [ ] Asset checksum verification expectations are defined for release-candidate validation and normal end-user import.
- [ ] The relationship between GitHub Release control ZIP, GHCR image digest, and asset bundle is explicit.
- [ ] Distribution/provenance notes are documented for each asset class.
- [ ] Restricted-network handling is either deferred to `TASK-070` or explicitly scoped for V1 RC1.
- [ ] Follow-on documentation requirements are handed to `TASK-071`.

## Dependencies

- `TASK-065`: Release packaging and runtime support follow-through.
- `webapp/asset_manifest.v1.json`: current manifest source of truth for required runtime assets.
- `docs/oci-quick-start.md`: current user-facing asset import guidance.
- `docs/oci-runtime-contract.md`: current container/runtime asset contract.
- `scripts/import-assets.cmd` and `scripts/import-assets.ps1`: current asset import mechanism.
- `TASK-069`: license/release policy review for any redistribution uncertainty.

## Implementation Plan

1. Inventory the current asset manifest and release package guidance.
2. Define the expected asset bundle folder layout for V1 RC1.
3. Define the bundle naming/versioning convention and release matching rules.
4. Define checksum and manifest verification expectations.
5. Document model weight provenance and ZIP-code data provenance.
6. Decide whether this task covers any restricted-network fallback or routes that entirely to `TASK-070`.
7. Update or create the durable asset contract artifact under `.agent_work/context/guides/` or `docs/`, depending on whether it is user-facing release documentation or internal planning material.
8. Hand off doc requirements to `TASK-071`.

---

## Implementation Log

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
**Test Date**: Pending  
**Test Environment**: Pending  
**Test Status**: NOT_STARTED

### Acceptance Criteria Validation
- [ ] Asset layout documented - PENDING
- [ ] Manifest mapping verified - PENDING
- [ ] Versioning rules defined - PENDING
- [ ] Checksum policy defined - PENDING
- [ ] Distribution/provenance notes documented - PENDING

### Issues Identified

None yet.

### Remediation Actions

None yet.

### Sign-off

Pending implementation and validation.
