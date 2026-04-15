# Removal Candidates for Containerization and Deployment

**Created**: April 6, 2026  
**Purpose**: Track files and folders that are candidates for removal, retention, or deferral as TowerScout moves toward Docker containerization  
**Status**: Updated after runtime path normalization closeout validation

---

## Primary Finding

Runtime-path normalization is now in place.

- Canonical runtime writes and reads now resolve under `webapp/` for config, cache, filesystem sessions, logs, uploads, temp/session artifacts, and model-relative assets.
- Remaining repo-root runtime-looking directories are now local cleanup or compatibility questions, not active-path ambiguity.
- Docker planning should use the canonical `webapp/` runtime surfaces, not legacy repo-root leftovers.

---

## Review Status Legend

- `RETAIN`: Keep in repo and keep available for current workflows.
- `TRANSITIONAL`: Not an active write target, but keep or re-evaluate until a documented compatibility fallback is removed.
- `DEFER`: Not needed for immediate container work, but removal or relocation should wait for a broader product/repo decision.
- `REMOVE`: Safe local cleanup candidate after confirmation.

---

## Root-Level Files

### Development and Testing Files

| File | Status | Reason | Action | Priority |
|------|--------|--------|--------|----------|
| `validate_stage_0.sh` | RETAIN | Still wired into frontend validation workflow via `package.json` | Keep | LOW |
| `pytest.ini` | RETAIN | Required for pytest configuration | Keep | - |
| `requirements-dev.txt` | RETAIN | Dev/test dependency manifest | Keep | - |
| `package.json` | RETAIN | Frontend build and test scripts | Keep | - |

### Documentation Files

| File | Status | Reason | Action | Priority |
|------|--------|--------|--------|----------|
| `README.md` | RETAIN | Primary project documentation | Keep | - |
| `LICENSE.TXT` | RETAIN | Legal requirement | Keep | - |

---

## Root-Level Directories

### Runtime-Looking Directories

| Directory | Status | Reason | Action | Priority |
|-----------|--------|--------|--------|----------|
| `cache/maps/` | REMOVE | Canonical map-cache writes now land under `webapp/cache/maps/`; repo-root cache dir is an empty legacy leftover | Remove local dir if present; do not mount in Docker | HIGH |
| `flask_session/` | REMOVE | Repo-root session files were not touched by the April 7 post-normalization smokes; active session writes now land under `webapp/flask_session/` | Safe local cleanup candidate; do not mount in Docker | HIGH |
| `logs/` | TRANSITIONAL | Current writes land under `webapp/logs/`, but `ts_config.get_recent_performance_stats()` still falls back to `cwd/logs/performance.log` if the canonical file is absent | Do not use for Docker; retire after fallback removal | MEDIUM |
| `uploads/` | REMOVE | Repo-root uploads dir is empty and no longer the canonical upload target | Remove local dir if present; do not mount in Docker | MEDIUM |
| `pytest-cache-files-*/` | REMOVE | Random pytest temp artifacts with no runtime value | Clean locally and keep ignored | LOW |

### Test Artifacts

| Directory | Status | Reason | Action | Priority |
|-----------|--------|--------|--------|----------|
| `tests/logs/` | RETAIN | Test-support output surface | Keep unless test workflow changes | LOW |
| `tests/mocks/` | RETAIN | Active test support | Keep | - |
| `tests/fixtures/` | RETAIN | Active test support | Keep | - |

### Research and Legacy Deployment Surfaces

| Directory | Status | Reason | Action | Priority |
|-----------|--------|--------|--------|----------|
| `Model/` | DEFER | Research/training notebooks and helper scripts | Keep in repo for now; revisit after Docker scope stabilizes | MEDIUM |
| `SyntheticData/` | DEFER | Synthetic data generation assets | Keep in repo for now; revisit after Docker scope stabilizes | MEDIUM |
| `TowerScoutSite/` | DEFER | Still served by Flask through `/site/` | Revisit only after explicit `/site/` product decision | MEDIUM |
| `hosting/` | RETAIN | Useful legacy deployment/operator reference until Docker replaces it | Keep in repo; likely exclude from runtime image | MEDIUM |

---

## Webapp Subdirectories

### Runtime and Persistence Surfaces

| Directory | Status | Reason | Action | Priority |
|-----------|--------|--------|--------|----------|
| `webapp/config/` | RETAIN | Current persisted `.env` location used by Setup Wizard/settings | Keep; canonical config surface | CRITICAL |
| `webapp/cache/` | RETAIN | Canonical cache location for geocoding and map-cache writes | Keep; canonical cache target | HIGH |
| `webapp/flask_session/` | RETAIN | Canonical filesystem-session location after normalization | Keep; canonical session target | HIGH |
| `webapp/logs/` | RETAIN | Canonical runtime log target after normalization | Keep; canonical log target | HIGH |
| `webapp/temp/` | RETAIN | Active temp/session working area already lives here | Keep | HIGH |
| `webapp/uploads/` | RETAIN | Canonical upload/debug-image target after normalization | Keep; canonical upload target | HIGH |

### Temporary and Generated Directories

| Directory | Status | Reason | Action | Priority |
|-----------|--------|--------|--------|----------|
| `webapp/tmp*/` | REMOVE | Leftover random temp directories with no runtime value | Clean locally and keep ignored | MEDIUM |

### Model Parameters

