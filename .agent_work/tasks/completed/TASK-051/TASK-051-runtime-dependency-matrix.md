# TASK-051 Phase 1 Runtime Dependency Matrix

**Audit date**: April 8, 2026  
**Task**: `TASK-051` Phase 1  
**Scope**: runtime dependency truth audit only; no manifest edits performed

## Environment Facts

- Host: Windows workspace at `C:\Users\bg90\TowerScout`
- Active project interpreter used for runtime proof: `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe`
- Active project interpreter facts:
  - `torch 2.2.1+cpu`
  - `torch.version.cuda is None`
  - `torch.cuda.is_available() == False`
  - `torch.cuda.device_count() == 0`
- Existing local Torch Hub cache was present at `C:\Users\bg90\.cache\torch\hub\ultralytics_yolov5_master`
- Windows PowerShell import/startup smoke required `PYTHONIOENCODING=utf-8` because `webapp/towerscout.py` prints a rocket emoji at import time

## Phase 1 Proof Methods

- Static import scan across `webapp/`, `tests/`, `Model/`, and `SyntheticData/`
- App import/startup smoke with:
  - `TOWERSCOUT_LAZY_MODEL_INIT=1`
  - test provider-key env vars
  - `PYTHONIOENCODING=utf-8`
- Clean install proof with isolated target install:
  - `python -m pip install --target .agent_work/tmp/task051-target-audit -r webapp/requirements.txt`
- Empty-cache YOLO smoke with temporary `TORCH_HOME`
- Focused blocker probes to simulate missing imports on the current YOLO Torch Hub path

## Declared `webapp/requirements.txt` Classification

| Package | Phase 1 classification | Evidence |
| --- | --- | --- |
| `aiofiles` | direct runtime | `webapp/ts_maps.py` imports `aiofiles` |
| `aiohttp` | direct runtime | `webapp/ts_maps.py` imports `aiohttp` |
| `efficientnet_pytorch` | direct runtime | `webapp/ts_en.py` imports `EfficientNet` |
| `fiona` | direct runtime | ZIP code runtime depends on `geopandas.read_file(...)`; clean install pulled `fiona` as the geospatial backend |
| `Flask` | direct runtime | `webapp/towerscout.py` imports Flask app/runtime objects |
| `python-dotenv` | direct runtime | `webapp/towerscout.py` and `webapp/ts_config.py` load dotenv config |
| `geopandas` | direct runtime | `webapp/ts_zipcode.py` imports `geopandas` for ZIP boundary search |
| `Pillow` | direct runtime | `webapp/ts_yolov5.py`, `webapp/ts_imgutil.py`, and `webapp/towerscout.py` import `PIL` |
| `Requests` | direct runtime | `webapp/ts_maps.py`, `webapp/ts_geocoding.py`, and `webapp/ts_config.py` import `requests` |
| `seaborn` | indirect runtime through current YOLO Torch Hub behavior | Blocker probe showed current `torch.hub.load(..., 'custom', ...)` reaches `utils/plots.py`, which imports `seaborn` before `check_requirements(...)` runs |
| `Shapely` | direct runtime | `webapp/ts_imgutil.py` and `webapp/ts_validation.py` import `shapely` |
| `torch` | direct runtime | `webapp/towerscout.py`, `webapp/ts_yolov5.py`, `webapp/ts_en.py`, and `webapp/ts_performance.py` import `torch` |
| `torchvision` | direct runtime | `webapp/ts_en.py` imports `torchvision.transforms` |
| `ultralytics` | indirect runtime through current YOLO Torch Hub behavior | Cached and empty-cache `hubconf.py` import `ultralytics.utils.patches.torch_load` |
| `waitress` | direct runtime | `webapp/towerscout.py` imports `waitress.serve` |
| `opencv-python` | indirect runtime through current YOLO Torch Hub behavior | Current YOLO load path imports `cv2` from `utils/general.py`, `models/common.py`, and `utils/plots.py` |
| `flask-session` | direct runtime | `webapp/towerscout.py` imports `Session` from `flask_session` |

## Verified Missing Explicit Runtime Dependencies

