# TASK-087: Host-Side TLS Repair Control Plane

**Status**: IN_PROGRESS - selected as Sprint 7 active work during Sprint 6 closeout
**Type**: B/C (Runtime Support / Setup UX / TLS Trust)
**Priority**: MEDIUM-HIGH
**Estimated Effort**: 4-7 days (32-56 hours), plus package validation on a managed TLS-inspected network
**Target Sprint**: Sprint 07
**Created**: 2026-06-29
**Owner**: TowerScout release owner / active agent support
**Depends On**: `TASK-086`; package launcher/runtime profile; provider setup error classification; Docker CPU/CUDA package paths; existing Podman Compose provider installer and approved-provider catalog if Podman remediation is included

## Canonical Source Note

This Sprint 7 task file on the active PR branch supersedes the older Task-087
copy that may still be visible on the GitHub default branch until the Sprint 6
closeout PR is merged. Review and implementation should use this file as the
canonical plan unless the team explicitly replaces it with a newer revision.

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

Podman users have a related host-side setup risk: `podman compose version` can
fail or resolve to an unapproved Compose provider. The existing package already
contains an approved-provider gate and the
`scripts\install-podman-compose-provider.cmd -Apply` command, but users still
have to run that path manually when the Podman runtime profile is otherwise
selected. If Task-087 includes Podman runtime remediation, it should be treated
as a separate helper operation, not as part of the TLS repair command itself.

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

The same helper framework may also expose a Podman Compose provider preflight
and remediation operation. That operation must be separate from provider TLS
repair, limited to captured `engine=podman` runtime profiles, and require
explicit user confirmation before running the existing package-local installer.
It must not silently install a Compose provider as a side effect of TLS repair.

## First Implementation Slice Boundary

The first user-facing implementation slice should focus on Docker CPU/CUDA
provider TLS repair and restart only. That slice may include sanitized Podman
Compose provider preflight status if needed to protect Podman restarts, but it
should not run the Podman Compose provider installer from the product UI until
the helper transport, security model, operation lifecycle, and Docker reconnect
UX are proven.

Podman Compose provider remediation remains valid scope for Task-087, but it is
a separate later slice unless the team explicitly approves it after Gates 1 and
2 pass. The first-slice success criterion is a support-safe Docker CPU repair
and restart path that preserves the manual `TASK-086` command fallback.
Any product UI that exposes the Podman Compose provider installer requires
explicit release-owner sign-off after the first Docker helper proof succeeds,
even if sanitized Podman preflight status is implemented earlier.

## Recommended Release Position

Do not treat `TASK-087` as part of the validated RC7.1 baseline unless the team
decides later tester workflow evidence requires one-click repair before the next
user-facing package.

`TASK-086` remains the validated repair baseline for RC7.1. `TASK-087` is now
the active Sprint 7 follow-on support UX improvement, but the command-based
repair path remains the fallback until the helper gates pass.

## Required Go/No-Go Gates

Implementation must proceed through gates. Do not start product UI integration
until Gates 1 and 2 pass.

### Gate 1: Helper Transport Proof

Proceed only if a package-local helper can:

- Bind to `127.0.0.1` without administrator URL ACL setup.
- Accept browser calls from the current TowerScout localhost origin with strict
  token and origin checks.
- Survive the TowerScout container stop/start sequence.
- Survive `setup-towerscout.ps1`, `bootstrap.ps1`, and `launch.ps1` process
  exit when needed for first-run UX, while still self-terminating through TTL,
  package-instance heartbeat, container-exit detection, or explicit stop
  cleanup.
- Integrate with the stop path so `scripts\stop.cmd` terminates or invalidates
  the helper session whenever practical.
- Launch package-local scripts reliably.
- Inspect Podman Compose provider status through the existing approved-provider
  checks when the captured runtime profile uses `engine=podman`.
- Exit cleanly when the package runtime exits.
- Work on the intended managed-network Windows validation environment.

### Gate 2: Security Proof

Proceed only if tests and review prove:

- There is no arbitrary command execution surface.
- Unknown providers, engines, GPU modes, ports, command paths, script paths, and
  extra arguments are rejected.
- Process invocations use validated argument arrays, not caller-supplied command
  strings.
- Podman provider remediation, if included, never accepts provider ids,
  install directories, Python paths, force flags, command paths, or extra
  arguments from the browser.
- The helper never changes `PODMAN_COMPOSE_PROVIDER` or installs a Compose
  provider without explicit user confirmation for a separate Podman remediation
  operation.
