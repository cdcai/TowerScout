# TASK-069 Open-Source Compliance Strategy

> 2026-05-13 update: This draft is superseded for Sprint 06 by
> `TASK-069-AGPL-YOLO-RELEASE-IMPLEMENTATION-2026-05-13.md` where the team
> chose to seek feedback on a YOLO-enabled `agpl-yolo` RC/pilot path. The ONNX
> runtime migration moves to a later permissive Apache-only release track unless
> reviewers reject AGPL as the release posture.

**Date**: 2026-05-12
**Status**: Draft for reviewer/legal/owner feedback
**Scope**: Licensing, model/runtime separation, and local deployment strategy for TowerScout
**Primary input report**: `C:\Users\bg90\OneDrive - CDC\TS Resources\Planning\Task-069 (Licensing)\TowerScout Local Deployment Strategy Report_2026.05.12.docx`

## Executive Summary

TowerScout can meet the client expectation for an easy GitHub-based local deployment path, but the release strategy needs a clearer open-source compliance boundary before broader distribution.

The reviewed deployment report is directionally correct: the repo already has the right release-package foundation through the Docker/OCI baseline, release ZIP packaging scripts, GHCR image publishing, asset import helpers, readiness checks, and setup wizard. The main adjustment is that the report focuses heavily on the current `CC-BY-NC-SA-4.0` mismatch and local deployment packaging, while the active repo now also has a larger default-runtime licensing issue: TowerScout vendors Ultralytics YOLOv5 AGPL code and requires `ultralytics==8.3.249` in the default detector path.

The recommended target state is:

1. TowerScout-authored application code is relicensed under `Apache-2.0`, subject to contributor/owner approval.
2. Model weights and data assets remain separate runtime assets with their own terms, provenance, hashes, and acceptance records.
3. The default detector runtime no longer vendors or depends on Ultralytics/YOLOv5.
4. The default release path uses a generic ONNX detector adapter and approved model artifacts published as separate GitHub Release assets.
5. End users get a simple flow: download release ZIP, run `start.cmd`, accept model terms, let the bootstrap script download/import verified assets, complete Setup Wizard, and run locally.

This is engineering analysis, not legal advice. A release decision still requires owner/legal sign-off for code relicensing, model asset rights, data redistribution, and provider terms.

## Client Expectation

The client expectation in the prompt is:

> "at the end of the day what i am interested in is creating a way for sites to easily deploy the code from the GITHUB to their laptops, with all of the appropriate folder structure intact, with clear instructions for any other files that are needed, and then a simplified way to set up and run the program locally."

The intended compliance-friendly interpretation should be:

- GitHub remains the public source and release control plane.
- The release ZIP gives sites a complete, predictable application folder structure.
- Required non-code files, especially model weights and ZIP-code data, are clearly identified and acquired/imported under separate terms.
- Setup is script-driven and wizard-assisted, not manual dependency installation.
- Source checkout remains available for developers, but the normal site user path is a GitHub Release package.

## Inputs Reviewed

- Local deployment strategy report dated 2026-05-12.
- Prompt used to create the report.
- Current repo context and Sprint 06 release-readiness plan.
- `README.md`, `LICENSE.TXT`, `package.json`, `Dockerfile`, Compose files, release packaging scripts, asset import scripts, asset manifest, runtime loader code, and current docs.
- Current vendored YOLOv5 runtime metadata and AGPL license text in `webapp/vendor/yolov5_local/`.
- Official license/deployment references:
  - Apache guidance on applying Apache-2.0 and including `LICENSE`/`NOTICE`.
  - Creative Commons guidance recommending against CC licenses for software.
  - OSI Open Source Definition, especially no field-of-endeavor restrictions.
  - Ultralytics licensing page.
  - PyTorch `torch.load` warning for unsafe pickle-backed model loading.
  - GitHub Releases documentation and release asset limits.
  - ONNX Runtime MIT license.

## Current Repo Findings

### What Already Supports The Client Goal

TowerScout is not starting from scratch on deployment. Current repo strengths include:

- `Dockerfile` and Compose baseline.
- `start.bat`, `scripts/launch.ps1`, and support scripts.
- `/api/health` and structured `/api/readiness`.
- Setup Wizard and settings flow for provider keys.
- `scripts/package-release.ps1` to produce a release control ZIP.
- `scripts/import-assets.ps1` for out-of-repo model/data assets.
- `webapp/asset_manifest.v1.json` with required file paths, byte sizes, and SHA-256 hashes.
- Existing docs for OCI quick start, runtime contract, and release asset bundle contract.
- Persistent runtime volumes for config, model assets, data, logs, sessions, uploads, and caches.

This means the deployment work should be a focused productization/compliance effort, not a new deployment architecture.

### Compliance And Policy Gaps

The main gaps are:

- **Conflicting license metadata**: `README.md` and `LICENSE.TXT` state `CC-BY-NC-SA-4.0`, while `package.json` says `MIT`.
- **Non-software license posture**: Creative Commons recommends against CC licenses for software. `CC-BY-NC-SA-4.0` is also noncommercial, which conflicts with normal OSI open-source expectations.
- **AGPL default runtime**: `webapp/vendor/yolov5_local/` vendors Ultralytics YOLOv5 under AGPL-3.0, and the default runtime imports it through `ts_yolov5_local.py`.
- **Ultralytics dependency**: `webapp/requirements.txt` currently pins `ultralytics==8.3.249`.
- **Model asset ambiguity**: The current asset manifest calls the YOLO and EfficientNet weights "TowerScout release asset" but does not include explicit model license terms, source owner, acceptance requirements, or redistribution authority.
- **README asset drift**: Top-level README still points to older external model links and a 2019 Census ZCTA path, while the runtime manifest expects 2025 ZCTA data and exact current filenames.
- **No model terms acceptance flow**: Current asset import verifies presence/size/hash but does not capture user acceptance of model terms.
- **No third-party notice inventory**: Release packages do not yet include complete `NOTICE`, `THIRD_PARTY_NOTICES.md`, or `MODEL_LICENSES.md`.

## Recommended End State

### Licensing Boundary

Use a three-layer distribution model:

1. **Application code**
   TowerScout-authored Python, JavaScript, CSS, templates, scripts, and docs intended as software should be under Apache-2.0, pending contributor/owner approval.

2. **Runtime model/data assets**
   Model weights and ZIP-code data should be separate release assets with independent terms in `MODEL_LICENSES.md` and the asset manifest. They should not be covered by the Apache app license.

3. **Third-party dependencies and services**
   Python, Node, container, map provider SDK/API, Census data, ONNX Runtime, PyTorch, and other third-party components should be inventoried in `THIRD_PARTY_NOTICES.md` and referenced in release docs.

### Default Inference Runtime

The default open-source-compliant runtime should not depend on Ultralytics/YOLOv5 code. The preferred direction is:

- Replace the default YOLOv5-specific loader with a generic detector interface.
- Use ONNX Runtime for the default detector implementation.
- Publish an approved ONNX model artifact as a separate GitHub Release asset.
- Preserve TowerScout's app-facing detection result contract so review/export workflows do not change.

Generic unsafe `.pt` loading should not be the default. PyTorch documents that unsafe `torch.load` paths can execute arbitrary code when loading untrusted pickle-backed files. If PyTorch remains in the runtime, it should be limited to trusted internal weights or safer formats and explicit policy language.

### User-Facing Deployment Flow

The target user flow should be:

1. User downloads `towerscout-<version>.zip` from GitHub Releases.
2. User extracts it to `C:\TowerScout` or another local folder.
3. User runs `start.cmd`.
4. Launcher checks prerequisites and readiness.
5. If assets are missing, launcher starts `scripts/setup-assets.cmd`.
6. Asset setup displays model/data terms from `MODEL_LICENSES.md`.
7. User accepts terms.
8. Script downloads pinned assets from GitHub Releases or imports a local asset bundle.
9. Script verifies SHA-256 and places assets in the runtime storage.
10. App starts and opens at `http://localhost:5000`.
11. Setup Wizard collects Google or Azure provider credentials.
12. User runs detection locally.

Manual folder placement remains a fallback, not the primary user experience.

## Strategy Workstreams

### Workstream 1: Legal/Policy Review

**Goal**: Resolve the release posture before public/pilot claims expand.

Tasks:

- Confirm all TowerScout-authored code can be relicensed under Apache-2.0.
- Decide whether existing docs, notebooks, training artifacts, synthetic data, and marketing site content are also Apache-2.0 or separately licensed.
- Decide whether model weights can be redistributed through GitHub Releases, downloaded by users from an owner-hosted URL, or only manually supplied.
- Decide whether current YOLO-derived weights can be used/converted in a non-Ultralytics default runtime.
- Confirm US Census ZIP-code data redistribution/notice requirements.
- Confirm Google/Azure provider key exposure and ToS guidance.

Deliverables:

- Release policy memo.
- Model asset authorization record.
- Relicensing approval record.
- Explicit go/no-go decision for public release and pilot release.

### Workstream 2: License File And Metadata Cleanup

**Goal**: Make the repo and release package machine-readable and reviewer-readable.

Tasks:

- Replace root `LICENSE.TXT` with Apache-2.0 `LICENSE`, if approved.
- Add `NOTICE`.
- Add `THIRD_PARTY_NOTICES.md`.
- Add `MODEL_LICENSES.md`.
- Fix `package.json` license field to match the approved app license.
- Update source headers from `CC-BY-NC-SA-4.0` to Apache-2.0 in TowerScout-authored files.
- Update README license section.
- Add a release checklist requiring these files in every ZIP and image.

Deliverables:

- Clean license metadata.
- Reviewable notice files.
- Release package includes all required licensing files.

### Workstream 3: Runtime Refactor Away From Ultralytics Default Path

**Goal**: Remove AGPL/Ultralytics from the default release path.

Tasks:

- Delete `webapp/vendor/yolov5_local/`.
- Remove `webapp/ts_yolov5_local.py`.
- Remove `ultralytics` from `webapp/requirements.txt`.
- Remove `YOLO_CONFIG_DIR` from Dockerfile, Compose, `.env.example`, and docs.
- Replace `YOLOv5_Detector` with a generic detector adapter.
- Add ONNX Runtime dependency and implementation.
- Preserve output format consumed by `towerscout.py`, review UI, exports, and tests.
- Rename user-facing language from "YOLOv5 model" to "detector model" where the exact implementation is no longer YOLO-specific.
- Keep any YOLO export/training dataset format language only where it refers to export format, not runtime implementation.

Deliverables:

- Default runtime has no vendored AGPL YOLO source.
- Default dependency set has no `ultralytics`.
- Detection workflow still works with approved ONNX model.

### Workstream 4: Asset Manifest And Terms Acceptance

**Goal**: Enforce the app/assets license boundary.

Tasks:

- Create `asset_manifest.v2.json` or extend the current manifest schema.
- Add fields for:
  - `format`
  - `loader`
  - `license_id`
  - `terms_file`
  - `terms_url`
  - `source_owner`
  - `source_release`
  - `download_url`
  - `requires_acceptance`
  - `accepted_terms_version`
- Update `ts_assets.py` to validate required metadata.
- Add acceptance marker under persisted config, e.g. `webapp/config/model_terms_acceptance.json`.
- Ensure readiness can report:
  - missing assets
  - corrupt assets
  - unaccepted model terms
  - unsupported model format
- Update `scripts/import-assets.ps1` to verify manifest/terms compatibility before import.

Deliverables:

- Assets are traceable, verifiable, and not silently treated as Apache code.
- The app cannot enter `ready` state with unaccepted required model terms.

### Workstream 5: Asset Bootstrap UX

**Goal**: Avoid asking non-technical users to manually manage folders.

Tasks:

- Add `scripts/setup-assets.cmd` and `scripts/setup-assets.ps1`.
- Support two paths:
  - Download approved assets from pinned GitHub Release URLs.
  - Import an already-downloaded local asset ZIP or extracted `assets/` directory.
- Show terms before download/import.
- Verify GitHub release asset SHA-256 against manifest.
- Support proxy/TLS errors with clear remediation.
- Keep manual `scripts/import-assets.cmd -Source assets -VerifyHashes` as fallback.
- Optionally add a Setup Wizard "Assets" step that shows status and starts the bootstrap script or links to instructions.

Deliverables:

- One-command asset setup for connected users.
- Clear fallback for restricted-network sites.
- No model weights in the Apache source repo or default control ZIP.

