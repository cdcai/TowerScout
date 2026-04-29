# Pre-Docker Release Hardening Contract

**Status**: Active for `TASK-063` and `TASK-025` planning
**Last Updated**: 2026-04-29
**Scope**: First local Docker-oriented TowerScout release boundary

## Purpose

This document records the release, CI, dependency, upload, provider-key, and support contracts that must be honored before Docker packaging turns the current host runtime into the v1 local deployment baseline.

## Dependency Repeatability

### Python Dependencies

- `webapp/requirements.txt` is the runtime dependency contract for the Flask application.
- Runtime dependencies remain top-level pinned for the pre-Docker release gate.
- `Pillow` and `Requests` must stay at versions that satisfy currently reviewed security findings before Docker work starts.
- Full transitive hash locking is deferred until the container image build policy is finalized in `TASK-025`; that task must decide whether to add a generated hash lock, use image digest pinning, or keep the current top-level pin strategy with explicit risk acceptance.

### Frontend Dependencies

- `package-lock.json` is the frontend install contract and must be tracked.
- Validation and release packaging should use `npm ci` from the repo root rather than `npm install`.
- The frontend test tooling requires Node 18 or newer because the committed lockfile resolves Puppeteer dependencies with a Node 18 engine requirement.

### Runtime Assets

- Large model/data assets are not solved by Python or npm pins.
- `TASK-025` must produce the runtime asset inventory and persistence strategy for YOLO weights, EfficientNet weights, ZIP-code data, and any first-run downloads.
- The expected v1 strategy remains first-run download plus persistent storage unless an asset is intentionally baked into the image and documented with its version/source.
- Browser model upload is not the normal v1 model-update path. Normal model updates should replace or download trusted weights into the persistent model asset directory or volume that `TASK-025` defines.
- Enabling `TOWERSCOUT_ENABLE_MODEL_UPLOAD=true` only re-enables a trusted local-admin/developer convenience path; it does not change the required Docker asset strategy for initial weights or larger model updates.

## CI Release Interpretation

For release-candidate readiness, treat CI checks as follows:

- Blocking: checkout/setup/install success, flake8 syntax/undefined-name gate, Python unit tests, workflow syntax validity, and successful generation/upload path for release-relevant artifacts where credentials are available.
- Advisory until separately hardened: Black formatting drift, mypy, Bandit, integration tests, Codecov upload, Docker build placeholder, Trivy scan, and SARIF upload.
- Advisory checks may remain `continue-on-error` only if the release handoff explicitly states that they did not pass or were not executed.
- Before a v1 release candidate is tagged, any advisory failure that indicates a real security, dependency, or packaging defect must be fixed or owner-approved as a release risk.

## GitHub Actions Pinning And Review Cadence

- Release-relevant third-party actions must use immutable commit SHAs in workflow `uses:` entries.
- Each pinned action line should keep a trailing comment with the reviewed source tag.
- Recurring review cadence: review pinned GitHub Actions monthly during sprint planning and immediately when GitHub, Trivy, Codecov, Docker, or Actions security advisories mention an action used by TowerScout.
- Updates should be made by resolving the desired tag to a new commit SHA, reviewing release notes/advisories, updating the trailing comment, and running workflow validation on a PR.

## Workflow Permissions

- Default workflow permissions are `contents: read`.
- The security job may request `security-events: write` so CodeQL SARIF upload can publish Trivy results to GitHub Security.
- New jobs must justify additional permissions in the PR or task log before being treated as release-relevant.

## Model Upload Boundary

- Browser `.pt`/`.pth` model upload is disabled by default for the first local release.
- Loading PyTorch model files is a trusted-code operation. Do not present model upload as a normal end-user workflow.
- Trusted local-admin/developer use may opt in with `TOWERSCOUT_ENABLE_MODEL_UPLOAD=true`.
- Flask `MAX_CONTENT_LENGTH`, Waitress `max_request_body_size`, and `TowerScoutValidator.MAX_FILE_SIZE` are aligned through `TOWERSCOUT_MAX_REQUEST_BODY_BYTES`; the default is 50 MiB.
- Larger trusted model replacement should use the configured model asset volume or filesystem path, not browser upload, unless a later task intentionally raises and validates the request-body boundary.

