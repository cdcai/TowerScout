# TASK-025 Containerization Decision Analysis

**Date**: 2026-05-01
**Status**: Decision-support analysis for `TASK-025`; updated with finalized pre-task decisions through May 5, 2026
**Scope**: Docker-compatible / OCI v1 local deployment baseline, runtime persistence, assets, startup behavior, validation, GitHub-first release packaging, host-runtime options, and path to a future polished local release
**Primary Audience**: Project owner, implementers, reviewers, and anyone making product or technical decisions before containerization work starts

---

## Executive Summary

TowerScout is ready to move into Docker containerization only because several earlier tasks corrected the runtime baseline: setup/settings now exist, config is persisted through `webapp/config/.env`, detection progress/cancel behavior exists, the YOLO path no longer depends on Torch Hub/GitHub at runtime, and a current smoke-test baseline exists.

`TASK-025` should not be treated as "just add a Dockerfile." It is the task that turns TowerScout's current host runtime into a supported v1 local deployment contract. That means the project must lock decisions about persistence, first-run assets, config and secrets, startup behavior, health/readiness, validation, logs, support diagnostics, and container image update behavior.

Recommended high-level direction:

- Support Windows AMD64 single-user local use first.
- Ship a CPU-first Docker-compatible / OCI container baseline.
- Keep the default Compose flow simple and CPU-only.
- Use persistent container volumes for durable config, assets, logs, uploads, sessions, and cache.
- Use a manifest-driven first-run asset bootstrap for large runtime assets, with checksum verification.
- Provide a manual asset-bundle fallback for restricted networks.
- Generate and persist `FLASK_SECRET_KEY` automatically on first container startup.
- Add a real health/readiness contract before `TASK-054` launcher work.
- Run the existing `TASK-052` smoke contract against the container instead of inventing a parallel Docker-only test.
- Keep `TASK-025` focused on build/run/persistence. Leave launcher UX, background jobs, native installer work, and broad backend decomposition to later tasks.
- Avoid Docker Desktop-specific implementation assumptions. Docker Desktop and Podman Desktop are host-runtime options that require separate licensing, endpoint, virtualization, Compose/provider, proxy/certificate, and support validation before either is promised to end users.
- Treat Podman as the preferred open-source Windows runtime target, with one adjustment mark: Podman support is not a release promise until the Windows Podman Desktop / Podman machine compatibility spike passes or is explicitly risk-accepted.
- Make GitHub Releases the default user-facing delivery control plane. The normal package should be a GitHub Release ZIP with a pinned GHCR image reference by digest, scripts, Compose-compatible configuration, manifests, checksums, and docs. Raw source clone/build remains a developer/support path, not the preferred normal-user path.
- Treat the client's runtime/tooling open-source preference as addressed by the Podman-first target, while keeping TowerScout's application license/open-source suitability as a separate product/legal clarification because the repo currently identifies `CC-BY-NC-SA-4.0`.

The ideal path is not "Docker forever." The ideal path is:

1. Use an OCI-compatible container baseline to make the runtime reproducible.
2. Add a lightweight launcher on top so end users do not need raw Docker CLI knowledge.
3. Use the container baseline to identify the true state/job boundaries.
4. Later evolve toward a more polished managed local package, remote managed container host, or installer if desktop container runtimes become a barrier for target users.

## May 4 Runtime-Host Review Addendum

After the original May 1 decision analysis, two additional reviewer inputs changed the host-runtime framing:

1. **Docker Desktop licensing and managed-endpoint review**
   - Government use of Docker Desktop introduces a real licensing/procurement gate.
   - Docker Desktop on Windows also depends on supported Windows versions, virtualization, WSL2 or Hyper-V configuration, RAM, and installation/permission prerequisites.
   - This does not invalidate the containerization architecture, because TowerScout does not require Docker Desktop-specific GUI features or extensions.
   - It does mean TowerScout should not treat "end users install Docker Desktop" as an unconditional v1 product assumption.

2. **Podman impact review**
   - Podman can run an OCI/Docker-compatible container approach and reduces dependency on Docker Desktop as a product.
   - Podman does not eliminate Windows-local container friction. Windows Podman still needs a Linux VM path such as WSL2 or Hyper-V, plus Podman machine setup, Compose/provider configuration, proxy/certificate handling, and support validation.
   - Podman strengthens the case for engine-aware commands, rootless/non-root assumptions, named volumes, and remote Linux container-host fallback.
   - Podman should be treated as a first-class compatibility target after a focused validation spike, not assumed equivalent without testing.

Updated framing:

- `TASK-025` should produce a **Docker-compatible / OCI runtime contract**, not a Docker Desktop-specific implementation.
- Docker Desktop, Podman Desktop, Linux Docker, Linux Podman, and remote managed container hosts are **runtime-host choices** layered over that contract.
- The final user-facing runtime does **not** have to be decided before `TASK-025` starts, but the implementation must avoid choices that make Docker Desktop the only viable path.
- Before release, the project must decide which runtime host is actually supported for users and validate that path end to end.

---

## May 4 Open-Source Deployment And GitHub Release Addendum

The client feedback changes the preferred release-packaging direction:

> The client wants an open-source-friendly way for sites to deploy TowerScout from GitHub to laptops with the correct folder structure, clear instructions for required extra files, and a simplified local start/run path.

Updated interpretation:

- "From GitHub" should mean **GitHub is the release control plane**, not that every normal user must clone source and build locally.
- A clean repository clone is not a complete TowerScout runtime package because model weights, EfficientNet assets, and ZIP-code data are intentionally outside git.
- GitHub Releases should carry the release notes, quick start, scripts, Compose-compatible runtime config, asset manifest, checksums, and either an image archive or image/registry reference.
- Heavy assets can be attached to GitHub Releases when practical, but the manifest may point to governed object storage or internal distribution if size, access control, bandwidth, or policy makes GitHub-hosted binaries awkward.
- Podman is the preferred open-source runtime target because it supports OCI/Docker-compatible images and Dockerfile/Containerfile-style builds, but Windows Podman still requires a Linux VM path such as WSL2 or Hyper-V and has Compose/provider, proxy/certificate, networking, volume, and support nuances.
- Docker compatibility should be preserved because it keeps the image portable and gives developers/support staff another validation path, but Docker Desktop should not be the assumed government end-user product path.
- If sites need visible local folders, support an optional host-visible data-directory profile. Keep named volumes as the safer default unless validation shows a host-visible profile is equally reliable.
- The application's own license suitability is separate from runtime-tooling choice. Choosing Podman may satisfy an open-source runtime/tooling preference, but it does not answer whether `CC-BY-NC-SA-4.0` satisfies the client's application licensing expectations.

Updated path:

1. Build the OCI-compatible runtime contract.
2. Package the normal user path through GitHub Releases.
3. Validate Podman as the preferred open-source runtime target before promising it.
4. Keep Docker-compatible commands as a supported developer/support fallback where licensing and endpoint policy allow.
5. Use `TASK-054` to wrap the selected runtime path in a simple start/stop/status UX.

---

## Finalized Pre-Task-025 Decision Lock

The major pre-task decision items now have accepted answers. `TASK-025` can begin from this locked contract rather than treating the items below as open-ended research questions.

The one adjustment mark is:

> Podman-first is the selected target, but it is not an already-proven release promise. The Windows Podman Desktop / Podman machine compatibility spike must pass, or receive explicit owner-approved risk acceptance, before end-user documentation promises Podman support.

### Accepted Decision Set

