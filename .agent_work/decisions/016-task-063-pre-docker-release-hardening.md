# Decision 016: TASK-063 Pre-Docker Release Hardening Decisions

**Status**: Accepted
**Date**: 2026-04-29
**Task**: `TASK-063: Pre-Docker Release Hardening And CI Reproducibility Gate`
**Scope**: Release engineering, dependency repeatability, CI security, upload policy, support boundary, and pre-Docker operational contracts

## Context

`TASK-063` was created as a release-hardening gate before `TASK-025` Docker containerization. The goal was to resolve or explicitly accept review findings before Docker turns the current host runtime into the v1 local deployment baseline.

The task intentionally stayed adjacent to Docker rather than becoming Docker implementation. It clarified the release/security/support contracts that Docker must inherit:

- dependency versions and repeatability
- frontend lockfile policy
- GitHub Actions pinning and permissions
- CI advisory versus blocking interpretation
- model upload support boundary
- upload request-size alignment
- insecure TLS troubleshooting boundary
- performance log file ownership
- provider API key restriction guidance
- v1 supported and unsupported environments
- minimum support diagnostics
- residual YOLO/Torch Hub audit evidence
- owner-approved risk acceptance requirements

`TASK-052` and `TASK-062` were already complete when `TASK-063` began, so this task built on the corrected smoke-test and local YOLO-loader baseline.

## Decision Summary

`TASK-063` made the following decisions:

1. Use patched exact Python dependency pins for the reviewed Pillow and Requests findings.
2. Track `package-lock.json` as the frontend install contract and require Node 18+.
3. Pin release-relevant GitHub Actions to immutable commit SHAs.
4. Keep workflow permissions least-privilege for the current public repository.
5. Treat CI checks as either release-blocking or advisory, rather than pretending every existing check is equally release-gating.
6. Keep the active YOLO runtime on the local vendored loader path, with runtime dependency preflight checks.
7. Disable browser `.pt` / `.pth` model upload by default.
8. Treat model-weight updates as a persistent asset-volume/filesystem concern, not a normal browser upload workflow.
9. Align Flask, Waitress, and validator request-body limits through one setting.
10. Keep insecure TLS disabled by default and document it only as local troubleshooting.
11. Split structured performance events away from CSV performance metrics.
12. Document provider key restriction guidance for Google and Azure.
13. Keep the v1 release boundary narrow and explicit.
14. Define minimum v1 support diagnostics.
15. Require explicit owner approval for any unresolved pre-Docker risk acceptance.

## Decisions

### 1. Python Dependency Baseline

**Decision**: Pin `Pillow==12.2.0` and `Requests==2.33.1` in `webapp/requirements.txt`, and align the YOLO runtime dependency preflight in `webapp/ts_yolov5.py`.

**Context**: The initial `TASK-063` pass moved from older vulnerable pins to reviewed fixed versions. GitHub Advanced Security / Trivy then reported that `Pillow==12.1.1` and `Requests==2.32.4` still had findings. The PR was updated to `Pillow==12.2.0` and `Requests==2.33.0`. A final reviewer noted that `Requests==2.33.1` was already available and preferable because the repo uses exact pins.

**Options Considered**:

- Keep older pins and risk-accept findings.
- Pin the first fixed versions only.
- Pin the latest reviewed patch versions available during PR review.

**Rationale**: Exact pins create a concrete release baseline. Since the repo intentionally uses exact runtime pins rather than lower bounds, the safer and cleaner release posture is to use the latest reviewed patch version for the affected dependency when compatibility validation passes.

**Impact**:

- Keeps code scanning clean for the reviewed findings.
- Makes the runtime dependency preflight stricter and aligned with the manifest.
- Slightly increases dependency drift risk compared with the prior environment, but focused and full unit validation passed.

**Review**: Revisit during pinned dependency review, Docker image build lockfile decisions, and any new dependency advisory.

### 2. Frontend Lockfile And Node Policy

**Decision**: Track `package-lock.json` and align the frontend engine policy to Node `>=18.0.0`.

**Context**: A local `package-lock.json` existed but was ignored by `.gitignore`, which made frontend dependency repeatability ambiguous. The committed lockfile resolves Puppeteer dependencies that require Node 18 or newer.

**Options Considered**:

- Continue ignoring `package-lock.json`.
- Track `package-lock.json` and keep the old Node 16 policy.
- Track `package-lock.json` and update Node policy to match the resolved dependency tree.

**Rationale**: A tracked lockfile is the normal npm reproducibility contract. Keeping Node 16 in `package.json` while the lockfile required Node 18 would create a misleading install policy.

**Impact**:

- Future frontend installs should use `npm ci`.
- CI/release packaging has a deterministic npm dependency baseline.
- Users or developers with Node 16 must upgrade to Node 18+ for frontend validation tooling.

