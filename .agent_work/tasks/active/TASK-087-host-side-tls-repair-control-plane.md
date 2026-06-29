# TASK-087: Host-Side TLS Repair Control Plane

**Status**: PLANNED_NOT_STARTED_REVIEWER_FEEDBACK_INCORPORATED  
**Type**: B/C (Runtime Support / Setup UX / TLS Trust)  
**Priority**: MEDIUM-HIGH  
**Estimated Effort**: 4-7 days (32-56 hours), plus package validation on a managed TLS-inspected network  
**Target Sprint**: Post-`TASK-086` / rc7 follow-up unless selected as a release blocker  
**Created**: 2026-06-29  
**Owner**: TBD  
**Depends On**: `TASK-086`; package launcher/runtime profile; provider setup error classification; Docker CPU/CUDA package paths

## Objective

Design and implement a support-safe host-side repair control plane that lets
TowerScout present a guided "repair TLS trust and restart" action when provider
setup detects a managed-network TLS certificate trust failure. The action should
reuse the validated `TASK-086` repair flow, preserve the user's selected runtime
mode, and restart TowerScout without requiring the user to manually run:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off
```

The goal is to reduce first-cohort support friction for managed-network users
while preserving the manual command path as the fallback and audited baseline.

## Problem Statement

`TASK-086` proved that TowerScout can repair the Google Maps managed-network TLS
trust failure by importing the organization/root TLS inspection CA into the
container trust bundle and persisting `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE`.
However, the validated repair still requires users or support staff to leave the
browser, run package-local scripts, stop the runtime, and restart with the same
CPU/GPU mode they intended to use.

The browser UI cannot safely execute host commands directly, and the Linux
container cannot inspect the Windows certificate store or control the host
Docker/Podman runtime by itself. Any one-click UX therefore needs a narrow,
explicit, host-side control plane launched by the trusted package scripts.

## Planning Decision

Implement this as a package-local Windows host helper, not as arbitrary command
execution from the web UI and not as a container-side Docker socket mount.

The host helper should:

- Start only from TowerScout's trusted Windows launcher/setup path.
- Bind only to loopback.
- Use a per-run random token.
- Expose a very small allowlisted API.
- Invoke only TowerScout-owned scripts with validated enum-style arguments.
- Preserve the captured runtime profile when restarting.
- Emit support-safe status messages without API keys, certificate thumbprints,
  certificate subjects, raw provider responses, or environment dumps.

## Recommended Release Position

Do not make `TASK-087` a default rc7 blocker unless the team decides the
first-cohort tester workflow requires one-click repair before user-facing rc7
publication.

`TASK-086` remains the validated repair baseline for rc7. `TASK-087` should be
treated as a follow-on support UX improvement unless upcoming tester evidence
shows that the command-based repair path is not usable enough for the planned
cohort.

## Required Go/No-Go Gates

Implementation must proceed through gates. Do not start product UI integration
until Gates 1 and 2 pass.

### Gate 1: Helper Transport Proof

Proceed only if a package-local helper can:

- Bind to `127.0.0.1` without administrator URL ACL setup.
- Accept browser calls from the current TowerScout localhost origin with strict
  token and origin checks.
- Survive the TowerScout container stop/start sequence.
- Launch package-local scripts reliably.
- Exit cleanly when the package runtime exits.
- Work on the intended managed-network Windows validation environment.

### Gate 2: Security Proof

Proceed only if tests and review prove:

- There is no arbitrary command execution surface.
- Unknown providers, engines, GPU modes, ports, command paths, script paths, and
  extra arguments are rejected.
- Process invocations use validated argument arrays, not caller-supplied command
  strings.
- Helper tokens are never written to readiness output, status output, logs,
  support bundles, browser console output, or DOM attributes.
- Helper progress is emitted as sanitized operation states, not raw subprocess
  output.

### Gate 3: Product Integration Proof

Proceed only if frontend/backend tests prove:

- The repair button appears only for repairable TLS trust categories.
- Invalid-key, quota, provider-disabled, provider HTTP, and generic network
  failures never show the host repair action.
- Setup Wizard preserves structured validation details end-to-end, including
  `category`, `provider`, `repairable`, `support_action`, `repair_command`, and
  `helper_available`.
- Helper-unavailable is treated as a normal fallback path, not a broken setup
  state.

### Gate 4: Managed-Network Package Validation

Proceed to user-facing package inclusion only after managed-network validation
confirms:

- The guided button path works.
- The documented command fallback still works.
- CPU and CUDA package variants include helper artifacts.
- CPU and CUDA package variants exclude helper token files, runtime profiles,
  helper logs unless explicitly support-safe, `.env`, TLS bundle material, and
  local certificate exports.

## Non-Goals

- Do not silently repair TLS trust without explicit user confirmation.
- Do not expose a general-purpose command runner, shell endpoint, or script path
  parameter.
- Do not mount the Docker or Podman control socket into the application
  container.
- Do not bake a CDC, organization, or site-specific root CA into the public
  TowerScout image.
- Do not move provider validation to the host as the primary product path.
- Do not require an admin-installed Windows service for the first slice unless
  the loopback helper proof of concept fails.
- Do not record raw certificate subjects, raw thumbprints, API keys, or provider
  response bodies in task docs, user-visible UI, support bundles, or package
  evidence.
- Do not stream raw `repair-provider-tls.cmd` or `import-tls-ca.cmd` subprocess
  output into the browser UI.

## Target User Flow

1. User starts TowerScout from the CPU or CUDA application package.
2. The launcher records the runtime profile: engine, GPU mode, port, package
   root, image/package identity, and any support-safe launch metadata needed for
   restart.
3. The launcher starts a package-local host helper bound to `127.0.0.1` on a
   random available port with a one-time random token.
4. User reaches Setup Wizard and enters a Google Maps key.
5. Provider validation detects a repairable TLS certificate trust failure.
6. Setup Wizard shows the current support command fallback and, when the helper
   is available, a guided repair button.
7. User confirms that TowerScout will inspect the local Windows certificate
   chain, update the container CA bundle, and restart the app.
8. The UI requests the repair operation through the helper control plane.
9. The helper runs the validated `TASK-086` repair path for the current provider
   and runtime mode, then stops and restarts TowerScout with the same selected
   engine, GPU mode, port, and package.
10. The UI enters a reconnecting state and polls readiness until TowerScout is
    available again.
11. Setup Wizard resumes and revalidates the provider key without presenting the
    TLS failure as an invalid key.

## Architecture Plan

### 1. Runtime Profile Capture

Add a package-local runtime profile written by the trusted launcher path. The
profile should contain only support-safe, non-secret values:

- Engine: `docker` or `podman`.
- GPU mode: `off`, `on`, or `auto` after existing package guardrails.
- Port and effective base URL.
- Package root path.
- Package flavor: CPU or CUDA 12.1.
- Compose project name if needed to target the active container.
- Image tag/digest or package manifest identity when available.
- Host helper port and token location, with the token stored outside logs.
- Helper session id and runtime profile creation timestamp.
- Package root identity and resolved script paths derived from the trusted
  launcher, not from browser input.
- Current container/service identity when available, so the helper can detect a
  stale or wrong-package operation before repairing or restarting.

The runtime profile should be ignored by git and excluded from release source
artifacts unless it is generated at package runtime.

The helper must reject stale or mismatched runtime profiles. This includes
profiles from another TowerScout folder, profiles whose package root no longer
matches the helper process, profiles whose container identity does not match the
active runtime, expired helper sessions, and multi-instance ambiguity. If the
helper cannot prove it is targeting the correct runtime, it should block the
guided repair and show the manual command fallback.

### 2. Host Helper Proof Of Concept

Build a minimal Windows helper proof of concept before UI integration. The first
candidate should be PowerShell because it is already available in the supported
Windows package environment.

The proof of concept must confirm:

- A loopback-only listener can run without requiring administrator URL ACL
  registration.
- Browser-to-loopback requests work from the current TowerScout origin with the
  intended CORS, origin, token, and private-network behavior.
- Corporate endpoint protection does not block the local listener in the target
  validation environment.
- The helper can remain available while Docker/Podman stops and restarts the
  TowerScout container.
- The helper exits cleanly when the package runtime is stopped.

If PowerShell `HttpListener` requires admin URL ACL setup or proves brittle,
evaluate a fallback such as a small package-local native helper or a narrower
protocol/IPC mechanism before attempting product UI integration.

For the first implementation slice, prefer direct browser-to-loopback-helper
calls if the proof of concept confirms the browser, CORS, origin, token, and
private-network behavior is reliable. This keeps host-control behavior local to
the host helper and avoids requiring the container backend to reach a host-side
control endpoint. If browser-to-loopback access proves brittle in the target
environment, revisit backend brokering as a fallback rather than switching
security models without a new design review.

### 3. Helper API

Expose only narrow, allowlisted operations:

- `GET /health`
  - Returns helper availability, helper version, and sanitized runtime profile
    summary.
- `GET /runtime-profile`
  - Returns engine, GPU mode, package flavor, port, and package/image identity.
  - Must not return provider keys, environment dumps, certificate subjects, or
    thumbprints.
- `POST /operations/provider-tls-repair`
  - Accepts a validated provider enum such as `google` or `azure`.
  - Optionally accepts `restart: true`.
  - Creates an operation id and starts the repair asynchronously.
- `GET /operations/{operation_id}`
  - Returns sanitized progress, terminal status, and support-safe next action.

The helper must reject:

- Unknown providers.
- Unknown engine or GPU values.
- Unexpected ports or package roots.
- Caller-supplied command paths.
- Caller-supplied arbitrary arguments.
- Non-loopback requests.
- Requests without the one-time token.
- Requests from unexpected origins.
- Stale helper tokens or runtime profiles.
- Requests that cannot be associated with the active TowerScout package
  instance.

### 4. Restart Orchestration

Reuse the existing validated scripts rather than duplicating repair logic:

```powershell
.\scripts\repair-provider-tls.cmd -Provider <provider> -Engine <engine> -Gpu <gpu> -Apply
.\scripts\stop.cmd -Engine <engine>
.\start.bat -Engine <engine> -Gpu <gpu> -Port <port> -NoBrowser
```

The helper should derive `<engine>`, `<gpu>`, and `<port>` from the launcher
runtime profile, not from the browser request. It should preserve the user's
original CPU/CUDA package intent and respect the existing CPU-package
`-Gpu on` guardrail.

Restart progress should distinguish:

- Certificate candidate selection failed.
- Multiple CA candidates had the same score and require manual support review.
- CA import failed.
- Provider TLS verification failed.
- Stop failed.
- Restart failed.
- Restart succeeded but readiness did not return before timeout.
- Restart succeeded and provider setup can be retried.

The helper must not stream raw `repair-provider-tls.cmd` or
`import-tls-ca.cmd` output into the browser. Those scripts intentionally print
support-sensitive local certificate details in the manual dry-run path. The
helper should map subprocess exit codes and known output markers to sanitized
states such as `inspecting_certificate_chain`, `ca_candidate_selected`,
`ca_candidate_ambiguous`, `importing_bundle`, `provider_tls_verified`,
`restarting`, `readiness_waiting`, `ready`, and `failed`.

### 5. Backend And Setup Wizard Integration

Extend the existing structured provider validation error path from `TASK-086`.

Backend responsibilities:

- Preserve existing TLS-vs-invalid-key categorization.
- Report whether a TLS failure is repairable.
- Report whether the host helper is available, without logging the helper token.
- Keep the manual `repair_command` fallback visible in the structured details.
- Avoid treating a repairable TLS certificate failure as a bad provider key.
- Preserve and return helper-specific structured fields without exposing token
  values: `category`, `provider`, `repairable`, `support_action`,
  `repair_command`, `helper_available`, and operation status when applicable.

Frontend responsibilities:

- Show the repair button only when the error category is repairable TLS and the
  helper is available.
- Show a confirmation modal before starting host repair/restart.
- Display progress from helper operation polling.
- Move to a reconnecting state during restart.
- Poll TowerScout readiness after restart and resume the provider setup flow.
- Continue to show the command-based fallback when the helper is unavailable or
  the repair operation fails.
- Treat helper-unavailable as a normal support fallback, not as a broken setup
  state.

### 6. Security And Privacy Requirements

This task changes the trust boundary because a browser-facing UI will initiate a
host-side runtime operation. Treat that as the central design constraint.

Requirements:

- Bind the helper to `127.0.0.1` only.
- Generate a random per-launch token and require it for every mutating request.
- Use strict CORS/origin checks limited to the current TowerScout localhost
  origin.
- Require explicit user confirmation before repair/restart.
- Validate all request inputs as enums or booleans.
- Build process invocations with argument arrays, not string-concatenated shell
  commands.
- Never accept command text, script paths, or arbitrary arguments from the UI.
- Never expose the helper token in readiness output, status output, logs,
  support bundles, browser console output, DOM attributes, or task evidence.
- Never expose raw helper subprocess output in the browser UI.
- Redact provider keys, provider URLs with keys, certificate subjects,
  thumbprints, environment variables, and raw HTTP responses from helper logs.
- Keep helper logs package-local and support-safe.
- Ensure support bundles and release packages do not include helper token files,
  local runtime profiles, `.env`, or TLS bundle material.

### 7. Test Plan

Automated coverage:

- Unit tests for runtime profile creation and parsing.
- Unit tests for stale, expired, wrong-package, and multi-instance runtime
  profile rejection.
- Unit tests for provider/engine/GPU enum validation.
- Unit tests proving the helper never exposes arbitrary command execution.
- Unit tests for sanitized progress and failure messages.
- Unit tests proving helper tokens are not emitted into status/readiness/log/UI
  surfaces.
- Backend tests for repairable TLS categories and helper availability metadata.
- Frontend tests for repair button visibility, confirmation, progress, failure,
  and reconnect states.
- Package-generation tests confirming helper scripts are included and runtime
  profile/token artifacts are excluded.
- Secret-safety tests or assertions covering API-key and certificate redaction.

Manual validation:

- Docker CPU package on a managed TLS-inspected network.
- Docker CUDA 12.1 package on a managed TLS-inspected network, or CPU-fallback
  CUDA validation if GPU hardware is not available.
- Helper-unavailable path still shows the documented manual commands.
- Repair failure path gives actionable, sanitized support guidance.
- Restart preserves port and CPU/GPU mode.
- Ambiguous CA candidate selection blocks one-click apply and directs support to
  the manual dry-run path.
- Setup Wizard resumes and Google Maps validation succeeds after repair.
- Logs and support artifacts contain no API keys, certificate subjects, raw
  thumbprints, or helper tokens.
- Multi-instance behavior is explicitly tested or blocked with a clear
  support-safe message.

Optional validation:

- Podman CPU path if selected for the same release train.
- Multi-instance behavior when another TowerScout package is already running.

### 8. Implementation Phases

#### Phase 1: Design Spike

- Decide whether the UI calls the helper directly over loopback or the backend
  brokers the helper request.
- Build a minimal loopback helper proof of concept.
- Confirm PowerShell listener feasibility without admin URL ACL setup.
- Define the runtime profile file shape and token handling.
- Define runtime profile identity checks, stale-profile rejection, and
  multi-instance behavior.
- Define sanitized operation states and the mapping from repair/restart script
  results to those states.
- Document the security model and rejection cases before product integration.

Exit criteria:

- Helper transport choice is proven on the target Windows environment.
- Security model is reviewed.
- Gates 1 and 2 pass.
- Manual command fallback remains intact.

#### Phase 2: Host Helper MVP

- Add package-local helper script and `.cmd` wrapper.
- Add runtime profile generation in the launcher path.
- Add token generation and helper lifecycle management.
- Add health/runtime-profile endpoint.
- Add asynchronous repair operation endpoint using existing scripts.
- Add support-safe progress output.
- Add stale-profile, wrong-package, and multi-instance rejection.

Exit criteria:

- From a local browser or scripted client, the helper can repair and restart a
  Docker CPU package using the captured runtime profile.
- No arbitrary command execution surface exists.
- Helper progress is sanitized and helper tokens are absent from observable
  output surfaces.

#### Phase 3: Product UI Integration

- Extend backend structured provider setup payloads with helper availability.
- Add Setup Wizard repair button, confirmation, progress, and reconnect states.
- Preserve the manual command fallback in all failure/unavailable cases.
- Add frontend/backend tests for structured behavior.

Exit criteria:

- Repair button appears only for repairable TLS failures when helper is
  available.
- Invalid-key, quota, provider-disabled, or network-unavailable failures do not
  show the host repair action.
- Gate 3 passes.

#### Phase 4: Package And Validation

- Include helper artifacts in CPU and CUDA packages.
- Exclude runtime profile/token/log artifacts from source and release packages.
- Build an internal validation package before any user-facing rc7+ package.
- Validate on a managed TLS-inspected network.
- Decide whether the feature is ready for rc7, rc7 patch, or later release.

Exit criteria:

- CPU and CUDA package variants include the helper.
- Managed-network validation proves the button path and fallback command path.
- Task evidence records sanitized outcomes only.
- Gate 4 passes.

## Acceptance Criteria

- When Google provider validation fails with a repairable TLS certificate trust
  category and the helper is available, Setup Wizard shows a guided repair and
  restart action.
- The action requires explicit user confirmation before host-side repair begins.
- The helper runs the validated `TASK-086` repair flow with the captured engine,
  GPU mode, package root, and port.
- TowerScout restarts in the same CPU/GPU mode the user originally selected.
- The UI enters a reconnecting state and resumes provider setup after readiness
  returns.
- The command-based `repair-provider-tls.cmd` fallback remains documented and
  visible when the helper is unavailable or fails.
- Helper-unavailable is a normal fallback state and does not block setup beyond
  the original TLS issue.
- The helper emits sanitized progress states only and never streams raw
  subprocess output to the browser.
- No API keys, helper tokens, certificate subjects, raw thumbprints, raw
  provider responses, or environment dumps appear in UI, logs, task evidence, or
  support bundles.
- Helper tokens do not appear in readiness output, status output, browser
  console output, DOM attributes, support bundles, helper logs, or task
  evidence.
- Runtime profiles include enough identity to reject stale, expired,
  wrong-package, wrong-container, and ambiguous multi-instance operations.
- Ambiguous CA candidate selection blocks one-click apply and directs support to
  the manual dry-run path.
- CPU and CUDA package variants pass package-generation checks and managed
  network validation, or the release notes clearly state any package-variant
  validation boundary.

## Open Questions

- Can a PowerShell loopback listener be used without admin URL ACL setup on the
  intended tester machines?
- Should the browser call the helper directly with strict CORS and token checks,
  or should the container backend broker requests to the helper through a host
  gateway endpoint?
- Should the helper be launched for all runs or only when Setup Wizard/provider
  validation enters a repairable TLS state?
- How should the helper behave if multiple TowerScout packages are running on
  different ports?
- Should Podman support be included in the first implementation slice or held as
  a follow-up after Docker CPU/CUDA validation?

## Risks

- A host-side helper increases the security sensitivity of the setup flow.
- Endpoint security tools may block a local listener or child process launch.
- PowerShell `HttpListener` may require URL ACL behavior that is not acceptable
  for non-admin users.
- Restarting the app from a setup screen can lose UI state unless the reconnect
  path is explicit and tested.
- Multiple concurrent TowerScout instances could target the wrong runtime if
  runtime profile identity is weak.
- Over-automating repair could make certificate trust changes feel opaque to
  users; confirmation and fallback documentation are required.

## Implementation Log

### 2026-06-29 - Initial Plan Created

**Objective**: Capture the proposed one-click managed-network TLS repair path as
a scoped follow-on to `TASK-086`.

**Decision**: Plan around a trusted package-local Windows host helper with a
narrow loopback API, per-launch token, explicit user confirmation, and strict
reuse of the validated `repair-provider-tls.cmd` plus stop/start flow. Keep the
manual command path as the support baseline and do not make this a default rc7
blocker unless user-testing evidence requires it.

**Next**: Review the plan with the team, decide whether `TASK-087` is selected
for active implementation before or after rc7, then run a helper transport proof
of concept before product UI work begins.

### 2026-06-29 - Reviewer Feedback Incorporated

**Objective**: Tighten the Task-087 plan before implementation by incorporating
reviewer feedback on helper security, transport feasibility, structured error
handling, runtime-profile correctness, packaging drift, and release gating.

**Context**: The reviewer agreed the guided repair button can materially reduce
managed-network setup friction, but highlighted that Task-087 introduces a new
browser-to-host trust boundary. The existing `TASK-086` command path remains the
validated repair baseline and should not be replaced until the host helper is
proven.

**Decision**: Keep Task-087 as a follow-on support UX improvement and require
four Go/No-Go gates before user-facing package inclusion: helper transport
proof, security proof, product integration proof, and managed-network package
validation. Prefer direct browser-to-loopback-helper calls for the first slice
only if the proof of concept validates CORS, origin, token, and
private-network behavior in the target Windows environment.

**Execution**:
- Added explicit Go/No-Go gates.
- Added runtime-profile identity and stale/wrong-package/multi-instance
  rejection requirements.
- Added a direct browser-to-loopback helper preference with backend brokering as
  a fallback if the proof of concept fails.
- Required sanitized operation states instead of raw subprocess output because
  the manual repair scripts can print support-sensitive certificate details.
- Added token non-leakage requirements for readiness, status, logs, support
  bundles, browser console output, DOM attributes, and task evidence.
- Required helper-unavailable to remain a normal command-fallback path.
- Added CPU/CUDA package inclusion and generated-artifact exclusion checks as
  Gate 4 requirements.

**Validation**: `python .agent_work\scripts\validate_agent_work.py` passed
after the Task-087 plan and current-task index updates.

**Next**: Validate task tracker hygiene, then decide whether to keep Task-087 as
post-rc7 follow-up or authorize only the Phase 1 helper transport proof of
concept while rc7 materials proceed from the validated Task-086 baseline.
