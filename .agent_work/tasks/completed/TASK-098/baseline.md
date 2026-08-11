# Task-098 Pre-Change Baseline

**Status**: COMPLETE - PYTHON 3.12 HOST AND PYTHON 3.11 DOCKER CPU CAPTURED
**Baseline Date**: July 24, 2026
**Planning Checkpoint**: `d336686`
**Source Commit Before Task-098 Code Changes**: `350d56deec7c85545386e3120c1896d48ba20b39`
**Execution Branch**: `fix/task-098-dependency-security`

## Purpose

Record the reproducible functional, dependency, model/output, startup, and
performance state required by Task-098 before dependency pins, application
code, runtime behavior, release assets, alert state, or external repositories
are changed.

## Baseline Contract

- Use only sanitized, repository-owned fixtures and trusted checksummed assets.
- Record exact interpreter, dependency, model, and asset identities.
- Run maintained unit and affected integration checks on Python 3.11 and 3.12
  where those interpreters are locally available.
- Record skipped or unavailable evidence as an explicit external gate; do not
  infer a pass.
- Use three warmed same-host runs for startup, YOLO/EfficientNet inference,
  total local detection, and peak-memory comparisons where the trusted assets
  and runtime profile are available.
- Do not begin Slice A implementation until the available pre-change evidence
  is captured and any unavailable runtime evidence is bounded.

## Environment

- Host: Windows 11 `10.0.26100`, AMD64.
- Available interpreters: Python 3.12.5 and 3.13; Python 3.11 is not installed
  on the host.
- Baseline interpreter: Python 3.12.5, 64-bit.
- Docker CPU interpreter: Python 3.11.15, 64-bit, from a fresh CPU image built
  from the source checkpoint.
- Node: 24.14.0; npm: 11.10.1. CI remains on Node 18.
- Clean environment:
  `tmp/task098-baseline/py312-clean` (ignored task scratch).
- ML policy: CPU forced with `TOWERSCOUT_DEVICE=cpu`; debug-image capture off.

### Docker CPU Isolation

- Docker Engine/client: 29.5.3; Docker Compose: 5.1.4.
- Unique baseline tag:
  `towerscout:task098-py311-baseline-350d56d`.
- Baseline image ID:
  `sha256:989279ec930076e8d44a8fed30469dfc01df9032ef8faa26a47df986ce6b1f29`.
- OCI revision label:
  `350d56deec7c85545386e3120c1896d48ba20b39`; flavor label: `cpu`.
- Fresh base pulls:
  - Node 18:
    `sha256:f9ab18e354e6855ae56ef2b290dd225c1e51a564f87584b9bd21dd651838830e`
  - Python 3.11:
    `sha256:b18992999dbe963a45a8a4da40ac2b1975be1a776d939d098c647482bcad5cba`
- The image was built with `--pull --no-cache`; no pre-existing application
  image or build-cache layer was reused.
- Test containers used no Compose project, published ports, or named volumes.
  Repository source and trusted models were mounted read-only. Test scratch
  and every image-declared writable runtime path used disposable tmpfs mounts.
- A pre-existing RC7.1 container on host port 5005 was not reused, stopped, or
  inspected for application data and remained healthy after the baseline.
- All Task-098 test containers and their disposable storage were removed. The
  uniquely tagged baseline image is retained only for after-change comparison.

## Dependency Resolution

- Reproduced Docker installation order: CPU PyTorch pair first, followed by
  `webapp/requirements.txt` and `requirements-dev.txt`.
- `pip check`: PASS; no broken requirements.
- Security-relevant direct resolution:
  - `aiohttp==3.9.3`
  - `fiona==1.9.6`
  - `Flask==3.0.2`
  - `geopandas==0.14.3`
  - `Pillow==12.2.0`
  - `python-dotenv==1.0.0`
  - `torch==2.2.1+cpu`
  - `torchvision==0.17.1+cpu`
  - `waitress==3.0.0`
- Other runtime pins resolved as declared, including `numpy==1.26.4`,
  `opencv-python==4.9.0.80`, `pandas==2.3.3`, `psutil==7.1.3`,
  `Requests==2.33.1`, and `ultralytics==8.3.249`.
- Python 3.11 resolved the same security-relevant and runtime versions from
  binary wheels in the fresh Docker CPU build:
  `aiohttp==3.9.3`, `fiona==1.9.6`, `Flask==3.0.2`,
  `geopandas==0.14.3`, `Pillow==12.2.0`, `python-dotenv==1.0.0`,
  `torch==2.2.1+cpu`, `torchvision==0.17.1+cpu`, and
  `waitress==3.0.0`.
