## TASK-057 broader app and host-side smoke

Date: 2026-04-13

### Objective

Run broader smoke checks after the bounded local-YOLO first-run proof to confirm:

- the current Flask app route surface still imports and responds in-process
- a live local server starts and serves key setup/provider endpoints
- the real app process can still load the active YOLO engine from the new local runtime path

### In-process app smoke

Command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\backend\test_endpoint_contract.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py -q -p no:cacheprovider
```

Results:

- `tests/backend/test_endpoint_contract.py`: PASS (`2 passed`)
- `tests/unit/test_flask_routes.py`: FAIL (`12 failed, 7 passed`)

Interpretation:

- The current endpoint contract test still passes, so the app imports and the actively tracked frontend/backend route contract is intact.
- The failing `tests/unit/test_flask_routes.py` cases are consistent with the known stale-test boundary already tracked in `.agent_work/current-tasks.md`:
  - removed or changed routes such as `/draw_polygon`, `/get_status`, `/incompatible`, `/unauthorized`
  - outdated assumptions about `GET /getobjects`
  - outdated mocks for symbols that no longer exist on `towerscout` or `ts_events`

These failures do not point to the Task-057 local YOLO runtime change.

### Host-side smoke 1: live server route/config surface

Launch mode:

```powershell
$env:TOWERSCOUT_LAZY_MODEL_INIT='1'
.\.venv\Scripts\python.exe webapp\towerscout.py dev
```

Probe targets:

- `/`
- `/getproviders`
- `/getengines`
- `/api/config/status`
- `/api/config/performance`

Result: PASS

Observed behavior:

- root page returned `200` and contained `TowerScout`
- `/getproviders` returned `200` with `azure` then `google`
- `/getengines` returned `200` with engine `newest`
- `/api/config/status` returned `200` and reported both Google and Azure configured, `needs_setup=false`
- `/api/config/performance` returned `200`

Artifacts:

- `.agent_work/context/analysis/TASK-057-host-side-smoke-server-stdout.txt`
- `.agent_work/context/analysis/TASK-057-host-side-smoke-server-stderr.txt`
- `.agent_work/context/analysis/TASK-057-host-side-smoke-probes.json`

### Host-side smoke 2: non-dev startup with real YOLO engine load

First attempt from repo root failed before server readiness because `Zipcode_Provider()` resolves `data/...` relative to the working directory. That failure was not in YOLO startup.

Successful launch mode:

```powershell
$env:TOWERSCOUT_LAZY_MODEL_INIT='1'
cd webapp
..\.venv\Scripts\python.exe towerscout.py
```

Probe targets:

- `/getengines`
- `/`

Result: PASS

Observed startup log highlights:

- `Loading zipcode data, this may take up to 10 seconds...`
- `Loading model: newest`
- `Initializing YOLOv5 detector with model: ...\\webapp\\model_params\\yolov5\\newest.pt`
- `YOLOv5 model loaded successfully`
- `CUDA not available, using CPU`

Observed route behavior:

- `/getengines` returned `200` with engine `newest`
- `/` returned `200` and contained `TowerScout`

Artifacts:

- `.agent_work/context/analysis/TASK-057-host-side-eager-yolo-smoke-server-stdout.txt`
- `.agent_work/context/analysis/TASK-057-host-side-eager-yolo-smoke-server-stderr.txt`
- `.agent_work/context/analysis/TASK-057-host-side-eager-yolo-smoke-probes.json`

### Outcome

Broader smoke evidence supports Task-057 completion:

- the current app contract imports and passes the tracked endpoint smoke
- the live local server serves the expected setup/provider/config endpoints
- the real app process can start and load the `newest.pt` YOLO engine through the new local runtime path

Remaining test noise is concentrated in the pre-existing stale Flask route test file and should be handled as baseline smoke/test-maintenance work rather than as a Task-057 rollback signal.
