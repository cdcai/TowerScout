# TASK-069 Final Strategy Precision Pass And Repo Roadmap

> 2026-05-13 update: This roadmap is superseded for Sprint 06 by
> `TASK-069-AGPL-YOLO-RELEASE-IMPLEMENTATION-2026-05-13.md` where the team
> chose to seek feedback on a YOLO-enabled `agpl-yolo` RC/pilot path. The ONNX
> runtime migration moves to a later permissive Apache-only release track unless
> reviewers reject AGPL as the release posture.

Date: 2026-05-12
Reviewed source: `TowerScout Final Strategy Precision Pass_2026.05.12.docx`
Repo context: `C:\Users\bg90\TowerScout`

## Bottom Line

I support the updated strategy and do not think it needs another strategy redesign round. The precision-pass document correctly identifies the remaining gaps as execution-readiness issues: Podman-first behavior must be true in the launcher, restricted-network wording must distinguish supported preload from future OCI archive packaging, provider terms must be packaged, current Ultralytics/YOLO and EfficientNet blockers must be explicit public-release gates, model import must be allowlist-only for the public line, and release revocation must be defined.

The strategy should now be treated as final in substance, pending reviewer second opinion and normal legal/owner signoff. The work ahead is implementation, validation, and cleanup.

This document is not legal advice. The rights, relicensing, model redistribution, provider API terms, and public-history decisions still need documented authority and, where appropriate, legal review.

## Supported Strategy Decisions

The following decisions should be considered accepted unless the project owner or legal reviewer changes them.

| Decision | Supported position | Repo-specific implication |
| --- | --- | --- |
| Release tracks | Keep restricted pilot and public compliant release separate | Sprint 06 can continue toward pilot readiness while the public line remains gated by TASK-069 compliance work |
| Source license target | Apache-2.0 for provably TowerScout-authored code | Requires rights evidence before changing root license and headers |
| Public history | Prefer clean public release line | Avoid publishing legacy vendored AGPL, model/data assets, internal artifacts, or ambiguous history |
| Runtime packaging | OCI-first, Podman-preferred | `scripts/lib/TowerScoutCompose.ps1` must stop preferring Docker in auto mode for release use |
| Docker Desktop | Optional compatible fallback only | Docs and launcher should not imply Docker Desktop is required |
| Restricted network | Support-managed preload now, productized OCI archive later | Current docs already say full OCI archive packaging is follow-on work |
| Model/data assets | Separate from Apache source code | Use manifest-backed local import unless redistribution authority is documented |
| Public asset import | Allowlist-only | Public builds should activate only manifest-approved, checksum-approved assets |
| Public ML runtime | Remove Ultralytics/YOLO AGPL default path or separately license it | `webapp/requirements.txt`, `webapp/vendor/yolov5_local/`, `webapp/ts_yolov5.py`, and related docs/tests are blockers |
| Target replacement runtime | Prefer ONNX Runtime after PoC, but prove detector and classifier paths together | Do not assume ONNX is complete until model conversion, accuracy, performance, and licensing are validated |
| GPU support | Prioritize GPU capability with automatic CPU fallback, but keep CPU as the supported baseline | Implement as explicit capability detection and optional acceleration path, not as a default dependency burden |
| Public cleanup | Complete a codebase cleanup/refactor tranche before public release | Cleanup should follow pilot stabilization and precede public repo publication |

## Current Repo Reality

The current repo already has the core deployment foundation:

- `Dockerfile`, `compose.yaml`, `compose.build.yaml`
- `scripts/package-release.ps1`
- `scripts/lib/TowerScoutCompose.ps1`
- `scripts/import-assets.ps1`
- `scripts/import-tls-ca.ps1`
- `docs/oci-quick-start.md`
- `docs/oci-runtime-contract.md`
- `docs/release-asset-bundle-contract.md`
- `webapp/asset_manifest.v1.json`
- `/api/health` and `/api/readiness`
- Setup Wizard and Settings
- Google and Azure provider support
- container volume contract for config, assets, logs, sessions, uploads, and cache

The current repo also has known public-release blockers:

