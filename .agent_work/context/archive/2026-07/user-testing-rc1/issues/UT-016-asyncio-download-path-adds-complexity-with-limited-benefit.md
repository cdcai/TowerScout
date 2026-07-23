# UT-016: Asyncio Download Plumbing Adds Complexity But The Request Path Still Blocks

**Status**: TRIAGED
**Severity**: MEDIUM
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The current tile-download path uses `asyncio`, but the surrounding request architecture remains synchronous. TowerScout still creates event loops, passes them into the map provider, and then blocks on `run_until_complete(...)`. The April 13 review reconfirmed that this is real complexity without a true asynchronous request architecture, but it remains secondary to the larger background-job and durable-state design work.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: Google and Azure
- GPU or CPU path: not relevant

## Reproduction

1. Inspect the global and per-request event loop setup in `webapp/towerscout.py`.
2. Inspect `webapp/ts_maps.py` to see how the async download helpers are invoked.
3. Observe that the request thread still blocks on loop execution and later loop cleanup.

## Expected Result

Concurrency plumbing should either provide a clear architectural benefit or be simplified so it is easier to reason about cancellation, failures, and cleanup.

## Actual Result

The current code still shows:

- a global event loop initialized in `webapp/towerscout.py`
- a per-request event loop created for imagery download
- `webapp/ts_maps.py` blocking on `loop.run_until_complete(...)`
- async download helpers inside `webapp/ts_maps.py`

TowerScout therefore carries event-loop complexity while still running detection synchronously inside the request lifecycle.

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/towerscout.py`
  - `webapp/ts_maps.py`
  - `UT-002`

## Triage Notes

- This captures senior engineer critique item 10.
- This issue is related to `UT-002` because the current partial-failure behavior lives in the async download layer.
- It should influence how the imagery path is touched, but it should not become a standalone Sprint 05 detour.
- Revisit simplification together with `TASK-058`.

## Retest Notes

- Retest owner: not applicable
- Retest date: not applicable
- Retest result: not applicable

## Resolution

Still open. Simplify only with care; if the current async download path remains, it should at least keep clear failure semantics and loop lifecycle boundaries.
