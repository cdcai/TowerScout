# UT-006: Pinned YOLO Hub Autoupdate Mutates Pillow/Requests And Breaks First Detection

**Status**: READY-FOR-RETEST
**Severity**: BLOCKER
**Reporter**: User tester
**Owner**: Unassigned
**Opened**: 2026-04-09
**Last Updated**: 2026-04-14

## Summary

The attached tester log is not the same issue as the older `UT-001` stale-`master.zip` Torch Hub failure. That run used the pinned Torch Hub cache path and appears to have failed because the old runtime contract still allowed upstream YOLO bootstrap code to mutate `pillow` and `requests` in-process during the first detection run. On commit `a2160dc` from April 13, 2026, the active loader no longer uses `torch.hub`, the local loader disables YOLO autoinstall behavior, and the original first-run mutation path should be gone. This issue should stay open only long enough to confirm that a clean-environment detection rerun no longer reproduces the Pillow `_im` failure.

## Environment

- OS: Windows
- Python: 3.12.13
- Branch: local checkout under `C:\Coding_local\TowerScout-Jono\TowerScout-feature-sprint-05`
- Commit: not captured in the tester log
- Guide used: not confirmed
- Provider used: Google
- GPU or CPU path: CPU (`torch-2.2.1+cpu`, `Torch CUDA: not available`)

## Reproduction

1. Install TowerScout from the runtime manifest used before `TASK-057`, leaving the older Torch Hub contract active.
2. Run `python towerscout.py dev` from `webapp`.
3. Load the app, complete a Google-backed estimate request, and then start a full detection request.
4. Let the pinned YOLO Hub path run `check_requirements(...)` during `torch.hub.load(...)`.
5. Observe runtime autoupdates for packages that do not meet the pinned YOLO repo's requirements.
6. Observe the process continue without restart and then fail while opening the first JPEG tile.

## Expected Result

First detection should not mutate core runtime packages in the live process. If dependencies are insufficient, the install flow should catch that before runtime, or TowerScout should fail with a clear dependency error before continuing detection.

## Actual Result

The tester log showed:

- pinned YOLO cache path:
  - `Using cache found in C:\\Users\\iek4/.cache\\torch\\hub\\ultralytics_yolov5_1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c`
- Ultralytics runtime autoupdate:
  - `requirements: Ultralytics requirements ['pillow>=10.3.0', 'requests>=2.32.2'] not found, attempting AutoUpdate...`
  - `Successfully installed pillow-12.2.0 requests-2.33.1`
  - `WARNING requirements: Restart runtime or rerun command for updates to take effect`
- successful model load
- successful imagery download
- first failure after the autoupdate:
  - `Failed to load image ... : 'JpegImageFile' object has no attribute '_im'`
  - `ts_errors.ProcessingError: Image loading failed`

The tester later reported that the application and detections worked afterward, which matches a one-time runtime mutation rather than a persistent model or imagery failure.

## Artifacts

- Artifact folder: none yet
- Screenshot: none provided
- Terminal log:
  - `C:\Users\bg90\Downloads\console_output_20260406_0241p.txt`
- Other evidence:
  - `webapp/requirements.txt`
  - historical Hub-based `webapp/ts_yolov5.py`
  - `UT-014`

## Triage Notes

- This is distinct from `UT-001`.
- `UT-001` depended on the old mutable `ultralytics_yolov5_master` / `master.zip` path.
- The stronger long-term fix delivered in `TASK-057` was to move TowerScout to a vendored local YOLO loader and explicitly disable YOLO autoinstall behavior during model load.
- The remaining YOLO follow-ups from the April 13 review are separate and are tracked in `UT-018` and `UT-019`, not here.

## Retest Notes

- Retest owner: original tester or future implementer
- Retest date: pending on `a2160dc` or newer
- Retest result: pending

## Resolution

Engineering review on April 14, 2026 found that commit `a2160dc` should resolve the original in-process package-mutation failure. Keep this issue in `READY-FOR-RETEST` until a clean-environment detection rerun confirms that first detection no longer mutates packages or throws the Pillow `_im` error.
