# File and Folder Organization Review

**Review Date**: April 6, 2026  
**Purpose**: Identify misplaced files, consolidation opportunities, and organizational improvements  
**Scope**: Full repository structure review  
**Status**: Updated after runtime path normalization closeout validation

---

## Executive Finding

The runtime-path normalization work is complete. TowerScout now uses app-anchored runtime paths under `webapp/` for config, cache, filesystem sessions, logs, uploads, temp/session artifacts, and model-relative assets.

The remaining organization problem is narrower:

- a few repo-root runtime-looking directories still exist as stale local leftovers from pre-normalization runs
- repo-root `logs/` still has limited transitional value because `ts_config.get_recent_performance_stats()` can fall back to `cwd/logs/performance.log`
- random pytest/temp artifacts still need local cleanup and ignore coverage

Cleanup is no longer blocked by active-path ambiguity, but it should still stay surgical and evidence-based.

---

## Review Methodology

1. Compare the review documents against the actual repo layout.
2. Check how the running app resolves config, cache, log, upload, session, and temp paths.
3. Distinguish current runtime behavior from recommended future organization.
4. Separate immediate Docker prerequisites from deferred repo-cleanup ideas.

---

## Current Structure Assessment

### Root-Level Organization: FAIR

**Strengths**:
- Clear top-level separation between application code, tests, research assets, and agent-work docs
- `.agent_work/` is already isolated from the runtime app
- `webapp/` remains the obvious application center of gravity

**Most important current risks**:
- Runtime path semantics are inconsistent, so folder duplication is partly a code-path issue rather than pure repo drift.
- `TowerScoutSite/` is still served by the Flask app through `/site/`, so moving it is a product/runtime decision, not just cleanup.
- `Model/`, `SyntheticData/`, and `hosting/` are non-blocking organization concerns and should be deferred until the runtime root is normalized.

---

## Identified Issues and Recommendations

### Issue 1: Canonical Runtime Root Established

**Current state**:

```text
canonical runtime today:
/webapp/config/
/webapp/cache/
/webapp/flask_session/
/webapp/logs/
/webapp/temp/
/webapp/uploads/
/webapp/model_params/

legacy repo-root leftovers:
/cache/maps/        # empty legacy dir
/flask_session/     # stale pre-normalization session files
/logs/              # transitional compatibility surface
/uploads/           # empty legacy dir
```

Additional nuance:
- The April 7 post-normalization smokes advanced `webapp/flask_session/` while leaving repo-root `flask_session/` untouched.
- Repo-root `logs/` should not be treated as a Docker/runtime target, but it cannot be fully retired until the performance-summary fallback is removed.

**Assessment**:
The repo-level duplication is now mostly legacy residue rather than active runtime behavior. The path-resolution ambiguity has been resolved in favor of `webapp/`-anchored helpers.

**Recommendation**: HIGH PRIORITY

1. Treat `webapp/` as the authoritative runtime root for Docker planning and current docs.
2. Remove or ignore only the confirmed stale local leftovers (`cache/maps/`, `uploads/`, repo-root `flask_session/`, random pytest/tmp dirs).
3. Treat repo-root `logs/` as transitional compatibility only until the performance-summary fallback is retired.
4. Keep deferred product/repo surfaces separate from runtime cleanup.

**Why this matters**:
- It gives Docker one authoritative persistence story.
- It makes logs, uploads, cache, and sessions predictable across dev, tests, and CI.
- It narrows cleanup to proven leftovers instead of speculative repo pruning.

---

### Issue 2: Mixed-Purpose Content at Root

**Current state**:

```text
/TowerScoutSite/      # Static site assets still served by Flask /site
/Model/               # Research and training notebooks/scripts
/SyntheticData/       # Synthetic data generation assets
/hosting/             # Legacy deployment/operator scripts
```

**Assessment**:
These directories are mixed-purpose content, but they are not the first organization problem to solve.

- `TowerScoutSite/` is still active because the app serves it via `/site/` and `/site/<path>`.
- `Model/` and `SyntheticData/` are research/training surfaces with clear project value even if they are not needed in the runtime image.
- `hosting/` remains a useful legacy deployment/operator reference until Docker formally replaces it.