**Review**: Revisit if `TASK-060` modernizes the frontend build or if Puppeteer/browser test tooling changes.

### 3. GitHub Actions Pinning

**Decision**: Pin release-relevant GitHub Actions to immutable commit SHAs and keep trailing comments showing the reviewed source tag.

**Context**: The previous workflow used movable refs such as `actions/checkout@v5` and `aquasecurity/trivy-action@master`. The release-hardening review called out supply-chain risk from floating action refs.

**Options Considered**:

- Keep movable version tags.
- Pin only Trivy and leave other actions on tags.
- Pin all release-relevant third-party actions to full commit SHAs.

**Rationale**: Full commit SHAs are immutable in practice and match GitHub Actions hardening guidance. Trailing tag comments preserve human readability and make future update reviews easier.

**Impact**:

- Improves CI supply-chain reproducibility.
- Requires an explicit update cadence so pinned actions do not silently age.
- Makes workflow file lines less readable, but the comments offset that.

**Review**: Monthly during sprint planning, and immediately after advisories affecting used actions.

### 4. Workflow Permissions

**Decision**: Use global `contents: read`; add `security-events: write` only to the security job.

**Context**: The security job uploads SARIF results. The repo is public, so the current permission set is sufficient for the current workflow shape. A reviewer noted that private repositories may also need `actions: read` for SARIF upload.

**Options Considered**:

- Leave default workflow permissions implicit.
- Grant broad permissions globally.
- Use a least-privilege default and job-specific elevated permission only where needed.

**Rationale**: Least-privilege permissions reduce blast radius if a workflow or third-party action is compromised. The repo is public, so the private-repo SARIF `actions: read` caveat is not needed now.

**Impact**:

- Better CI security posture.
- Future jobs must explicitly justify extra permissions.
- If repository visibility changes to private, the security job permissions may need review.

**Review**: Revisit if the repo becomes private, SARIF upload fails due to permissions, or new CI jobs are added.

### 5. CI Release Interpretation

**Decision**: Document which CI checks are release-blocking and which remain advisory.

**Context**: The CI workflow already had several `continue-on-error` checks. Without explicit interpretation, release readiness could be misread as stronger than the actual maintained baseline.

**Options Considered**:

- Treat all checks as equally blocking.
- Leave advisory status implicit.
- Explicitly document blocking versus advisory checks for v1 release candidates.

**Rationale**: The project benefits from advisory scans, but release decision-making must be honest about which checks currently block a candidate and which require manual interpretation.

**Impact**:

- Reduces ambiguity in release sign-off.
- Preserves advisory coverage without blocking on known environment-sensitive suites.
- Requires release notes/handoff to call out meaningful advisory failures.

**Review**: Revisit after integration/browser/Docker checks become stable enough to promote.

### 6. YOLO Runtime And Torch Hub Audit

**Decision**: Preserve the local vendored YOLO loader as the supported runtime path and keep runtime dependency preflight checks aligned with the manifest.

**Context**: Earlier tasks replaced the mutable Torch Hub load path with a TowerScout-owned local loader. `TASK-063` needed to prove no supported runtime path fell back to Torch Hub, GitHub bootstrap, or stale legacy inference behavior.

**Options Considered**:

- Reopen the loader architecture.
- Rely on documentation only.
- Keep the local loader and validate/test the current contract.

**Rationale**: `TASK-057` and `TASK-062` already established the corrected loader contract. `TASK-063` needed evidence and alignment, not another loader redesign.

**Impact**:

- Docker can inherit a local source runtime instead of relying on first-run GitHub access.
- Dependency preflight failures are clearer before model initialization.
- Any future loader change must preserve this no-Hub-supported-runtime contract unless explicitly approved.

**Review**: Revisit if model loading changes, if model weight formats change, or if Docker asset packaging introduces new loader paths.

### 7. Browser Model Upload Default

**Decision**: Disable browser `.pt` / `.pth` upload by default with `TOWERSCOUT_ENABLE_MODEL_UPLOAD=false`; allow opt-in only for trusted local-admin/developer workflows.

**Context**: PyTorch model files must be treated as trusted code artifacts. Loading untrusted `.pt` files can execute code. The previous browser upload surface made model upload appear like a normal end-user workflow.

**Options Considered**:

- Leave browser model upload enabled for all users.
- Remove model upload permanently.
- Disable by default and keep an explicit trusted override.

**Rationale**: The v1 local release should not normalize arbitrary browser-uploaded model execution. The trusted override preserves developer/admin flexibility without exposing normal users to the risky path.

**Impact**:

- Safer default for end users.
- Reduces support risk around arbitrary model uploads.
- Developers/admins can still opt in for trusted local testing.
- Users need a separate documented model-weight update path.

**Review**: Revisit if TowerScout adopts a safer model artifact format, signed weights, hash validation, admin authentication, or a formal model registry/update workflow.

