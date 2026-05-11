# TASK-051 Phase 1 Dependency Doc Truth Table

**Audit date**: April 8, 2026  
**Reviewed surfaces**:

- `README.md`
- `.agent_work/context/guides/TowerScout_Development_Setup_Guide.txt`
- `.agent_work/context/guides/TowerScout_User_Testing_Guide.txt`
- `.agent_work/context/guides/TowerScout_User_Testing_Guide_Windows_Miniconda.txt`

## Truth Table

| Topic | Manifest state | Current doc state | Observed runtime truth | Phase 1 readout |
| --- | --- | --- | --- | --- |
| Base install from `webapp/requirements.txt` | docs and manifest both say install `webapp/requirements.txt` | `README.md`, the general user guide, and the development guide treat this as the main install step | clean install from the manifest resolved successfully, but the current YOLO path still has undeclared runtime gaps | docs are directionally right, but the manifest is not fully truthful yet |
| `psutil` | not declared explicitly | not called out in reviewed docs | TowerScout imports `psutil` directly in `webapp/ts_performance.py`; current environment only gets it transitively from `ultralytics` | verified missing explicit runtime dependency |
| `tqdm` | not declared | only the Windows Miniconda guide tells users to install it separately | current YOLO Hub load reaches `utils/dataloaders.py`, which imports `tqdm` before `check_requirements(...)` can help | the Windows Miniconda guide is closer to runtime truth than the manifest and other guides |
| `pkg_resources` / `setuptools<82` | not declared | Windows Miniconda guide requires `setuptools<82` and asks users to verify `pkg_resources` imports | fresh current-upstream YOLO Hub snapshots no longer require `pkg_resources`, but stale cached `ultralytics_yolov5_master` snapshots still can; official setuptools docs say `pkg_resources` was removed in `setuptools 82.0.0` on February 8, 2026 | the Miniconda workaround is stale for fresh-cache installs, but stale Hub caches can still trigger this failure until refreshed or bypassed |
| First YOLO load needs network | manifest does not express it | only the Windows Miniconda guide clearly warns that first `torch.hub` model load still needs GitHub access | empty-cache YOLO smoke with temporary `TORCH_HOME` failed without network and succeeded after network was allowed | the general setup/testing docs understate this first-run dependency |
| `seaborn` | declared in runtime manifest | docs do not justify it | blocker probe proved current YOLO Hub load reaches `utils/plots.py`, which imports `seaborn` before `check_requirements(...)` | not a safe Phase 1 remove candidate under the current runtime path |
| `packaging` | not declared explicitly | docs are silent | current YOLO Hub load imports `packaging` before `check_requirements(...)`; clean install gets it only because `geopandas` pulls it in | hidden runtime dependency currently satisfied transitively |
| CUDA enablement | manifest pins generic `torch==2.2.1` / `torchvision==0.17.1` only | development guide says CUDA-capable GPU is optional; other reviewed docs do not explain install-time wheel choice | TowerScout auto-uses CUDA if `torch.cuda.is_available()` is true, but users still have to install a CUDA-enabled PyTorch build and meet system prerequisites | docs are incomplete; this is primarily a documentation problem, not a `requirements.txt` pin problem |

## Guide-Specific Notes

### `README.md`

- Contains model-file links and project overview only.
- Does not describe runtime dependency caveats, first-run Torch Hub behavior, or CUDA install choices.

### `TowerScout_Development_Setup_Guide.txt`

- Correctly identifies `webapp/requirements.txt` as the runtime list.
- Correctly treats CUDA-capable GPU as optional.
- Does not mention:
  - first-run GitHub dependency for `torch.hub`
  - the current `tqdm` gap
  - install-time CPU-vs-CUDA wheel choice for PyTorch

### `TowerScout_User_Testing_Guide.txt`

- Gives a simple install path using only `webapp/requirements.txt`.
- Does not mention:
  - first-run GitHub/Torch Hub dependency
  - current `tqdm` gap
  - CUDA wheel choice

### `TowerScout_User_Testing_Guide_Windows_Miniconda.txt`

- Correctly warns that first YOLO load still needs network access to GitHub.
- Correctly compensates for the current missing `tqdm` gap.
- Correctly preserves a real historical workaround, but overstates it as part of the universal current runtime truth. The real state is cache-dependent.

## Phase 1 Documentation Implications

- The current docs are split between:
  - a mostly clean general install story
  - one Windows-specific guide carrying extra workaround knowledge
- The main doc corrections suggested by Phase 1 are:
  - promote first-run Torch Hub / GitHub access as a real runtime note
  - explain that CUDA enablement requires a CUDA-enabled PyTorch install choice
  - stop treating `pkg_resources` / `setuptools<82` as universally required, while still recognizing that stale cached Hub snapshots can hit that failure
  - align the manifest or docs around the verified `tqdm` and `psutil` gaps
