# TASK-051 Phase 1 Decision Memo

**Status**: Phase 1 complete; Option 2 selected and executed for Phase 2 follow-through, with a post-close stale-cache correction recorded  
**Date**: April 8, 2026

## Decision Update

- Selected follow-on path: **Option 2**
- Selection date: **April 8, 2026**
- Authorized Phase 2 scope:
  - add `psutil` and `tqdm` to `webapp/requirements.txt`
  - update active runtime/setup guides to remove stale `pkg_resources` / `setuptools<82` guidance
  - document first-run Torch Hub / GitHub dependence
  - document CUDA install-time wheel choice and automatic runtime use
- Explicit non-goals for the selected path:
  - no Torch Hub redesign
  - no Docker work
  - no broader YOLO-adjacent dependency reduction pass

## Phase 2 Execution Confirmation

- Phase 2 execution date: **April 8, 2026**
- `webapp/requirements.txt` now explicitly includes:
  - `psutil==7.1.3`
  - `tqdm==4.67.1`
- Active runtime/setup guides were updated to:
  - remove the stale `pkg_resources` / `setuptools<82` workaround from the current runtime path
  - document first-run Torch Hub / GitHub dependence
  - document CUDA wheel-selection requirements and automatic runtime use
- Validation rerun results:
  - startup/import smoke passed
  - `pytest --collect-only tests -q` collected `159` tests
  - clean-manifest install proof passed
  - empty-cache YOLO proof still fails offline and succeeds once network access is allowed
- Residual risk intentionally left in place:
  - first-run GitHub / Torch Hub dependence remains part of the current runtime contract until a separate hardening task changes that behavior

## Post-Close Correction: Stale Hub Cache Drift

- On April 8, 2026, a user terminal log showed TowerScout loading a cached `ultralytics_yolov5_master` snapshot that still imported `pkg_resources` from `utils/general.py`.
- The earlier `TASK-051` statement that `pkg_resources` was not part of the current runtime truth was correct for the audited fresh-cache upstream path, but too narrow for stale cached Hub snapshots.
- Current upstream/fresh-cache YOLOv5 no longer imports `pkg_resources`; stale cached Hub repos still can.
- A short-term mitigation now exists in `webapp/ts_yolov5.py`:
  - detect the `pkg_resources` stale-cache failure
  - clear the stale cached YOLOv5 Hub repo
  - retry once with `force_reload=True`
- This corrects the immediate user-facing regression without changing the larger conclusion that mutable Torch Hub runtime loading is the root design risk.

## Verified Runtime Keeps

- Direct runtime keeps:
  - `aiofiles`
  - `aiohttp`
  - `efficientnet_pytorch`
  - `fiona`
  - `Flask`
  - `python-dotenv`
  - `geopandas`
  - `Pillow`
  - `Requests`
  - `Shapely`
  - `torch`
  - `torchvision`
  - `waitress`
  - `flask-session`
- Indirect current-YOLO-path keeps:
  - `ultralytics`
  - `opencv-python`
  - `seaborn`

## Verified Move/Remove Candidates

- None were proven safe in Phase 1.
- `seaborn` was the strongest initial removal candidate, but blocker proof showed the current YOLO Torch Hub load reaches `utils/plots.py`, which imports `seaborn` before `check_requirements(...)` can intervene.

## Verified Missing Dependencies

- `psutil`
  - direct TowerScout runtime import in `webapp/ts_performance.py`
  - currently present only because `ultralytics` installs it transitively
- `tqdm`
  - not installed by the current clean manifest proof
  - current YOLO Torch Hub load reaches `utils/dataloaders.py`, which hard-imports `tqdm`

## Verified Non-Runtime / Stale-Doc Items

- `pkg_resources`
  - not required by the current fresh-cache TowerScout runtime path
  - still reachable through stale cached YOLO Torch Hub snapshots created before upstream removed the `pkg_resources` import
  - should be treated as a cache-drift compatibility surface rather than a fresh runtime manifest gap

## CUDA Packaging and Enablement Conclusions

- TowerScout already auto-uses CUDA when `torch.cuda.is_available()` is true.
- No TowerScout-specific runtime toggle is needed to enable CUDA after installation.
- User action is still required on CUDA-capable machines:
  - install a CUDA-enabled PyTorch build instead of a CPU-only/default path
  - have a compatible NVIDIA GPU/driver environment
- Current evidence does not support adding direct `nvidia-*` package pins to `webapp/requirements.txt`.
- CUDA belongs in setup/runtime documentation, not in extra TowerScout manifest pins, unless a later task changes the PyTorch install contract.

## Additional Hidden Runtime Edges

- `packaging`
  - current YOLO load path imports it before `check_requirements(...)`
  - currently satisfied transitively by `geopandas`
- `pandas`
  - current YOLO load path imports it before `check_requirements(...)`
  - currently satisfied transitively by `geopandas`
- `PyYAML`
  - current YOLO load path imports it
  - currently satisfied transitively by explicit `ultralytics`
- `cachelib`
  - runtime dependency of `flask-session`
  - currently satisfied transitively

## Unresolved Items

- Whether Phase 2 should add only the two strongest explicit gaps:
  - `psutil`
  - `tqdm`
- Whether Phase 2 should also make hidden transitive YOLO edges explicit:
  - `packaging`
  - `pandas`
- Whether the first-run GitHub/Torch Hub dependency should merely be documented or eliminated through runtime hardening
- Whether a future dependency split is worth pursuing before replacing the current `torch.hub` loading strategy

## Smallest Safe Next-Step Options

### Option 1: Manifest Cleanup Only

- Add only:
  - `psutil`
  - `tqdm`
- Keep all current YOLO-adjacent packages
- Leave docs mostly unchanged except where directly wrong

### Option 2: Manifest Cleanup Plus Runtime-Doc Cleanup

**Selected** for Phase 2 on April 8, 2026.

- Do Option 1
- Also:
  - remove `pkg_resources` / `setuptools<82` as a required runtime workaround from the Windows Miniconda guide
  - document first-run GitHub/Torch Hub dependency
  - document CUDA wheel choice and auto-use behavior

### Option 3: Runtime Hardening First, Then Revisit Cleanup

- First replace or harden the current `torch.hub` runtime path so TowerScout no longer depends on:
  - live GitHub retrieval on first load
  - YOLOv5's broader import graph
- Then re-run the dependency split audit
- This is the right path if the goal is to truly reduce the runtime set rather than just make today's contract more truthful

### Option 4: Document Current Truth Only and Defer Manifest Changes

- Accept the current runtime contract for now
- Treat Phase 1 as a deployment-readiness reality check only
- Defer all manifest edits to a later task

## Recommended Readout

- If the goal is **truthfulness without redesign**, Option 2 is the smallest safe Phase 2.
- If the goal is **shrinking YOLO-adjacent runtime dependencies or removing first-run GitHub dependence**, Option 3 is the technically sounder next step.

## Phase Boundary

- Phase 1 is complete.
- Option 2 is selected and authorized for Phase 2 execution.
- No runtime-hardening changes or Docker work are part of the selected Phase 2 path.