- Helper tokens are never written to readiness output, status output, logs,
  support bundles, browser console output, or DOM attributes.
- Helper progress is emitted as sanitized operation states, not raw subprocess
  output.
- The durable helper token never goes to the frontend. Browser-visible code may
  receive only a short-lived operation credential or one-time operation nonce
  that expires quickly and is not rendered into static HTML, DOM attributes,
  readiness payloads, status payloads, logs, or support bundles.
- The helper allows at most one active host operation per package instance.
  Duplicate starts, reloads, and double-clicks return the existing operation or
  a support-safe busy state instead of launching a second repair/install action.

### Gate 3: Product Integration Proof

Proceed only if frontend/backend tests prove:

- The repair button appears only for repairable TLS trust categories.
- Invalid-key, quota, provider-disabled, provider HTTP, and generic network
  failures never show the host repair action.
- Setup Wizard preserves structured validation details end-to-end, including
  `category`, `provider`, `repairable`, `support_action`, `repair_command`, and
  `helper_available`.
- Setup Wizard retains the last structured validation failure object per
  provider for repair-button rendering and does not collapse repairable
  failures into booleans plus message strings.
- Podman Compose provider remediation, if exposed in product UI or launcher UI,
  appears only for captured `engine=podman` runtime profiles and
  missing/unapproved/multiple-provider states.
- Product UI exposure for the Podman Compose provider installer is blocked
  until the release owner signs off after the Docker CPU/CUDA helper proof.
- Podman Compose provider remediation is not shown for Docker runs, invalid
  provider keys, quota failures, provider-disabled failures, or generic
  provider HTTP failures.
- Helper-unavailable is treated as a normal fallback path, not a broken setup
  state.

### Gate 4: Managed-Network Package Validation

Proceed to user-facing package inclusion only after managed-network validation
confirms:

- The guided button path works.
- The documented command fallback still works.
- If Podman remediation is included, the package validates the approved
  provider check, user-confirmed installer path, sanitized failure states, and
  manual fallback instructions on a Podman-assigned validation host.
- CPU and CUDA package variants include helper artifacts.
- CPU and CUDA package variants exclude helper token files, runtime profiles,
  helper logs unless explicitly support-safe, `.env`, `.env.backup.*`, TLS
  bundle material, local certificate exports, and Podman provider install
  caches unless intentionally packaged.

## Phase 1 Evidence Template

Use this template for Gate 1 and Gate 2 evidence before product UI work starts.
Record sanitized outcomes only. Do not include local listener ports, helper
tokens, operation credentials, certificate subjects, certificate thumbprints,
provider keys, raw provider responses, raw subprocess output, full local paths,
browser network traces, screenshots, `.env` values, or support logs.

```markdown
### Phase 1 Evidence - [YYYY-MM-DD] - [Scenario]

**Gate**: Gate 1 Helper Transport Proof / Gate 2 Security Proof
**Environment**: Windows package context, engine, GPU mode, package flavor, and
managed-network status using public-safe labels only
**Objective**: [What the proof validates]
**Command Category**: [helper start / health check / origin-token check /
allowlist rejection / script invocation / restart survival / stop cleanup]
**Inputs**: Provider enum, engine enum, GPU enum, confirmation value, and
sanitized operation state only
**Observed States**: [sanitized helper states such as ready, operation_busy,
restarting, readiness_waiting, rejected_unknown_provider, failed]
**Result**: PASS / FAIL / PARTIAL
**Redaction Check**: Confirm no tokens, credentials, certificate details, raw
output, local paths, `.env` values, or support logs were recorded
**Follow-Up**: [Next action or blocker]
```

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
- Do not silently install or reconfigure a Podman Compose provider.
- Do not let the browser choose a Podman provider id, install directory, Python
  executable, force flag, provider path, command path, or installer arguments.
- Do not treat a successful Podman Compose provider install as proof that the
  Podman machine, GPU CDI path, image pull path, or managed-network access is
  otherwise ready.
- Do not record raw certificate subjects, raw thumbprints, API keys, or provider
  response bodies in task docs, user-visible UI, support bundles, or package
  evidence.
- Do not stream raw `repair-provider-tls.cmd` or `import-tls-ca.cmd` subprocess
  output into the browser UI.

## Target User Flow

