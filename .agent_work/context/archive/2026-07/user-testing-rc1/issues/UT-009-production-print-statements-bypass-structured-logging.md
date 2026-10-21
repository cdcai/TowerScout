# UT-009: Production Runtime Paths Still Use `print()` Instead Of Structured Logging

**Status**: READY-FOR-RETEST
**Severity**: MEDIUM
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The codebase already has a TowerScout logging layer, but active backend paths still emit diagnostics with raw `print()` calls. On commit `a2160dc`, the hot `POST /getobjects` path is much cleaner than it was on April 10, but `webapp/towerscout.py` still contains 60 active `print()` calls outside the archived legacy block and another 74 `print()` calls inside that archived block. The remaining live calls are concentrated in `get_objects_custom()`, model upload, dataset export/write, manual-tower addition, dataset restore, and startup. This still weakens observability and would create noisy container logs during non-detection operations.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not specific
- GPU or CPU path: both

## Reproduction

1. Search the runtime backend modules for active `print()` usage.
2. Separate the archived string-literal block from the active runtime code.
3. Compare that with the structured logging helpers already present in `webapp/ts_logging.py`.

## Expected Result

Production runtime paths should emit structured logs through TowerScout's logging helpers, with consistent levels and sanitization rules.

## Actual Result

The current evidence shows:

- 60 active `print()` calls remain in `webapp/towerscout.py` outside the archived legacy block
- 74 additional `print()` calls remain inside the archived legacy block that should be deleted with `UT-003`
- `webapp/ts_imgutil.py:33-34` still prints parsing failures directly
- `webapp/ts_logging.py` already contains structured logging helpers, but the affected paths have not been fully migrated

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/towerscout.py`
  - `webapp/ts_imgutil.py:33-34`
  - `webapp/ts_logging.py`

## Triage Notes

- This captures senior engineer critique item 3.
- `TASK-056` already cleaned the touched detection and network paths, so the issue is narrower than it looked on April 10.
- The remaining highest-value cleanup is in export, upload, dataset restore, and manual-addition paths that users can still hit during normal workflows.
- Treat the active-path cleanup as a bounded pre-Docker follow-up and leave repo-wide or architectural logging consolidation to `TASK-059`.

## Retest Notes

- Retest owner: teammate tester or reviewer
- Retest date: pending
- Retest result: pending

## Resolution

`TASK-062` replaced the bounded active-path `print()` calls in
`webapp/towerscout.py` and `webapp/ts_imgutil.py` with structured TowerScout
logging, including model upload, dataset export/write, manual-addition restore
paths, startup, and polygon-parse failures. Validation covered the affected
route surface and loader contract:

- `.\\.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_flask_routes.py -q -p no:cacheprovider`
- `.\\.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_yolov5_local_loader.py -q -p no:cacheprovider`

Retest by searching the bounded runtime paths for active `print()` usage and
spot-checking the touched routes in logs. Broader repo-wide logging work stays
deferred to `TASK-059`.
