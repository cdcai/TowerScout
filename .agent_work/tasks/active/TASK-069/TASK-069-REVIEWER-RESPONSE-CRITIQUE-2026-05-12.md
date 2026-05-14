# TASK-069 Reviewer Response Critique

**Date**: 2026-05-12
**Status**: Draft critique for owner/legal/reviewer discussion
**Reviewer input**: `C:\Users\bg90\OneDrive - CDC\TS Resources\Planning\Task-069 (Licensing)\TowerScout Local Deployment and Compliance Strategy_2026.05.12.docx`
**Prior analysis**: `.agent_work/tasks/active/TASK-069/TASK-069-OPEN-SOURCE-COMPLIANCE-STRATEGY-2026-05-12.md`

## Executive Summary

The reviewer's response is directionally strong. It agrees with the key deployment strategy: GitHub Releases should be the site-user channel, source checkout should remain a developer path, model/data assets should remain separate, and the app should continue to use the container-first release baseline rather than asking end users to build a Python/Node/GDAL stack.

The response should be tightened in four areas before it drives implementation:

1. The AGPL/Ultralytics issue should be treated as **verified on the current repo**, not a possible issue.
2. The plan should distinguish **open-source app compliance** from **model asset distribution permission** more explicitly.
3. Asset verification should happen at import/bootstrap and release-validation time, not as an expensive default readiness hash on every normal startup.
4. Host-visible runtime folders should be designed as an explicit profile with privacy warnings, not blindly adopted as the only default persistence model.

The reviewer does not materially change the recommended destination. They do change the recommended sequencing: before the ONNX/runtime refactor, the team should run a short policy and evidence gate that decides whether V1 RC1 can proceed with caveats or whether public/open-source release must wait for the Ultralytics removal and model-license boundary work.

## What The Reviewer Got Right

### Release ZIP First, Source Checkout Second

The reviewer correctly reinforces that ordinary sites should not be asked to clone, build, and understand the repository internals. The best user-facing path is:

- GitHub Release ZIP.
- Pinned OCI image digest.
- Matching asset bundle or asset bootstrap flow.
- One launcher command.
- Setup Wizard for provider keys.

This is consistent with the current repo direction and the client expectation.

### Separate Control Plane And Asset Layer

The reviewer correctly treats the app release package and runtime assets as separate layers. This aligns with the current `webapp/asset_manifest.v1.json`, `scripts/import-assets.ps1`, and `docs/release-asset-bundle-contract.md` pattern.

This should remain a core design principle even if the model distribution method changes from local asset ZIP to GitHub Release download.

### Host-Visible Folder Profile Is Worth Adding

The reviewer is right that named volumes do not fully satisfy the client's "folder structure intact on laptops" language. A `compose.hostdirs.yaml` or equivalent profile would make support and user comprehension easier.

The plan should adopt this idea, but with a privacy-sensitive design: the visible runtime folders can contain API keys, logs, addresses, coordinates, session state, uploads, cached provider responses, and investigation data.

### License Metadata Conflict Is A Real Release Blocker

The reviewer correctly flags the mismatch between the repo-level `CC-BY-NC-SA-4.0` posture and `package.json` saying `MIT`. This should be fixed before any release is described as open-source compliant.

### README Needs To Become Release-First

The reviewer is right that the top-level README is stale relative to the current runtime. It still points users toward older model/data instructions and should be rewritten around the release ZIP and asset bootstrap path.

## Issues Or Weaknesses In The Reviewer Response

### 1. AGPL/Ultralytics Is Not Merely Conditional

The reviewer says they could not independently verify the Ultralytics/YOLOv5 issue and treats it as a reported risk. In this local repo, it is verified:

- `webapp/vendor/yolov5_local/LICENSE` is AGPL-3.0.
- `webapp/vendor/yolov5_local/README.md` states the snapshot comes from `ultralytics/yolov5`.
- `webapp/ts_yolov5_local.py` loads `vendor.yolov5_local`.
- `webapp/requirements.txt` pins `ultralytics==8.3.249`.
- `Dockerfile`, `compose.yaml`, and `.env.example` still carry `YOLO_CONFIG_DIR`.

This should be upgraded from "verify before final release" to "known blocker for an Apache-2.0 default release path unless removed or separately licensed."

### 2. The Reviewer's Timeline Underestimates The Runtime Refactor

The reviewer frames "verify reported AGPL/Ultralytics issue" as a 7-day policy item and "asset bootstrap scripts" as 10 days. The harder work is likely the detector runtime migration and validation:

- Existing `.pt` weights are not automatically usable in a generic runtime.
- ONNX export may depend on the original Ultralytics model architecture and tooling.
- Output postprocessing must preserve TowerScout's current `xyxyn`-style normalized boxes, confidence scores, class labels, and secondary classifier handoff.
- Detection quality must be compared against current behavior on known tiles.