**Recommendation**: DEFER

Do not move or split these directories before runtime path normalization. Revisit them after:

1. the runtime root is normalized,
2. Docker scope is clearer, and
3. there is an explicit product decision on whether the `/site/` route should remain.

---

### Issue 3: Agent Documentation Structure

**Current state**:
- `.agent_work/README.md` already exists.
- `AGENTS.md/README.md` already exists.
- `.agent_work/tasks/active/` is currently empty.

**Assessment**:
This is mostly a workflow-clarity issue, not a broken structure.

**Recommendation**: MAINTAIN AND CLARIFY

1. Keep `.agent_work/` as active planning and delivery context.
2. Keep `AGENTS.md/` as stable reference/onboarding guidance.
3. Clarify `tasks/active/` usage only if the team wants to enforce symlinked active-task workflow.

**Do not treat these as missing-work items**:
- create a new `.agent_work` overview file
- create a new `AGENTS.md` overview file

Those actions are already obsolete.

---

### Issue 4: Test Directory Structure

**Assessment**: ALREADY ADDRESSED

- `webapp/tests/` was archived during Sprint 04 cleanup.
- The top-level `tests/` structure remains the active test surface.
- No folder move is needed here for Sprint 05.

---

### Issue 5: Build and Generated Files

**Current state**:

```text
/webapp/js/towerscout.js                # Generated bundle
/webapp/js/towerscout.original.js       # Deliberate rollback/reference asset
/webapp/js/src/towerscout.js.stage3.bak # Local-only backup artifact
/pytest-cache-files-*/                  # Random pytest cache dirs
/.agent_work/pytest-cache-files-*/      # Random pytest cache dirs
```

**Assessment**:
- `towerscout.js` and `towerscout.original.js` are intentional parts of the current frontend workflow.
- `towerscout.js.stage3.bak` remains a local-only cleanup candidate, but it is low-priority compared with path normalization.
- Random pytest/temp directories are legitimate cleanup targets once ignore rules are tightened.

**Recommendation**: MEDIUM PRIORITY

1. Tighten `.gitignore` for random pytest/temp artifacts.
2. Remove confirmed local-only temp/cache artifacts.
3. Treat `towerscout.original.js` as preserve-for-now unless the rollback strategy changes.

---

### Issue 6: Model Weights and Large Files

**Current state**:

```text
/webapp/model_params/
```

**Assessment**:
`webapp/model_params/` is a required runtime asset area, but current model loading still relies on relative `model_params/...` paths. That means the current layout is coupled to present path behavior.

**Recommendation**: HIGH PRIORITY FOR TASK-025

1. Keep `webapp/model_params/` as a required runtime surface.
2. Document the acquisition strategy for Docker.
3. Treat path normalization and model-path resolution as related concerns.

---

## Containerization Impact Analysis

### Files/Folders Needed in the Runtime Image Today

**Required**:
- `/webapp/`
- `/webapp/requirements.txt`
- `/webapp/model_params/` or an explicit model-acquisition strategy
- `/.env.example` for reference

**Conditionally required**:
- `/TowerScoutSite/` only if the `/site/` Flask route remains part of the product/runtime surface

### Likely Excludable From the Runtime Image

These are good `.dockerignore` candidates, but they are not necessarily delete-from-repo candidates:

- `/Model/`
- `/SyntheticData/`
- `/tests/` (if not needed in the runtime image)
- `/AGENTS.md/`
- `/.agent_work/`
- `/.git/`
- `/hosting/` if kept only as operator reference outside the runtime image

### Runtime Persistence Guidance

**Current truth**:
Canonical runtime persistence now lives under `webapp/`, including:

- `/webapp/config/`
- `/webapp/flask_session/`
- `/webapp/logs/`
- `/webapp/temp/`
- `/webapp/uploads/`
- `/webapp/cache/`

**Transitional compatibility note**:
`ts_config.get_recent_performance_stats()` still falls back to `cwd/logs/performance.log` if `webapp/logs/performance.log` is absent. Treat that as a local compatibility surface, not part of the Docker mount contract.