## TLS Troubleshooting Boundary

- `TOWERSCOUT_ALLOW_INSECURE_TLS` is off by default.
- Enabling it disables certificate verification in provider validation/geocoding paths and is only a local troubleshooting exception for constrained enterprise networks or broken local certificate stores.
- Do not document insecure TLS as a normal supported runtime mode, and do not enable it in Docker defaults.

## Provider API Key Restrictions

### Google

- Google Maps JavaScript API keys are browser-exposed by design when used by the client map.
- Restrict browser-exposed Google keys by HTTP referrer for the expected local origin, and restrict enabled APIs to the minimum needed for Maps JavaScript, Places, and Static Maps.
- If a separate server-side Google key is introduced later for backend-only geocoding/static calls, restrict it by IP where practical and separate it from browser-exposed usage.

### Azure

- Azure Maps subscription keys are currently used by the local app for provider workflows.
- Keep Azure keys local to the user's machine and masked in UI/status responses.
- For managed or enterprise deployments, prefer Azure Entra ID, SAS, or restricted key-rotation procedures over broad long-lived shared subscription keys.
- Rotate Azure primary/secondary keys periodically and after suspected exposure.

## Performance Log Contract

- `webapp/logs/performance.log` is the CSV detection metrics contract read by setup/settings performance summaries.
- `webapp/logs/performance.jsonl` is detailed JSON Lines output from `ts_performance.py`.
- `webapp/logs/performance_events.jsonl` is structured performance-event logging from `ts_logging.py`.
- Do not write multiple formats to the same filename.

## V1 Supported And Unsupported Environments

Supported for the first local release:

- Windows host on AMD64/x86_64.
- Docker Desktop or equivalent local Docker runtime capable of running Linux AMD64 containers.
- CPU execution required; NVIDIA/CUDA acceleration is optional only on compatible AMD64 hosts.
- Online setup with access to provider APIs and any documented first-run asset download endpoints.
- Single-user local operation.

Unsupported for v1 unless a later task changes this contract:

- Offline or air-gapped operation.
- Mac, Linux desktop support promises, ARM64 hosts, Raspberry Pi, or Apple Silicon native images.
- Native installer or launcher-only distribution.
- Multi-user/shared-server operation.
- Provider-key-free operation.
- Enterprise SSO, centralized secrets management, or centrally managed key distribution.

## Minimum Support Diagnostics

The v1 support contract must expose or document:

- Log locations: `webapp/logs/towerscout.log`, `webapp/logs/towerscout_errors.log`, `webapp/logs/performance.log`, `webapp/logs/performance.jsonl`, and `webapp/logs/performance_events.jsonl`.
- Config location: `webapp/config/.env`.
- Writable runtime locations: filesystem sessions, uploads, temp session directories, map/geocode caches, and configured model asset directories.
- Startup diagnostic categories: missing/invalid provider key, invalid `FLASK_SECRET_KEY`, model asset missing, first-run asset bootstrap failure, port conflict, Docker not running, network/proxy failure, and provider quota/auth failure.
- Asset/version visibility: app version or release tag, Python runtime version, Node/frontend lockfile version, YOLO model filename/version, EfficientNet model filename/version, ZIP-code data version/source, and pinned CI action review date.
- Sensitive-data handling: provider keys, investigation locations, imagery, exports, uploaded datasets, and logs should be treated as local sensitive data. Support bundles must not include unmasked secrets.

## Risk Acceptance Rule

Any unresolved `TASK-063` finding must have an owner-approved note before `TASK-025` starts. The note must include:

- issue
- deferral rationale
- expected user or release impact
- mitigation or workaround
- review timing
- follow-up owner and task
- explicit owner approval
