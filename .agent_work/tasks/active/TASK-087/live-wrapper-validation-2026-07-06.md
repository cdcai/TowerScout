# TASK-087 Live Wrapper Validation Evidence - 2026-07-06

## Purpose

Prepare and record the first explicit internal live-wrapper validation window
for Task-087 after reviewer approval of PR #45 at `0132b13` and the pre-run
note at `4139993`.

This note is task-local evidence. Record sanitized states only. Do not record
raw subprocess output, helper tokens, operation credentials, `.env` contents,
certificate subjects, certificate thumbprints, provider keys, full local paths,
browser network traces, screenshots, or support logs.

## Planned Run Scope

- PR / branch head before execution: `4139993`
- Branch: `feature/task-087-helper-transport`
- Package / checkout label: local PR #45 source checkout, path omitted
- Validation mode: internal live-wrapper controlled validation
- Runtime engine: `docker`
- GPU mode: `off`
- App port: `5000`
- Provider: `google`
- Package flavor label: source-checkout Docker CPU/off validation
- Product UI repair path: blocked
- `provider_tls_repair=true`: blocked
- Browser-triggered default mutation: blocked
- Podman remediation: blocked
- Tester-facing guided repair packaging: blocked

## Planned Wrapper Sequence

Expected helper-controlled step order:

1. `repair`
2. `stop`
3. `start`

No other wrapper or shell command is in scope for the first live run.

Expected timeout budget:

- Repair: 300 seconds
- Stop: 120 seconds
- Start/readiness: 180 seconds
- Overall operation timeout and operation-lock behavior remain unchanged.

## Manual Fallback Commands

