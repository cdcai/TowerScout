# UT-005: NumPy 2 Compatibility Is Coupled Across Shapely And OpenCV

**Status**: INVESTIGATED
**Severity**: MEDIUM
**Reporter**: Engineering investigation from first-run issue review
**Owner**: Unassigned
**Opened**: 2026-04-09
**Last Updated**: 2026-04-09

## Summary

The NumPy 2 concern is real, but the current repo state is more nuanced than the suspected list implies. Today, `Shapely==2.0.3` still declares `numpy <2`, so a clean resolver should stay on NumPy 1.x and avoid the exact Shapely import failure on a fresh install. That means suspected issue 4 is not confirmed as a current clean-install blocker under the existing pins. However, this protection is brittle: once Shapely is moved to a NumPy-2-compatible wheel such as `2.0.4+`, the current `opencv-python==4.9.0.80` becomes the next likely break point because OpenCV did not add official NumPy 2 support in its pre-built Python packages until `4.10.0.84`.

## Environment

- OS: any
- Python: especially 3.11 and 3.12
- Branch: current repo state on 2026-04-09
- Commit: not captured in this document
- Guide used: not applicable
- Provider used: not relevant
- GPU or CPU path: not relevant

## Reproduction

### Current manifest behavior

1. Install the current `webapp/requirements.txt`.
2. Let the resolver satisfy `Shapely==2.0.3`.
3. Observe that local installed metadata for Shapely requires `numpy <2,>=1.14`.

### Follow-on risk if the stack moves to NumPy 2

1. Upgrade Shapely to a NumPy-2-compatible release or otherwise allow NumPy 2.x into the environment.
2. Leave `opencv-python==4.9.0.80` in place.
3. Load YOLO through the current Torch Hub path, which imports `cv2` inside the pinned YOLO repo before model load completes.
4. Observe that any `cv2`/NumPy incompatibility would fail during `torch.hub.load()`.

## Expected Result

The dependency set should either:

- stay explicitly on a validated NumPy 1.x stack, or
- move together to a validated NumPy 2-compatible stack

## Actual Result

The current evidence is:

- `webapp/requirements.txt:14` pins `Shapely==2.0.3`.
- Local installed metadata for Shapely 2.0.3 declares `Requires-Dist: numpy <2,>=1.14`.
- `webapp/requirements.txt:20` pins `opencv-python==4.9.0.80`.
- Local installed metadata for OpenCV 4.9.0.80 declares only lower bounds on NumPy and does not itself prevent NumPy 2.
- Shapely release notes show:
  - `2.0.4`: wheels for Python `>= 3.9` are compatible with the upcoming NumPy 2.0 release
  - `2.0.6`: fixes compatibility with NumPy 2.1.0
- OpenCV `4.10.0.84` release notes state: `NumPy 2.0 support in pre-built OpenCV packages for Python 3.9+`
- The pinned YOLO Hub repo imports `cv2` from multiple modules during model load:
  - `models/common.py`
  - `utils/general.py`
  - `utils/plots.py`

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log:
  - `C:\Users\bg90\Downloads\console_output_20260406_0241p.txt` was reviewed and does not show a Shapely or OpenCV import failure
- Other evidence:
  - `webapp/requirements.txt:14,20`
  - local installed metadata:
    - `shapely-2.0.3.dist-info/METADATA`
    - `opencv_python-4.9.0.80.dist-info/METADATA`
  - Shapely release notes for `2.0.4` and `2.0.6`
  - OpenCV `4.10.0.84` release notes
  - OpenCV issue `#997`

## Triage Notes

- Suspected issue 4 is only partially confirmed.
- The exact Shapely/NumPy 2 ABI failure is not the current clean-install baseline because Shapely 2.0.3 still constrains NumPy below 2.
- Suspected issue 5 is a credible follow-on risk and becomes much stronger if Shapely is upgraded or NumPy 2 is otherwise introduced.
- The current tester failure is not this issue because:
  - TowerScout started successfully, which argues against a Shapely startup import failure
  - YOLO loaded successfully, which argues against an immediate `cv2` import failure
- A Shapely fix and an OpenCV fix should be evaluated together because changing only one side changes the resolver behavior and failure surface.

## Retest Notes

- Retest owner: future dependency-update owner
- Retest date: pending
- Retest result: pending

## Resolution

Not fixed. The safest choices are either:

1. explicitly hold the current stack on NumPy 1.x until all runtime packages are validated together, or
2. move Shapely and OpenCV together to validated NumPy-2-compatible releases and rerun first-run/install smoke coverage
