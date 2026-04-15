# TASK-051 Phase 1 CUDA Packaging and Enablement Audit

**Audit date**: April 8, 2026  
**Scope**: document current TowerScout CUDA behavior and determine whether CUDA enablement belongs in docs or in `webapp/requirements.txt`

## Local Facts

- Current project interpreter: `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe`
- Current local PyTorch facts:
  - `torch.__version__ == 2.2.1+cpu`
  - `torch.version.cuda is None`
  - `torch.cuda.is_available() == False`
  - `torch.cuda.device_count() == 0`
- This machine is CPU-only for Phase 1 validation purposes.
- Live CUDA execution was not possible locally because no CUDA-capable device was exposed to the interpreter.

## Current TowerScout Runtime Behavior

### What the code does today

- `webapp/ts_yolov5.py`
  - calls `torch.cuda.is_available()`
  - if true, moves the model to CUDA with `.cuda()`
  - if false, falls back to CPU
- `webapp/ts_en.py`
  - calls `torch.cuda.is_available()`
  - if true, loads the EfficientNet model and inputs onto CUDA
  - if false, falls back to CPU
- `webapp/towerscout.py`
  - logs whether Torch CUDA is available at startup

### Phase 1 conclusion on runtime behavior

- TowerScout already auto-uses CUDA when a compatible CUDA-enabled PyTorch build reports CUDA availability.
- No TowerScout-specific setting, env var, or UI action is required to turn CUDA on after the correct PyTorch build is installed.
- TowerScout's CUDA question is primarily an install/setup question, not an app configuration question.

## Official Packaging Guidance Reviewed

Reviewed on April 8, 2026:

- PyTorch Get Started Locally:
  - https://pytorch.org/get-started/locally/
- PyTorch Previous Versions:
  - https://pytorch.org/get-started/previous-versions/

## What the Official PyTorch Guidance Means for TowerScout

### Current install guidance

- The current official PyTorch local install page tells users to choose:
  - OS
  - package manager
  - language
  - compute platform
- For Windows pip installs, the page distinguishes between:
  - no CUDA
  - with CUDA

### Exact relevance to TowerScout's pinned version

- TowerScout currently pins:
  - `torch==2.2.1`
  - `torchvision==0.17.1`
- The official PyTorch previous-versions page lists separate pip commands for PyTorch `2.2.1`:
  - CPU only via `--index-url https://download.pytorch.org/whl/cpu`
  - CUDA 11.8 via `--index-url https://download.pytorch.org/whl/cu118`
  - CUDA 12.1 via `--index-url https://download.pytorch.org/whl/cu121`

### Phase 1 conclusion on user action

- Yes, user action is required to enable CUDA on a CUDA-capable machine.
- The required action is install-time, not runtime:
  - choose the CUDA-enabled PyTorch wheel/index that matches the target machine
  - ensure the machine has a compatible NVIDIA GPU/driver environment
- The generic current TowerScout manifest pin by itself does not document or guarantee CUDA enablement.

## `nvidia-*` Python Packages and Manifest Implications

- Local installed `torch 2.2.1` metadata shows `nvidia-*` package dependencies only under Linux/x86_64 environment markers.
- The clean Windows install proof for the current TowerScout manifest did not install separate `nvidia-*` Python packages.

### Phase 1 conclusion

- CUDA-related `nvidia-*` Python packages should not be added directly to `webapp/requirements.txt` based on current evidence.
- For TowerScout, CUDA packaging should be documented as:
  - a PyTorch wheel-selection/install choice
  - plus machine-level GPU/driver prerequisites
- This should remain documentation guidance unless a future runtime-hardening task changes the PyTorch install contract.

## CPU Fallback Behavior

- Current TowerScout behavior on a non-CUDA machine is correct and automatic:
  - YOLO falls back to CPU
  - EfficientNet falls back to CPU
  - startup logs report that CUDA is unavailable

## Phase 1 Documentation Recommendation

- Document CUDA support in setup/testing docs, not as extra pins in `webapp/requirements.txt`.
- The docs should explicitly say:
  - TowerScout will auto-use CUDA if the installed PyTorch build exposes it
  - enabling CUDA requires a CUDA-enabled PyTorch install choice on compatible hardware
  - no extra TowerScout config step is needed after that
  - CPU-only installs remain supported and are the current local proof path

## Net Result

- CUDA enablement is not a missing TowerScout runtime package problem.
- CUDA enablement is a user-install-choice and environment-prerequisite problem.
- The right immediate Phase 2 surface, if chosen, is documentation cleanup rather than adding CUDA-specific packages to `webapp/requirements.txt`.