Use these only as the audited fallback path if the live validation leaves the
runtime stopped, degraded, or blocked:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off -Port 5000 -NoBrowser -TimeoutSeconds 180
```

If the selected port changes before execution, update the fallback start
command here before running the live sequence.

## Pre-Run Checklist

- [x] Reviewer cleared `0132b13` for internal live-wrapper validation only.
- [x] First live run is Docker CPU/off only.
- [x] Product UI, advertised helper capability, default browser-triggered
  mutation, Podman remediation, and tester-facing packaging remain blocked.
- [x] Release owner confirms the validation window and accepts that the run may
  change TLS trust material and stop/restart the Docker runtime.
- [x] Confirm no other TowerScout package instance is using port `5000`:
  readiness was not reachable on port `5000` during the pre-run status check.
- [x] Confirm the current runtime initial state immediately before execution:
  stopped / not reachable.
- [x] Confirm the internal execution path, not browser input, supplies
  `ExecutionEnabled=true`.
- [x] Confirm the manual fallback commands above are available.

## Execution Outcome - 2026-07-06

- Run result: PARTIAL
- Runtime initial state: stopped / not reachable
- Operation states observed: repair step accepted, stop step reached, then the
  helper operation status could not be persisted because the stop cleanup
  invalidated the active helper session metadata.
- Actual terminal state: no helper terminal state was available after the
  operation lock was cleared.
- Step order observed: repair, stop; start was not reached by the controlled
  runner.
- Terminal classification: validation blocker in helper-controlled stop
  cleanup.
- Readiness returned: no.
- Provider setup could be retried: no, because the runtime was not reachable.
- Fallback command needed: yes.
- Fallback result: manual start fallback was attempted, but the local Docker
  image for the source-checkout runtime was unavailable / pull denied, so the
  runtime remained not reachable on port `5000`.
- Sanitization check: no raw subprocess output, helper token, operation
  credential, `.env` content, certificate subject, certificate thumbprint,
  provider key, full local path, browser network trace, screenshot, or support
  log was recorded.

## Follow-Up Fix - 2026-07-06

- `scripts\stop.ps1` now preserves normal stop behavior by invalidating helper
  session metadata for ordinary user/support stops.
- Helper-controlled stop calls now receive the internal
  `TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION=1` process environment marker.
- When that marker is present, `scripts\stop.ps1` defers helper-session
  invalidation so the controlled operation can persist the stop result and
  proceed to the start step.
- Focused Task-087 unit coverage now asserts the marker reaches the controlled
  stop wrapper and that normal stop cleanup remains present.
- Because the code changed after the partial live run, do not rerun the
  mutating Docker CPU/off validation without a fresh explicit approval.

## Rerun Preparation - 2026-07-06

- Patched PR head prepared for rerun: `7177cc1`.
- The source-checkout runtime still resolves to the local Docker image label
  `towerscout:local`.
- The local image prerequisite has been prepared: `towerscout:local` now exists
  after a source-checkout Docker build.
- This checkout's Docker Compose project remains stopped / clear after the
  targeted cleanup and image build.
- A separate extracted-package TowerScout container is running on a different
  host port and does not conflict with the planned port `5000` rerun.
- No broad Docker prune, unrelated image deletion, or product UI validation was
  performed.
- Do not rerun the mutating Docker CPU/off validation until the release owner
  gives fresh explicit approval for the patched `7177cc1` branch.

## Rerun Outcome - 2026-07-06

- Patched PR head executed: `c55814b`.
- Run result: PASS.
- Runtime initial state: stopped / not reachable.
- Operation states observed: terminal helper state `ready`, current step
  `start`, terminal classification `terminal_success`.
- Actual terminal state: `ready`.
- Step order observed: helper-controlled repair, stop, start sequence completed
  according to the allowlisted operation contract.
- Readiness returned: yes; the application responded on port `5000`.
- Runtime health after rerun: Docker service running / healthy.
- Runtime image after rerun: `towerscout:local`.
- Provider setup could be retried: yes; the application returned to the setup
  flow and the helper response directed provider validation retry.
- Fallback command needed: no.
- Product UI repair path: still blocked.
- `provider_tls_repair=true`: still blocked.
- Browser-triggered default mutation: still blocked.
- Podman remediation: still blocked.
- Tester-facing guided repair packaging: still blocked.
- Sanitization check: no raw subprocess output, helper token, operation
  credential, `.env` content, certificate subject, certificate thumbprint,
  provider key, full local path, browser network trace, screenshot, support log,
  raw Docker JSON, or container labels were recorded.

## Sanitized Evidence To Record After Execution

- Run result: PASS / FAIL / PARTIAL / BLOCKED
- Runtime initial state: running / stopped / degraded / unknown
- Operation states observed:
  - `tls_repair_completed`
  - `runtime_stopped`
  - `ready`
  - `readiness_timeout`
  - `tls_repair_failed`
  - `runtime_stop_failed`
  - `runtime_start_failed`
  - `operation_timeout`
- Actual terminal state:
- Step order observed:
- Terminal classification:
- Readiness returned: yes / no / partial
- Provider setup could be retried: yes / no / not tested
- Fallback command needed: yes / no
- Sanitization check: confirm no raw subprocess output, helper token,
  operation credential, `.env` content, certificate subject, certificate
  thumbprint, provider key, full local path, browser network trace, screenshot,
  or support log was recorded.

## Abort Conditions

Abort and record `BLOCKED` or `PARTIAL` if any of these occur:

- The wrapper contract differs from repair, stop, start.
- Browser input can enable execution or change wrapper paths, arguments,
  interpreter, GPU mode, engine, port, or timeouts.
- Public status, task evidence, PR evidence, or helper output includes raw
  subprocess output, helper credentials, certificate details, provider keys,
  `.env` values, or full local paths.
- The runtime profile is stale, ambiguous, wrong-package, or wrong-port.
- Endpoint protection blocks helper execution in a way that would require
  bypassing the security model.

## Post-Run Gate

Keep product UI, `provider_tls_repair=true`, browser-triggered default mutation,
Podman remediation, and tester-facing guided repair packaging blocked until the
live evidence is reviewed.

Ask the reviewer to evaluate the sanitized evidence before any Gate 3 product
integration design begins.
