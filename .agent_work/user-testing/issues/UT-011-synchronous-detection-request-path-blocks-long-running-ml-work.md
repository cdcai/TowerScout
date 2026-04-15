# UT-011: Detection Still Runs Synchronously Inside The HTTP Request Path

**Status**: TRIAGED
**Severity**: HIGH
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The current detection architecture still performs the full ML workflow inside the request that handles `POST /getobjects`. Progress polling improves UX, but it does not change the fact that the request thread performs model loading, tile download, model inference, and geocoding before returning the final response. The April 13 review reconfirmed that this remains the most consequential architecture issue for production-style deployment, but it is still broader than the bounded smoke and Docker baseline work already completed.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: Google and Azure
- GPU or CPU path: both

## Reproduction

1. Start a full detection request through `POST /getobjects`.
2. Follow the route from `get_objects()` into `_run_detection_request()`.
3. Observe that the request path performs detection work inline and only returns after model inference and later post-processing finish.
4. Observe that the progress endpoint is a side-channel into in-process state, not a background job system.

## Expected Result

Long-running detection work should eventually run as an explicit background job with stable job identity and clear completion and error states, especially for containerized deployment.

## Actual Result

The current request path still does the following inline:

- `POST /getobjects` dispatches directly into `_run_detection_request()`
- `_run_detection_request()` performs validation, model initialization, tile download, inference, and result processing in that same request lifecycle
- progress polling reports process-local state, not queued background work

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: senior critique references request durations in the ~70-160 second range
- Other evidence:
  - `webapp/towerscout.py`
  - `webapp/ts_progress.py`

## Triage Notes

- This captures senior engineer critique item 5.
- This is primarily an architecture and deployment risk, not a newly discovered first-run bug.
- This interacts directly with `UT-013` and `UT-015` because stable job identity and durable state become more important once work leaves the request thread.
- Route this to `TASK-058` rather than reopening `TASK-052`.

## Retest Notes

- Retest owner: not applicable
- Retest date: not applicable
- Retest result: not applicable

## Resolution

Still open. Keep the current synchronous path stable for the immediate Docker baseline, but treat background-job architecture as the next required step before claiming production-style deployment readiness.
