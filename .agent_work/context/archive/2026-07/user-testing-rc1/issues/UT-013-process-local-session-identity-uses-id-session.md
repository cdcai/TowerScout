# UT-013: Runtime Session Identity Is Derived From `id(session)` Instead Of A Stable Session Token

**Status**: READY-FOR-RETEST
**Severity**: HIGH
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The original concern was valid when this issue was opened, but the active runtime path has since changed. On commit `a2160dc`, `webapp/towerscout.py` now persists a stable random session token under `SESSION_ID_KEY = "ts_session_id"` and derives run identity from that value instead of `id(session)`. This issue should stay open only long enough to confirm that the updated path is what the next smoke or user rerun actually exercises.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not specific
- GPU or CPU path: both

## Reproduction

1. Inspect `_get_session_run_id()` in `webapp/towerscout.py`.
2. Follow the call sites for progress tracking, abort handling, and performance tracking.
3. Confirm that the runtime contract now uses a session-persisted stable token rather than `id(session)`.

## Expected Result

TowerScout should generate and persist a stable session identifier, then derive run identifiers from that stable session identity rather than Python object identity.

## Actual Result

The current code now shows:

- `SESSION_ID_KEY = "ts_session_id"` in `webapp/towerscout.py`
- `_get_session_run_id()` reading or creating a stable random session token and storing it in `session`
- progress, cancel, and detection run-state paths using that session-persisted identifier
- the earlier `id(session)` usage surviving only in stale comments or historical references, not in the active runtime path

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/towerscout.py`
  - `tests/unit/test_runtime_hardening.py`

## Triage Notes

- This captures senior engineer critique item 7.
- The active runtime fix landed as part of `TASK-056`.
- This issue still matters for future background-job work because durable state will need stable IDs anyway.

## Retest Notes

- Retest owner: future implementer
- Retest date: pending
- Retest result: pending

## Resolution

Engineering review on April 14, 2026 found that commit `a2160dc` resolves the original active-runtime issue. Keep this in `READY-FOR-RETEST` until the next smoke or user rerun confirms that no active path still derives session identity from `id(session)`.