---

## Proposed Action Plan

### Phase 1: Runtime Path Normalization (Sprint 05 Prerequisite)

**Tasks**:
1. Complete the app-anchored runtime-path migration under `webapp/`.
2. Update documentation and task notes to reflect the now-canonical runtime contract.
3. Classify repo-root leftovers based on post-normalization smoke evidence.

**Priority**: HIGH  
**Why first**: Docker mounts and cleanup decisions were unreliable until this was done.

---

### Phase 2: Safe Cleanup and Ignore Rules

**Tasks**:
1. Tighten `.gitignore` for random pytest/temp artifacts.
2. Remove confirmed stale temp/cache artifacts and empty legacy dirs.
3. Preserve deliberate build/rollback assets and the temporary root-log fallback unless their workflow changes.

**Priority**: MEDIUM  
**Benefits**: Cleaner working tree without risking active runtime paths.

---

### Phase 3: Final Docker Volume Strategy

**Tasks**:
1. Derive the final persistent mount set from the canonical `webapp/` runtime root.
2. Document conditional runtime/image treatment for `TowerScoutSite/`.
3. Update Docker notes and image exclusions to match the normalized path strategy.

**Priority**: HIGH  
**Benefits**: Consistent container behavior and clearer local deployment.

---

### Phase 4: Model Weights Strategy

**Tasks**:
1. Verify ignore/acquisition strategy for model weights.
2. Decide whether Docker should download, mount, or otherwise stage model files.
3. Keep the chosen model strategy aligned with normalized runtime paths.

**Priority**: HIGH  
**Integration**: Part of TASK-025.

---

### Phase 5: Deferred Content Separation

**Tasks**:
1. Decide whether `/site/` remains part of the application runtime.
2. Revisit whether `TowerScoutSite/` should stay in-repo or move elsewhere.
3. Revisit `Model/`, `SyntheticData/`, and `hosting/` after Docker scope stabilizes.

**Priority**: LOW  
**Timing**: Post-Sprint-05 or after the runtime-root decision is complete.

---

## Recommendations Summary

### Immediate Before Docker
1. Use the normalized `webapp/` runtime root as the current source of truth.
2. Keep `webapp/model_params/` as a required runtime surface and define the Docker model strategy.
3. Treat repo-root `logs/` as transitional only; do not use it as a Docker mount.

### Short-Term Follow-Through
4. Tighten ignore rules for random pytest/temp and browser-run artifacts.
5. Clean only confirmed stale local artifacts.
6. Update path-sensitive docs after the canonical runtime root is chosen.

### Deferred Decisions
7. Revisit `TowerScoutSite/` only after an explicit `/site/` product decision.
8. Revisit research/deployment directory moves only after Docker scope is stable.

---

## Integration With Existing Tracking

This review complements:
- `REMOVAL-CANDIDATES-CONTAINERIZATION.md` for removal/defer decisions
- `TASK-051` for runtime dependency verification
- `TASK-025` for Docker containerization

---

## Success Metrics

**Phase 1 success**: Every runtime path is classified as current behavior or target behavior.  
**Phase 2 success**: Cleanup only removes confirmed stale artifacts, not active runtime paths.  
**Phase 3 success**: Docker persistence guidance is derived from normalized paths, not folder duplication.  
**Phase 4 success**: Model-weight handling is explicit and compatible with the normalized runtime root.  
**Phase 5 success**: Deferred content moves happen only after route/runtime decisions are explicit.

---

## Review Completion Checklist

- [x] Root-level structure assessed
- [x] Runtime path behavior checked against code
- [x] Documentation organization reviewed
- [x] Test directory structure verified
- [x] Containerization impact re-evaluated
- [x] Action plan reordered around runtime path normalization
- [x] Path normalization implemented
- [x] Cleanup performed after normalization
- [ ] Docker mount strategy finalized from canonical paths

---

**Review Status**: Updated and ready for Sprint 05 execution reference  
**Next Action**: Use the canonical `webapp/` runtime contract in `TASK-025` and retire the root-log fallback when safe