- The other recorded direct runtime resolutions also match Python 3.12:
  `numpy==1.26.4`, `opencv-python==4.9.0.80`, `pandas==2.3.3`,
  `psutil==7.1.3`, `Requests==2.33.1`, and
  `ultralytics==8.3.249`.
- Python 3.11 `pip check`: PASS; no broken requirements.

## Maintained Functional Tests

- Clean Python 3.12 unit suite: PASS, 259 passed and 74 skipped in 117.52
  seconds. The skips are the repository-level Azure, framework, legacy image,
  and legacy validation markers that Task-098 may not count as touched-path
  coverage.
- Clean Python 3.12 broad integration suite: BASELINE DRIFT, 20 passed, 2
  skipped, and 4 failed.
  - Two failures use Flask session state outside a request context.
  - Two failures expect geocache clustering at the exact 100 m boundary.
  - These failures are outside the current Task-098 touched surfaces and are
    preserved as pre-change drift; they are not silently treated as passes.
- ML-focused maintained gate: PASS, 8 passed across the local YOLO loader and
  current end-to-end smoke.
- Setup Wizard validation contract: PASS.
- ProviderStateManager regression contract: PASS; forced Azure failure output
  is the expected negative-path assertion.
- Status-output contract: PASS.
- Blocking flake8 syntax/undefined-name gate: PASS, zero findings.
- Clean Docker CPU Python 3.11 unit suite: PASS, 212 passed and 121
  Linux/platform-feature skips in 28.42 seconds. The lower pass count and
  higher skip count reflect the repository's Windows-gated tests.
- Docker CPU Python 3.11 broad integration suite: reproduced the Python 3.12
  baseline drift exactly, with 20 passed, 2 skipped, and the same 4 geocoding
  failures in 30.57 seconds.
- Docker CPU Python 3.11 ML-focused gate: PASS, 8 passed across the local YOLO
  loader and current end-to-end smoke in 26.83 seconds.

## Model, Output, And Performance Evidence

- Trusted asset hashes match `webapp/asset_manifest.v1.json`:
  - YOLO `newest.pt`:
    `27315E156D8370D51D9C2A3C047C4BF5CC0C8AE1521036BDF800B7A8A81554E6`
  - EfficientNet `b5_unweighted_best.pt`:
    `645113BADFCD17A1F9B451AABB54BF80E115A4FAACEB65E0CE3FC8DBFB108A5D`
  - All seven local ZCTA files match the manifest checksums.
- Deterministic fixture: generated 640x640 solid RGB `(127, 127, 127)` image.
- Three warmed CPU runs:
  - TowerScout lazy import: 9.661896, 10.214581, 10.417987 seconds; median
    10.214581 seconds.
  - YOLO inference: 2.361409, 2.432936, 2.505506 seconds; median 2.432936
    seconds; detection counts `[0, 0, 0]`.
  - EfficientNet inference: 0.946941, 1.016758, 1.165284 seconds; median
    1.016758 seconds; score `0.82664424` on all three runs.
- Model-load times: YOLO 9.569950 seconds; EfficientNet 0.936259 seconds.
- Process RSS after both model probes: 1,373,687,808 bytes.
- The maintained probe is
  [`baseline_probe.py`](./baseline_probe.py). This synthetic fixture is a
  deterministic compatibility sentinel, not a claim about real-world
  detection accuracy.

Docker CPU Python 3.11 used the same trusted assets and deterministic fixture:

- TowerScout lazy import: 7.029895, 8.841539, 8.144371 seconds; median
  8.144371 seconds.
- YOLO inference: 9.053584, 4.437404, 7.094404 seconds; median 7.094404
  seconds; detection counts `[0, 0, 0]`.
- EfficientNet inference: 2.891212, 1.602714, 1.074042 seconds; median
  1.602714 seconds; score `0.8266443` on all three runs.
- Model-load times: YOLO 17.449871 seconds; EfficientNet 4.103931 seconds.
- Process RSS after both model probes: 1,385,152,512 bytes.
- These Docker timings form the Docker CPU after-change comparison baseline.
  They are not compared directly with the host-Python timings because the
  runtime profile differs.

## External Runtime Gates

- Docker GPU, Podman CPU/GPU, physical-GPU model parity, and live-provider
  Google/Azure evidence are later slice/final-qualification gates and have not
  been requested yet.
- The active agent must name the exact required profiles and wait for user
  confirmation before each runtime-dependent stage.

## Baseline Disposition

The Python 3.12 host and Python 3.11 Docker CPU functional, dependency,
model-output, and profile-specific performance baselines are complete. Existing
Docker images, containers, ports, volumes, and build cache did not influence
the clean Python 3.11 evidence. The pre-change gate is closed and Slice A may
begin. No Slice A application, dependency, Compose, runtime, release,
alert-state, or external-repository change had been made when this baseline was
captured.