The plan should avoid implying that removing Ultralytics is a small metadata cleanup. It is an ML/runtime migration with licensing, accuracy, and support consequences.

### 3. "Default On" Runtime Hash Verification Is Too Expensive

The reviewer suggests `TOWERSCOUT_VERIFY_ASSET_HASHES` should be "default on in supported releases." That conflicts with the current release docs and runtime reality. The ZCTA `.shp` asset is large, and hashing large files on every readiness poll or normal startup would slow routine launch/support flows.

Recommended adjustment:

- Verify SHA-256 during asset download/import.
- Verify SHA-256 during release-candidate validation and support diagnostics.
- Record a local activation/acceptance marker after successful verification.
- Keep routine readiness to presence, size, manifest version, and acceptance state unless explicit hash validation is requested.

### 4. Host-Visible Folders Need A Privacy Design

The reviewer strongly recommends host-visible folders. I agree, but the implementation should be explicit about sensitivity:

- `runtime/config` can contain provider keys and `FLASK_SECRET_KEY`.
- `runtime/logs` can contain addresses, coordinates, errors, and support evidence.
- `runtime/flask_session`, `runtime/temp`, and `runtime/uploads` can contain investigation artifacts.
- `runtime/cache` can contain provider/cache data.

Recommended adjustment:

- Add the profile, but keep named volumes as the low-friction default until the user chooses "visible runtime folders" or the release owner explicitly selects hostdirs as the normal support profile.
- Add a support-bundle policy that does not blindly zip all runtime folders.

### 5. The Entry Point Naming Should Be Standardized

The reviewer uses `start.cmd`, `start.bat`, and scripts interchangeably. The current repo has top-level `start.bat` and script-level `.cmd` wrappers. This is a user-experience detail that will matter.

Recommended adjustment:

- Pick one top-level user entry point for docs, probably `start.bat` for current compatibility or add a top-level `start.cmd` if that becomes the preferred Windows convention.
- Keep script-level helpers under `scripts/`.
- Avoid telling users to choose among similarly named launchers.

### 6. Model Rights Need A More Concrete Decision Matrix

The reviewer correctly asks whether assets are approved for GitHub Release distribution, but the plan should distinguish:

- Owner-hosted canonical model URL.
- Owner-owned GitHub Release.
- TowerScout-hosted GitHub Release under explicit redistribution permission.
- Manual local import only.

Each has different compliance and support consequences. The plan should require a written model distribution authorization before implementing automatic download.

### 7. Git History And Existing Vendored Code Need A Decision

Removing `webapp/vendor/yolov5_local/` from the current branch and release package does not erase the fact that prior commits may contain vendored AGPL code. That may be acceptable if the historical third-party code remains under its own license, but it should be reviewed before the repo is publicly marketed as Apache-2.0.

Recommended adjustment:

- Decide whether to preserve git history with explicit historical-license caveats.
- Or, if legal requires it, plan a repository history rewrite or fresh public repository for the Apache-compliant release line.

This is a policy/legal decision, not something engineering should do casually.

### 8. The Reviewer Understates The Provider-Terms Track

The reviewer mentions provider keys and TLS, but the broader release should also cover Google/Azure terms and key restrictions. This already appears as `TASK-076` in Sprint 06 planning and should remain a parallel release policy gate.

Recommended adjustment:

- Keep provider-key exposure policy as a sibling to license policy, not a footnote in deployment docs.

## Changes I Would Make To The Plan

### Change 1: Promote AGPL Removal To A Release Blocker For Apache Default Path

Old framing:

- Verify whether Ultralytics/YOLOv5 is in the current runtime.

New framing:

- Treat Ultralytics/YOLOv5 AGPL dependency as verified.
- Block any Apache-2.0 default release until either:
  - Ultralytics/YOLOv5 is removed from the default path, or
  - the project obtains a license/permission that supports the intended distribution, or
  - the release is explicitly not presented as Apache/open-source compliant.

### Change 2: Split V1 RC1 Into Two Possible Tracks

Add an explicit decision:

1. **Restricted pilot track**
   - Keep current runtime temporarily.
   - Distribute only to controlled reviewers with explicit CC/AGPL/model caveats.
   - Do not market as Apache-2.0 or open-source-compliant.

2. **Open-source-compliant release track**
   - Pause public release until Apache metadata, model-license files, Ultralytics removal, and asset terms flow are complete.

The team should not blur these tracks.

### Change 3: Add A Model Distribution Decision Record

Before implementing download automation, create a decision record covering:

- Model owner.
- Model artifact format.
- Whether GitHub Releases hosting is approved.
- Whether TowerScout may mirror/redistribute.
- Whether users must accept terms.
- Whether conversion to ONNX is allowed.
- Whether retraining/export pipeline rights are clear.
- Terms version and checksum policy.

### Change 4: Use ONNX As The Preferred End State, But Add A Proof Gate

Keep ONNX Runtime as the likely destination, but add a proof gate:

- Produce or obtain an approved ONNX detector artifact.
- Verify it loads without Ultralytics.
- Validate preprocessing/postprocessing.
- Compare detection output on known tiles.
- Measure CPU performance against current baseline enough to identify unacceptable regression.

If the current model cannot be converted or licensed, the plan must include retraining or alternate detector selection.

### Change 5: Implement Asset Bootstrap As A First-Class Flow

Keep the reviewer's asset bootstrap idea, but specify:

- `setup-assets.ps1` verifies terms and hashes before activation.
- Downloads are pinned by release tag and SHA-256, not "latest".
- Failed/partial downloads are not activated.
- Proxy/TLS/restricted-network fallbacks are documented.
- Manual asset ZIP import remains supported.
- Terms acceptance is stored under persistent config and invalidated when model terms version changes.

### Change 6: Make Hashing A Bootstrap/Validation Step

Do not default `TOWERSCOUT_VERIFY_ASSET_HASHES=1` for routine readiness. Instead:

- Always verify on download/import.
- Enable hash verification during release candidate validation.
- Provide a support command for full verification.
- Keep normal launcher readiness fast.

### Change 7: Add Hostdirs As A Profile With Clear Data Handling

Implement `compose.hostdirs.yaml`, but document:

- What data appears in each folder.
- How to clean it.
- How to avoid sending sensitive data in support bundles.
- When named volumes are preferable.

### Change 8: Add Package/CI Compliance Gates

Add release checks for:

- Required license/notice/model-license files present.
- No `ultralytics` in default requirements.
- No `webapp/vendor/yolov5_local` in release package.
- No `YOLO_CONFIG_DIR` in default release env after migration.
- Asset manifest has license/terms metadata for all model assets.
- Release ZIP and asset files have checksums.
- Image digest is pinned.

## Revised Recommended Path Forward

### Phase 0: Evidence And Policy Gate

- Confirm code relicensing authority.
- Confirm model owner/distribution rights.
- Confirm current AGPL/Ultralytics facts in writing.
- Decide restricted pilot vs open-source-compliant release track.

### Phase 1: Documentation And Metadata Cleanup

- Fix license metadata conflict.
- Add preliminary `NOTICE`, `THIRD_PARTY_NOTICES.md`, and `MODEL_LICENSES.md`.
- Rewrite README to release-first.
- Remove stale model/ZCTA instructions.

### Phase 2: Asset Governance

- Create manifest v2 with license/terms metadata.
- Add import/download verification.
- Add model terms acceptance marker.
- Keep manual asset import fallback.

### Phase 3: Runtime Decoupling

- Add generic detector adapter.
- Add ONNX Runtime detector proof.
- Validate output and performance.
- Remove Ultralytics and vendored YOLO from default path.

### Phase 4: User Experience Productization

- Add asset bootstrap script.
- Add optional setup wizard asset status flow.
- Add host-visible runtime profile.
- Standardize top-level launcher naming.

### Phase 5: Release Validation

- Build release ZIP.
- Inspect compliance contents.
- Validate clean-machine install.
- Validate restricted-network fallback.
- Run one bounded detection smoke.
- Produce pilot go/no-go recommendation.

## Bottom-Line Critique

The reviewer response is useful and mostly supports the existing plan. I would adopt these parts:

- Release ZIP instead of source checkout for ordinary users.
- Separate app/control package and asset layer.
- Host-visible folder profile.
- README rewrite.
- License metadata cleanup.
- Asset bootstrap.

I would change these parts:

- Treat AGPL/Ultralytics as verified, not speculative.
- Do not imply ONNX migration is a small or optional cleanup if Apache/open-source compliance is the goal.
- Do not turn full SHA-256 hashing on for every normal readiness check.
- Do not make host-visible runtime folders the only persistence model without privacy handling.
- Add an explicit restricted-pilot vs compliant-public-release decision gate.
- Add a model distribution authorization record before any automatic GitHub Release download.

The resulting plan is more conservative but safer: it preserves the strong local-deployment direction while preventing the team from accidentally labeling a CC/AGPL/proprietary-model package as open-source compliant.

## References

- Apache Software Foundation, "Applying the Apache License, Version 2.0": https://www.apache.org/legal/apply-license
- Creative Commons FAQ, software license guidance: https://creativecommons.org/faq/
- Open Source Initiative, Open Source Definition: https://opensource.org/definition-annotated
- Open Source Initiative FAQ, commercial use and restrictions: https://opensource.org/faq/
- Ultralytics licensing page: https://www.ultralytics.com/license
- PyTorch `torch.load` documentation and unsafe loading warning: https://docs.pytorch.org/docs/stable/generated/torch.load
- GitHub Releases documentation: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
- Docker bind mounts documentation: https://docs.docker.com/engine/storage/bind-mounts/
- Docker volumes documentation: https://docs.docker.com/engine/storage/volumes/
- Docker Compose multiple-file merge documentation: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
