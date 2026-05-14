# TASK-069 V2 Strategy Feedback

**Date**: 2026-05-12
**Status**: Draft feedback for next strategy iteration
**Reviewer input**: `C:\Users\bg90\OneDrive - CDC\TS Resources\Planning\Task-069 (Licensing)\TowerScout Local Deployment and Compliance Strategy_2026.05.12_v2.docx`
**Related analysis**:

- `.agent_work/tasks/active/TASK-069/TASK-069-OPEN-SOURCE-COMPLIANCE-STRATEGY-2026-05-12.md`
- `.agent_work/tasks/active/TASK-069/TASK-069-REVIEWER-RESPONSE-CRITIQUE-2026-05-12.md`

## Executive Summary

The v2 strategy is a substantial improvement over the prior reviewer response. It addresses the main critique points:

- It now treats the Ultralytics/YOLOv5 AGPL issue as verified, not hypothetical.
- It separates restricted pilot from public open-source-compliant release.
- It keeps hash verification out of routine readiness and ties it to import, validation, and support diagnostics.
- It treats host-visible folders as useful but sensitive.
- It adds release-package compliance gaps, including the fact that `scripts/package-release.ps1` currently omits license and notice files.
- It identifies provider drift around legacy Bing handling.

I agree with the updated strategic direction. I would not materially change the high-level path:

> Use GitHub Releases as the user-facing distribution channel, keep the container-first runtime, separate application code from model/data assets, add a guided asset bootstrap/import flow, add a privacy-aware host-visible folder profile, and treat the current license conflict plus Ultralytics/AGPL runtime as release-gating issues.

The remaining work is to make the plan more explicit about legal authority, model provenance, hidden model-download behavior, image/SBOM compliance, and the practical risk of the detector migration.

## Suggestions Addressed In V2

### AGPL/Ultralytics Is Now Correctly Treated As Verified

V2 explicitly states that the repo includes:

- `webapp/vendor/yolov5_local/` under AGPL-3.0.
- A local README identifying the vendored source as `ultralytics/yolov5`.
- `ts_yolov5_local.py` importing the vendored package.
- `ultralytics==8.3.249` in `webapp/requirements.txt`.

This is the correct framing. It should remain a release blocker for any Apache-2.0/default open-source-compliant distribution unless the default runtime is changed or separate rights are obtained.

### Restricted Pilot Versus Public Compliant Release Is Now Explicit

V2 now distinguishes:

- A restricted pilot path that may temporarily carry caveats.
- A public/open-source-compliant release path that must clear the licensing/runtime issues.

This is important. The team should avoid saying "open source compliant" for any release that still ships the current CC/AGPL/Ultralytics default path without explicit legal approval and clear caveats.

### Asset Bootstrap Is Correctly Treated As Future Work

V2 correctly says hosted asset bootstrap is not currently implemented and should be designed separately. This avoids a common documentation failure: promising "one click" setup before checksum, terms, proxy/TLS, partial download, and restricted-network behavior exist.

### Host-Visible Runtime Folders Are Now Privacy-Sensitive

V2 correctly notes that host-visible folders are useful for the client's folder-visibility expectation but risky for secrets, logs, sessions, uploads, caches, coordinates, and investigation data.

The plan should keep this profile, but it should not silently turn every runtime folder into a support ZIP.

### Release Package Notice Gap Is Correctly Identified

V2 correctly observes that `scripts/package-release.ps1` currently stages launchers, docs, scripts, and the asset manifest, but not `LICENSE.TXT`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, or `MODEL_LICENSES.md`.

That should become a concrete release-gate fix.

### Provider Drift Is Correctly Identified

V2 correctly identifies a setup/support ambiguity:

- `ts_config.py` and validation surfaces support `google` and `azure`.
- `towerscout.py` still logs/loads `BING_API_KEY` and has a `bing` provider entry.

This should be handled before pilot docs are finalized, either as a compatibility note or a cleanup task.

## Remaining Issues In V2

### 1. Legal Authority To Relicense Needs More Emphasis

V2 correctly says root license posture must be resolved, but the next iteration should be more explicit that Apache-2.0 is not just an engineering decision.

TowerScout has multiple apparent contributors and history:

- Original graduate project contributors.
- Later CDC and non-CDC contributors.
- Potential work-for-hire or government-work issues.
- Documentation, notebooks, synthetic data, marketing site, generated frontend bundles, and model/training artifacts that may not all share the same ownership.

Required decision:

- Determine who owns each category of content and who can authorize relicensing.
- Decide whether the public Apache-2.0 release uses the existing repo history, a cleaned branch, or a fresh public release repository.

### 2. Existing Git History Is Still Not Addressed Enough

V2 focuses on current release artifacts, which is correct for packaging, but it does not clearly address historical repository contents.

If the repo is publicly presented as Apache-2.0 after removing vendored YOLO from the current branch, older commits may still contain:

- AGPL vendored YOLO source.
- CC-BY-NC-SA source notices.
- Stale or ambiguous model links.
- Possibly generated or third-party assets.

This may be acceptable if historical files retain their own notices, but it needs legal/owner review. The plan should add a decision point:

- Preserve history with explicit historical-license caveats.
- Or create a clean public repository/branch for the Apache-compliant release line.

Engineering should not rewrite history without explicit approval.

### 3. The Container Image Needs Its Own Compliance Treatment

V2 covers the Release ZIP well, but the default deployment also depends on a GHCR image. The image is a distribution artifact too.

The plan should add image-level compliance checks:

- No vendored YOLO/Ultralytics in the compliant image.
- License/notice files present in the image.
- SBOM generated for OS, Python, and Node/build dependencies.
- Container labels include source, license, image revision, and digest.
- Trivy/license scan output reviewed before release.
- Base image and OS package license inventory captured.

Release ZIP compliance is not enough if users pull a non-compliant image.

### 4. EfficientNet Also Needs Asset And Runtime Review

The v2 strategy focuses mostly on YOLO/Ultralytics, but TowerScout's secondary classifier also deserves explicit review.

Current `webapp/ts_en.py` uses:

- `efficientnet_pytorch`.
- `EfficientNet.from_pretrained('efficientnet-b5', include_top=True)`.
- A local `b5_unweighted_best.pt` loaded with `torch.load`.

Potential issues:

- `from_pretrained` may perform or depend on an external pretrained-weight acquisition/cache path.
- The EfficientNet base model/source weights have their own license/provenance.
- The local `.pt` file is still a pickle-backed PyTorch artifact and should be treated as trusted code/data.
- If the open-source-compliant default avoids unsafe `.pt` loading for the primary detector, the same question should be asked of EfficientNet.

Recommended adjustment:

- Include EfficientNet in `MODEL_LICENSES.md`, model provenance review, runtime dependency review, and any future safer-format conversion plan.

### 5. Model Conversion And Validation Are Still Under-Specified

V2 correctly says "remove or replace default AGPL runtime path" and gives it 20 days, but it still understates the uncertainty.

A compliant ONNX path requires:

- Confirming model owner permission to convert.
- Producing an approved ONNX detector artifact.
- Defining preprocessing exactly.
- Defining NMS/postprocessing exactly.
- Matching output schema used by TowerScout.
- Comparing detections on known regression tiles.
- Measuring CPU performance.
- Deciding how EfficientNet is handled.

The next plan should add a proof-of-concept gate before committing to a full migration timeline.

### 6. Model Terms Need A Stronger Distribution Matrix

V2 asks whether assets can be redistributed, but the next iteration should force one of these models:

| Distribution option | Who hosts | TowerScout may mirror? | User experience | Compliance requirement |
| --- | --- | --- | --- | --- |
| Owner-hosted URL | Model owner | No | Bootstrap downloads from owner URL | Terms shown before download |
| Owner GitHub Release | Model owner | No | Bootstrap downloads pinned owner release | Release tag and SHA pinned |
| TowerScout GitHub Release | TowerScout repo/org | Yes | Simplest bootstrap | Written redistribution permission required |
| Manual import only | Site/support | No | More friction | Clear local staging instructions |

The plan should not implement download automation until this decision is recorded.

### 7. "Model/Data Terms" Should Separate Models From Public Census Data

V2 sometimes groups model and data terms together. That is useful in the UI, but the legal/provenance handling should separate:

- Proprietary or project-owned model weights.
- US Census ZCTA data.
- User-provided exported/restored datasets.
- Map provider imagery/cache data.

Each category has different terms and redistribution concerns.

### 8. Support Bundle And Data Retention Policy Should Be A First-Class Deliverable

V2 mentions support-bundle redaction, but this should be promoted to a concrete deliverable if host-visible runtime folders are added.

Needed policy:

- What files users can safely send to support.
- What files may contain keys, addresses, coordinates, uploaded data, provider responses, or session state.
- Whether logs are redacted by default.
- How to clear caches and sessions.
- How long runtime data should persist.

This matters for public-health investigation workflows.

### 9. The Setup Wizard Asset Flow Needs Careful UX Boundaries