### 8. Model Weight Packaging And Update Path

**Decision**: Treat model weights and other large runtime assets as Docker/runtime assets managed through persistent storage, not through browser upload.

**Context**: Users still need a way to obtain and update YOLO weights, EfficientNet weights, ZIP-code data, and other large assets after containerization. Disabling browser model upload does not solve or block that; it clarifies that browser upload is not the primary update channel.

**Options Considered**:

- Bake all weights into the container image.
- Require users to upload weights through the web UI.
- Download weights on first run and persist them in a Docker volume.
- Bundle weights beside the release and mount/copy them into a persistent asset directory.

**Rationale**: Large model files are operational assets. A persistent volume or filesystem asset directory survives container replacement and is better suited for initial bootstrap, upgrades, rollback, and support diagnostics. Browser upload is poorly suited for large weights, trusted-code validation, and repeatable release packaging.

**Impact**:

- `TASK-025` must define the final asset inventory and delivery method.
- Docker packaging must provide a persistent model asset directory or volume.
- Users should receive model updates through a release asset, first-run download, or documented filesystem replacement path.
- The trusted upload override remains a convenience path, not a packaging strategy.

**Review**: Revisit in `TASK-025` when deciding whether specific assets are baked into the image, shipped beside the image, or downloaded on first run.

### 9. Upload And Request-Body Limits

**Decision**: Align Flask `MAX_CONTENT_LENGTH`, Waitress `max_request_body_size`, and `TowerScoutValidator.MAX_FILE_SIZE` through `TOWERSCOUT_MAX_REQUEST_BODY_BYTES`, defaulting to 50 MiB.

**Context**: Upload validation and server request-body limits were not aligned. Waitress defaults are much larger than TowerScout's application validation expectations.

**Options Considered**:

- Leave each layer with separate defaults.
- Raise limits to support large browser model uploads.
- Use one conservative v1 request-size setting across app/server/validator.

**Rationale**: One setting reduces confusion and prevents the server from accepting request bodies that the app later rejects. Since browser model upload is not the normal model-update path, the default can remain conservative.

**Impact**:

- Reduces exposure to accidental or abusive large requests.
- Makes the limit app-wide, not model-upload-specific.
- Large dataset and image workflows must fit the configured limit or require a deliberate later change.

**Review**: Revisit if dataset restore or upload workflows require larger supported request sizes.

### 10. Insecure TLS Boundary

**Decision**: Keep `TOWERSCOUT_ALLOW_INSECURE_TLS=false` by default and document it only as a local troubleshooting exception.

**Context**: Some enterprise networks or local certificate stores can break TLS validation. The environment flag exists as an escape hatch, but it should not become normal supported operation.

**Options Considered**:

- Remove the insecure TLS option.
- Leave it undocumented.
- Keep it off by default and document it as local troubleshooting only.

**Rationale**: Removing the option would make some difficult local environments harder to diagnose. Leaving it undocumented invites misuse. A troubleshooting-only contract is the right balance.

**Impact**:

- Normal v1 runtime remains TLS-verified.
- Support can use the flag for constrained environments.
- Docker defaults must not enable insecure TLS.

**Review**: Revisit if enterprise certificate configuration becomes a formal setup feature.

### 11. Performance Log File Contract

**Decision**: Keep `webapp/logs/performance.log` as CSV metrics and move structured performance events to `webapp/logs/performance_events.jsonl`.

**Context**: Before `TASK-063`, structured logging and CSV performance metrics could target the same `performance.log` filename with incompatible formats.

**Options Considered**:

- Leave both writers targeting `performance.log`.
- Rename the CSV file.
- Keep the existing CSV filename and move structured events to a new JSON Lines file.

**Rationale**: Existing setup/settings performance summaries already read `performance.log` as CSV. Preserving that file name avoids breaking the current support path while removing format collision.

**Impact**:

- Support tools can reliably parse `performance.log` as CSV.
- Structured event logs have a clear separate destination.
- Future documentation must reference the correct file for each use case.

**Review**: Revisit if performance telemetry is redesigned or centralized.

### 12. Provider API Key Guidance

**Decision**: Document provider-side key restriction guidance for Google and Azure, including browser-exposed versus server-side key concerns.

**Context**: TowerScout uses provider keys for map and geocoding workflows. Setup/settings mask keys locally, but provider-side restrictions remain part of safe release operation.

**Options Considered**:

- Treat provider key restrictions as out of scope.
- Document only that keys are required.
- Document practical provider-side restrictions and rotation guidance.

**Rationale**: Local masking is not enough. Users need clear guidance that browser-exposed Google keys should be referrer/API-restricted and Azure keys should remain local, rotated, and treated as sensitive.

**Impact**:

