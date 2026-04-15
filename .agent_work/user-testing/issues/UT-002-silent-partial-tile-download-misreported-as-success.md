# UT-002: Silent Partial Tile Download Is Treated As Success

**Status**: CONFIRMED
**Severity**: HIGH
**Reporter**: Engineering investigation from first-run issue review
**Owner**: Unassigned
**Opened**: 2026-04-09
**Last Updated**: 2026-04-09

## Summary

The current imagery download path confirms the suspected partial-download bug. `fetch_all()` collects per-tile exceptions with `asyncio.gather(..., return_exceptions=True)`, logs them, and raises only when every tile fails. The calling detection flow then assumes all tiles succeeded, assigns `.jpg` filenames to every tile, and marks imagery download progress as complete. If even one tile was not written, the later YOLO image-open step fails with an image-loading error that hides the real download problem.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-09
- Commit: not captured in this document
- Guide used: not applicable
- Provider used: Google or Azure
- GPU or CPU path: not relevant

## Reproduction

1. Start a detection run where at least one tile request fails but at least one other tile succeeds.
2. Let `webapp/ts_maps.py` run `fetch_all()` through `Map.get_sat_maps()`.
3. Observe that the download phase completes with warnings instead of failing the detection request.
4. Observe that `webapp/towerscout.py` assigns `.jpg` filenames to every tile anyway and later detection tries to open files that may not exist.

## Expected Result

Any tile download failure should either abort the imagery phase immediately or produce a validated reduced tile set with accurate success counts and filenames.

## Actual Result

The code currently behaves as follows:

- `webapp/ts_maps.py:272-289` logs failed tiles and raises only if `failed_count == len(urls)`.
- `webapp/towerscout.py:808-809` assigns filenames for all tiles without checking that the files exist.
- `webapp/towerscout.py:832-833` reports imagery progress as if every tile downloaded successfully.
- `webapp/ts_yolov5.py:323-333` then raises an image-loading error on the first missing or invalid file.

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required for code-path confirmation
- Other evidence:
  - `webapp/ts_maps.py:265-291`
  - `webapp/towerscout.py:799-809`
  - `webapp/ts_yolov5.py:323-333`

## Triage Notes

- This matches suspected first-run issue 1.
- The current user tester log in `C:\Users\bg90\Downloads\console_output_20260406_0241p.txt` is not evidence for this issue because that run logged `46/46 tiles successful`.
- The user-facing failure mode is misleading because the download phase reports success and the later model phase reports the first visible error.
- Progress reporting is also inaccurate under partial download failure because it hard-codes all imagery tiles as downloaded.

## Retest Notes

- Retest owner: future implementer or tester
- Retest date: pending
- Retest result: pending

## Resolution

Not fixed. The download path should fail on any tile error unless TowerScout is intentionally redesigned to support partial-tile detection with explicit filtering and accurate progress/reporting.