| Decision | Finalized answer for `TASK-025` |
| --- | --- |
| `D-001` Supported v1 environment | Windows 11/AMD64, single-user local, CPU-first. NVIDIA/CUDA remains optional on compatible AMD64 hosts after validation. Mac, ARM64, offline, air-gapped, VDI, shared deployment, native installer behavior, and managed/remote hosting are not v1 promises. |
| `D-002` Image/distribution strategy | Registry-first, bundle-assisted. Use a GitHub Release ZIP as the normal user package with `compose.yaml`, `.env` template, scripts, docs, asset manifest, checksums, and a pinned GHCR image reference by digest. Optional OCI image archives are restricted-network fallbacks. Source clone/build is developer/support only. |
| `D-014` Large asset strategy | Use a versioned manifest and durable asset storage. Assets are staged before activation, verified with SHA-256, rechecked on startup/update, and recoverable through manual/restricted-network import. Large assets do not belong in git or the normal source checkout. |
| `D-016` Asset hosting/source | GitHub Releases host release metadata, manifests, checksums, and package files. Large binaries may live in governed object storage or an internal mirror when size, access control, bandwidth, or policy makes GitHub-hosted binaries unsuitable. |
| `D-020` Health/readiness contract | Add `/api/health` for liveness and `/api/readiness` for structured readiness. Readiness states are `starting`, `setup_required`, `degraded`, `ready`, and `fatal`, with redacted component details for config, assets, provider setup, version, and recovery guidance. |
| `D-030` CI container validation | Split routine CI from release-candidate validation. Routine CI builds/starts the image and checks health/readiness without private or heavyweight assets. Release-candidate/local validation runs real asset bootstrap and detection smoke. |
| `D-031` Runtime validation commands | Keep validation engine-aware. Podman commands are the preferred open-source path after the spike passes; Docker commands remain the compatible alternate where licensed/approved. Scripts should hide engine differences where practical. |
| `D-038` Runtime-host risk | Podman Desktop plus WSL2/Hyper-V is the preferred open-source Windows runtime target after validation. Docker Desktop remains secondary where licensing/procurement/endpoint policy allow. Linux Docker/Podman remain reference/developer/CI-compatible paths where practical. |
| `D-040` Documentation/support boundaries | Ship two layers: a GitHub-first end-user/operator guide and a technical OCI runtime contract. Both must cover prerequisites, unsupported environments, assets, persistence, reset/update, troubleshooting, support diagnostics, and sensitive local data handling. |
| `D-041` Application license/open-source suitability | Runtime/tooling open-source preference is addressed by the Podman-first target. TowerScout's application license suitability remains a separate product/legal clarification; choosing Podman does not change the current application license. |

### Accepted Technical Defaults

The remaining decision items are accepted as implementation defaults unless `TASK-025` discovers a concrete blocker:

- `D-003` through `D-008`: Python 3.11 slim or digest-pinned equivalent, explicit runtime dependencies, Dockerfile/Containerfile-compatible structure, frontend build stage, repeatable dependency policy, and practical non-root/rootless posture where feasible.
- `D-009` through `D-013`: normalized `webapp/` runtime path contract, named volumes by default, explicit persistence map, provider keys/config saved through setup/settings, and automatic first-run `FLASK_SECRET_KEY` generation into persistent config.
- `D-015` and `D-017` through `D-019`: asset manifest schema, EfficientNet base/project weights as managed assets, ZIP-code data as managed/versioned asset with path fix if needed, and startup behavior that lets setup/recovery remain reachable when recoverable assets are missing.
- `D-021` through `D-029`: categorized startup failure behavior, best-effort cache durability, persistent logs, persisted uploads with cleanup docs, trusted-admin-only model update policy, proxy/TLS defaults, localhost port binding with conflict recovery, GPU deferral, and realistic image-size expectations.
- `D-032` through `D-037`: documented update, backup, reset, sensitive-data, launcher-boundary, background-job deferral, and version/asset visibility contracts.
- `D-039`: practical v1 container hardening rather than strict read-only-root hardening in the first container release.

---

## 1. Containerization Roadmap Overview

### Phase 0: Already Completed Foundation

These completed or near-complete pieces are what make containerization realistic:

- `TASK-046`: Setup Wizard and Settings implemented.
- `TASK-051`: Runtime dependency audit and decision gate.
- `TASK-052`: Current integration smoke-test baseline.
- `TASK-056`: First-run reliability and runtime determinism hardening.
- `TASK-057`: Local YOLO runtime ownership and Torch Hub independence.
- `TASK-062`: Pre-Docker runtime cleanup and YOLO loader hardening.
- `TASK-063`: Pre-Docker release-hardening gate.
- `TASK-064`: Targeted runtime responsiveness and inference baseline.

These tasks mean containerization no longer has to solve foundational runtime uncertainty. `TASK-025` can focus on packaging, persistence, and validation.

### Phase 1: Lock The Container Runtime Contract

Before writing most containerization code, `TASK-025` should create or finalize:

- supported and unsupported v1 environments
- versioned runtime/persistence map
- large asset strategy and asset manifest
- first-run bootstrap/recovery behavior
- `FLASK_SECRET_KEY` generation and persistence behavior
- cache and geocode durability classification
- startup/health/readiness contract
- container runtime validation commands
- support diagnostics contract
- primary and secondary runtime-host targets, including Docker Desktop and Podman caveats

This phase prevents us from building a container that starts locally but fails as a real user release.

### Phase 2: Implement Image Definition And Compose-Compatible Run Config

Implementation should provide:

- Docker-compatible / OCI image definition, likely a `Dockerfile`
- Compose-compatible run configuration
- app startup command using Waitress
- pinned/runtime-controlled Python dependencies
- required Linux system packages for geospatial and image libraries
- persistent volumes
- sane defaults for CPU execution
- no dependency on host Python, host Node, or local manual package installs
- no Docker Desktop-specific implementation dependency unless the project explicitly accepts that release constraint

### Phase 3: Implement First-Run Runtime Preparation

The container should be able to start from an empty persistent data volume and:

- create required writable directories
- create or update `webapp/config/.env`
- generate and persist `FLASK_SECRET_KEY` if absent
- verify required assets
- download or report missing assets with actionable recovery guidance
- expose readiness/status clearly enough for later launcher polling

### Phase 4: Validate The Container As A Runtime Baseline

Validation should prove:

- clean build works
- container starts
- Setup Wizard works
- Settings save/load survives restart
- `FLASK_SECRET_KEY` survives restart/recreate
- assets are available or recoverable
- ZIP-code lookup works
- detection smoke path works
- logs are available
- upload/request limits match policy
- unsupported environments are not accidentally promised

### Phase 5: Document User-Facing Docker Use

Documentation should explain:

- prerequisites
- how to start
- how to stop
- where config lives
- where logs live
- where large assets live
- what first-run download means
- how to recover from missing/corrupt assets
- what is supported and unsupported

### Phase 6: Build A Launcher Over Docker (`TASK-054`)

After Docker is stable enough to target, `TASK-054` should add a launcher-first experience:

- start Docker services
- poll readiness
- open browser only when the app is reachable
- distinguish "Docker is running" from "TowerScout app is ready" from "assets are still bootstrapping"
- expose logs/status for troubleshooting

### Phase 7: Post-Docker Architecture Work

After Docker and launcher work:

- `TASK-058` should introduce a local job/state boundary for long-running detection work.
- More reliable crash/restart behavior can follow.
- A native installer, managed local package, or remote managed container-host option can be considered only after the container runtime contract is known and stable.

---

## 2. Context Needed To Make Informed Decisions

### Product Context

TowerScout is a Flask web application for identifying cooling towers from satellite/aerial imagery. It is intended to support public-health investigation and registry-building workflows. The most important user value is not a polished marketing page. It is reliable area definition, detection, review, manual correction, export, and restoration.

The Docker release should preserve:

- Google Maps and Azure Maps workflows
- location, ZIP-code, circle, and polygon search
- tile estimate before detection
- full detection workflow
- progress and cancel behavior
- review list and map interaction
- manual tower additions
- CSV/KML/dataset export
- dataset restore
- provider key setup/settings

### Current Runtime Shape

The app runs through `webapp/towerscout.py` using Waitress:

- host: `0.0.0.0`
- port: `5000`
- route surface includes setup/config, providers, geocoding, detection estimate/progress, detection, export, and restore

Important startup behavior:

- reads config from `webapp/config/.env` when present
- can migrate legacy `webapp/.env` into `webapp/config/.env`
- uses server-side filesystem sessions through Flask-Session
- currently generates an in-memory temporary Flask secret if `FLASK_SECRET_KEY` is absent
- loads EfficientNet eagerly unless `TOWERSCOUT_LAZY_MODEL_INIT` is enabled
- starts ZIP-code data and default YOLO engine when not run in `dev` mode

Nuance: the current host behavior can hide Docker issues. A developer may already have model weights, cached EfficientNet base weights, local Python packages, or working GDAL libraries. A clean container will not have those unless we explicitly add or bootstrap them.

### Current Path Helpers And Writable Locations

`webapp/ts_paths.py` anchors most runtime paths under `webapp/`:

- logs: `webapp/logs/`
- uploads: `webapp/uploads/`
- model params: `webapp/model_params/`
- YOLO models: `webapp/model_params/yolov5/`
- EfficientNet models: `webapp/model_params/EN/`
- map cache: `webapp/cache/maps/`
- geocoding cache: `webapp/cache/geocoding/`
- sessions: `webapp/flask_session/`
- temp: `webapp/temp/`
- session temp: `webapp/temp/session/`

