# Senior Engineering Review Response Memo

**Created**: April 22, 2026  
**Audience**: TowerScout contributors and reviewers  
**Purpose**: Capture TowerScout's repo-backed response to the April 2026 senior engineering review, record which recommendations should be adopted as-is, refine points that need correction, and translate the review into immediate Sprint 05 planning updates

**Superseded**: April 28, 2026 by [Senior Engineering Review Response Memo V2](./SENIOR-ENGINEERING-REVIEW-RESPONSE-MEMO-V2-2026-04-28.md), which incorporates the second senior-engineer review and corrects the frontend lockfile/reproducibility assessment.

---

## Executive Summary

The senior review is substantively useful and should be adopted with minor refinements rather than treated as a competing plan.

The review is correct on the most important points:

- Docker should be treated as a deployment phase, not the final end-user experience.
- The largest medium-term architecture risks are still synchronous detection in the Flask request path, filesystem-coupled workflow state, and the concentration of responsibility in `webapp/towerscout.py`.
- The right sequence is to stabilize the runtime and Docker contract first, then introduce a job boundary around long-running work, then decompose the main server module.

The practical response is:

- keep Sprint 05 focused on a reliable Docker baseline under `TASK-025`
- keep `TASK-054` focused on launcher-first local UX over that Docker baseline
- explicitly answer the remaining planning questions so Docker work does not proceed on vague assumptions
- defer broad rewrite work, shared-deployment redesign, and native-installer work until the runtime contract is stable

---

## What We Agree With

### 1. The overall sequencing is sound

The review correctly favors staged stabilization over rewrite. TowerScout has already done meaningful runtime and UX hardening, so the next win is not a broad redesign. The next win is a well-defined local deployment contract.

### 2. Docker is the right first deployment layer

The repo's current Sprint 05 structure already points this way. `TASK-025` is the Docker baseline and `TASK-054` is the launcher-first UX bridge. That should remain the plan.

### 3. The synchronous execution path is the main architectural pressure point

The repo now has setup/configuration, progress, cancellation, and stronger local model ownership, but long-running detection still runs inside the request lifecycle. That is acceptable for the Docker baseline as an explicitly contained limitation, but it should remain the highest-value post-Docker refactor target.

### 4. Persistence and supportability matter as much as packaging

The review is right that stable secret handling, volume strategy, startup diagnostics, asset versioning, and rollback behavior are not "DevOps polish." They are part of the product contract for local users.

---

## Key Refinements

### 1. The active YOLO runtime is already local-first

The review is directionally right to keep shrinking legacy YOLO surface area, but it should not be read as if TowerScout still depends on Torch Hub at runtime in the active path. `webapp/ts_yolov5.py` now loads through `webapp/ts_yolov5_local.py`, and the remaining work is cleanup and hardening around the local loader contract.

### 2. Dependency reproducibility is partly present already

The Python runtime requirements are pinned, and the frontend has a lockfile plus fixed browser-test tooling. The larger gap is not "no dependency pinning exists." The larger gap is release reproducibility across container images, large runtime assets, and rollback/version coordination.

### 3. The first-run asset inventory is broader than two model files

The review correctly flags asset ambiguity, and the repo confirms that the actual inventory is broader than the project `.pt` files alone. It must account for:

- YOLO weights
- EfficientNet project weights
- EfficientNet base-model bootstrap behavior
- ZIP-code boundary data and its year/version

If that inventory is not locked before Docker implementation, the team will ship a misleading runtime contract.

### 4. The near-term product contract still reads as single-user local

Nothing in the current repo or planning artifacts suggests that shared multi-user deployment should drive Sprint 05 decisions. The right next state boundary after Docker is a local structured store, not an immediate service split.

### 5. `TowerScoutSite/` is still a live runtime surface

The review is correct to call this out. `/site/` is still served by Flask, so the runtime image must either include it intentionally or exclude it intentionally. It should not remain accidental.

---

## Recommended Decision Positions

### 1. Deployment model

Treat the supported product for the first release as single-user local deployment on individual machines.

### 2. Primary target environments

Prioritize managed Windows analyst and lab laptops/desktops with normal internet access. Do not promise VDI, air-gapped, or Mac support in the first release.

### 3. Platform contract

Support `AMD64` first. CPU is the required baseline. NVIDIA/CUDA is a supported accelerated path on compatible `AMD64` hosts, not a universal promise. `ARM64` and Mac remain deliberate follow-on targets.

### 4. Large runtime assets

Use first-run download plus persistence across restarts and updates. Do not require every large asset to ship inside the container image. The asset list and versioning policy must be explicit.

### 5. Release model

Use a GitHub release package as the user-facing distribution surface and keep container images in a registry behind the scenes. That preserves a later path to a more managed installer without forcing installer work into Sprint 05.

### 6. Restart and upgrade durability

The following should survive restart and upgrade:

- `webapp/config/.env`
- stable `FLASK_SECRET_KEY`
- downloaded model/data assets
- user exports/imported project data
- support-relevant logs

Browser-session continuity can remain best-effort for the Docker baseline.

### 7. Network assumptions

Assume real users may be behind proxies, TLS interception, and outbound filtering. Do not claim general offline or air-gapped support for the first release because imagery and geocoding remain network-dependent.

### 8. Data sensitivity

Treat stored imagery, locations, API keys, and investigation exports as sensitive local data. That implies explicit storage locations, bounded logging, and documented cleanup/reset behavior.

### 9. Release engineering support

Assume limited/manual release engineering support. The release/update/rollback path should therefore stay simple, documented, and reversible.

### 10. Runtime surface decision

Make an explicit `/site/` decision before finalizing the Docker image scope.

---

## Immediate Sprint 05 Implications

### `TASK-025`

`TASK-025` should explicitly lock:

- supported platform and support boundary
- persistence categories
- secret-key continuity
- full first-run asset inventory
- release-package and registry assumptions
- container readiness and support diagnostics

It should not absorb:

- background-job redesign
- session/state redesign
- native-installer work
- launcher/browser UX

### `TASK-054`

`TASK-054` should explicitly target:

- release-package-friendly launcher scripts
- start/stop/logs/status behavior
- browser-open only after readiness
- user-facing first-run download messaging
- common troubleshooting for Docker availability, port conflicts, and restricted networks

It should not absorb:

- Docker baseline implementation
- cross-platform packaging promises
- warm-start/runtime redesign beyond a bounded readiness contract

---

## Conclusion

The senior review improves the plan. It does not invalidate the existing direction.

The right response is to keep the current Sprint 05 structure, tighten the Docker and launcher task definitions, answer the remaining planning questions explicitly, and preserve the larger architecture refactors for the next phase rather than reopening the whole system before the runtime contract is stable.
