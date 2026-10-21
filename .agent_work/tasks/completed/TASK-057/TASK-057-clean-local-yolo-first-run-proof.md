# TASK-057 Clean Local YOLO First-Run Proof

**Proof date**: 2026-04-13
**Status**: PASS
**Task**: [TASK-057](../tasks/TASK-057-local-yolo-runtime-ownership-and-offline-readiness.md)

## Objective

Record a clean-environment first-run proof for the Task-057 local YOLO runtime contract on the current branch.

This proof is intentionally bounded to the YOLO initialization contract that
Task-057 changed. It does not try to prove the full Flask/browser workflow,
because full app startup still includes unrelated EfficientNet behavior and the
broader app-level smoke contract belongs to `TASK-052`.

## Environment Facts

- Host: Same-device isolated proof run on the primary Windows development machine
- OS: Windows-11-10.0.26100-SP0
- Python: 3.12.5 (tags/v3.12.5:ff3bc82, Aug 6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)]
- Branch: feature-sprint-05
- Commit: 03295ce (dirty worktree with Task-057 changes not yet committed)
- Runtime used for proof: fresh virtual environment at `.agent_work/tmp/task057-proof-venv`
- Proof model: `webapp/model_params/yolov5/newest.pt`
- `torch.__version__`: torch 2.2.1+cpu
- `torch.version.cuda`: None
- `torch.cuda.is_available()`: False
- `ultralytics`: 8.3.249
- `seaborn`: 0.13.2
- `TORCH_HOME`: `C:\Users\bg90\TowerScout\.agent_work\tmp\task057-proof-torchhome`
- `TOWERSCOUT_ALLOW_INSECURE_TLS`: unset

## Proof Method

1. Created a fresh isolated proof environment on the same device.
2. Installed `webapp\requirements.txt` into that environment.
3. Pointed `TORCH_HOME` at a brand-new empty directory for the proof run.
4. Confirmed `TOWERSCOUT_ALLOW_INSECURE_TLS` was unset.
5. Ran a direct `YOLOv5_Detector` initialization against `webapp/model_params/yolov5/newest.pt`.
6. Patched `torch.hub.load` and `torch.hub.download_url_to_file` to raise immediately during the proof run.
7. Confirmed detector initialization still succeeded and left `TORCH_HOME` empty.

## Commands Used

```powershell
Remove-Item .agent_work\tasks\active\TASK-057\evidence\TASK-057-clean-local-yolo-first-run-proof-env.txt -ErrorAction SilentlyContinue
Remove-Item .agent_work\tasks\active\TASK-057\evidence\TASK-057-clean-local-yolo-first-run-proof-terminal.txt -ErrorAction SilentlyContinue

Remove-Item -Recurse -Force .agent_work\tmp\task057-proof-venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .agent_work\tmp\task057-proof-torchhome -ErrorAction SilentlyContinue

py -3.12 -m venv .agent_work\tmp\task057-proof-venv
& .\.agent_work\tmp\task057-proof-venv\Scripts\python.exe -m pip install --upgrade pip
& .\.agent_work\tmp\task057-proof-venv\Scripts\python.exe -m pip install -r .\webapp\requirements.txt

New-Item -ItemType Directory -Force .agent_work\tmp\task057-proof-torchhome | Out-Null
Remove-Item Env:TOWERSCOUT_ALLOW_INSECURE_TLS -ErrorAction SilentlyContinue
$env:TORCH_HOME = (Resolve-Path .\.agent_work\tmp\task057-proof-torchhome).Path

git rev-parse --abbrev-ref HEAD | Tee-Object .agent_work\tasks\active\TASK-057\evidence\TASK-057-clean-local-yolo-first-run-proof-env.txt
git rev-parse --short HEAD | Tee-Object -Append .agent_work\tasks\active\TASK-057\evidence\TASK-057-clean-local-yolo-first-run-proof-env.txt
git status --short | Tee-Object -Append .agent_work\tasks\active\TASK-057\evidence\TASK-057-clean-local-yolo-first-run-proof-env.txt

& .\.agent_work\tmp\task057-proof-venv\Scripts\python.exe -c "import os,platform,sys,torch; from importlib import metadata; print(platform.platform()); print(sys.version); print('torch', torch.__version__); print('torch.version.cuda', torch.version.cuda); print('torch.cuda.is_available', torch.cuda.is_available()); print('ultralytics', metadata.version('ultralytics')); print('seaborn', metadata.version('seaborn')); print('TORCH_HOME', os.environ.get('TORCH_HOME')); print('TOWERSCOUT_ALLOW_INSECURE_TLS', os.environ.get('TOWERSCOUT_ALLOW_INSECURE_TLS'))" | Tee-Object -Append .agent_work\tasks\active\TASK-057\evidence\TASK-057-clean-local-yolo-first-run-proof-env.txt

# Proof runner executed in the clean venv with:
# - torch.hub.load patched to fail
# - torch.hub.download_url_to_file patched to fail
# - direct YOLOv5_Detector load against webapp/model_params/yolov5/newest.pt
```

## Artifacts

- Environment facts log:
  - `C:\Users\bg90\TowerScout\.agent_work\tasks\active\TASK-057\evidence\TASK-057-clean-local-yolo-first-run-proof-env.txt`
- Terminal log:
  - `C:\Users\bg90\TowerScout\.agent_work\tasks\active\TASK-057\evidence\TASK-057-clean-local-yolo-first-run-proof-terminal.txt`
- Screenshot(s):
  - none captured

## Observed Results

### Runtime Install

- Fresh runtime install completed successfully: yes
- Notes:
  - `webapp/requirements.txt` installed successfully into the fresh proof venv.
  - The proof used the validated CPU baseline.

### First Local YOLO Load

- `webapp/model_params/yolov5/newest.pt` loaded successfully: yes
- Resulting model type: `DetectionModel`
- Batch size on this proof machine: `10`
- Notes:
  - `YOLOv5_Detector` initialized successfully from the fresh proof environment.
  - The proof log shows normal model initialization and CPU fallback messaging.

### Torch Hub Independence Check

- `torch.hub.load` patched to fail during proof: yes
- `torch.hub.download_url_to_file` patched to fail during proof: yes
- Detector still initialized successfully: yes
- `TORCH_HOME` remained empty after proof: yes
- Notes:
  - `PROOF_TORCH_HOME_CONTENT_COUNT` was `0`.
  - No Hub cache or download artifact was needed for the YOLO model load.

## Runtime Contract Checks

- CPU baseline used for proof: pass
- TLS bypass was not enabled by default: pass
- Local YOLO load succeeded without Torch Hub cache state: pass
- Local YOLO load succeeded with Torch Hub entrypoints forcibly disabled: pass
- No GitHub/Torch Hub runtime fetches were required for YOLO initialization: pass
- Vendored local runtime contract behaved as intended: pass

## Outcome

- Final result: PASS
- Summary:
  - The isolated same-device proof succeeded on the CPU baseline using a fresh virtual environment and an empty `TORCH_HOME`.
  - `YOLOv5_Detector` loaded `webapp/model_params/yolov5/newest.pt` successfully through the Task-057 local loader path.
  - The same proof still succeeded when both `torch.hub.load` and `torch.hub.download_url_to_file` were patched to fail.
  - `TORCH_HOME` remained empty after the proof, which supports the intended result that Task-057 removed the active YOLO runtime dependence on Torch Hub bootstrap behavior.

## Follow-Up

- Required remediation:
  - None required for the bounded Task-057 proof itself.
- Can `TASK-057` treat the clean local first-run proof item as satisfied: yes
- If no, what remains:
  - N/A