Nuance: `webapp/ts_zipcode.py` currently reads ZIP-code data from a relative path:

```text
data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp
```

That works when the process working directory is `webapp/`, but it is fragile. Docker should either start with `WORKDIR /app/webapp` or the code should be adjusted to use an app-anchored path. The better long-term fix is app-anchored path resolution.

### Large Runtime Assets

Current local assets in this workspace include:

| Asset | Current path | Approx size | Notes |
| --- | --- | ---: | --- |
| YOLO weights | `webapp/model_params/yolov5/newest.pt` | 175 MB | Primary detector weights |
| EfficientNet project weights | `webapp/model_params/EN/b5_unweighted_best.pt` | 119 MB | Secondary classifier weights |
| ZIP-code shapefile | `webapp/data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp` | 823 MB | Boundary geometry |
| ZIP-code support files | `.dbf`, `.shx`, `.prj`, `.cpg`, metadata XML | 3 MB plus | Required by shapefile reader |

These folders are gitignored:

- `webapp/model_params/*`
- `webapp/data/*`
- `*.pt`
- `*.pth`

That means a clean repository clone will not necessarily include the assets needed for detection or ZIP-code lookup.

Nuance: EfficientNet uses `EfficientNet.from_pretrained('efficientnet-b5')`, which may require a base-model download/cache if not already present. That is a hidden first-run asset concern separate from the TowerScout-specific `b5_unweighted_best.pt` file.

### Provider And Network Reality

TowerScout is not fully offline:

- Google/Azure maps require internet.
- Provider key validation requires internet.
- imagery downloads require internet.
- reverse/forward geocoding require provider access.

The Docker release should not imply offline or air-gapped support.

### Security And Support Reality

Important support and security facts:

- API keys are stored locally in `.env` and masked in UI/status responses.
- Google Maps JavaScript API keys are browser-exposed by design.
- Provider keys should be restricted in the provider console.
- `.pt`/`.pth` model files are trusted-code artifacts, not normal end-user uploads.
- Browser model upload is disabled by default and should remain outside the normal release path.
- Logs, imagery, exports, uploaded datasets, and provider keys are sensitive local data.

### CI Reality

Current CI runs Python and frontend checks, but Docker build validation is still effectively placeholder behavior. After `TASK-025`, Docker build/run validation should become meaningful.

---

## 3. Decision Register

The following decisions should be made before or during early `TASK-025` implementation. The highest-risk decisions are marked "Lock before image definition" because changing them late is likely to cause rework.

### D-001: Supported V1 Environment

**Decision needed**: What host environments and runtime hosts does containerized v1 officially support?

Options:

1. Windows AMD64 local only, with one validated desktop runtime host.
2. Windows AMD64 local plus Linux AMD64 reference/support path.
3. Windows, Linux, Mac, ARM64, and broader platforms.

Pros and cons:

- Windows AMD64 local only:
  - Pros: matches current target, smaller validation matrix, easier support.
  - Cons: excludes some potential users.
  - Considerations: Docker Desktop licensing/endpoint policy and Podman machine/WSL2/Hyper-V may be unavailable on managed machines.
- Windows and Linux AMD64:
  - Pros: still manageable, helps developer and CI parity.
  - Cons: doubles support assumptions.
  - Considerations: Linux can be validated in CI, but end-user support still differs.
- Broad platform support:
  - Pros: attractive product story.
  - Cons: high validation cost, likely ARM64/PyTorch/geospatial friction.
  - Considerations: too much scope for v1.

**Final decision**: Lock the product boundary as Windows 11/AMD64 single-user local support, keep Linux AMD64 as a reference/developer/CI path where practical, and validate Podman as the preferred open-source Windows runtime target before release.

**Rationale**: This keeps v1 honest and testable while leaving room to expand after the container runtime works.

### D-002: Image Distribution Strategy

**Final decision**: Users receive a GitHub Release ZIP package backed by a pinned GHCR image reference by digest. Optional OCI image archives are restricted-network fallbacks. Local source build remains developer/support only.

Options:

1. Users build locally from repo.
2. Users pull a prebuilt image.
3. Users download a GitHub Release ZIP package containing scripts/config plus a pinned GHCR image reference by digest.
4. Support both release package and local build, but document release package as preferred.

Pros and cons:

- Local build:
  - Pros: no image registry required, transparent.
  - Cons: slow, fragile, requires Docker build knowledge, may fail on network/package issues.
- Prebuilt image:
  - Pros: easiest for users, repeatable, build complexity handled by release process.
  - Cons: requires image publishing, tagging, and security scanning.
- GitHub Release ZIP package:
  - Pros: best match for client request; can bundle quick start, scripts, Compose-compatible config, manifest, checksums, troubleshooting, and a pinned GHCR image reference by digest.
  - Cons: release packaging must be maintained and tested.
- Both:
  - Pros: user-friendly default plus developer escape hatch.
  - Cons: two paths must be tested or clearly tiered.

**Recommendation**: Use a GitHub Release ZIP package as the preferred user-facing path, backed by a prebuilt GHCR image pinned by digest. Preserve optional OCI image archives for restricted networks and local clone-and-build as a developer/support path.

**Rationale**: Non-technical local deployment should not depend on users compiling geospatial/PyTorch dependencies during first setup, and the client explicitly wants a GitHub-centered deployment path.

### D-003: Base Image And Python Version

**Decision needed**: Which base image should the Dockerfile use?

Options:

1. `python:3.11-slim` or digest-pinned equivalent.
2. `python:3.12-slim` or digest-pinned equivalent.
3. Full Debian/Ubuntu image.
4. CUDA-enabled base image.

Pros and cons:

- Python slim:
  - Pros: smaller, official, practical for CPU baseline.
  - Cons: requires explicit system dependencies.
- Full Debian/Ubuntu:
  - Pros: fewer missing library surprises.
  - Cons: larger image.
- CUDA base:
  - Pros: easier GPU story.
  - Cons: much larger, not needed for CPU baseline, increases support burden.

**Recommendation**: Start with Python 3.11 slim or digest-pinned equivalent for v1 CPU. Validate 3.12 later if needed.

**Rationale**: CI already covers Python 3.11 and 3.12, but PyTorch/geospatial compatibility is usually safer on the more established runtime. CPU v1 should not inherit CUDA image complexity.

### D-004: System Dependency Set

**Decision needed**: Which Linux packages are required in the image?

Likely required categories:

- GDAL runtime/development libraries for Fiona/GeoPandas.
- geospatial support libraries.
- OpenCV runtime libraries if keeping `opencv-python`.
- compiler/build tools only in build stage if needed.
- curl/ca-certificates for asset bootstrap and provider validation.

Options:

1. Minimal packages only, then fix failures.
2. Explicit known-good geospatial/image package set.
3. Use a larger geospatial-oriented base image.

Pros and cons:

- Minimal:
  - Pros: smaller image.
  - Cons: more trial-and-error; hidden runtime failures.
- Explicit known-good set:
  - Pros: controlled and reviewable.
  - Cons: slightly larger.
- Geospatial base:
  - Pros: fewer GDAL/Fiona surprises.
  - Cons: larger, extra supply-chain surface.

**Recommendation**: Use explicit packages on Python slim, validated by ZIP-code and smoke tests.

**Rationale**: TowerScout only needs a bounded set of geospatial behavior. A full geospatial base is probably more than v1 needs.

### D-005: Dockerfile Shape

**Decision needed**: Single-stage or multi-stage Dockerfile?

Options:

1. Single-stage image.
2. Multi-stage image with frontend build stage.
3. Multi-stage image with Python wheelhouse/build stage.

Pros and cons:

- Single-stage:
  - Pros: easier to understand.
  - Cons: may carry build tools and Node into runtime image.
- Frontend build stage:
  - Pros: runtime image does not need Node; bundle is reproducible.
  - Cons: more Dockerfile complexity.
- Full wheelhouse stage:
  - Pros: cleaner runtime image.
  - Cons: higher complexity with PyTorch/geospatial packages.

**Recommendation**: Use a multi-stage Dockerfile with a Node 18 frontend build stage and a Python runtime stage. Defer wheelhouse optimization unless build size/time becomes unacceptable.

**Rationale**: Node is needed to build `webapp/js/towerscout.js`, but should not be needed at runtime.

