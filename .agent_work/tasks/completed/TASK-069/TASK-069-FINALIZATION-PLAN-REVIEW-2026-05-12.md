# TASK-069 Finalization Plan Review

Date: 2026-05-12
Source reviewed: `TowerScout Local Deployment and Compliance Plan Finalization.docx`
Purpose: Review the updated local deployment and open-source compliance strategy, identify remaining gaps, and propose responses to the open questions at the end of the document.

## Executive Assessment

The updated finalization plan is materially stronger than the prior strategy drafts and addresses the main concerns raised in the previous critique. It correctly separates the near-term restricted pilot from the future public permissive/open-source-compliant release, treats model weights and geospatial datasets as separate governed assets, and no longer assumes that pinning or removing a single package is enough to resolve licensing risk.

The plan should be approved as the working direction, with a few clarifications before implementation:

1. The restricted pilot must not be described as the public open-source-compliant release.
2. J-Schulein can act as project decision authority for TowerScout-controlled choices, but cannot independently grant rights for third-party code, model weights, datasets, prior outside contributors, or government/client materials unless those rights are documented.
3. The public release should use a clean public release line unless counsel explicitly approves preserving legacy history.
4. The model and data import flow should use staged verification before activation, especially for any `.pt` assets that could otherwise be loaded by PyTorch.
5. The container image compliance work should be treated as a release gate, not a documentation-only task.
6. The model runtime migration should be proven with a small detector/classifier proof of concept before committing to ONNX as the final architecture.

## Confirmation Against Prior Feedback

The finalization plan addresses the major issues from the earlier feedback:

- It establishes a two-track approach: restricted pilot now, public compliant release later.
- It recognizes that AGPL/Ultralytics and vendored YOLO cannot remain in the default public permissive release path.
- It includes EfficientNet and other `.pt` model loading in the licensing and security scope.
- It adds rights inventory, relicensing authority, model/data terms, notices, and image-level compliance as gates.
- It acknowledges Git history treatment as a separate decision.
- It treats model weights, Census/geospatial data, provider cache data, and user-generated files as separate categories.
- It prioritizes container-first local deployment rather than a fragile native installer.
- It incorporates end-user experience through a control ZIP, launcher scripts, manifest validation, and simplified setup.

## Remaining Issues To Address

### 1. Restricted Pilot Labeling

The plan should explicitly state that the restricted pilot is not the public Apache-2.0 release. It may be a controlled evaluation or internal deployment package, but it should not be marketed or distributed as the open-source-compliant release until the compliance gates are complete.

Recommended plan language:

> The restricted pilot is a controlled deployment path for approved users and approved assets. It is not the public Apache-2.0/open-source-compliant release line. Public release occurs only after the rights inventory, notices, image compliance artifacts, model/data terms, and AGPL/Ultralytics replacement gates are complete.

### 2. Authority Boundary

The document correctly says J-Schulein can act as decision-making authority when sufficient context is provided. It should further distinguish project decisions from legal rights.

J-Schulein can decide:

- Target source license for TowerScout-authored code.
- Whether to pursue restricted pilot and public compliant release tracks.
- Whether to use GitHub Releases, control ZIPs, container images, and launcher scripts.
- Which runtime migration path to prioritize.
- Which folders should be host-visible by default.

J-Schulein cannot alone decide, without documentation:

- Whether all historical contributors assigned or licensed their contributions for Apache-2.0 release.
- Whether third-party code can be relicensed.
- Whether model weights can be redistributed by TowerScout.
- Whether Census/geospatial data or cached provider data can be bundled or redistributed.
- Whether existing git history can be published with legacy restricted or copyleft content.

### 3. Release Package Compliance Contents

The repo's current release package script is useful, but the plan should keep a specific action item to add compliance files to the control ZIP. Current package composition does not include root-level license and notice artifacts as release payload files.

Recommended required files for the public release package:

- `LICENSE`
- `NOTICE`
- `THIRD_PARTY_NOTICES.md`
- `MODEL_LICENSES.md`
- `DATA_LICENSES.md` or equivalent data-source notice file
- `SBOM` for the application container image
- Container image digest and checksum manifest
- Asset manifest with expected filenames, sizes, hashes, source URLs, and terms references

### 4. Asset Import Safety

The finalization plan correctly identifies that asset import should not copy untrusted model assets directly into active runtime volumes before validation. This should become a design requirement.

Recommended requirement:

> Asset import must stage files in a temporary location, validate manifest requirements before activation, and only then move assets into the active runtime volume. Failed imports must leave the previously active assets intact.

This matters for both compliance and security. Model weights may be proprietary, licensed separately, or unsafe to load if the format executes deserialization paths such as PyTorch pickle-backed `.pt` loading.

### 5. ONNX Should Remain A PoC-Gated Target

The plan is right to favor a generic ONNX/PyTorch-independent path, but ONNX should not be treated as already proven for TowerScout. The public release should be gated on a proof of concept that confirms:

- Model conversion or export is legally and technically permitted.
- Inference outputs match current TowerScout expectations.
- Performance is acceptable on the target laptop class.
- CPU-only operation is acceptable or GPU requirements are documented.
- Pre/post-processing is not still dependent on Ultralytics code.
- Classifier handling, including EfficientNet replacement or conversion, is covered.

### 6. End-User UX Needs One Owning Workflow

The plan mentions multiple workable flows. Before implementation, the project should choose one default flow and document others as fallbacks.

Recommended default:

1. User downloads the TowerScout control ZIP from GitHub Releases.
2. User extracts it to a local folder.
3. User places authorized asset files into `assets-inbox/`, or selects them through the setup wizard.
4. User runs `start.bat`.
5. Launcher performs preflight checks.
6. Launcher imports assets into Docker volumes after staged validation.
7. Browser opens to local setup only after API readiness passes.

Fallback flows:

- Restricted networks: preload OCI image archive and manually provide assets.
- Authorized hosted assets: launcher downloads assets after showing model/data terms and requiring user acceptance.
- Advanced users: direct Docker Compose operation.

## Suggested Responses To Remaining Open Questions

### 1. Should the restricted pilot proceed immediately while the public-compliant line continues in parallel?

Suggested response:

Yes. Proceed with the restricted pilot immediately, but label it clearly as a controlled pilot, not the public open-source-compliant release. The pilot can validate the container-first deployment model, launcher scripts, asset manifest, local setup instructions, and user experience while the public-compliant release track resolves licensing, notices, model governance, git history, and runtime replacement work.

Required conditions:

- Access limited to approved users.
- Assets distributed only under documented authority.
- README/release notes clearly state pilot limitations.
- Pilot artifacts do not claim Apache-2.0/public compliance.
- Any feedback from pilot setup flows feeds into the public release plan.

### 2. Can J-Schulein document authority for all TowerScout-authored software, or only a subset?

Suggested response:

J-Schulein should document authority for TowerScout-authored software only to the extent that authorship and ownership can be confirmed. The plan should start with a rights inventory that classifies files as TowerScout-authored, third-party, generated, vendor-derived, client/government-provided, model/data assets, or uncertain.

If J-Schulein can confirm authority over all TowerScout-authored code, then Apache-2.0 relicensing can proceed for that subset. Files with uncertain authorship, third-party provenance, or legacy vendor-derived content should be excluded, replaced, or escalated for legal review before inclusion in the public release line.

### 3. Which model distribution channel is authorized: owner-hosted, owner release, TowerScout-controlled release, or manual import only?

Suggested response:

Default to manual import until written redistribution authority is available. If the model owner authorizes redistribution, the preferred channel is a versioned GitHub Release asset or owner-controlled public URL with immutable versioning, checksums, and visible terms.

Recommended priority:

1. Owner-hosted URL or owner-controlled release, if available.
2. TowerScout-controlled GitHub Release asset, only with written redistribution authority.
3. Manual import by the user, with clear instructions and required model terms.