1. User starts TowerScout from the CPU or CUDA application package.
2. The launcher records the runtime profile: engine, GPU mode, port, package
   root, image/package identity, and any support-safe launch metadata needed for
   restart. Runtime profile generation should come from a shared launcher helper
   used by setup and direct start/launch paths, not from setup-only code.
3. The launcher starts a package-local host helper bound to `127.0.0.1` on a
   random available port with a durable package-local token that never reaches
   the frontend directly.
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

Optional Podman Compose provider remediation flow:

1. User starts TowerScout with a captured `engine=podman` runtime profile, or
   support selects the Podman runtime path before launch.
2. The launcher/helper checks the existing approved-provider rules:
   `PODMAN_COMPOSE_PROVIDER`, approved providers on `PATH`, and
   `podman compose version` output.
3. If no approved provider is present, multiple approved providers are present,
   or the resolved provider is disallowed, the helper reports a sanitized
   Podman provider status and keeps the manual command fallback visible.
4. User explicitly confirms installing the package-local approved provider.
5. The helper runs only `.\scripts\install-podman-compose-provider.cmd -Apply`
   with no browser-supplied installer arguments.
6. The helper reports sanitized operation states and, on success, reruns the
   provider check before any Podman restart attempt.
7. If installation fails because Python, download access, hash validation, or
   environment policy blocks the installer, the helper shows support-safe
   fallback guidance instead of raw installer output.

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
- Podman Compose provider status when `engine=podman`: `approved`, `missing`,
  `unapproved`, `multiple`, or `unknown`, plus a support-safe provider label
  when one can be shown without exposing full local paths.
- Image tag/digest or package manifest identity when available.
- Host helper port and token location, with the token stored outside logs.
- Helper session id and runtime profile creation timestamp.
- Package root identity and resolved script paths derived from the trusted
  launcher, not from browser input.
- Current container/service identity when available, so the helper can detect a
  stale or wrong-package operation before repairing or restarting.

Runtime profile generation belongs in a shared launcher helper that is called
by setup/bootstrap/start/launch entry points. It must not live only in
`setup-towerscout.ps1`, because direct `start.bat` / `scripts\launch.ps1`
sessions need the same profile freshness, identity checks, and restart
metadata.

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
- The helper can survive launcher/setup process exit through a deliberate
  detached, supervised, or heartbeat-based lifecycle model.
- The helper self-terminates when its TTL expires, the package-instance
  heartbeat disappears, the active container exits and is not being restarted,
  or the package stop cleanup explicitly asks it to stop.
- `scripts\stop.cmd` terminates the helper process or invalidates the helper
  session whenever practical, so a stopped package cannot retain a usable
  browser-to-host operation credential.
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
- `GET /runtime-preflight`
  - Returns sanitized host-runtime readiness for the captured profile.
  - For Podman, includes approved Compose provider status without raw
    `podman compose version` output or full local provider paths.
- `POST /operations/provider-tls-repair`
  - Accepts a validated provider enum such as `google` or `azure`.
  - Accepts only a fixed confirmation value such as
    `repair_tls_and_restart`; restart behavior is derived from the operation
    type and runtime profile, not from a browser-selected restart mode.
  - Creates an operation id and starts the repair asynchronously.
- `POST /operations/podman-compose-provider-repair`
  - Available only when the captured runtime profile uses `engine=podman`.
  - Accepts only an explicit confirmation boolean or equivalent CSRF-safe
    acknowledgement.
  - Runs the fixed package-local installer command
    `scripts\install-podman-compose-provider.cmd -Apply`.
  - Must not accept provider id, install path, Python path, force flag,
    provider path, command path, or arbitrary arguments from the caller.
- `GET /operations/{operation_id}`
  - Returns sanitized progress, terminal status, and support-safe next action.

The helper must reject:

- Unknown providers.
- Unknown engine or GPU values.
- Unexpected ports or package roots.
- Caller-supplied command paths.
- Caller-supplied arbitrary arguments.
- Caller-supplied Podman provider ids, install roots, Python executables, force
  flags, provider paths, or installer arguments.
- Non-loopback requests.
- Requests without the one-time token.
- Requests from unexpected origins.
- Stale helper tokens or runtime profiles.
- Requests that cannot be associated with the active TowerScout package
  instance.

Operation lifecycle rules:

- The helper must allow only one active mutating operation per package instance.
- Duplicate-clicks, page reloads, and repeated POSTs with the same operation
  nonce should return the existing operation id and status when safe.
- A different operation request while one is active should return a sanitized
  `operation_busy` state.