### D-006: Frontend Bundle Policy

**Decision needed**: How does Docker handle the frontend bundle?

Options:

1. Use committed `webapp/js/towerscout.js`.
2. Run `node webapp/build.js` during Docker build.
3. Require host user to build before Docker.

Pros and cons:

- Use committed bundle:
  - Pros: fast.
  - Cons: stale bundle risk.
- Build during Docker:
  - Pros: reproducible from source.
  - Cons: needs Node build stage.
- Host build:
  - Pros: simple Dockerfile.
  - Cons: bad user experience.

**Recommendation**: Build during Docker image build using `npm ci` and Node 18.

**Rationale**: This prevents stale frontend artifacts and avoids host Node requirements for users.

### D-007: Dependency Repeatability Policy

**Decision needed**: How tightly do we lock Python and image dependencies?

Options:

1. Top-level pinned `webapp/requirements.txt` only.
2. Add generated hash lock for Python dependencies.
3. Pin Docker base image digest.
4. Combine top-level pins, base image digest, and later hash lock.

Pros and cons:

- Top-level pins:
  - Pros: current project pattern, easier updates.
  - Cons: transitive dependency drift remains possible.
- Hash lock:
  - Pros: stronger repeatability.
  - Cons: harder PyTorch/platform management.
- Base digest:
  - Pros: stable OS layer.
  - Cons: requires update cadence.

**Recommendation**: For first Docker PR, pin the base image by tag and record the digest/review policy. Keep `webapp/requirements.txt` as the runtime contract. Add full hash locking as a follow-up only if Docker builds show drift.

**Rationale**: Full hash locking may slow the first Docker baseline. Digest awareness plus pinned top-level runtime dependencies is a pragmatic v1 step.

### D-008: Runtime User And File Permissions

**Decision needed**: Should the app run as root or non-root?

Options:

1. Run as root.
2. Run as non-root app user.
3. Start as root only for initialization, then run app as non-root.

Pros and cons:

- Root:
  - Pros: fewer volume permission issues.
  - Cons: weaker security posture.
- Non-root:
  - Pros: better security.
  - Cons: Windows bind mounts and generated files can be tricky.
- Root init then non-root:
  - Pros: balances setup and runtime.
  - Cons: more entrypoint complexity.

**Recommendation**: Prefer non-root runtime if volume write tests pass. If not, use root only for an entrypoint ownership fix and then drop to non-root.

**Rationale**: Config, logs, sessions, assets, and cache must be writable. Security is important, but a non-root setup that cannot persist config is not acceptable.

### D-009: App Working Directory And Path Contract

**Decision needed**: What working directory does the container use?

Options:

1. `WORKDIR /app`
2. `WORKDIR /app/webapp`
3. Fix all code to use app-anchored paths and make working directory less important.

Pros and cons:

- `/app`:
  - Pros: common repo-root layout.
  - Cons: current ZIP-code relative path may fail.
- `/app/webapp`:
  - Pros: matches current local run instructions and ZIP-code path.
  - Cons: repo-root relative tooling needs care.
- App-anchored paths:
  - Pros: most robust.
  - Cons: requires a small code fix for ZIP-code data.

**Recommendation**: Use `WORKDIR /app/webapp` for v1 and also fix ZIP-code loading to use `ts_paths` or `Path(__file__)` anchored data paths.

**Rationale**: Relying on working directory is fragile. Fixing ZIP-code pathing reduces future launcher and test surprises.

### D-010: Compose Volume Strategy

**Decision needed**: One data volume or several named volumes/bind mounts?

Options:

1. One named volume for all runtime data.
2. Several named volumes by data category.
3. Host bind mounts into repo folders.
4. Hybrid named volumes plus optional bind mounts for developers.

Pros and cons:

- One volume:
  - Pros: simple.
  - Cons: harder support and backup targeting.
- Several volumes:
  - Pros: clearer durability classes.
  - Cons: more Compose complexity.
- Bind mounts:
  - Pros: visible files on host.
  - Cons: Windows permissions/path friction.
- Hybrid:
  - Pros: user-safe default, developer flexibility.
  - Cons: must document clearly.

**Recommendation**: Use named volumes for default user deployment, with documented bind-mount override for development/support.

**Rationale**: Named volumes reduce Windows path mistakes and permission surprises. A support path can still expose files when needed.

### D-011: Versioned Runtime/Persistence Map

**Decision needed**: Which paths are durable, best-effort, or cleanup-safe?

Recommended v1 map:

| Path | Class | Recommendation |
| --- | --- | --- |
| `webapp/config/` | Durable | Preserve across restart/update. Contains `.env`, backups, lock file. |
| `webapp/model_params/` | Durable | Preserve model assets and first-run downloads. |
| `webapp/data/` | Durable | Preserve ZIP-code data and other static runtime data. |
| `webapp/logs/` | Durable/support | Preserve for support, with later rotation policy. |
| `webapp/uploads/` | Runtime-writable | Preserve during normal use; cleanup guidance needed. |
| `webapp/flask_session/` | Runtime-writable | Preserve for running app, but not guaranteed across app upgrades. |
| `webapp/temp/` | Cleanup-safe | Safe to clear between runs if no active detection. |
| `webapp/cache/maps/` | Best-effort | Preserve when convenient; safe to rebuild. |
| `webapp/cache/geocoding/` | Best-effort | Preserve when convenient; safe to rebuild subject to provider limits. |

**Recommendation**: Lock this map before Dockerfile implementation and include it in docs.

**Rationale**: Persistence is the heart of Docker correctness for TowerScout. If it is implicit, users will lose config/assets or support data.

### D-012: Config And Provider Key Storage

**Decision needed**: Where do provider keys live in Docker?

Options:

1. Environment variables passed through Compose.
2. Persisted `webapp/config/.env` written by Setup Wizard/Settings.
3. Docker secrets.
4. Managed secret store.

Pros and cons:

- Compose env vars:
  - Pros: common Docker pattern.
  - Cons: less friendly for non-technical users; does not match in-app Settings flow.
- Persisted `.env`:
  - Pros: matches current app design and Setup Wizard.
  - Cons: file contains secrets and must be treated carefully.
- Docker secrets:
  - Pros: better secret pattern.
  - Cons: more complex and not natural for local Docker Desktop users.
- Managed store:
  - Pros: enterprise-ready.
  - Cons: out of v1 scope.

**Recommendation**: Use persisted `webapp/config/.env` as the v1 source of truth, with optional env overrides only for advanced support.

**Rationale**: The app already has first-launch Setup Wizard and Settings. Docker should preserve that user path.

### D-013: `FLASK_SECRET_KEY` Generation

**Decision needed**: How should missing `FLASK_SECRET_KEY` be handled?

Options:

1. Require user to provide it manually.
2. Generate temporary in-memory value each start.
3. Generate once and persist to `.env`.

Pros and cons:

- Manual:
  - Pros: explicit.
  - Cons: poor end-user experience.
- Temporary:
  - Pros: current behavior, easy.
  - Cons: rotates on restart, bad for session continuity and support.
- Generate and persist:
  - Pros: best user experience, stable.
  - Cons: needs careful write path and tests.

**Recommendation**: Generate a secure key on first Docker startup when missing, write it to `webapp/config/.env`, and never display it in the UI.

**Rationale**: Users should not need to know what a Flask secret key is.

### D-014: Large Asset Strategy

**Decision needed**: How are model weights and large data files delivered?

Options:

1. Bake all assets into the Docker image.
2. First-run download into persistent storage.
3. Separate manual asset bundle.
4. User-managed bind-mounted asset folder.
5. Hybrid: first-run download plus persistent storage, with manual bundle fallback.

Pros and cons:

- Bake all assets:
  - Pros: easiest startup.
  - Cons: very large image; updates require full image rebuild; assets are gitignored today.
- First-run download:
  - Pros: smaller image; assets persist and can update separately.
  - Cons: first run depends on asset hosting/network; needs checksum and recovery logic.
- Manual bundle:
  - Pros: works for restricted networks.
  - Cons: more user steps and support risk.
- User-managed folder:
  - Pros: flexible for advanced users.
  - Cons: error-prone for normal users.
- Hybrid:
  - Pros: best balance of simple default and recovery path.
  - Cons: requires manifest and bootstrap implementation.

**Recommendation**: Use hybrid strategy. Default to manifest-driven first-run download into persistent asset storage. Provide a manual asset bundle fallback.