| Directory | Status | Reason | Action | Priority |
|-----------|--------|--------|--------|----------|
| `webapp/model_params/` | RETAIN | Required runtime asset surface for model weights | Keep; align Docker strategy and path normalization with current model loading | CRITICAL |

**Notes**:
- `webapp/model_params/` remains the correct runtime area to preserve.
- Model-path resolution now flows through shared app-anchored path helpers under `webapp/`.

---

## AGENTS.md Documentation

| Directory | Status | Reason | Action | Priority |
|-----------|--------|--------|--------|----------|
| `AGENTS.md/` | RETAIN | Development/agent reference docs, not runtime content | Keep in repo; likely exclude from runtime image | LOW |

---

## Session and Runtime Artifact Notes

- `webapp/flask_session/`, `webapp/logs/`, `webapp/uploads/`, `webapp/cache/`, and `webapp/temp/` are the canonical runtime locations after `PRE-SPRINT-05-01`.
- The April 7 post-normalization smokes updated `webapp/flask_session/` while repo-root `flask_session/` retained its April 6 timestamp, which confirms the root session files are stale leftovers.
- Repo-root `cache/maps/` and `uploads/` are empty local leftovers, not active write targets.
- Repo-root `logs/` is now a transitional/local-only compatibility surface because the performance-summary helper still falls back to `cwd/logs/performance.log` when `webapp/logs/performance.log` is absent.
- `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/` summary JSON files can contain live provider request URLs and should remain local-only and ignored.

---

## Docker Containerization Considerations

### Canonical Persistent Directories

With runtime-path normalization complete, Docker planning should use these canonical persistent surfaces:

1. `webapp/config/`
2. `webapp/flask_session/`
3. `webapp/logs/`
4. `webapp/temp/`
5. `webapp/uploads/`
6. `webapp/cache/`

Treat this as the current canonical runtime contract for Docker planning. Repo-root `logs/` remains a transitional compatibility surface only and should not be used as a Docker mount.

### Environment Variables Required

From setup wizard and configuration system:
- `GOOGLE_API_KEY`
- `AZURE_MAPS_SUBSCRIPTION_KEY`
- `DEFAULT_MAP_PROVIDER`
- `FLASK_SECRET_KEY` (must be stable across restarts)

### Likely `.dockerignore` Candidates

These are image-scope recommendations, not delete-from-repo recommendations:

- `Model/**`
- `SyntheticData/**`
- `tests/**` (if not needed in the runtime image)
- `AGENTS.md/**`
- `.agent_work/**`
- `.git/**`
- `pytest-cache-files-*/**`
- `webapp/tmp*/**`
- `*.log`
- `*.pyc`
- `__pycache__/`
- `hosting/**` if kept only as repo/operator reference
- `TowerScoutSite/**` only if the `/site/` route is intentionally removed or externalized

---

## Next Steps

### Phase 1: Runtime Path Normalization
1. Complete the app-anchored runtime-path migration under `webapp/`.
2. Reclassify repo-root runtime leftovers based on post-normalization smoke evidence.
3. Keep transitional compatibility notes explicit where fallback readers still exist.

### Phase 2: Safe Cleanup Planning
1. Remove only confirmed stale temp/cache artifacts and empty legacy dirs.
2. Tighten `.gitignore` for random pytest/temp artifacts and local browser-run captures.
3. Preserve only the transitional root surfaces that still have documented compatibility value.

### Phase 3: Docker Planning
1. Derive the final volume-mount set from normalized paths.
2. Document conditional treatment for `TowerScoutSite/`.
3. Document model-weight strategy in the Docker plan.

### Phase 4: Deferred Repo-Organization Decisions
1. Revisit `TowerScoutSite/` after an explicit `/site/` decision.
2. Revisit `Model/` and `SyntheticData/` after Docker scope and research needs are clearer.
3. Revisit `hosting/` only after Docker formally replaces legacy deployment guidance.

---

## Review Checklist

Before making any removal or relocation changes:
- [x] Verify the path is not still used by current launch modes
- [x] Separate current behavior from recommended future state
- [x] Normalize runtime paths before removing duplicated runtime directories
- [x] Confirm any Docker exclusion does not imply repo deletion
- [ ] Get approval for product/runtime-surface changes such as `/site/`

---

## Historical Context

### Sprint 04 Cleanup Work
- TASK-049 already removed low-risk stale tracked files
- TASK-050 completed full-repo stale-surface audit
- pytest collection gate was repaired
- stale test surfaces were archived, not deleted

### TASK-051 Goals
- Verify runtime dependencies
- Separate true runtime requirements from drift
- Confirm Torch CPU/CUDA behavior
- Remove or reclassify low-risk dependency drift

---

## Change Log

| Date | Action | Files | Rationale | Approved By |
|------|--------|-------|-----------|-------------|
| 2026-04-06 | Document created | N/A | Sprint planning prep | - |
| 2026-04-06 | Document updated | N/A | Align removal guidance with actual runtime path behavior | User request |
| 2026-04-07 | Document updated | N/A | Reclassify runtime leftovers after normalization closeout validation | User request |

---

## Notes

- Focus on containerization readiness, not aggressive cleanup.
- Preserve research and legacy reference surfaces unless there is a deliberate decision to move them.
- Treat repo-root `logs/` as transitional until the performance-summary fallback is retired.
- Treat confirmed-stale repo-root runtime dirs as local cleanup candidates, not Docker surfaces.