- Each operation must have a timeout, terminal state, cleanup path, and safe
  retry rule after terminal failure.
- Terminal-state polling must continue to work across the TowerScout restart
  window.
- Stop cleanup must terminate or invalidate active operations and helper
  credentials whenever `scripts\stop.cmd` is used for the selected engine.

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

When `<engine>` is `podman`, the helper should run the approved Compose
provider preflight before stopping the current app or attempting restart. If
the provider is missing, unapproved, ambiguous, or `podman compose version`
does not complete, the TLS repair operation should block with a sanitized
Podman-provider-required state and offer the separate Podman remediation path
or the manual command fallback. It should not stop a running TowerScout
container when the captured restart path is likely to fail because the Compose
provider is not approved.

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

### 5. Podman Compose Provider Preflight And Remediation

If included, Podman Compose provider remediation should reuse the current
approved-provider implementation rather than inventing a second validation
model:

- Use the same approved-provider catalog that backs
  `scripts\install-podman-compose-provider.cmd`.
- Reuse the existing checks for `PODMAN_COMPOSE_PROVIDER`, approved providers
  on `PATH`, Docker Desktop provider rejection, and
  `podman compose version` inspection.
- Treat `missing`, `unapproved`, `multiple`, `version_failed`, and
  `install_failed` as support-safe states.
- Run only `scripts\install-podman-compose-provider.cmd -Apply` after explicit
  confirmation.
- Recheck provider status after install before continuing.
- Redact or omit full local provider paths, Python paths, install directories,
  `.env` backup paths, download URLs, and raw installer output from browser UI
  and task evidence.
- Preserve the manual command fallback:

```powershell
.\scripts\install-podman-compose-provider.cmd -Apply
```

This operation is host-runtime remediation, not provider-key validation and
not TLS certificate repair. It should be safe to skip without weakening the
validated `TASK-086` command fallback.

Product UI exposure for this installer operation requires explicit
release-owner sign-off after the Docker CPU/CUDA helper proof succeeds. Until
that sign-off exists, product UI may surface sanitized Podman preflight status
and the manual command fallback, but it must not start the installer operation.

### 6. Backend And Setup Wizard Integration

Extend the existing structured provider validation error path from `TASK-086`.

Backend responsibilities:

- Preserve existing TLS-vs-invalid-key categorization.
- Report whether a TLS failure is repairable.
- Report whether the host helper is available, without logging the helper token.
- Mediate short-lived helper operation authorization when browser-visible code
  needs to call the helper. The durable helper token should remain
  package-local and should not be emitted through config/status/readiness
  routes, hidden DOM fields, inline script state, browser console output, or
  logs.
- Keep the manual `repair_command` fallback visible in the structured details.
- Avoid treating a repairable TLS certificate failure as a bad provider key.
- Preserve and return helper-specific structured fields without exposing token
  values: `category`, `provider`, `repairable`, `support_action`,
  `repair_command`, `helper_available`, and operation status when applicable.

Frontend responsibilities:

- Show the repair button only when the error category is repairable TLS and the
  helper is available.
- Preserve the last structured validation failure per provider, including
  `category`, `provider`, `repairable`, `support_action`, `repair_command`,
  `helper_available`, and any short-lived operation authorization metadata
  needed to render and start a repair operation.
- Show any Podman Compose provider remediation action only when the captured
  runtime profile is `engine=podman` and the helper reports a provider
  readiness state that is explicitly repairable by the package-local installer.
- Show a confirmation modal before starting host repair/restart.
- Use a separate confirmation modal for Podman provider installation because it
  downloads an approved package, creates a package-local environment, backs up
  `.env`, and updates `PODMAN_COMPOSE_PROVIDER`.
- Display progress from helper operation polling.
- Move to a reconnecting state during restart.
- Poll TowerScout readiness after restart and resume the provider setup flow.
- Suppress duplicate-clicks and page-reload duplicate starts by reusing the
  active operation id when the helper reports one.
- Continue to show the command-based fallback when the helper is unavailable or
  the repair operation fails.
- Treat helper-unavailable as a normal support fallback, not as a broken setup
  state.

### 7. Security And Privacy Requirements

This task changes the trust boundary because a browser-facing UI will initiate a
host-side runtime operation. Treat that as the central design constraint.

Requirements:

- Bind the helper to `127.0.0.1` only.
- Generate a random per-launch token and require it for every mutating request.
- Keep the durable helper token package-local. Browser-visible code may receive
  only a short-lived operation credential or one-time operation nonce that is
  scoped to the requested operation, expires quickly, and is never persisted in
  static HTML, DOM attributes, readiness/status output, logs, task evidence, or
  support bundles.
