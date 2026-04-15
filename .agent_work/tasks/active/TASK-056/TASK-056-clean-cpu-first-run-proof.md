# TASK-056 Clean CPU First-Run Proof

**Proof date**: 2026-04-13
**Status**: PASS
**Task**: [TASK-056](../tasks/TASK-056-first-run-reliability-and-runtime-determinism-hardening.md)

## Objective

Record a clean-environment first-run proof against the validated Sprint 05 CPU-baseline runtime contract on the current branch.

## Environment Facts

- Host: Same-device isolated proof run on the primary Windows development machine
- OS: Windows-11-10.0.26100-SP0
- Python: 3.12.5 (tags/v3.12.5:ff3bc82, Aug 6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)]
- Branch: feature-sprint-05
- Commit: e4a43c5 (dirty worktree with Task-056 changes not yet committed)
- Working directory used to launch app: `C:\Users\bg90\TowerScout\webapp`
- Provider used for proof: Azure Maps
- `torch.__version__`: torch 2.2.1+cpu
- `torch.version.cuda`: None
- `torch.cuda.is_available()`: False
- `TORCH_HOME`: `C:\Users\bg90\TowerScout\.agent_work\tmp\task056-proof-torchhome`
- `TOWERSCOUT_ALLOW_INSECURE_TLS`: unset
- Browser used: Edge
- Private/incognito session used: yes

## Proof Method

1. Created a fresh isolated proof environment on the same device.
2. Installed `webapp\requirements.txt` into that environment.
3. Pointed `TORCH_HOME` at a brand-new empty directory for the proof run.
4. Confirmed `TOWERSCOUT_ALLOW_INSECURE_TLS` was unset.
5. Started TowerScout from `webapp` with `python towerscout.py dev`.
6. Opened a fresh browser session.
7. Ran estimate on a small area.
8. If estimate succeeded, ran the first full detection.

## Commands Used

```powershell
Remove-Item .agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-env.txt -ErrorAction SilentlyContinue
Remove-Item .agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-terminal.txt -ErrorAction SilentlyContinue

Remove-Item -Recurse -Force .agent_work\tmp\task056-proof-venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .agent_work\tmp\task056-proof-torchhome -ErrorAction SilentlyContinue

py -3.12 -m venv .agent_work\tmp\task056-proof-venv
& .\.agent_work\tmp\task056-proof-venv\Scripts\python.exe -m pip install --upgrade pip
& .\.agent_work\tmp\task056-proof-venv\Scripts\python.exe -m pip install -r .\webapp\requirements.txt

New-Item -ItemType Directory -Force .agent_work\tmp\task056-proof-torchhome | Out-Null
Remove-Item Env:TOWERSCOUT_ALLOW_INSECURE_TLS -ErrorAction SilentlyContinue
$env:TORCH_HOME = (Resolve-Path .\.agent_work\tmp\task056-proof-torchhome).Path

git rev-parse --abbrev-ref HEAD | Tee-Object .agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-env.txt
git rev-parse --short HEAD | Tee-Object -Append .agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-env.txt
git status --short | Tee-Object -Append .agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-env.txt

& .\.agent_work\tmp\task056-proof-venv\Scripts\python.exe -c "import platform,sys,torch; from importlib import metadata; print(platform.platform()); print(sys.version); print('torch', torch.__version__); print('torch.version.cuda', torch.version.cuda); print('torch.cuda.is_available', torch.cuda.is_available()); print('seaborn', metadata.version('seaborn'))" | Tee-Object -Append .agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-env.txt

Push-Location .\webapp
& ..\.agent_work\tmp\task056-proof-venv\Scripts\python.exe .\towerscout.py dev *>&1 | Tee-Object ..\.agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-terminal.txt
Pop-Location
```

## Artifacts

- Environment facts log:
  - `C:\Users\bg90\TowerScout\.agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-env.txt`
- Terminal log:
  - `C:\Users\bg90\TowerScout\.agent_work\tasks\active\TASK-056\evidence\TASK-056-clean-cpu-first-run-proof-terminal.txt`
- Screenshot(s):
  - none captured

## Observed Results

### Startup

- App served successfully at `http://localhost:5000`: yes
- Notes:
  - Startup completed successfully.
  - EfficientNet loaded on CPU.
  - The first run downloaded the EfficientNet checkpoint into the isolated `TORCH_HOME`.

### Estimate Step

- Estimate completed successfully: yes
- Tile count returned: 4
- Notes: Terminal log shows `Estimate complete ... 4 tile(s), ~1.2 seconds`.

### First Full Detection

- First full detection started: yes
- First full detection completed: yes
- Result type:
  - successful detections returned (Yes)
  - successful zero-detection completion (No)
  - failed before completion (No)
- Notes:
  - The first YOLO model load downloaded the pinned Torch Hub ref into the isolated `TORCH_HOME` and completed successfully.
  - Imagery download completed successfully for all 4 tiles.
  - YOLOv5 inference completed on CPU.
  - Post-processing completed with 32 detections, 31 selected after duplicate filtering.
  - Address lookup completed successfully.
  - End-to-end detection request completed in `20.35 seconds`.

## Runtime Contract Checks

- CPU baseline used for proof: pass
- TLS bypass was not enabled by default: pass
- No in-process package mutation occurred during first detection: pass
- No runtime autoupdate of `Pillow`, `Requests`, or equivalent core packages was observed: pass
- Imagery phase behavior matched current contract: pass
- Stable session-based progress/cancel identity was not contradicted by the run: pass

## Torch Hub / Network Notes

- First run used an empty Torch Hub cache: yes
- GitHub/network access was required on the first model load: yes
- If yes, was that behavior expected under the current Task-056 contract: yes
- Notes:
  - The log shows fresh downloads for both the EfficientNet checkpoint and the pinned YOLO ref.
  - The first empty-cache model load succeeded on the current runtime manifest.

## Outcome

- Final result: PASS
- Summary:
  - The isolated same-device proof succeeded on the CPU baseline using a fresh virtual environment and an empty `TORCH_HOME`.
  - Startup, estimate, first pinned-ref YOLO load, imagery download, inference, post-processing, and address lookup all completed successfully.
  - No in-process package mutation or runtime autoupdate of `Pillow`, `Requests`, or similar core packages was observed during first detection.
  - The current Task-056 clean-environment first-run acceptance item is satisfied by this proof artifact.

## Follow-Up

- Required remediation:
- None required for the clean-environment proof itself.
- Can `TASK-056` mark the clean-environment first-run proof item complete: yes
- If no, what remains:
  - N/A