### Workstream 6: Host-Visible Runtime Folder Profile

**Goal**: Match the client's "folder structure intact" expectation.

Tasks:

- Add `compose.hostdirs.yaml` or equivalent profile.
- Bind-mount:
  - `runtime/config`
  - `runtime/model_params`
  - `runtime/data`
  - `runtime/logs`
  - `runtime/flask_session`
  - `runtime/temp/session`
  - `runtime/uploads`
  - `runtime/cache`
- Update launcher to optionally select named volumes or host-visible folders.
- Document sensitivity of local folders: API keys, session data, addresses, coordinates, logs, cached imagery/provider responses, uploads, and investigation data.

Deliverables:

- Sites can see and support the local folder layout.
- Named volumes remain available for the normal simple path if preferred.

### Workstream 7: Release Packaging And CI Gates

**Goal**: Make compliance enforceable, not only documented.

Tasks:

- Update `scripts/package-release.ps1` to include:
  - `LICENSE`
  - `NOTICE`
  - `THIRD_PARTY_NOTICES.md`
  - `MODEL_LICENSES.md`
  - asset bootstrap scripts
  - updated README/quick start
- Add CI checks that fail when:
  - `ultralytics` is in the default requirements.
  - `webapp/vendor/yolov5_local` exists.
  - root metadata conflicts on license.
  - release package omits required notice files.
  - asset manifest entries lack model license metadata.
- Add release notes template with model terms, asset versions, image digest, checksums, and known limitations.

Deliverables:

- Repeatable compliance release gate.
- Reviewer can verify each release artifact without tribal knowledge.

## Proposed Implementation Phases

### Phase 0: Decision Gate

Do before implementation:

- Confirm Apache-2.0 relicensing authority.
- Confirm model hosting/distribution authority.
- Confirm whether current model weights can be used in the new default runtime.
- Decide whether V1 RC1 pauses for compliance refactor or ships with explicit current-license caveats.

Exit criteria:

- Written owner/legal decision or explicit blocker.

### Phase 1: Documentation And Metadata Remediation

Implement low-risk clarity fixes:

- Fix `package.json` license mismatch.
- Add preliminary `THIRD_PARTY_NOTICES.md` and `MODEL_LICENSES.md`.
- Update README so it no longer presents stale asset instructions.
- Update release asset docs to state assets are separately licensed.

Exit criteria:

- Reviewer can understand current license posture and known blockers.

### Phase 2: Model Asset Governance

Implement asset manifest and terms boundary:

- Add manifest fields for model license and terms.
- Add terms acceptance record.
- Update readiness/import behavior.
- Define GitHub Release asset layout for models and ZIP-code data.

Exit criteria:

- App distinguishes missing/corrupt/unaccepted model assets.

### Phase 3: Runtime Decoupling

Refactor the detector:

- Add generic detector interface.
- Add ONNX Runtime implementation.
- Remove Ultralytics and vendored YOLO from default path.
- Validate detection smoke workflow with approved ONNX model.

Exit criteria:

- Default image and release ZIP have no Ultralytics/YOLO AGPL runtime dependency.

### Phase 4: Release UX

Productize user setup:

- Add asset bootstrap script.
- Add optional Setup Wizard asset status affordance.
- Add host-visible runtime profile.
- Package release ZIP with scripts, notices, docs, and checksums.

Exit criteria:

- Clean Windows laptop can run from GitHub Release ZIP without manual model folder construction.

### Phase 5: Compliance Validation

Validate before pilot:

- Run clean-machine package validation.
- Run dependency/license scan.
- Run release ZIP inspection.
- Run smoke detection.
- Confirm notices and model terms are present.

Exit criteria:

- Written pass/fail recommendation for pilot/UAT.

## Acceptance Criteria