- Use strict CORS/origin checks limited to the current TowerScout localhost
  origin.
- Require explicit user confirmation before repair/restart.
- Require explicit user confirmation before Podman provider installation or
  `PODMAN_COMPOSE_PROVIDER` changes.
- Validate all request inputs as enums or booleans.
- Build process invocations with argument arrays, not string-concatenated shell
  commands.
- Never accept command text, script paths, or arbitrary arguments from the UI.
- Never accept installer options, provider paths, Python paths, install
  directories, or `-Force` from the UI.
- Never expose the helper token in readiness output, status output, logs,
  support bundles, browser console output, DOM attributes, or task evidence.
- Never expose short-lived operation credentials after their immediate use, and
  never persist them in support evidence.
- Never expose raw helper subprocess output in the browser UI.
- Redact provider keys, provider URLs with keys, certificate subjects,
  thumbprints, environment variables, and raw HTTP responses from helper logs.
- Keep helper logs package-local and support-safe.
- Ensure support bundles and release packages do not include helper token files,
  local runtime profiles, `.env`, `.env.backup.*`, TLS bundle material, or
  generated Podman provider install caches unless those caches are deliberately
  included as release artifacts.

### 8. Test Plan

Automated coverage:

- Unit tests for runtime profile creation and parsing.
- Unit tests for stale, expired, wrong-package, and multi-instance runtime
  profile rejection.
- Unit tests for provider/engine/GPU enum validation.
- Unit tests proving the provider TLS repair operation accepts only provider
  enum plus the fixed confirmation value and rejects browser-selected restart
  modes.
- Unit tests for helper operation locking, duplicate-click idempotency,
  operation timeout, terminal-state cleanup, and safe retry after terminal
  failure.
- Unit tests for Podman Compose provider preflight states if that operation is
  included: approved, missing, unapproved, multiple, version failed, and
  install failed.
- Unit tests proving the helper never exposes arbitrary command execution.
- Unit tests proving the Podman provider operation cannot receive provider id,
  install directory, Python path, force flag, command path, or arbitrary args
  from browser input.
- Unit tests for sanitized progress and failure messages.
- Unit tests proving durable helper tokens and short-lived operation credentials
  are not emitted into status/readiness/log/UI/support-bundle surfaces.
- Backend tests for repairable TLS categories and helper availability metadata.
- Frontend tests for structured provider-failure retention, repair button
  visibility, confirmation, duplicate-click suppression, progress, failure, and
  reconnect states.
- Package-generation tests confirming helper scripts are included and runtime
  profile/token artifacts are excluded.
- Package-generation tests confirming `.env`, `.env.backup.*`, runtime
  profiles, helper tokens, helper logs, and generated Podman provider install
  caches are excluded unless explicitly intended.
- Secret-safety tests or assertions covering API-key and certificate redaction.

Manual validation:

- Docker CPU package on a managed TLS-inspected network.
- Docker CUDA 12.1 package on a managed TLS-inspected network, or CPU-fallback
  CUDA validation if GPU hardware is not available.
- Helper-unavailable path still shows the documented manual commands.
- Repair failure path gives actionable, sanitized support guidance.
- Restart preserves port and CPU/GPU mode.
- Duplicate-click and page-reload behavior does not start concurrent repair or
  install operations.
- Ambiguous CA candidate selection blocks one-click apply and directs support to
  the manual dry-run path.
- Setup Wizard resumes and Google Maps validation succeeds after repair.
- If included, Podman Compose provider remediation succeeds only after explicit
  confirmation and the helper revalidates `podman compose version` through an
  approved provider before restart.
- If included, Podman provider install failure due to Python, download access,
  hash verification, or policy restrictions returns sanitized fallback guidance.
- Logs and support artifacts contain no API keys, certificate subjects, raw
  thumbprints, or helper tokens.
- Multi-instance behavior is explicitly tested or blocked with a clear
  support-safe message.

Optional validation:

- Podman CPU path if selected for the same release train, including approved
  Compose provider check/remediation when that scope is included.
- Multi-instance behavior when another TowerScout package is already running.

### 9. Implementation Phases

#### Phase 1: Design Spike

- Treat Docker CPU/CUDA TLS repair and restart as the first implementation
  slice. Podman installer remediation is held until after Gates 1 and 2 unless
  separately approved.