- `webapp/requirements.txt` still pins `ultralytics==8.3.249`.
- `webapp/vendor/yolov5_local/` contains vendored YOLOv5 AGPL code.
- `webapp/ts_yolov5.py` imports `ts_yolov5_local` and relies on the current YOLO path.
- `webapp/ts_en.py` still uses `EfficientNet.from_pretrained()` and `torch.load()`.
- `scripts/package-release.ps1` does not yet package final compliance files such as `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, or `PROVIDER_TERMS.md`.
- `scripts/import-assets.ps1` copies assets into active volumes before verification.
- `scripts/lib/TowerScoutCompose.ps1` currently selects Docker before Podman in `auto` mode.
- `towerscout.py` and `.env.example` still contain `BING_API_KEY` / Bing drift while current release docs emphasize Google and Azure.
- CI has useful checks, but several are advisory rather than release-blocking.
- Node 18 is still used in CI and is noted as needing a future LTS migration.

## Roadmap Overview

The path forward should be managed as four coordinated tracks:

1. Restricted Pilot Track: finish the V1 RC1 local deployment path without claiming public Apache/open-source compliance.
2. Public Compliance Track: prepare a clean, legally supported, Apache-2.0-compatible public source/release line.
3. Runtime Modernization Track: replace the public default ML runtime, add GPU auto-detect with CPU fallback, and preserve detection behavior.
4. Public Quality Track: perform cleanup/refactor, CI hardening, docs cleanup, and final release-readiness validation before opening the repo.

These tracks should not all block the restricted pilot. They do block a public compliant release.

## Phase 0: Strategy Closure And Governance

Timing: immediate, before broad release claims.

Primary tasks:

- Promote `TASK-069` into active Sprint 06 policy work or run it in parallel with the release docs lane.
- Create a decision record confirming the two-track release model.
- Create a formal rights evidence pack.
- Decide clean public release line vs preserving legacy history. Recommendation: clean public line.
- Define who signs off on TowerScout-authored code, third-party code, model weights, datasets, and provider terms.
- Decide model distribution authority: manual import by default, owner-hosted or TowerScout-hosted only with written permission.
- Add the release revocation policy.

Deliverables:

- `.agent_work/decisions/` record for release-track split.
- Rights evidence pack template.
- Public release blocker table tied to repo paths.
- Revocation runbook.
- Decision on whether the restricted pilot package can proceed while public compliance work continues.

Exit criteria:

- No one is describing the restricted pilot as the public open-source-compliant release.
- Public release blockers are explicitly tracked.
- J-Schulein's authority boundary is documented.

## Phase 1: Finish Sprint 06 Restricted Pilot Path

This phase should stay aligned with the current sprint plan rather than creating a parallel release process.

### TASK-071: End-User Release Package Documentation

Update the package docs to reflect:

- OCI-first deployment.
- Podman as preferred runtime.
- Docker Desktop as optional fallback only where site policy allows it.
- Required Podman machine / WSL2 / Hyper-V / admin / virtualization prerequisites.
- `localhost` as the expected browser origin.
- Asset bundle placement under `assets/`.
- Manual/local asset import as the supported path.
- Restricted-network support-managed image preload as the current fallback.
- Full OCI archive distribution as follow-on work, not current support.
- Provider terms and user-owned API keys.
- CPU baseline with optional GPU capability planned separately.
- Support bundle privacy exclusions.

### TASK-066: Release Candidate Validation Gate

Validate the release package from a clean user-facing environment:

- Download/extract control ZIP.
- Verify ZIP checksum.
- Confirm pinned image digest.
- Run Podman-first launch path.
- Confirm Docker fallback only when explicitly selected or Podman unavailable.
- Confirm Compose provider visibility and logging.
- Import model/data assets.
- Verify asset manifest and hashes.
- Complete Setup Wizard with Google or Azure key.
- Confirm config persists across restart.
- Run a bounded detection smoke.
- Stop/restart/update.
- Capture diagnostics without leaking secrets or user data.

### TASK-073: Clean-Machine Pilot / UAT Plan

Define:

- Test machine requirements.
- Tester instructions.
- Expected files and folder structure.
- Acceptance checklist.
- Support escalation path.
- Issue report template.
- What logs/diagnostics are safe to collect.
- Which failures block pilot vs become support notes.

### Pull TASK-074 Forward If Needed

`TASK-074 Runtime Prerequisite Preflight` should become active before UAT if clean-machine validation shows any launch friction. It likely should be pulled forward because the final strategy depends on predictable Podman-first setup.

Preflight should check:

- `podman` availability.
- Podman machine existence/running state.
- Compose provider availability.
- `PODMAN_COMPOSE_PROVIDER` validity.
- Docker availability only as fallback.
- port availability.
- image availability or GHCR reachability.
- disk space.
- asset folder presence.
- manifest version.
- TLS CA bundle path validity.
- provider setup state.

## Phase 2: Precision-Pass Implementation Tasks

These are the concrete corrections from the precision-pass review.

### 2.1 Podman-First Launcher Behavior

Files:

- `scripts/lib/TowerScoutCompose.ps1`
- `scripts/launch.ps1`
- `scripts/start.ps1`
- `scripts/status.ps1`
- `docs/oci-quick-start.md`
- `docs/oci-runtime-contract.md`
- `tests/unit/test_release_package_script.py` or new script tests

Changes:

- Change release auto-detection to prefer Podman before Docker.
- Keep `-Engine docker` as an explicit fallback.
- Consider an environment override such as `TOWERSCOUT_ENGINE=podman|docker|auto`.
- Validate and log the actual Compose provider for Podman.
- Fail clearly if Podman is installed but no machine/provider is usable.
- Avoid silently using Docker-oriented Compose tooling when Podman is intended.

Acceptance:

- On a machine with both Docker and Podman, release auto mode selects Podman.
- On a machine with only Docker, Docker fallback still works if allowed.
- On a machine with no supported runtime, the user gets actionable guidance.
- Provider summary is visible in logs/status output.

### 2.2 Release Package Compliance Payload

Files:

- `scripts/package-release.ps1`
- `Dockerfile`
- `docs/`
- root compliance files
- package tests

Create or update:

- `LICENSE`
- `NOTICE`
- `THIRD_PARTY_NOTICES.md`
- `MODEL_LICENSES.md`
- `DATA_LICENSES.md`
- `PROVIDER_TERMS.md`
- `release-manifest.v1.json` or generated equivalent
- `SBOM.spdx.json` or SBOM reference

Changes:

- Package compliance files into the control ZIP.
- Include or reference compliance files inside the image.
- Generate and package `release-manifest.v1.json`.
- Include `IMAGE.txt` and checksums.
- Include provider/API terms.

Acceptance:

- A packaged release has all required compliance files.
- The image exposes or contains the same compliance payload.
- Package tests fail if required files are absent.

### 2.3 Provider Terms And API Key Policy

Related task:

- `TASK-076 Provider API Key Exposure And Restriction Policy`

Files:

- `PROVIDER_TERMS.md`
- `webapp/templates/towerscout.html`
- setup wizard docs/UI text as appropriate
- `docs/oci-quick-start.md`
- `webapp/.env.example`
- `webapp/towerscout.py`

Changes:

- Document that users bring their own Google/Azure accounts and keys.
- Document provider-side restrictions, quotas, referrers/origins, and allowed use.
- State that TowerScout's source license does not grant rights to provider APIs, imagery, geocoding output, tiles, caching, or redistribution.
- Resolve Bing drift: remove from public line or explicitly mark unsupported legacy compatibility.

Acceptance:

- Release package includes provider terms.
- Setup/user docs point users to provider-specific obligations.
- Public docs only advertise supported providers.

### 2.4 Staged And Allowlist-Only Asset Import

Files:

- `scripts/import-assets.ps1`
- `webapp/ts_assets.py`
- `webapp/asset_manifest.v1.json`
- `docs/release-asset-bundle-contract.md`
- `docs/oci-runtime-contract.md`

Changes:

- Import into a staging location first.
- Validate manifest version, required paths, byte sizes, and hashes before activation.
- Activate atomically into the runtime volume only after validation.
- Keep previous active asset set intact if validation fails.
- Make public builds allowlist-only.
- Disable arbitrary model upload/import in public builds by default.

Acceptance:

- Bad model/data files never replace the last known good active set.
- Hash mismatch blocks activation.
- Public package cannot activate unmanifested model files.

### 2.5 Release Manifest, Integrity, SBOM, And Revocation

Files:

- `scripts/package-release.ps1`
- `.github/workflows/container-publish.yml`
- `.github/workflows/ci.yml`
- release docs

Changes:

- Generate `release-manifest.v1.json`.
- Record app version, control ZIP hash, image ref, image digest, asset manifest version, compatible asset hashes, model/data versions, model terms version, SBOM reference, and public/pilot track.
- Publish image SBOM/provenance where supported.
- Publish fallback SBOM/checksum artifacts if GitHub-native features are unavailable.
- Add revocation policy for bad ZIP, bad digest, bad model/data asset, and license-defective release.

Acceptance:

- Every release artifact can be tied to a manifest.
- Users/support can verify what they are running.
- A bad artifact can be withdrawn with a documented rollback target.

### 2.6 Automated Compliance Gates

Related task:

- `TASK-067 CI Release Gate Tightening`

CI gates to add or harden:

- Prohibited dependency scan for public release path.
- Known blocked path scan for `webapp/vendor/yolov5_local/` in public line.
- License scan.
- Secret scan.
- Large-file and model/data tracking scan.
- Compliance-file presence check.
- Package assembly check.
- Image digest/pinning check.
- SBOM generation check.
- Release manifest schema check.
- Node LTS migration plan or explicit CI maintenance task.

Acceptance:

- Public release cannot be assembled with known blocked dependencies or missing notices.
- CI produces actionable failures, not advisory-only warnings, for release gates.

## Phase 3: Prioritized GPU Capability With CPU Fallback

Related task:

- `TASK-075 GPU / CUDA Support Decision`

Recommendation: promote `TASK-075` from a decision-only candidate into an early design task, then create an implementation task if accepted. This should be prioritized, but it should not block the restricted pilot unless GPU support is a pilot requirement.

### GPU Policy

Supported position:

- CPU remains the guaranteed baseline.
- GPU is an optional acceleration path.
- Runtime should auto-detect GPU capability and fall back to CPU.
- Users should not need separate code paths.
- Failure to initialize GPU should not prevent CPU detection unless the user explicitly requires GPU.

### Implementation Shape

Add a runtime device abstraction:

- New or refactored module: `webapp/ts_model_runtime.py` or similar.
- Environment controls:
  - `TOWERSCOUT_DEVICE=auto|cpu|cuda`
  - `TOWERSCOUT_REQUIRE_GPU=0|1`
  - future ONNX equivalent for provider preference
- Readiness/status output:
  - selected device
  - GPU available
  - GPU attempted
  - fallback reason
  - CUDA/driver/runtime summary when available

For the current restricted-pilot PyTorch path:

- Use `torch.cuda.is_available()` for current GPU detection.
- Keep CPU fallback as default.
- Log GPU selection clearly.
- Add a bounded test stub that can simulate GPU available/unavailable.

For the public ONNX path:

- Prefer ONNX Runtime provider order:
  - `CUDAExecutionProvider`
  - `CPUExecutionProvider`
- If CUDA provider is unavailable or fails initialization, fall back to CPU and log why.
- Keep CPU-only ONNX package as the default unless GPU packaging is intentionally validated.

### Packaging Decision

Do not silently bloat the default public image with GPU runtime dependencies. Use one of these models after validation:

1. CPU-only default image plus optional GPU image.
2. CPU-only default image plus documented local GPU runtime extension.
3. Single image only if GPU dependencies are license-compatible, size-acceptable, and validated on target hardware.

Acceptance:

- CPU-only machine starts and detects normally.
- GPU-capable machine uses GPU automatically when configured and supported.
- If GPU initialization fails, CPU fallback works with clear diagnostics.
- Release docs distinguish validated GPU environments from best-effort support.
- Public GPU packaging does not introduce new license or redistribution issues.

## Phase 4: Public-Compliant ML Runtime Migration

This phase is the largest public-release blocker.

### Detector Migration

Files:

- `webapp/ts_yolov5.py`
- `webapp/ts_yolov5_local.py`
- `webapp/vendor/yolov5_local/`
- `webapp/requirements.txt`
- `Dockerfile`
- `compose.yaml`
- model asset manifest/docs
- detection tests

Plan:

- Create a detector interface that preserves current TowerScout outputs.
- Build an ONNX detector PoC, or another legally clean runtime if ONNX fails.
- Confirm preprocessing, postprocessing, NMS, confidence thresholds, class mapping, and output schema.
- Compare against current YOLO path on a fixed validation sample.
- Remove Ultralytics and vendored YOLO from the public default path.
- Keep any legacy AGPL path only in restricted/private branches or under separate licensing.

Acceptance:

- No Ultralytics package dependency in public default runtime.
- No vendored YOLO code in public default release line.
- Detection output remains compatible with review/export workflows.
- Accuracy/performance deltas are documented and accepted.

### Classifier Migration

Files:

- `webapp/ts_en.py`
- classifier model assets
- `webapp/requirements.txt`
- tests

Plan:

- Treat EfficientNet as in-scope for model governance, not an unrelated detail.
- Confirm rights for the base architecture, pretrained weights, project weights, and conversion.
- Replace `torch.load()` with safer loading where possible.
- Prefer ONNX export or another non-pickle runtime for public builds.
- Keep classifier output contract stable.

Acceptance:

- Public classifier path does not load untrusted pickle-backed weights.
- Model terms and hashes are documented.
- Classifier behavior is validated against current known outputs.

## Phase 5: Public Codebase Cleanup And Refactor

This is the work needed to be proud of the public repo. It should happen before the public line opens, but after the restricted pilot path is stable enough that cleanup can be regression-tested against real workflows.

### Cleanup Principles

- Preserve outbreak-investigation workflows.
- Preserve Google and Azure behavior unless intentionally changed.
- Preserve export/restore/manual tower semantics.
- Keep cleanup staged and test-backed.
- Avoid broad rewrites without behavior anchors.

### Backend Refactor

Targets:

- `webapp/towerscout.py`
- detection routes
- config/setup routes
- provider routes
- export/restore/upload routes
- asset management
- support diagnostics

Plan:

- Split route groups into Flask blueprints or well-scoped modules.
- Move detection orchestration into a service layer.
- Move model runtime behind detector/classifier interfaces.
- Consolidate provider selection and provider availability logic.
- Remove or explicitly quarantine Bing compatibility drift.
- Standardize structured errors and logging.
- Add support-bundle generation as a safe allowlist service.

Acceptance:

- `towerscout.py` is no longer the catch-all for unrelated concerns.
- Detection/export/restore tests still pass.
- Setup/settings behavior is preserved.
- Support diagnostics avoid secrets and sensitive data by design.

### Frontend Cleanup

Targets:

- `webapp/js/src/`
- `webapp/build.js`
- generated `webapp/js/towerscout.js`
- provider state and review flows

Plan:

- Preserve current modular source layout.
- Treat generated bundle as build output.
- Consider `TASK-060 Frontend Build Modernization` after release package stability.
- Remove stale generated/original JS artifacts if safe.
- Tighten provider state handling and reduce legacy globals where practical.
- Maintain browser smoke tests for Google and Azure.

Acceptance:

- Build is reproducible.
- Generated files are clearly marked.
- Provider switching, detection review, manual tower, and export flows remain stable.

### Repo Hygiene And Public Surface Cleanup

Plan:

- Remove or exclude training notebooks, scratch artifacts, restricted data, model files, and private planning docs from the clean public line unless intentionally included.
- Normalize license headers after Apache-2.0 authority is established.
- Remove `LICENSE.TXT`/package metadata conflicts.
- Clean `.env.example` of unsupported provider drift.
- Review README for public-facing claims.
- Run secret and large-file scans.
- Decide which `.agent_work` artifacts, if any, belong in the public repo.

Acceptance:

- Public repo contains only intended public source, docs, tests, and release scripts.
- No model weights or restricted data are tracked.
- No internal-only or CDC/client-sensitive references remain unless explicitly approved.

### Quality Gates

Plan:

- Make black formatting blocking after a repo-wide format pass.
- Decide when mypy and bandit become blocking or scoped-blocking.
- Move CI from Node 18 to a supported Node LTS after validating frontend tests.
- Add release package tests.
- Add image build and smoke checks as required release gates.
- Keep Windows/PowerShell validation explicit through `TASK-068`.

Acceptance:

- Public release branch has clean, predictable CI.
- Release gates fail on meaningful public-release risks.
- Tests cover setup, readiness, asset validation, launcher behavior, provider config, and bounded detection.

## Phase 6: Public Release Line Creation

Prerequisites:

- Rights evidence pack complete.
- Clean public history decision complete.
- Ultralytics/YOLO default path removed or separately licensed.
- EfficientNet/classifier governance resolved.
- Compliance files created and packaged.
- Provider terms packaged.
- Asset import allowlist-only.
- Release manifest and SBOM flow implemented.
- Code cleanup/refactor tranche complete.
- CI public-release gates active.

Steps:

1. Create clean public release line.
2. Import only approved source/docs/tests/scripts.
3. Apply Apache-2.0 to approved TowerScout-authored code.
4. Add third-party, model, data, and provider notices.
5. Build public image.
6. Publish SBOM/checksums/manifest.
7. Publish public source release.
8. Publish control ZIP through GitHub Releases.
9. Publish model/data instructions or assets only under documented authority.
10. Run clean-laptop acceptance test.
11. Get final owner/legal/reviewer signoff.

Exit criteria:

- A non-developer user can deploy from GitHub Releases with intact folder structure and clear asset instructions.
- The source release does not include model weights under the Apache source license.
- The public default runtime does not depend on Ultralytics/YOLO AGPL components.
- Release artifacts are verifiable and revocable.

## Phase 7: Pilot, Feedback, And Public Go/No-Go

Restricted pilot:

- Use current container-first release package once Sprint 06 validation passes.
- Keep distribution controlled.
- Capture install/setup/runtime friction.
- Capture GPU demand and hardware profile data.
- Capture support-bundle adequacy.
- Triage pilot issues into:
  - public-release blockers
  - V1 patch items
  - V2 backlog
  - documentation fixes

Public go/no-go:

- Do not publish public compliant release until all public blockers are closed.
- Do not open the public repo until cleanup/refactor and rights evidence are complete.
- Do not promise GPU support unless the validated GPU path exists.

## Recommended Task Ordering

Near-term Sprint 06:

1. Continue `TASK-071`.
2. Pull `TASK-069` into active parallel work.
3. Pull `TASK-076` into active parallel work.
4. Promote `TASK-075` to an early decision/design task for GPU support.
5. Run `TASK-066`.
6. Pull `TASK-074` if runtime setup friction appears, or proactively if capacity allows.
7. Complete `TASK-073`.

Post-RC / before public:

8. `TASK-067` CI release gate tightening.
9. `TASK-068` Windows test portability.
10. New task: Podman-first auto-detection implementation if not handled under `TASK-074`.
11. New task: compliance file/package/image payload.
12. New task: staged allowlist-only asset import.
13. New task: release manifest/SBOM/revocation implementation.
14. New task: public ML runtime PoC and migration.
15. New task: GPU auto-detect and CPU fallback implementation, depending on `TASK-075`.
16. New task: public repo cleanup/refactor tranche.
17. `TASK-060` frontend build modernization if still beneficial after cleanup planning.
18. `TASK-058` and `TASK-059` backend architecture work after release path stabilizes, unless public cleanup requires pulling parts forward.

## Questions For Reviewer Second Opinion

Ask the reviewer to challenge these points specifically:

1. Is the clean public release line preferable to preserving legacy history with caveats?
2. Is manual model import the correct default until redistribution permission is written?
3. Is ONNX Runtime the right preferred target, or should another non-Ultralytics runtime be evaluated first?
4. Should Podman-first auto-detection be enforced globally or only in release packages?
5. Should GPU support ship as a separate optional image/profile or only as documented best-effort acceleration?
6. Which repo folders and planning artifacts should be excluded from the clean public line?
7. Are provider API terms sufficiently handled by `PROVIDER_TERMS.md`, Setup Wizard references, and docs?
8. Are the revocation mechanics strong enough for both pilot and public releases?

## References

- Apache license application guidance: https://www.apache.org/legal/apply-license
- Podman Compose documentation: https://docs.podman.io/en/latest/markdown/podman-compose.1.html
- Podman save/load documentation: https://docs.podman.io/en/latest/markdown/podman-save.1.html
- GitHub artifact attestations: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
- GitHub Releases: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
- Docker BuildKit SBOM attestations: https://docs.docker.com/build/metadata/attestations/sbom/
- PyTorch `torch.load` warning: https://docs.pytorch.org/docs/stable/generated/torch.load.html
- Google Maps Platform terms: https://cloud.google.com/maps-platform/terms
- Microsoft Product Terms: https://www.microsoft.com/licensing/terms/productoffering/MicrosoftAzure/MCA