V2 recommends asset bootstrap but does not fully define whether it is a script-only flow or app UI flow.

Recommended UX:

- Launcher/preflight owns download/import, because it can manage files and container volumes before app readiness.
- Setup Wizard displays asset status and recovery guidance.
- Browser upload of large model files should remain disabled by default unless a trusted admin mode is explicitly enabled.

This keeps the setup flow intuitive without reintroducing risky browser model upload behavior.

### 10. The Strategy Should Add A Decision On Release Timing

The plan should explicitly decide:

- Does `TASK-069` block the current V1 RC1 pilot?
- Or does V1 RC1 proceed as a restricted internal pilot with clear caveats while the open-source-compliant release track continues separately?

Without this decision, the team may mix release-readiness work with a larger runtime migration and lose the ability to pilot the already-working package path.

## Recommended Changes To The Strategy

### Add A Phase -1: Release Track Decision

Before implementation, decide:

- **Restricted pilot path**: current runtime may be tested by controlled users with explicit licensing caveats and no public open-source-compliant claim.
- **Public compliant path**: release waits for app relicensing, model authorization, notice files, and removal/replacement of the default AGPL/Ultralytics runtime.

This decision should be written into `TASK-069`.

### Add A Rights Inventory

Create a rights inventory table for:

- TowerScout-authored backend code.
- TowerScout-authored frontend code.
- Docs and guides.
- Notebooks and training artifacts.
- Synthetic data.
- Marketing site.
- YOLO detector weights.
- EfficientNet weights.
- ZIP-code data.
- Vendored/third-party code.
- Generated frontend bundle.
- Container base images and OS packages.

Each row should include owner, current license, desired license, redistribution status, and release action.

### Add An Image Compliance Workstream

Add explicit tasks for:

- SBOM generation.
- License scan.
- Image labels.
- Notice files inside image.
- Confirmation that compliant image has no vendored YOLO/Ultralytics.

### Add A Detector Migration PoC

Before full ONNX migration:

- Build/load a candidate ONNX detector.
- Run known test tiles.
- Confirm output schema and confidence behavior.
- Compare against current model results.
- Measure CPU inference time.
- Decide go/no-go.

### Add EfficientNet To The Model Compliance Scope

Do not treat only the primary detector as model compliance. Include the secondary classifier and its runtime in the asset/model review.

### Add Asset Terms UX And Acceptance Design

Define:

- Terms versioning.
- Acceptance storage location.
- How acceptance is invalidated when terms or model version changes.
- Offline/manual import terms display.
- Support flow when users decline.

### Add Restricted-Network Strategy As A Named Follow-Up

The plan correctly says current restricted-network support is support-managed image preload plus asset import. Make this a named future track:

- OCI archive or mirrored registry.
- Local asset ZIP.
- Offline checksum verification.
- TLS/CA import.
- No internet bootstrap assumption.

## Updated Recommended Path

1. **Policy/evidence gate**
   - Resolve release track, code relicensing authority, model distribution authority, and current AGPL facts.

2. **Low-risk compliance cleanup**
   - Fix license metadata mismatch, add notice/model-license files, update release packaging to include them, rewrite README release-first.

3. **Asset governance**
   - Extend manifest with license/provenance/terms metadata, add acceptance tracking, define model distribution channel.

4. **User-experience hardening**
   - Add asset bootstrap/import UX, standardize `start.bat` as the top-level entry point, add host-visible profile with privacy guidance.

5. **Runtime compliance migration**
   - Run ONNX detector PoC, decide model conversion/retraining path, remove Ultralytics/YOLO default path, address EfficientNet.

6. **Release validation**
   - Build compliant release ZIP and image, inspect license artifacts, validate clean machine, validate restricted-network fallback, run detection smoke.

## Bottom-Line Feedback

The v2 strategy is strong enough to use as the basis for TASK-069 planning, with revisions. It correctly incorporates the prior critique and adds useful new findings from the repo.

The main changes I would still make are:

- Add a formal release-track decision before implementation.
- Treat the container image as a compliance artifact, not only the ZIP.
- Add a rights inventory across code, models, docs, data, generated files, and containers.
- Include EfficientNet and PyTorch `.pt` model loading in the model compliance scope.
- Add a detector migration PoC before committing to ONNX as the full path.
- Define support-bundle/privacy behavior before enabling host-visible runtime folders broadly.
- Record the model distribution option before implementing GitHub Release downloads.

With those additions, the strategy will be much less likely to encounter surprises during implementation or legal review.