- Decide whether the UI calls the helper directly over loopback or the backend
  brokers the helper request.
- Build a minimal loopback helper proof of concept.
- Confirm PowerShell listener feasibility without admin URL ACL setup.
- Define the runtime profile file shape and token handling.
- Define the shared runtime-profile generation helper and the setup/bootstrap/
  start/launch call sites that must refresh it.
- Define the helper lifecycle model that survives launcher exit but terminates
  through TTL, heartbeat, container-exit detection, or stop cleanup.
- Define how `scripts\stop.cmd` terminates the helper process or invalidates
  the helper session.
- Define runtime profile identity checks, stale-profile rejection, and
  multi-instance behavior.
- Decide whether Podman Compose provider remediation belongs in the first slice,
  and whether it is surfaced through launcher preflight, helper API, or both.
- Define short-lived operation authorization so the durable helper token never
  reaches frontend code.
- Define single-operation locking, idempotency keys or operation nonces,
  timeouts, terminal states, cleanup, and safe retry behavior.
- Define sanitized Podman provider status states and failure mapping.
- Define sanitized operation states and the mapping from repair/restart script
  results to those states.
- Use the Phase 1 evidence template for Gate 1 and Gate 2 proof notes.
- Document the security model and rejection cases before product integration.

Exit criteria:

- Helper transport choice is proven on the target Windows environment.
- Security model is reviewed.
- Gates 1 and 2 pass.
- Manual command fallback remains intact.

#### Phase 2: Host Helper MVP

- Add package-local helper script and `.cmd` wrapper.
- Add runtime profile generation through the shared launcher helper used by
  setup/bootstrap/start/launch paths.
- Add token generation and helper lifecycle management.
- Add stop-path cleanup so `scripts\stop.cmd` terminates or invalidates helper
  sessions whenever practical.
- Add health/runtime-profile endpoint.
- Add asynchronous repair operation endpoint using existing scripts.
- Add single-operation locking, duplicate-start idempotency, operation timeout,
  terminal-state cleanup, and safe retry handling.
- Optionally add a separate Podman Compose provider preflight and remediation
  operation using the fixed package-local installer command.
- Add support-safe progress output.
- Add stale-profile, wrong-package, and multi-instance rejection.

Exit criteria:

- From a local browser or scripted client, the helper can repair and restart a
  Docker CPU package using the captured runtime profile.
- The helper can survive launcher/setup process exit during the repair/restart
  flow and still self-terminate when the package runtime is no longer active.
- The durable helper token is never exposed to frontend-visible surfaces; only a
  short-lived operation credential or one-time operation nonce is used when
  browser-visible code initiates an operation.
- Concurrent repair/install attempts are rejected or deduplicated through a
  support-safe operation status.
- If Podman remediation is included, a scripted client can prove the separate
  operation uses only the fixed installer command, requires confirmation, and
  never accepts caller-supplied installer arguments.
- No arbitrary command execution surface exists.
- Helper progress is sanitized and helper tokens are absent from observable
  output surfaces.

#### Phase 3: Product UI Integration

- Extend backend structured provider setup payloads with helper availability.
- Add Setup Wizard repair button, confirmation, progress, and reconnect states.
- Preserve structured provider validation failures per provider so repair UI
  uses the actual failure category and support fields, not only booleans and
  message text.
- If Podman provider remediation is included in product UI, add a separate
  runtime-preflight action and confirmation path that is not tied to invalid-key
  or TLS error categories.
- Require release-owner sign-off before product UI can expose the Podman
  Compose provider installer operation.
- Preserve the manual command fallback in all failure/unavailable cases.
- Add frontend/backend tests for structured behavior.

Exit criteria:

- Repair button appears only for repairable TLS failures when helper is
  available.
- Invalid-key, quota, provider-disabled, or network-unavailable failures do not
  show the host repair action.
- Duplicate-clicks, reloads, and repeated operation starts do not create
  concurrent host-side operations.
- Gate 3 passes.

#### Phase 4: Package And Validation

- Include helper artifacts in CPU and CUDA packages.
- Exclude runtime profile/token/log artifacts from source and release packages.
- Exclude `.env`, `.env.backup.*`, generated Podman provider caches, and raw
  installer logs from source and release packages unless deliberately included.
- Build an internal validation package before any user-facing package
  inclusion.
- Validate on a managed TLS-inspected network.
- Decide whether the feature is ready for the next RC patch or a later release.

Exit criteria:

