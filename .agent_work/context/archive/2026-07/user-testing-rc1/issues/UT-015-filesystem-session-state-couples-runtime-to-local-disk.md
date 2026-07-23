# UT-015: Filesystem Sessions And Session-Persisted Paths Make Deployment State Too Local

**Status**: TRIAGED
**Severity**: HIGH
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

TowerScout currently uses filesystem-backed Flask sessions and stores local-path-dependent workflow state inside those sessions. This works for the current single-host local model, but it is a poor fit for containerized or multi-worker deployment. The April 13 review reconfirmed that values like `tmpdirname` and large workflow payloads are still part of the active contract, even after the stable session-identity fix landed.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not specific
- GPU or CPU path: both

## Reproduction

1. Inspect the Flask session configuration in `webapp/towerscout.py`.
2. Inspect the detection, export, and upload flows that write paths and workflow data into `session`.
3. Observe that the app expects session data and local disk state to stay co-located.

## Expected Result

Deployment-facing state should either be durable and portable, or the session should store only lightweight identifiers that can be resolved in a shared backing store.

## Actual Result

The current code still shows:

- filesystem session configuration in `webapp/towerscout.py`
- local temp directory paths stored in `session['tmpdirname']`
- detection metadata, tiles, and results persisted into the session
- later flows reading local temp paths and session-backed results directly

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/towerscout.py`

## Triage Notes

- This captures senior engineer critique item 9.
- This issue interacts directly with `UT-013`; stable IDs and durable state are linked problems.
- This also affects Docker planning, because replacing a container or adding workers changes the assumptions around local disk affinity.
- Preserve the current contract explicitly for the first Docker milestone, but keep the redesign routed to `TASK-058`.

## Retest Notes

- Retest owner: not applicable
- Retest date: not applicable
- Retest result: not applicable

## Resolution

Still open. Short-term Docker work may still need to support the current local-disk contract, but the longer-term direction should move session data toward stable IDs plus shared backing state rather than local paths and large workflow payloads.
