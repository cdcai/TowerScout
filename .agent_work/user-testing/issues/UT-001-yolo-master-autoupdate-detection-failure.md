# UT-001: Pre-Task-055 YOLO Master Autoupdate Detection Failure

**Status**: READY-FOR-RETEST
**Severity**: BLOCKER
**Reporter**: User-testing teammate (name TBD)
**Owner**: Unassigned
**Opened**: 2026-04-09
**Last Updated**: 2026-04-09

## Summary

A teammate's Windows Miniconda run reached the live app and completed the estimate step, but the first detection attempt dropped into the old mutable `ultralytics_yolov5_master` Torch Hub path, auto-updated runtime packages, and then failed image loading with `'JpegImageFile' object has no attribute '_im'`. This matches the pre-Task-055 YOLO runtime contract rather than a new unrelated issue. Task-055 landed the pinned-ref hardening in commit `e4a43c5` on 2026-04-09, so this issue now needs retest on a checkout that includes that change.

## Environment

- OS: Windows (exact version not captured)
- Python: 3.12.13
- Branch: local checkout under `C:\Coding_local\TowerScout-Jono\TowerScout-feature-sprint-05` (exact git branch name not captured)
- Commit: not captured in the artifact
- Guide used: likely `TowerScout_User_Testing_Guide_Windows_Miniconda.txt` (not explicitly confirmed)
- Provider used: Google
- GPU or CPU path: CPU (`Torch CUDA: not available`)

## Reproduction

1. Activate the `towerscout` Miniconda environment and run `python towerscout.py dev` from `webapp`.
2. Open the app, complete a Google-backed estimate request, and confirm the estimate succeeds.
3. Start a full detection request with model `newest`.
4. Observe Torch Hub using `ultralytics_yolov5_master`, downloading `master.zip`, autoupdating runtime packages, and then failing while opening the first JPEG tile.

## Expected Result

The tester can launch TowerScout and complete detection without TowerScout mutating core runtime packages during model startup.

## Actual Result

TowerScout launches successfully, but the detection pipeline fails before inference completes. The artifact shows:

- `Using cache found in C:\\Users\\iek4/.cache\\torch\\hub\\ultralytics_yolov5_master`
- `Downloading: "https://github.com/ultralytics/yolov5/zipball/master"`
- runtime package autoupdates for `requests`, `pillow`, and `pi-heif`
- `AttributeError: 'JpegImageFile' object has no attribute '_im'`
- final backend failure: `ts_errors.ProcessingError: Image loading failed`

## Artifacts

- Artifact folder: [2026-04-09-ut-001-yolo-master-autoupdate-detection-failure](../artifacts/2026-04-09-ut-001-yolo-master-autoupdate-detection-failure/README.md)
- Screenshot: pending
- Terminal log: [conda_output_20260409.txt](../artifacts/2026-04-09-ut-001-yolo-master-autoupdate-detection-failure/conda_output_20260409.txt)
- Other evidence: none

## Triage Notes

- This is not a startup blocker. The app served `/`, returned the Google key to the frontend, and completed tile estimate before the failure.
- The artifact aligns directly with the old mutable Torch Hub behavior that Task-055 replaced:
  - cached repo path: `ultralytics_yolov5_master`
  - download target: `zipball/master`
  - runtime package mutation during detection startup
- Related engineering work:
  - [TASK-055](../../tasks/TASK-055-yolo-torch-hub-pinned-ref-hardening.md)
  - fix commit: `e4a43c5` (`Pin YOLO Torch Hub runtime to tested commit`, 2026-04-09)
- Task-055 changed `webapp/ts_yolov5.py` to load pinned ref `1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c` instead of `master`, refresh only the pinned cache, and document the new runtime contract.
- `TASK-052` smoke coverage has not been completed yet, so keep this issue open for tester verification rather than closing it on engineering analysis alone.
- If a rerun on `e4a43c5` or newer still fails without the `master.zip` path appearing, split that into a new follow-on issue or reopen this one as a post-Task-055 regression.

## Retest Notes

- Retest owner: original tester
- Retest date: pending
- Retest result: pending on a checkout containing `e4a43c5` or newer

## Resolution

Provisional classification: likely resolved by Task-055 because the captured failure depends on the pre-hardening `master` Torch Hub path that no longer exists on the current branch. Do not close this issue until the tester reruns on the hardened branch and confirms detection succeeds.