- CPU and CUDA package variants include the helper.
- Podman-assigned validation proves the approved-provider check and separate
  installer path if Podman remediation is included.
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
- The first user-facing slice repairs and restarts Docker CPU/CUDA package
  profiles only; Podman provider installation is not product-exposed until the
  helper transport, security, and Docker reconnect path are proven and
  separately approved.
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
- Browser-visible code receives only a short-lived operation credential or
  one-time operation nonce, and operation credentials are not persisted in
  logs, support bundles, DOM attributes, readiness/status output, or task
  evidence.
- The helper allows only one active host operation per package instance and
  handles duplicate starts, timeouts, terminal cleanup, and safe retry with
  sanitized states.
- `scripts\stop.cmd` terminates the helper process or invalidates the helper
  session whenever practical, including any active operation credentials.
- Runtime profiles include enough identity to reject stale, expired,
  wrong-package, wrong-container, and ambiguous multi-instance operations.
- Runtime profile generation is shared by setup/bootstrap/start/launch paths so
  direct `start.bat` sessions and first-run setup sessions get the same profile
  freshness and restart metadata.
- Ambiguous CA candidate selection blocks one-click apply and directs support to
  the manual dry-run path.
- If the runtime profile uses `engine=podman` and no approved Compose provider
  is available, the helper blocks guided restart with a sanitized Podman
  provider-required state rather than stopping the current runtime.
- If Podman Compose provider remediation is included, it requires explicit user
  confirmation, runs only `scripts\install-podman-compose-provider.cmd -Apply`,
  revalidates the approved provider before restart, and is exposed in product
  UI only after explicit release-owner sign-off.
- Podman Compose provider remediation is never run automatically as a side
  effect of provider TLS repair.
- Browser input cannot select Podman provider ids, install directories, Python
  executables, force flags, command paths, provider paths, or arbitrary
  installer arguments.
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
- If Podman support is included, should Compose provider remediation be exposed
  through the launcher before the app starts, through the loopback helper after
  the app starts, or both?
- Should the first Podman remediation slice run the connected installer, or only
  surface preflight status and manual instructions until managed-network
  download/proxy behavior is validated?

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
- Mixing Podman provider installation with TLS repair could obscure the actual
  failure if the helper does not keep those operations separate.
- The Podman provider installer depends on Python and connected package
  download/hash verification, so managed-network or restricted-network policy
  can block the remediation even when TLS repair would otherwise work.
- Podman provider paths, Python paths, `.env` backup paths, and installer output
  can expose local environment details if helper output is not sanitized.

## Implementation Log

### 2026-07-02 - Reviewer Minor Follow-Up Added

**Objective**: Incorporate the reviewer's non-blocking follow-up suggestions
before merging the Sprint 6 closeout / Task-087 planning PR.

**Context**: The reviewer approved the updated Task-087 direction and suggested
three implementation-support additions: a sanitized Phase 1 evidence template,
explicit `scripts\stop.cmd` helper-session cleanup, and release-owner sign-off
before any product UI exposes the Podman Compose provider installer operation.

**Decision**: Accept all three suggestions as documentation refinements because
they reduce implementation ambiguity without changing the approved first-slice
scope. Keep the first user-facing slice limited to Docker CPU/CUDA TLS repair
and restart while allowing sanitized Podman preflight status only.

**Execution**: Added the Phase 1 evidence template, explicit stop-path helper
termination/invalidation requirements, and release-owner sign-off language for
any future Podman installer UI exposure.

**Validation**: `python .agent_work\scripts\validate_agent_work.py`,
`python .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .`,
and `git diff --check -- .agent_work\tasks\active\TASK-087-host-side-tls-repair-control-plane.md`
passed.

**Next**: Push the final Task-087 planning update to PR #44 for merge
readiness, then start implementation from a fresh post-merge Task-087 branch.

### 2026-07-02 - Reviewer Boundary And Security Follow-Up Added

**Objective**: Incorporate reviewer feedback on Task-087's first-slice scope,
helper lifecycle, token delivery, operation locking, restart request shape,
runtime-profile generation, and frontend validation-state handling.

**Context**: The reviewer approved the gated helper direction but recommended
holding Podman Compose provider remediation out of the first user-facing slice
until the Docker CPU/CUDA helper proof validates the transport, security model,
and reconnect UX. Local code review confirmed that current setup validation
already carries structured TLS categories, but Setup Wizard state collapses
provider validation to booleans, launcher scripts exit after readiness, and
Podman provider scripts print local paths/version/installer details that must
not be streamed to browser-visible helper output.