**Rationale**: The ZIP-code shapefile alone is about 823 MB. Baking all assets into every image makes updates and distribution heavy. Pure manual setup is too fragile for target users.

### D-015: Asset Manifest Contents

**Decision needed**: What does the asset manifest track?

Options:

1. No manifest, only file existence checks.
2. Manifest with names and paths.
3. Manifest with names, paths, sizes, versions, sources, checksums, and recovery instructions.

Pros and cons:

- Existence checks:
  - Pros: easy.
  - Cons: cannot detect corrupt/partial files.
- Basic manifest:
  - Pros: better visibility.
  - Cons: still weak integrity.
- Full manifest:
  - Pros: supports validation, support, updates, recovery.
  - Cons: more work.

**Recommendation**: Use a full manifest.

Minimum fields:

- asset id
- display name
- required/optional
- target path
- source URL or manual bundle source
- expected size
- SHA-256 checksum
- version/source date
- license/source notes
- recovery instructions

**Rationale**: Without checksums, first-run download support will be unreliable.

### D-016: Asset Hosting

**Decision needed**: Where are first-run assets downloaded from?

Options:

1. GitHub Releases.
2. Cloud object storage.
3. Bundled release ZIP next to app package.
4. Internal/private source.

Pros and cons:

- GitHub Releases:
  - Pros: easy release association, versioned.
  - Cons: large files/bandwidth limits and access policies must be checked.
- Cloud storage:
  - Pros: scalable, resumable, controllable.
  - Cons: needs operational ownership.
- Bundled ZIP:
  - Pros: simple offline-ish transfer after download.
  - Cons: larger release package and manual extraction unless automated.
- Private source:
  - Pros: controlled.
  - Cons: bad for external users unless access is solved.

**Recommendation**: Use GitHub Releases if file-size/bandwidth policy is acceptable. Otherwise use cloud object storage. In either case, treat asset URLs as versioned release inputs.

**Rationale**: Assets need durable, versioned, supportable URLs. Ad hoc links will create long-term failures.

### D-017: EfficientNet Base-Model Bootstrap

**Decision needed**: How do we handle `EfficientNet.from_pretrained('efficientnet-b5')`?

Options:

1. Allow library to download/cache at runtime.
2. Pre-populate/cache base weights during image build.
3. Switch to local base weights in asset manifest.
4. Revisit whether pretrained base load is needed when custom checkpoint is loaded.

Pros and cons:

- Runtime download:
  - Pros: no code change.
  - Cons: hidden first-run network dependency and cache location uncertainty.
- Build-time cache:
  - Pros: startup is smoother.
  - Cons: image grows; build depends on network.
- Local manifest asset:
  - Pros: explicit and checksum-verified.
  - Cons: requires code/config work.
- Revisit model load:
  - Pros: may eliminate unnecessary download.
  - Cons: needs ML/runtime validation.

**Recommendation**: During `TASK-025`, explicitly inventory this as an asset/bootstrap dependency. Prefer avoiding hidden runtime download. If safe, load architecture without external pretrained download and rely on TowerScout checkpoint. If not safe, put base weights under manifest control.

**Rationale**: Hidden downloads are exactly what Docker should eliminate.

### D-018: ZIP-Code Data Handling

**Decision needed**: How is ZIP-code data packaged and read?

Options:

1. Keep current shapefile in `webapp/data/`.
2. Download shapefile bundle on first run.
3. Convert to a smaller format such as GeoPackage or simplified GeoJSON.
4. Make ZIP-code lookup optional until data is present.

Pros and cons:

- Keep shapefile:
  - Pros: current code already uses it.
  - Cons: huge `.shp`, multiple sidecar files, path fragility.
- First-run download:
  - Pros: keeps image smaller.
  - Cons: large first-run transfer.
- Convert format:
  - Pros: may reduce file count and simplify packaging.
  - Cons: requires validation of geometry accuracy and performance.
- Optional:
  - Pros: app can start without ZIP-code data.
  - Cons: user-facing feature may be unavailable.

**Recommendation**: For v1, keep the current shapefile contract but deliver it through the asset manifest and fix path anchoring. Consider GeoPackage conversion as a later optimization if size/startup remains a problem.

**Rationale**: Do not change geographic data format during Docker unless necessary. Preserve behavior first.

### D-019: Startup Model Loading Policy

**Decision needed**: Should container startup load models eagerly or lazily?

Options:

1. Keep current production startup eager behavior.
2. Enable lazy model initialization by default in Docker.
3. Add explicit startup preflight/status and lazy runtime load.

Pros and cons:

- Eager:
  - Pros: failures surface immediately.
  - Cons: slow startup; missing assets can prevent setup page from loading.
- Lazy:
  - Pros: app shell and setup can load faster.
  - Cons: model failures appear later at detection time.
- Preflight/status plus lazy:
  - Pros: best user experience if implemented well.
  - Cons: more code.

**Recommendation**: Use preflight/status plus lazy model initialization for Docker if feasible. At minimum, ensure missing model assets do not prevent Setup Wizard/config recovery from loading.

**Rationale**: A user with no `.env` or missing assets should still be able to open the app and see actionable setup/recovery guidance.

### D-020: Health And Readiness Contract

**Decision needed**: What tells Docker/launcher the app is ready?

Options:

1. Basic HTTP 200 on `/`.
2. Dedicated `/api/health`.
3. Dedicated `/api/readiness` with setup and asset state.
4. Both health and readiness.

Pros and cons:

- `/` only:
  - Pros: no new endpoint.
  - Cons: cannot distinguish setup/assets/provider state.
- `/api/health`:
  - Pros: simple liveness.
  - Cons: not enough for launcher.
- `/api/readiness`:
  - Pros: useful for launcher and support.
  - Cons: requires careful status schema.
- Both:
  - Pros: clear separation.
  - Cons: slightly more work.

**Recommendation**: Add both:

- `/api/health`: process/app is alive.
- `/api/readiness`: setup required, config writable, secret present, assets ready/missing/bootstraping, provider configured, optional warnings.

**Rationale**: `TASK-054` needs a clear polling contract. A single 200 response is not enough.

### D-021: Startup Failure Mode

**Decision needed**: Should the app stop on missing assets or start in degraded recovery mode?

Options:

1. Stop container with clear logs.
2. Start app shell with degraded status and recovery guidance.
3. Mix: stop for impossible corruption, degraded for recoverable missing assets.

Pros and cons:

- Stop:
  - Pros: obvious failure.
  - Cons: user may not know how to read Docker logs.
- Degraded:
  - Pros: user sees browser guidance.
  - Cons: app must guard unavailable features.
- Mixed:
  - Pros: practical.
  - Cons: requires categorization.

**Recommendation**: Use mixed behavior. Start degraded when assets are missing or downloading. Stop only for unrecoverable config/runtime errors that prevent Flask from serving status.

**Rationale**: Non-technical users need visible recovery paths.

### D-022: Cache And Geocode Durability

**Decision needed**: Are caches durable?

Options:

1. Durable.
2. Best-effort.
3. Cleanup-safe.

Pros and cons:

- Durable:
  - Pros: fewer repeated provider calls.
  - Cons: cache growth and privacy implications.
- Best-effort:
  - Pros: preserves when convenient, safe to remove.
  - Cons: support must understand cache loss is not data loss.
- Cleanup-safe:
  - Pros: simple cleanup.
  - Cons: more repeated API calls and slower use.

**Recommendation**: Classify map/geocode cache as best-effort for v1.

**Rationale**: Losing cache should not break core data. But preserving it reduces repeated calls and improves user experience.

### D-023: Logs And Diagnostics

**Decision needed**: How are logs persisted and found?

Options:

1. Docker stdout/stderr only.
2. File logs only.
3. Both Docker logs and file logs.

Pros and cons:

- stdout/stderr:
  - Pros: Docker-native.
  - Cons: app already writes file logs; users may need support files.
- File logs:
  - Pros: matches existing support contract.
  - Cons: harder to view without volume access.
- Both:
  - Pros: best support coverage.
  - Cons: logging config complexity.

**Recommendation**: Keep file logs under `webapp/logs/` and also ensure important startup messages reach container logs.

**Rationale**: Support needs persistent logs, but Docker startup failures are easiest to inspect with `docker compose logs`.

### D-024: Uploads, Exports, And Imported Datasets

**Decision needed**: How are user-generated files handled?

Options:

1. Persist `webapp/uploads/`.
2. Treat uploads as temp.
3. Split imports, exports, and debug images into separate paths.