| Package | Current state | Evidence | Phase 1 conclusion |
| --- | --- | --- | --- |
| `psutil` | not declared in `webapp/requirements.txt` | `webapp/ts_performance.py` directly imports `psutil`; clean install only received it transitively from `ultralytics` | verified missing explicit runtime dependency |
| `tqdm` | not declared in `webapp/requirements.txt` | clean install target did not include `tqdm`; simulating missing `tqdm` caused current local YOLO Hub load to fail in `utils/dataloaders.py` before `check_requirements(...)` could recover | verified missing runtime dependency under the current YOLO Torch Hub path |

## Hidden Runtime Dependencies Currently Satisfied Transitively

| Package | Where it comes from today | Evidence | Phase 1 conclusion |
| --- | --- | --- | --- |
| `packaging` | transitively installed by `geopandas` in the current manifest | current YOLO load path imports `packaging` in `utils/general.py` before `check_requirements(...)`; blocker probe confirmed it is required on load | real runtime dependency, currently hidden by `geopandas` transitive install |
| `pandas` | transitively installed by `geopandas` in the current manifest | current YOLO load path imports `pandas` in `models/common.py`, `utils/general.py`, and `utils/plots.py` | real runtime dependency, currently hidden by `geopandas` transitive install |
| `PyYAML` | transitively installed by explicit `ultralytics` dependency metadata | current YOLO load path imports `yaml` in `utils/general.py` and related modules | real runtime dependency, already satisfied transitively |
| `cachelib` | transitively installed by `flask-session` | clean install pulled `cachelib`; runtime session support comes from `flask-session` | transitive runtime dependency, not a current install gap |
| `pyproj` | transitively installed by `geopandas` | clean install pulled `pyproj`; ZIP boundary support depends on the geopandas stack | transitive runtime dependency, not a current install gap |

## Verified Non-Runtime or Optional Items

| Item | Evidence | Phase 1 conclusion |
| --- | --- | --- |
| `pkg_resources` via `setuptools` | not part of the current fresh-cache upstream path, but still referenced by some stale cached `ultralytics_yolov5_master` snapshots | Phase 1 fresh-cache blocker did not break the current custom YOLO load; a post-close user terminal log on April 8, 2026 showed a cached Hub snapshot importing `pkg_resources` from `utils/general.py` and failing under a newer setuptools environment | cache-dependent compatibility surface, not a fresh-manifest add candidate; stale cached Hub repos remain a runtime risk until refreshed or bypassed |
| `redis` | `webapp/ts_geocache.py` imports `redis` only inside the `if redis_url:` branch; default TowerScout cache factory does not pass a Redis URL | optional enhancement dependency, not part of the default runtime contract |

## Research and Test Surface Separation

- `tests/` imports `pytest`, `pytest-mock`, `numpy`, and test helpers; these are not runtime requirements.
- `Model/` imports `tqdm`, `cv2`, `numpy`, and Torch training helpers, but those findings were kept separate from runtime conclusions.
- `SyntheticData/` imports `cv2`, `numpy`, `scipy`, and augmentation helpers; these are research/training surfaces, not evidence by themselves for runtime manifest needs.
- No package currently declared in `webapp/requirements.txt` was proven safe to reclassify as dev/test-only or research-only in Phase 1.

## Phase 1 Readout

- No verified remove/move candidates were found inside the current runtime manifest.
- `seaborn`, `opencv-python`, and `ultralytics` remain keep-for-now packages because the current YOLO Torch Hub import path reaches them before any runtime hardening change is made.
- The strongest manifest truthfulness gaps are:
  - `psutil`
  - `tqdm`
- The strongest hidden transitive runtime edges are:
  - `packaging`
  - `pandas`
- `pkg_resources` is not part of the current fresh-cache upstream path, but stale cached Torch Hub snapshots can still require it; this is a cache-drift risk, not a reason to add `pkg_resources` back to the runtime manifest.

## Post-Close Correction

- On April 8, 2026, a real user terminal log showed TowerScout loading a cached `ultralytics_yolov5_master` snapshot that still imported `pkg_resources` in `utils/general.py`.
- The original Phase 1 conclusion about `pkg_resources` was therefore too narrow: it was correct for the audited fresh-cache upstream path, but not for stale cached Hub snapshots.
- A short-term mitigation now exists in `webapp/ts_yolov5.py` to clear `pkg_resources`-era cached Hub repos and retry a fresh load once.
