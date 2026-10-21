# TowerScout Host Helper

**Applies to**: Deferred Task-087 source code and its exclusion from release control packages
**Last reviewed**: 2026-10-21
**Audience**: Release maintainers, support staff, and reviewers of the Task-087 control plane

## What it is

TowerScout retains Windows host-helper source code intended for a
future guided "repair TLS trust and restart" flow. The helper exists because a
browser app running inside the TowerScout container cannot safely inspect the
Windows certificate store or execute trusted host-side restart commands by
itself.

The deferred helper code is designed to mediate a very small allowlisted set of
TowerScout-owned host actions such as provider TLS repair and restart, while
preserving the selected runtime profile.

## Current release status

The host-helper listener, worker, and entrypoints are **excluded from release
control ZIPs**. Their source and tests remain in Git for deferred Task-087 work.
Local antivirus blocked execution of the unchanged helper module during the
PR #4 audit. Excluding unused executables avoids distributing that module; it
does not certify compatibility with every endpoint's security policy.

Two independent gates keep the browser-triggered mutation path dark:

- Public helper capability gate: `webapp/ts_host_helper.py`
- Frontend browser-mutation gate: `webapp/js/src/setup-wizard.js` and the built
  `webapp/js/towerscout.js`

The Windows launcher leaves the review transport disabled. In an extracted
release package, an inherited `TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED=1` setting
produces a warning and continues through normal startup or shutdown with stale
helper state cleared. It cannot enable the excluded helper. The supported TLS
repair path remains the manual script workflow documented in the Quick Start
and Package Guide:

```powershell
.\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Apply
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off
```

## Security model

The deferred helper scaffolding is intended to follow these constraints when it
is eventually enabled:

- package-local only
- loopback-only listener
- package-root-derived singleton mutex
- bounded session lease with PID/start-time metadata and heartbeat
- durable helper token retained in the package-local host state directory
- explicit Windows ACLs for the state directory, session records, operation
  records, and durable token files
- separate per-launch HMAC key used only to issue narrow, short-lived browser
  authorizations
- allowlisted operations only
- validated enum-style arguments, not browser-provided command strings
- sanitized public operation states rather than raw subprocess output

The helper command map is limited to TowerScout-owned scripts such as repair,
stop, and start operations. The goal is support-safe orchestration, not general
host command execution.

## Package boundary

These executable files remain in the source repository but are excluded from
the release control ZIP:

- `scripts/host-helper.cmd`
- `scripts/host-helper.ps1`
- `scripts/host-helper-worker.ps1`
- `scripts/lib/TowerScoutHostHelper.ps1`

The package retains these shared libraries:

- `scripts/lib/TowerScoutHostHelperState.ps1`
- `scripts/lib/TowerScoutCertificateStore.ps1`

Normal launch and stop use the state library to clear stale session metadata
and bridge environment values. Manual TLS repair and CA import use the
certificate-store library. Removing these dependencies would break supported
operations. Neither library starts the deferred helper listener by itself.
The container image does not copy the Windows `scripts` directory.

## Review-only transport checkpoint

The source tree retains an opt-in Gate 3 review path for deferred work. It is
not available in the release ZIP or supported as an end-user workflow. In a
source checkout with the helper files present, when a maintainer sets
`TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED=1` before using the Windows launcher,
the launcher creates a per-launch helper session, starts the visible
loopback-only PowerShell helper directly, retains its process handle through
startup, and passes only that session's bridge values to the app container.

Do not put the generated session id, session key, or helper port in `.env`.
They are launcher-generated runtime values. The browser receives only
scope-bound, expiring authorizations for helper discovery, repair planning,
and operation polling. It never receives the durable helper token.

The helper holds one package-wide active-operation record, starts only its fixed
detached worker, and returns `202 Accepted` before controlled execution. A
terminal transition releases the active record immediately while retaining a
sanitized status record for bounded reload recovery. The worker rechecks the
session lease, listener PID/start time, and heartbeat while commands run so
explicit invalidation or loss of the supervising listener cancels the process
tree.

Start-authorization replay is idempotent only while the original operation is
active. The helper stores a full SHA-256 fingerprint of the submitted start
authorization for at least the authorization lifetime. Reusing that credential
after a terminal result returns the retained operation as a conflict and never
creates a second operation.

This checkpoint still supports non-mutating contract review only. The helper
continues to advertise `provider_tls_repair: false`, its controlled execution
default is false, and the browser mutation constant remains false.

## What enabling would require

Enabling the browser-triggered helper path is deferred Task-087 work and would
require a separately reviewed change to the package boundary.

Minimum gates before release exposure:

- release-owner sign-off on the helper-availability and browser-mutation gates
- managed-network package validation of helper discovery and live polling
- explicit review of lifecycle cleanup, restart behavior, and rollback evidence
- confirmation that the documented manual fallback remains intact

Until those gates pass, retain the helper as deferred source code and keep its
executables out of release control packages. Do not disable endpoint protection
to run it.
