# UT-003: Archived Legacy Detection Block Still Lives In `towerscout.py`

**Status**: READY-FOR-RETEST
**Severity**: LOW
**Reporter**: Engineering investigation from first-run issue review
**Owner**: Unassigned
**Opened**: 2026-04-09
**Last Updated**: 2026-04-14

## Summary

The original dead-code problem changed shape, but it is not gone. On commit `a2160dc` from April 13, 2026, `POST /getobjects` correctly delegates to `_run_detection_request()`, but the older implementation still remains in `webapp/towerscout.py` as a 475-line module-level string literal beginning `Legacy detection route archived during TASK-056.` The active runtime no longer risks executing the stale path, but engineers still have to read around it and search results still surface it as if it were live code.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not relevant
- GPU or CPU path: not relevant

## Reproduction

1. Inspect `webapp/towerscout.py`.
2. Find `get_objects()` and the active `return _run_detection_request()` delegation.
3. Observe the large triple-quoted block immediately below it beginning `Legacy detection route archived during TASK-056.`
4. Confirm the block is no longer executable code, but still lives inside the production module.

## Expected Result

The route should contain only the active implementation path, with old logic preserved in git history or task documentation rather than inside the runtime module.

## Actual Result

`webapp/towerscout.py` still contains both:

- the active delegation path
- the archived legacy implementation as a large in-module string literal

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/towerscout.py:2084-2090`

## Triage Notes

- This matches suspected first-run issue 2.
- This also corresponds to senior engineer critique item 2.
- `TASK-056` removed the live duplicate execution path but stopped short of actually deleting the old implementation.
- Treat this as a small pre-Docker cleanup item rather than a reason to reopen `TASK-052`.
- The risk is engineering confusion, stale edits, and misleading code review or debugging sessions rather than immediate user-facing failure.

## Retest Notes

- Retest owner: teammate tester or reviewer
- Retest date: pending
- Retest result: pending

## Resolution

`TASK-062` removed the archived legacy `get_objects()` string-literal block from
`webapp/towerscout.py` and left the active route delegation as the only runtime
implementation. Validation reused the bounded host-runtime checks:

- `.\\.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_flask_routes.py -q -p no:cacheprovider`
- `.\\.venv\\Scripts\\python.exe -m pytest tests\\integration\\test_end_to_end.py -q -p no:cacheprovider`

Retest by confirming the archive block no longer exists in
`webapp/towerscout.py`; reopen only if stale detection code is still present in
the production module.