Pros and cons:

- Persist uploads:
  - Pros: safest; avoids surprise loss.
  - Cons: can grow over time.
- Temp uploads:
  - Pros: less storage growth.
  - Cons: may lose user data or restore assets unexpectedly.
- Split paths:
  - Pros: cleaner support.
  - Cons: requires code changes.

**Recommendation**: Persist `webapp/uploads/` for v1 and document cleanup. Consider path split later.

**Rationale**: Avoid data loss in the first Docker release.

### D-025: Request Body And Model Upload Policy

**Decision needed**: Preserve `TASK-063` upload policy in Docker.

Options:

1. Keep model upload disabled by default.
2. Enable model upload for all users.
3. Keep disabled, allow trusted local-admin override.

Pros and cons:

- Disabled:
  - Pros: safest.
  - Cons: less convenient for model updates.
- Enabled:
  - Pros: convenient.
  - Cons: PyTorch model files are trusted code artifacts; bad default.
- Override:
  - Pros: supports admin/developer needs.
  - Cons: must be clearly documented as trusted-only.

**Recommendation**: Keep disabled by default, preserve `TOWERSCOUT_ENABLE_MODEL_UPLOAD=true` override, and direct normal model updates through asset volume/manifest.

**Rationale**: This matches the release-hardening contract.

### D-026: Network, TLS, And Proxy Policy

**Decision needed**: How does Docker handle provider access, asset downloads, proxy, and TLS?

Options:

1. Assume normal internet only.
2. Add documented proxy env passthrough.
3. Add insecure TLS defaults.

Pros and cons:

- Normal internet:
  - Pros: simple.
  - Cons: constrained enterprise networks may fail.
- Proxy passthrough:
  - Pros: helps managed environments.
  - Cons: more support docs.
- Insecure TLS:
  - Pros: workaround for broken local cert stores.
  - Cons: security risk.

**Recommendation**: Support normal internet by default, document proxy env passthrough as troubleshooting, keep insecure TLS off by default.

**Rationale**: Provider validation and asset download need network clarity. Insecure TLS must remain exceptional.

### D-027: Port Binding

**Decision needed**: What host port does the app use?

Options:

1. Always bind host `5000:5000`.
2. Allow configurable host port with default 5000.
3. Random host port.

Pros and cons:

- Fixed:
  - Pros: simple docs.
  - Cons: port conflict risk.
- Configurable:
  - Pros: handles conflict.
  - Cons: launcher/docs need to know selected port.
- Random:
  - Pros: avoids conflicts.
  - Cons: confusing for users.

**Recommendation**: Default to `5000:5000`, allow documented override through Compose env/override.

**Rationale**: Simple first path with recovery for conflicts.

### D-028: GPU/CUDA Support

**Decision needed**: What GPU support is included in v1?

Options:

1. CPU only.
2. CPU default plus optional documented GPU profile.
3. CUDA image as default.

Pros and cons:

- CPU only:
  - Pros: simple, testable.
  - Cons: slower.
- Optional GPU profile:
  - Pros: future-friendly.
  - Cons: must be validated with NVIDIA runtime.
- CUDA default:
  - Pros: faster when compatible.
  - Cons: heavy and fragile for normal users.

**Recommendation**: CPU-only default. Add GPU only as an optional documented path after validation.

**Rationale**: The v1 supported baseline is CPU. GPU should not block Docker release.

### D-029: Image Size And Layer Strategy

**Decision needed**: How much image size is acceptable?

Options:

1. Optimize aggressively.
2. Accept a large but understandable ML image.
3. Split app and assets.

Pros and cons:

- Aggressive optimization:
  - Pros: smaller downloads.
  - Cons: slows implementation and can destabilize dependencies.
- Large ML image:
  - Pros: faster delivery.
  - Cons: user downloads may be large.
- Split assets:
  - Pros: app image smaller.
  - Cons: first-run asset bootstrap needed.

**Recommendation**: Accept a moderately large CPU ML image, but keep very large assets out of the image by default.

**Rationale**: PyTorch will make the image large anyway. Do not also bake the 823 MB ZIP-code shapefile unless intentionally justified.

### D-030: CI Container Validation

**Decision needed**: How does CI validate the container image and runtime contract?

Options:

1. Build only.
2. Build and HTTP health check.
3. Build, run, health/readiness, and smoke tests.

Pros and cons:

- Build only:
  - Pros: cheap.
  - Cons: misses runtime errors.
- Build and health:
  - Pros: catches startup issues.
  - Cons: misses model/data paths.
- Full smoke:
  - Pros: best confidence.
  - Cons: may require assets or skip logic.

**Recommendation**: Build and run health/readiness in CI. Add asset-dependent smoke where assets are available, otherwise use explicit skips. Run full container smoke locally/release-candidate.

**Rationale**: CI should catch broken images without depending on private/large release assets unless configured.

### D-031: Runtime Validation Commands

**Decision needed**: What commands prove `TASK-025` is complete?

Recommended minimum:

```powershell
docker compose build
docker compose up
```

Equivalent commands should be documented for any secondary supported engine after validation, for example Podman with the chosen Compose provider:

```powershell
podman compose build
podman compose up
```

Then validate:

- `GET /api/health`
- `GET /api/readiness`
- first-run Setup Wizard
- config save
- restart/recreate persistence
- `FLASK_SECRET_KEY` unchanged
- Settings save/load
- asset manifest state
- ZIP-code lookup
- `TASK-052` smoke against container
- bounded detection smoke
- logs visible in file volume and container-engine logs

**Recommendation**: Make this a formal container runtime validation checklist in `TASK-025`, with Docker as the initial validation path and Podman added only after a focused compatibility spike passes.

**Rationale**: Containerization is not done until persistence and app workflows are proven on the runtime host the project plans to support.

### D-032: Release Update Behavior

**Decision needed**: What survives an image update?

Options:

1. Preserve all named volumes.
2. Preserve only config/assets/logs.
3. Recreate all state on update.

Pros and cons:

- Preserve all:
  - Pros: safest for user data.
  - Cons: stale temp/session buildup.
- Preserve config/assets/logs:
  - Pros: cleaner.
  - Cons: may surprise users if uploads/session data vanish.
- Recreate all:
  - Pros: clean.
  - Cons: unacceptable config/asset loss.

**Recommendation**: Preserve config, assets, data, logs, uploads, cache, and sessions by default. Document temp cleanup separately.

**Rationale**: Users should not lose setup or assets after updating the app.

### D-033: Backup And Reset Behavior

**Decision needed**: How can users reset Docker state?

Options:

1. Manual Docker volume removal only.
2. App-level reset only.
3. Documented reset commands by category.

Pros and cons:

- Manual only:
  - Pros: no code work.
  - Cons: users may delete everything accidentally.
- App reset:
  - Pros: user-friendly for session/cache.
  - Cons: should not delete config/assets accidentally.
- Documented category reset:
  - Pros: safest support model.
  - Cons: more docs.

**Recommendation**: Document category reset:

- reset session/temp
- reset cache
- reset config
- reset assets
- full reset

**Rationale**: Support should not tell users to blindly delete all volumes unless necessary.

### D-034: Sensitive Local Data Handling

**Decision needed**: How should release docs describe sensitive data?

Options:

1. Minimal warning.
2. Explicit local sensitive-data section.
3. Support bundle automation with redaction.

Pros and cons:

- Minimal:
  - Pros: short.
  - Cons: users may share secrets/logs.
- Explicit section:
  - Pros: clear.
  - Cons: relies on user discipline.
- Automated redaction:
  - Pros: best support path.
  - Cons: likely out of `TASK-025` scope.

**Recommendation**: Add explicit sensitive-data documentation in `TASK-025`; defer automated support bundle to later.

**Rationale**: Provider keys, locations, imagery, exports, uploads, and logs can be sensitive.

### D-035: Launcher Boundary

**Decision needed**: What does the container runtime own versus launcher work?

Options:

1. Containerization owns CLI-only startup.
2. Containerization also owns launcher UX.
3. Containerization exposes stable contract; `TASK-054` builds launcher.

Pros and cons:

- CLI-only:
  - Pros: small scope.
  - Cons: weak end-user experience.
- Docker plus launcher:
  - Pros: user-friendly sooner.
  - Cons: expands `TASK-025`.
- Contract then launcher:
  - Pros: clean separation and lower risk.
  - Cons: user experience waits for `TASK-054`.