The application code should remain Apache-2.0, while model weights remain separately licensed and separately accepted.

### 4. Is the target public-compliant runtime ONNX-based, or another detector/classifier path after PoC?

Suggested response:

Use ONNX Runtime as the preferred target, but make the final runtime decision after a PoC. The PoC should evaluate detector and classifier needs together, including the YOLO-derived detector path and EfficientNet/classifier path. The goal is not merely to remove the Ultralytics package; it is to remove Ultralytics-specific runtime logic and any default dependency that brings AGPL obligations into the public permissive release path.

Decision rule:

- If ONNX meets accuracy, performance, packaging, and licensing requirements, adopt ONNX as the default public runtime.
- If ONNX fails, evaluate a generic PyTorch loader only if it avoids Ultralytics/AGPL code, handles `.pt` loading risk, and fits the model license.
- Do not ship the public compliant line until the replacement runtime is proven.

### 5. Should the compliant public line use a clean branch/cleaned release line, or preserve legacy history with caveats?

Suggested response:

Use a clean public release line unless legal review explicitly approves preserving legacy history. A clean line reduces the chance that old vendored YOLO, AGPL-covered files, proprietary model assets, restricted data, or inconsistent license statements remain available through git history.

The legacy private repository can remain the development archive. The public release line should contain only the reviewed source, notices, package files, documentation, and manifests that are intended for public distribution.

### 6. Which folders should be host-visible by default, and what support-bundle allowlist accompanies that?

Suggested response:

Default to Docker named volumes for runtime state and expose only a narrow support-safe host folder by default. Host-visible folders should be added only when they improve end-user support or setup clarity without exposing secrets, provider cache data, sessions, model files, or user-generated data unnecessarily.

Recommended default host-visible folders:

- `assets-inbox/` for user-provided model/data files before import.
- `support/` for sanitized support bundles.
- `logs/` only if logs are scrubbed or known not to contain secrets, URLs with keys, provider responses, user locations, or user-generated data.

Recommended not host-visible by default:

- `config/`
- `sessions/`
- `provider_cache/`
- `uploads/`
- active model/data volumes
- API key storage

Support bundle allowlist:

- App version and release identifier.
- Container image digest.
- Docker/Compose version.
- Readiness status.
- Asset manifest status without raw asset contents.
- Sanitized recent application logs.
- Environment summary with secrets redacted.
- Setup/import result summaries.

Support bundle exclusions:

- API keys and tokens.
- Session cookies.
- Uploaded images or generated detections.
- Provider cache payloads.
- Model weights.
- Census/geospatial data files unless explicitly approved.
- Raw `.env` values.

## Recommended Implementation Changes To The Plan

Add the following implementation gates to the final strategy:

1. Create a release-track decision record distinguishing restricted pilot, public source release, and public asset-enabled release.
2. Perform a file-level rights inventory before changing the root license.
3. Create or update `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, and data-source notices.
4. Modify the release packaging process to include compliance files and asset manifests.
5. Implement staged asset import with hash validation before activation.
6. Remove Ultralytics, vendored YOLO, and Ultralytics-specific loader paths from the public default runtime.
7. Include EfficientNet/classifier handling in the runtime migration plan.
8. Add container image SBOM, provenance, vulnerability scan, digest pinning, and license notices as public release gates.
9. Decide the public git history strategy before publishing.
10. Define support-bundle privacy rules and host-visible folder policy before pilot distribution.

## Bottom Line

The updated strategy is ready to become the basis for execution, provided it is treated as a gated two-track plan rather than a single packaging task. The strongest path is:

1. Proceed with a restricted pilot using the current container-first deployment approach.
2. In parallel, prepare a clean public Apache-2.0 source release line.
3. Keep model weights, Census/geospatial data, provider cache data, and user assets outside the source license.
4. Replace the default Ultralytics/YOLO runtime path only after a detector/classifier PoC proves the alternative.
5. Make compliance artifacts and end-user setup flow part of the release process, not optional documentation.
