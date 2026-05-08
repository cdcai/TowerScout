# TASK-065 Browser Provider Regression Evidence

**Date**: 2026-05-08
**Runtime**: Podman on Windows with `podman-compose 1.5.0` selected through `PODMAN_COMPOSE_PROVIDER`
**Service URL**: `http://localhost:5001` for browser validation
**Sensitive Artifact Handling**: Raw browser-run artifacts may contain provider request URLs and key-bearing query strings. This summary records only sanitized status, counts, and artifact locations.

## Preconditions

- TowerScout was running through the Task-065 Podman validation path.
- Readiness reported `ready`.
- Google and Azure provider credentials had been entered through Setup Wizard after importing the local TLS inspection CA bundle into the Podman config volume.
- Required runtime assets were present and readiness reported assets `ok`.

## Google Detection Smoke

**Command**:

```powershell
node tests\frontend\test_detection_workflow_smoke.js --provider=google --base-url=http://127.0.0.1:5001
```

**Result**: PASS

**Summary**:

- Estimate endpoint returned HTTP 200.
- Estimated tile count: 1.
- Detection workflow completed in 20.567 seconds.
- Detection count: 8.
- Selected count: 8.
- Detections with addresses: 8.
- Review list count: 8.
- Visible map detections: 5.
- UI provider: `google`.
- Backend provider: `google`.

**Artifact**: `.agent_work/context/analysis/browser-runs/20260508-125149-google/summary.json`

## Azure Detection Smoke

**Initial Command**:

```powershell
node tests\frontend\test_detection_workflow_smoke.js --provider=azure --base-url=http://127.0.0.1:5001
```

**Result**: FAIL

**Summary**:

- Azure SDK loaded in the browser.
- Provider readiness did not complete within the smoke timeout.
- Browser console/network evidence showed an Azure Maps satellite styling request failing CORS preflight from the `127.0.0.1` origin with HTTP 503 and no `Access-Control-Allow-Origin` response header.
- No TowerScout backend provider-validation or detection failure was identified in this attempt.

**Artifact**: `.agent_work/context/analysis/browser-runs/20260508-124932-azure/summary.json`

**Rerun Command**:

```powershell
node tests\frontend\test_detection_workflow_smoke.js --provider=azure --base-url=http://localhost:5001
```

**Result**: PASS

**Summary**:

- Estimate endpoint returned HTTP 200.
- Estimated tile count: 1.
- Detection workflow completed in 8.129 seconds.
- Detection count: 14.
- Selected count: 14.
- Detections with addresses: 14.
- Review list count: 14.
- Visible map detections: 9.
- UI provider: `azure`.
- Backend provider: `azure`.

**Artifact**: `.agent_work/context/analysis/browser-runs/20260508-125226-azure/summary.json`

## Decision

Use `http://localhost:<port>` as the release launcher browser URL. The Azure browser workflow passed from `localhost` and failed from `127.0.0.1` in this validation environment due to provider-side CORS behavior. Support and readiness tooling may still use loopback addresses for direct API checks, but user-facing browser launch should prefer `localhost`.

## Validation Outcome

The broad provider detection regression requirement is satisfied for Google and Azure when the release launcher uses the `localhost` browser origin. The `127.0.0.1` Azure behavior is documented as a support caveat and mitigated by changing the launcher URL.