**Recommendation**: `TASK-025` exposes stable engine-aware commands and readiness/status. `TASK-054` owns launcher UX.

**Rationale**: Separate failure modes. The runtime contract must be stable before a launcher can target it.

### D-036: Background Jobs And Session Redesign

**Decision needed**: Should containerization redesign long-running detection state?

Options:

1. Keep current filesystem session/progress behavior.
2. Add a job queue/state store inside Docker now.
3. Defer job boundary to `TASK-058`.

Pros and cons:

- Keep current:
  - Pros: lower risk.
  - Cons: crash/restart continuity remains limited.
- Add queue now:
  - Pros: more robust architecture.
  - Cons: too much scope and regression risk.
- Defer:
  - Pros: aligns with current roadmap.
  - Cons: v1 container runtime still has known state limitations.

**Recommendation**: Keep current behavior for `TASK-025`, document limitations, defer job boundary to `TASK-058`.

**Rationale**: Containerization should package the corrected runtime, not redesign the app.

### D-037: Application Version And Asset Version Visibility

**Decision needed**: How can support identify what is running?

Options:

1. No version endpoint.
2. Add version/manifest file only.
3. Add endpoint and file.

Pros and cons:

- No endpoint:
  - Pros: no work.
  - Cons: poor support.
- File only:
  - Pros: simple.
  - Cons: harder for launcher/browser.
- Endpoint and file:
  - Pros: best support.
  - Cons: minor implementation.

**Recommendation**: Add a machine-readable manifest file and expose a redacted `/api/version` or include version data in `/api/readiness`.

**Rationale**: Asset/version visibility is required by the support contract.

### D-038: Container Runtime Host And Managed Machine Risk

**Decision needed**: Which runtime host can TowerScout safely depend on for v1 users?

Options:

1. Treat Docker Desktop as guaranteed.
2. Support Docker Desktop where licensed/approved and document managed-machine caveats.
3. Support Podman as an equal desktop runtime.
4. Support both Docker and Podman as engine-aware paths, with one primary validated path.
5. Build a non-container/native fallback now.

Pros and cons:

- Docker Desktop guaranteed:
  - Pros: simple.
  - Cons: may fail for public-health users on locked-down machines and may require licensing/procurement approval.
- Docker Desktop with caveats:
  - Pros: honest and supportable.
  - Cons: less polished product story.
- Podman equal runtime:
  - Pros: reduces Docker Desktop product/licensing dependency and aligns with OCI/rootless patterns.
  - Cons: still requires Windows VM/Podman machine setup, Compose/provider validation, proxy/certificate handling, and user support documentation.
- Both engines with one primary path:
  - Pros: keeps the container contract portable while avoiding overpromising unvalidated parity.
  - Cons: requires a compatibility matrix and clear support language.
- Native fallback now:
  - Pros: broader access.
  - Cons: too much scope.

**Final decision**: Treat the application container as OCI-compatible and engine-aware, make Podman the preferred open-source Windows runtime target after client feedback, and keep Docker Desktop as a secondary compatible path where licensing, procurement, endpoint policy, and installation prerequisites are approved. Run a focused Podman compatibility spike before promising Podman support, and do not build a native fallback in `TASK-025`.

**Rationale**: We need the runtime baseline first. Docker Desktop and Podman are host choices layered over the same contract, but each has separate user-environment risks. Native fallback is a later product decision.

### D-039: Container Security Hardening

**Decision needed**: How much hardening goes into v1?

Options:

1. Basic local-only container.
2. Non-root, minimal packages, no unnecessary ports, sane env defaults.
3. Read-only root filesystem, dropped capabilities, strict seccomp, etc.

Pros and cons:

- Basic:
  - Pros: fast.
  - Cons: weaker baseline.
- Practical hardening:
  - Pros: good balance.
  - Cons: requires permission testing.
- Strict hardening:
  - Pros: strongest posture.
  - Cons: likely friction with writable app paths and ML libraries.

**Recommendation**: Use practical hardening in v1: non-root if feasible, minimal exposed port, no hardcoded secrets, model upload disabled, explicit writable volumes. Defer strict read-only root until after runtime writes are fully isolated.

**Rationale**: Reliability and safe defaults matter most for first local release.

### D-040: Documentation Set

**Decision needed**: What docs must ship with the containerized release?

Recommended docs:

- quick start
- GitHub Release package contents
- supported/unsupported environments
- Podman-first path if Podman validation passes
- Docker-compatible fallback/developer support path
- source clone/build boundary
- setup wizard guide
- provider key restrictions
- asset bootstrap and recovery
- manual/restricted-network asset bundle procedure
- named-volume and optional host-visible data profile
- persistence/volume map
- update procedure
- reset procedure
- troubleshooting
- support diagnostics
- sensitive-data warning

**Recommendation**: Create one GitHub-first user-facing release guide and one technical OCI runtime contract. Link both from `TASK-025`.

**Rationale**: Users need simple steps; maintainers need exact contracts.

### D-041: Application License And Open-Source Suitability

**Decision needed**: Does the client's open-source preference apply only to runtime tooling, or also to TowerScout's application license?

Options:

1. Treat open source as a runtime/tooling requirement only.
2. Treat open source as both runtime/tooling and application licensing requirement.
3. Defer legal/license decision while documenting the current license clearly.

Pros and cons:

- Runtime/tooling only:
  - Pros: Podman-first runtime path may satisfy the immediate Docker Desktop concern.
  - Cons: may miss a client procurement or reuse requirement tied to the application license.
- Runtime plus application license:
  - Pros: resolves product/legal suitability before release promises.
  - Cons: may require owner/legal review and possibly relicensing decisions outside `TASK-025`.
- Defer with disclosure:
  - Pros: keeps container work moving.
  - Cons: leaves a real release-readiness question open.

**Recommendation**: Track this as a separate product/legal clarification item before release. Do not treat Podman selection as automatically satisfying TowerScout application open-source suitability.

**Rationale**: Podman can address the runtime-tooling preference, but the repo currently identifies `CC-BY-NC-SA-4.0`; that may or may not satisfy the client's application licensing expectations.

---

## 4. Overall Recommendation: Best Path Forward

If I controlled the path forward, I would design `TASK-025` around a narrow, explicit, testable OCI-compatible container runtime contract:

### Recommended Final Decision Set

Use this combination:

- Supported target: Windows AMD64, single-user local use.
- Runtime: CPU-first OCI-compatible image.
- Base image: Python 3.11 slim or digest-pinned equivalent.
- Image definition: multi-stage Dockerfile/Containerfile-compatible build with Node 18 frontend build stage and Python runtime stage.
- Compose-compatible run config: CPU default, named volumes, host port 5000 with documented override.
- Runtime host: choose one primary supported path before release; validate Docker where licensed/approved and run a Podman spike before promising Podman support.
- Release package: GitHub Release ZIP package with pinned GHCR image digest is the default user-facing delivery path; source clone/build is developer/support only.
- Open-source runtime target: Podman-first after validation, Docker-compatible as fallback/developer support where allowed.
- Assets: manifest-driven first-run download into persistent storage.
- Asset fallback: manual asset bundle for restricted networks.
- Asset integrity: SHA-256 verification and clear partial-download cleanup.
- Config: persisted `webapp/config/.env`.
- Secret key: generate and persist `FLASK_SECRET_KEY` automatically if missing.
- Provider keys: saved through Setup Wizard/Settings, not manual file editing.
- Volumes: use normalized `webapp/` runtime paths.
- Cache/geocode: best-effort.
- Logs: persistent file logs plus important container logs.
- Uploads: persist for v1, document cleanup.
- Model upload: disabled by default, trusted local-admin override only.
- Startup: allow app shell/status to load even when recoverable assets are missing.
- Model loading: prefer lazy/preflight behavior for the container so setup and recovery are reachable.
- Readiness: add `/api/health` and `/api/readiness`.
- Version visibility: expose app and asset manifest status.
- CI: build image and run health/readiness; full asset smoke in release/local validation.
- Launcher: defer to `TASK-054`, but design readiness for it now.
- Background jobs: defer to `TASK-058`.

### What The Ideal User Experience Looks Like

The ideal v1 user flow:

1. User installs the supported container runtime for their environment, such as Docker Desktop where licensed/approved, Podman Desktop after validation, or a supported Linux/remote container host.
2. User downloads the TowerScout GitHub Release package.
3. User starts TowerScout with a simple script or launcher from the release package.
4. The container engine starts the app and creates persistent local storage.
5. TowerScout generates its secret key automatically.
6. TowerScout checks large assets.
7. If assets are missing, TowerScout downloads and verifies them.
8. The browser opens only when the app is ready enough for setup.
9. User enters Google or Azure provider key in Setup Wizard.
10. User searches an area, estimates tiles, runs detection, reviews results, and exports data.
11. On restart or update, config, keys, model/data assets, logs, and user work survive.

The user should not need to understand:

- Python versions
- Node versions
- GDAL
- PyTorch installation
- model file paths
- Flask secret keys
- container volume internals
- local source builds unless they are acting as a developer/support user

### Why This Leads Toward The "Perfect" Product Path

The perfect solution for TowerScout is probably not a raw container CLI workflow. It is a dependable local application experience for users who may not be developers. However, an OCI-compatible container baseline is the right next step because it stabilizes the runtime.

Good decisions today make the later perfect solution easier:

- A versioned persistence map becomes the basis for backup, reset, update, and migration.
- An asset manifest becomes the basis for support, upgrades, checksums, and offline/manual bundles.
- A readiness endpoint becomes the basis for a launcher and later installer.
- Stable config/secret behavior prevents user setup from being lost.
- Clear unsupported-environment boundaries prevent overpromising.
- Keeping background jobs out of container v1 keeps the task shippable, while preserving a clear path to `TASK-058`.

The ideal long-term architecture would look like:

1. OCI-compatible reproducible runtime.
2. Launcher wraps the selected container engine and hides CLI details.
3. Detection runs move behind a local job boundary with durable job metadata.
4. Asset manager handles model/data versions, downloads, verification, and repair.
5. Support diagnostics can collect redacted logs and version/asset state.
6. If desktop container runtimes prove difficult for target users, the same runtime contract informs a remote managed container host, native installer, or packaged local service.

This avoids a common trap: building a launcher or installer on top of an unclear runtime. The runtime contract should come first.

---

## 5. Second Review: Easy-To-Miss Items

After reviewing the analysis for missing pieces, these are the items most likely to be overlooked:

1. **ZIP-code path fragility**
   - `ts_zipcode.py` uses a relative `data/...` path. Docker should not rely only on current working directory. Fix or explicitly control it.

2. **EfficientNet hidden base-model download**
   - `EfficientNet.from_pretrained('efficientnet-b5')` may pull/cache base weights. Treat this as an asset decision, not an incidental library detail.

3. **Setup must work before assets are perfect**
   - If missing model assets prevent Flask from serving the Setup Wizard, users cannot recover in-browser.

4. **Gitignored assets mean clean clones are incomplete**
   - `webapp/model_params/` and `webapp/data/` are ignored. Docker build/release must not assume they exist in source control.

5. **Model upload is not a normal update path**
   - `.pt` files are trusted-code artifacts. Normal users should receive trusted release assets through manifest/volume replacement, not browser upload.

6. **Container success is not just `docker build`**
   - The app must survive restart/recreate with config, secret, assets, and settings intact.

7. **Cache can contain sensitive location/provider-use information**
   - Best-effort does not mean irrelevant. Docs should warn that logs/cache/exports can be sensitive.

8. **Provider keys are not fully hidden**
   - Browser map providers expose client-side keys by design. Docs must tell users to restrict keys in Google/Azure consoles.

9. **Port conflicts need a user path**
   - Default `localhost:5000` is fine, but conflict recovery must be documented.

10. **Windows managed machines are a product risk**
    - Docker Desktop licensing, WSL2/Hyper-V, Podman machine setup, and endpoint policy may be blocked by IT policy. Do not overstate any desktop container runtime as universal end-user deployment.

11. **CI container validation needs asset-aware skip behavior**
    - Full detection smoke may require assets. CI should clearly skip asset-dependent paths when assets are unavailable rather than pass ambiguously.

12. **Logs need both file and Docker visibility**
    - If startup fails before file logging is useful, `docker compose logs`, `podman compose logs`, or the selected runtime's equivalent must still show actionable information.

13. **Session persistence is not the same as durable job state**
    - Filesystem sessions are acceptable for Docker v1 containment, but not the final architecture for crash-safe long-running detections.

14. **Image size will be large even without assets**
    - PyTorch/geospatial dependencies are heavy. Optimize obvious waste, but do not derail v1 chasing a tiny image.

15. **Asset licensing/source metadata matters**
    - ZIP-code data and model weights should have source/version/license notes in the manifest or release docs.

---

## 6. Proposed `TASK-025` Phase Breakdown

### Phase 1: Decision Lock

Deliverables:

- runtime/persistence contract
- asset manifest schema
- container runtime validation checklist
- health/readiness schema
- support diagnostics list
- final Compose volume plan
- runtime-host support statement, including whether Docker Desktop, Podman Desktop, Linux engine, or remote host is the primary supported path

Exit criteria:

- decisions in this document are accepted, modified, or explicitly deferred
- no open ambiguity blocks image-definition implementation

### Phase 2: Docker Build And Basic Run

Deliverables:

- Docker-compatible / OCI image definition
- Compose-compatible run configuration
- frontend build stage
- Python runtime stage
- system dependencies
- Waitress startup

Exit criteria:

- clean build passes
- container starts
- health endpoint works

### Phase 3: Persistence And Bootstrap

Deliverables:

- persistent config and generated `FLASK_SECRET_KEY`
- asset preflight/bootstrap
- writable directories
- logs and support paths
- readiness endpoint

Exit criteria:

- empty-volume first run works
- restart persistence works
- missing/corrupt asset behavior is visible and recoverable

### Phase 4: Workflow Validation

Deliverables:

- Setup Wizard validated
- Settings persistence validated
- ZIP-code lookup validated
- detection smoke validated
- `TASK-052` smoke reused against container
- docs complete

Exit criteria:

- acceptance criteria in `TASK-025` are checked with evidence
- release handoff names any residual risk explicitly

---

## 7. Concise Decision Lock Checklist

- [x] Confirm v1 host support boundary: Windows 11/AMD64, single-user local, CPU-first.
- [x] Choose release path: GitHub Release ZIP plus pinned GHCR image digest; source build is developer/support only.
- [x] Select base image direction: Python 3.11 slim or digest-pinned equivalent unless implementation finds a blocker.
- [x] Select Linux system dependency approach: explicit minimal runtime dependencies with geospatial/image libraries verified in the image.
- [x] Decide runtime user/permissions: practical non-root/rootless posture where feasible.
- [x] Decide image-definition stage structure: Dockerfile/Containerfile-compatible multi-stage build.
- [x] Decide frontend build policy: build frontend assets in the image/release process, not on end-user laptops.
- [x] Lock volume/persistence map: named volumes default; optional host-visible data profile only after validation.
- [x] Lock config and provider-key behavior: Setup Wizard/Settings write persistent config.
- [x] Lock first-run `FLASK_SECRET_KEY` behavior: generate and persist when absent.
- [x] Lock large asset strategy: manifest-managed, staged, SHA-256 verified, durable storage.
- [x] Define asset manifest and checksum policy.
- [x] Choose asset hosting/source policy: GitHub Release metadata/package plus governed object storage/internal mirror when large binaries require it.
- [x] Decide EfficientNet base-model handling: treat base and project weights as managed assets.
- [x] Decide ZIP-code data packaging direction: managed/versioned asset with path fix if needed.
- [x] Decide startup eager/lazy model behavior direction: setup/recovery should remain reachable when recoverable assets are missing.
- [x] Define health/readiness endpoints: `/api/health` plus `/api/readiness` states `starting`, `setup_required`, `degraded`, `ready`, and `fatal`.
- [x] Define startup failure categories and degraded-mode behavior.
- [x] Classify map/geocode caches as best-effort unless implementation evidence requires a narrower contract.
- [x] Define logs/support diagnostics direction.
- [x] Define upload/model-update policy: normal users receive trusted manifest assets; model upload is not the normal update path.
- [x] Define network/proxy/TLS defaults.
- [x] Define port binding and conflict recovery.
- [x] Define GPU support boundary: optional AMD64 CUDA acceleration only after validation.
- [x] Define CI validation split: routine image health/readiness plus release-candidate real-asset smoke.
- [x] Define release update and reset procedure categories.
- [x] Document sensitive local data handling requirement.
- [x] Keep launcher and job-state redesign out of `TASK-025`.

Implementation still needs to prove these decisions with files, scripts, container runs, asset checks, and validation evidence during `TASK-025`.