**Decision**: Keep Podman Compose provider remediation in Task-087 as a valid
later slice, but define Docker CPU/CUDA provider TLS repair and restart as the
first implementation target. Add explicit design requirements for detached or
heartbeat-based helper lifecycle, short-lived operation authorization instead
of frontend exposure to durable helper tokens, one active host operation per
package instance, fixed `repair_tls_and_restart` confirmation semantics, shared
runtime-profile generation across setup/bootstrap/start/launch paths, and
structured provider failure retention in Setup Wizard.

**Execution**: Added a canonical-source note for the active PR branch, a first
implementation slice boundary, Gate 1 and Gate 2 additions, helper API operation
lifecycle rules, backend/frontend responsibilities, security/privacy
requirements, test-plan coverage, phase-plan updates, and acceptance criteria.

**Validation**: `python .agent_work\scripts\validate_agent_work.py`,
`python .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .`,
and `git diff --check -- .agent_work\tasks\active\TASK-087-host-side-tls-repair-control-plane.md`
passed.

**Next**: Run `.agent_work` validators and `git diff --check`, then ask the
reviewer to re-review the active PR branch plan before implementation begins.

### 2026-07-02 - Podman Compose Provider Remediation Scope Added

**Objective**: Incorporate the proposed Podman Compose provider check and
installer path into the Task-087 design before reviewer feedback.

**Context**: The package already validates Podman Compose provider selection and
includes `scripts\install-podman-compose-provider.cmd -Apply` for connected
support/setup use. The new host helper framework could reduce Podman support
friction, but the provider installer changes `.env`, creates a package-local
provider environment, and may require network/Python access. It should not be
hidden inside TLS repair.

**Decision**: Treat Podman Compose provider remediation as an optional,
separately confirmed runtime-preflight operation within the Task-087 helper
framework. Keep provider TLS repair and Podman provider installation separate,
derive all runtime context from the trusted launcher profile, and reject all
browser-supplied installer arguments.

**Execution**: Updated the Task-087 problem statement, gates, helper API,
runtime profile, restart orchestration, security requirements, test plan,
acceptance criteria, open questions, and risks to include the optional Podman
Compose provider remediation path.

**Validation**: `python .agent_work\scripts\validate_agent_work.py`,
`python .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .`,
and `git diff --check -- .agent_work\tasks\active\TASK-087-host-side-tls-repair-control-plane.md`
passed.

**Next**: Ask the reviewer to assess whether Podman Compose provider
remediation should be included in the first Task-087 implementation slice or
held behind the Docker CPU/CUDA helper proof.

### 2026-07-02 - Selected For Sprint 7

**Objective**: Promote Task-087 from post-RC7.1 follow-up planning into the active Sprint 7 lane.

**Context**: Sprint 6 closed with RC7.1 validated for tester-facing use and `TASK-086` established as the command-based managed-network TLS repair baseline. The team selected the host-side TLS repair control plane as the next active sprint focus.

**Decision**: Keep Task-086 as the validated fallback while starting Task-087 with the gated helper transport proof. Product UI integration remains blocked until the helper transport and security gates pass.

**Execution**: Updated task status and Sprint target during Sprint 6 closeout. Kept this task file in `.agent_work/tasks/active/` while completed Sprint 6 task files moved to `.agent_work/tasks/completed/`.

**Validation**: Closeout validation will run after tracker updates and file moves.

**Next**: Start Gate 1 with a package-local helper transport proof that validates loopback binding, token/origin checks, helper lifetime, and script invocation behavior on the target Windows environment.

### 2026-06-29 - Initial Plan Created

**Objective**: Capture the proposed one-click managed-network TLS repair path as
a scoped follow-on to `TASK-086`.

**Decision**: Plan around a trusted package-local Windows host helper with a
narrow loopback API, per-launch token, explicit user confirmation, and strict
reuse of the validated `repair-provider-tls.cmd` plus stop/start flow. Keep the
manual command path as the support baseline and do not make this a default
RC7.1 baseline requirement unless user-testing evidence requires it.

**Next**: Review the plan with the team, decide whether `TASK-087` is selected
for active implementation before or after RC7.1, then run a helper transport
proof of concept before product UI work begins.

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
post-RC7.1 follow-up or authorize only the Phase 1 helper transport proof of
concept while RC7.1 materials proceed from the validated Task-086 baseline.