- WHEN a reviewer opens the repo, THE SYSTEM SHALL present a single non-conflicting application license.
- WHEN a release ZIP is built, THE SYSTEM SHALL include `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, and `MODEL_LICENSES.md`.
- WHEN default dependencies are inspected, THE SYSTEM SHALL NOT include `ultralytics`.
- WHEN default source tree is inspected, THE SYSTEM SHALL NOT include `webapp/vendor/yolov5_local`.
- WHEN required model assets are missing, THE SYSTEM SHALL report a degraded/unready asset state with clear recovery instructions.
- WHEN required model terms have not been accepted, THE SYSTEM SHALL not report full readiness.
- WHEN model assets are downloaded or imported, THE SYSTEM SHALL verify expected checksum before activation.
- WHEN a site user runs `start.cmd`, THE SYSTEM SHALL guide them through asset setup and provider setup without manual source-code editing.
- WHEN a release is prepared, THE SYSTEM SHALL pin the runtime image digest and asset checksums.
- WHEN a clean-machine validation is run, THE SYSTEM SHALL prove launch, setup, asset import/download, and one bounded detection workflow.

## Risk Matrix

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Contributor/owner relicensing cannot be approved | Blocks Apache-2.0 target | Keep current license with clearer caveats or split newly authored code only; legal decision required. |
| Current YOLO-derived weights cannot be used in non-Ultralytics runtime | Blocks default detector migration | Retrain/export approved model or obtain explicit license/permission. |
| ONNX model output differs from current YOLOv5 output | Detection quality/regression risk | Build adapter tests and side-by-side validation on known tiles before replacing runtime. |
| Asset downloads fail in restricted networks | User setup blocker | Keep manual asset ZIP import and support-managed preload path. |
| Terms acceptance adds user friction | Setup friction | Make terms display concise and only show on first import or terms version change. |
| Host-visible folders expose sensitive data | Privacy/support risk | Document sensitivity, keep named volumes available, and avoid packaging runtime folders in support bundles. |
| Release package omits notices | Compliance failure | Add CI/release script gate that inspects package contents. |

## Reviewer Questions

1. Does the organization want TowerScout application code under Apache-2.0, or should it remain under a restrictive/noncommercial posture?
2. Who has authority to approve relicensing of historical TowerScout-authored code?
3. Are current model weights owned/controlled in a way that permits GitHub Release distribution?
4. Can current model weights be converted to ONNX and distributed under approved terms?
5. Should the V1 pilot pause for the runtime decoupling work, or ship as a restricted pilot with explicit AGPL/CC caveats?
6. Are GitHub Releases acceptable as the model asset hosting channel for target users?
7. Is the first supported target still Windows 11 AMD64 with Podman/Docker-compatible Compose?
8. Is automatic model download acceptable, or should V1 require manual local asset import?

## Recommended Reviewer Decision

The recommended decision is:

> Proceed with a compliance-focused release architecture that separates Apache-2.0 application code from separately licensed model/data assets, removes Ultralytics/YOLOv5 from the default release path, and provides a guided GitHub Release asset bootstrap flow for local laptop deployment.

This decision best satisfies the client expectation while reducing downstream ambiguity around open-source compliance, model rights, runtime reproducibility, and supportability.

## Source References

### Local Repo References

- `README.md`
- `LICENSE.TXT`
- `package.json`
- `Dockerfile`
- `compose.yaml`
- `.env.example`
- `webapp/requirements.txt`
- `webapp/asset_manifest.v1.json`
- `webapp/ts_yolov5.py`
- `webapp/ts_yolov5_local.py`
- `webapp/vendor/yolov5_local/README.md`
- `webapp/vendor/yolov5_local/LICENSE`
- `docs/oci-quick-start.md`
- `docs/oci-runtime-contract.md`
- `docs/release-asset-bundle-contract.md`
- `scripts/package-release.ps1`
- `scripts/import-assets.ps1`
- `.github/workflows/container-publish.yml`
- `.agent_work/context/status/SPRINT-06-PLAN.md`

### External References

- Apache Software Foundation, "Applying the Apache License, Version 2.0": https://www.apache.org/legal/apply-license
- Creative Commons FAQ, "Can I apply a Creative Commons license to software?": https://creativecommons.org/faq/
- Open Source Initiative, Open Source Definition: https://opensource.org/definition-annotated
- Ultralytics licensing page: https://www.ultralytics.com/license
- PyTorch `torch.load` documentation and unsafe loading warning: https://docs.pytorch.org/docs/stable/generated/torch.load
- GitHub Releases documentation: https://docs.github.com/repositories/releasing-projects-on-github/about-releases
- ONNX Runtime repository and MIT license: https://github.com/microsoft/onnxruntime
