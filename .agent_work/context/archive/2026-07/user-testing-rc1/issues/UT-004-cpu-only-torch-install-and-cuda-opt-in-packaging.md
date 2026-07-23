# UT-004: Default Install Path Yields CPU-Only Torch; CUDA Requires Explicit Install Choice

**Status**: NEEDS-DECISION
**Severity**: MEDIUM
**Reporter**: Engineering investigation from first-run issue review
**Owner**: Unassigned
**Opened**: 2026-04-09
**Last Updated**: 2026-04-09

## Summary

The current generic install path does not give CUDA-enabled PyTorch to Windows or Linux users automatically. `webapp/requirements.txt` pins plain `torch==2.2.1` and `torchvision==0.17.1`, while the PyTorch installation matrix for `v2.2.1` shows Linux and Windows CUDA installs using explicit `--index-url` targets such as `https://download.pytorch.org/whl/cu118` or `.../cu121`. Both the local workspace and the tester log show `torch 2.2.1+cpu`, which confirms that the observed install path is CPU-only. TowerScout will auto-use CUDA if a compatible CUDA build is already present, but users must choose that install path themselves.

## Environment

- OS: Windows and Linux packaging behavior
- Python: current runtime targets
- Branch: current repo state on 2026-04-09
- Commit: not captured in this document
- Guide used: not applicable
- Provider used: not relevant
- GPU or CPU path: packaging concern

## Reproduction

1. Install TowerScout from the current `webapp/requirements.txt`.
2. Check the installed Torch build.
3. On observed environments, Torch reports as `2.2.1+cpu`.
4. Run TowerScout on a machine with a CUDA-capable GPU and note that CUDA remains unavailable unless Torch was explicitly reinstalled from a CUDA wheel index.

## Expected Result

TowerScout's install story should make the CPU-versus-CUDA choice explicit so GPU-capable users know whether extra steps are required.

## Actual Result

The current state is:

- `webapp/requirements.txt:15-16` pins plain `torch==2.2.1` and `torchvision==0.17.1`.
- Local workspace evidence reports `torch 2.2.1+cpu`, `torch.version.cuda is None`, and `torch.cuda.is_available() == False`.
- The tester log also reports `YOLOv5 ... torch-2.2.1+cpu CPU`.
- TowerScout itself is already coded to use CUDA automatically if available:
  - `webapp/towerscout.py:287`
  - `webapp/ts_en.py:80-86`
  - `webapp/ts_yolov5.py:263-277`

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log:
  - `C:\Users\bg90\Downloads\console_output_20260406_0241p.txt`
- Other evidence:
  - `webapp/requirements.txt:15-16`
  - PyTorch previous versions docs for `v2.2.1`

## Triage Notes

- This confirms suspected first-run issue 3.
- This is not the cause of the current tester failure because the CPU path successfully loaded both models.
- Users who already installed the CPU build into an environment will need to replace it with a matching CUDA build if they want GPU acceleration in that same environment.
- The cleaner long-term packaging path is usually one of:
  - separate documented install commands for CPU and CUDA
  - split requirements files or installer paths
  - keeping Torch out of the universal requirements file and asking the user to choose the appropriate Torch install first

## Retest Notes

- Retest owner: future implementer or documentation owner
- Retest date: pending
- Retest result: pending

## Resolution

Not fixed. This is a packaging and documentation decision rather than a code-path defect inside detection itself.