- Improves user operational security.
- Makes support documentation clearer.
- Does not implement enterprise centralized secret management, which remains out of v1 scope.

**Review**: Revisit if server-side proxying, separate server/browser keys, Azure Entra ID, SAS tokens, or enterprise deployment support become active work.

### 13. V1 Supported And Unsupported Environment Boundary

**Decision**: Keep v1 support narrow: Windows AMD64/x86_64 local Docker-oriented operation, online setup, single-user local use, CPU required, optional NVIDIA/CUDA only on compatible AMD64 hosts.

**Context**: Docker work can accidentally imply broad platform support. `TASK-063` needed to make support promises explicit before packaging begins.

**Options Considered**:

- Promise broad platform support now.
- Leave support boundary vague.
- Name supported and unsupported environments before Docker work starts.

**Rationale**: A narrow explicit promise reduces user confusion and prevents the first Docker milestone from inheriting unvalidated Mac, ARM64, offline, shared-server, or native-installer commitments.

**Impact**:

- Easier v1 support and validation.
- Some users may need to wait for later platform support.
- Docker documentation must align with the stated boundary.

**Review**: Revisit after v1 Docker baseline, launcher UX, and platform-specific validation mature.

### 14. Minimum Support Diagnostics

**Decision**: Define minimum support diagnostics for v1: log locations, config location, writable runtime locations, startup failure categories, asset/version visibility, and sensitive-data handling.

**Context**: A local packaged app needs enough diagnostics for users and support to distinguish app failures from Docker, network, provider-key, asset, and permission failures.

**Options Considered**:

- Defer diagnostics until after Docker.
- Document only log file paths.
- Define a minimum support contract before Docker packaging.

**Rationale**: Docker packaging should not start without knowing which runtime surfaces must be visible, persistent, or diagnosable. The minimum contract helps `TASK-025` avoid hiding critical failure modes.

**Impact**:

- Improves future support readiness.
- Gives Docker work concrete diagnostics and persistence targets.
- Requires release notes and user-facing docs to stay aligned.

**Review**: Revisit during Docker implementation and launcher/support tooling work.

### 15. Risk Acceptance Governance

**Decision**: Any unresolved `TASK-063` finding must have explicit owner-approved risk acceptance before `TASK-025` starts.

**Context**: The owner confirmed they are willing to approve risk acceptances when given sufficient context. The task needed to prevent implicit acceptance of known release risks.

**Options Considered**:

- Allow implicit deferral.
- Require informal comments only.
- Require structured owner-approved risk notes.

**Rationale**: Release-hardening findings are meaningful only if unresolved items are fixed or consciously accepted with impact, mitigation, timing, owner, and follow-up.

**Impact**:

- Prevents untracked pre-Docker risks from becoming the baseline.
- Adds governance overhead for any unresolved finding.
- No unresolved `TASK-063` finding remained after the final PR follow-up.

**Review**: Carry this pattern forward to `TASK-064`, `TASK-025`, and future release gates.

## Validation Evidence

`TASK-063` validation included:

- `.agent_work` structure validation
- dependency install/import smoke
- `pip check`
- focused upload route tests
- performance summary log parsing tests
- YOLO local-loader tests
- CI YAML parse
- package-lock tracking check
- floating GitHub Actions ref scan
- full unit suite
- PR code-scanning follow-up validation

Final local unit result recorded for the task:

```text
65 passed, 74 skipped, 17 warnings, 5 subtests passed
```

Warnings were existing `datetime.utcnow()` deprecation warnings in `ts_config.py` and `ts_errors.py`; they were not `TASK-063` blockers.

## Consequences For TASK-025

Docker work must inherit these contracts:

- Use the pinned Python and frontend dependency baselines unless deliberately revised.
- Preserve the tracked `package-lock.json` / `npm ci` frontend install contract.
- Preserve writable persistent storage for config, sessions, logs, uploads, temp/session data, map/geocode cache, and model assets as appropriate.
- Define the final runtime asset inventory and delivery method for YOLO weights, EfficientNet weights, ZIP-code data, and any first-run downloads.
- Keep browser model upload disabled by default.
- Treat model updates as persistent asset-directory or volume operations, not normal browser uploads.
- Preserve the performance log file split.
- Keep insecure TLS off by default.
- Preserve the narrow v1 support boundary unless the project intentionally expands validation scope.

## References

- `.agent_work/tasks/active/TASK-063-pre-docker-release-hardening.md`
- `.agent_work/context/guides/Pre-Docker-Release-Hardening-Contract.md`
- `.github/workflows/ci.yml`
- `webapp/requirements.txt`
- `webapp/towerscout.py`
- `webapp/ts_yolov5.py`
- `webapp/ts_logging.py`
- `webapp/ts_performance.py`
- `tests/unit/test_flask_routes.py`
- `tests/unit/test_yolov5_local_loader.py`
