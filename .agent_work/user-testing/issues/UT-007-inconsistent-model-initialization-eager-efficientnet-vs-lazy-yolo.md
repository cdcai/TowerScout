# UT-007: Inconsistent Model Initialization - Eager EfficientNet Vs Lazy YOLO In Dev

**Status**: CONFIRMED
**Severity**: LOW
**Reporter**: User tester question / engineering investigation
**Owner**: Unassigned
**Opened**: 2026-04-09
**Last Updated**: 2026-04-09

## Summary

TowerScout currently initializes its two ML models using different startup rules. EfficientNet is eagerly instantiated at module import time unless `TOWERSCOUT_LAZY_MODEL_INIT` is enabled, while YOLO is loaded on demand through `get_engine()` and, in `dev` mode, is not preloaded at app startup at all. This is why the tester sees EfficientNet load on boot but YOLO wait until the first search/detection request.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-09
- Commit: not captured in this document
- Guide used: not applicable
- Provider used: not relevant
- GPU or CPU path: both

## Reproduction

1. Start TowerScout with `python towerscout.py dev`.
2. Watch startup logs.
3. Observe that EfficientNet initializes immediately on boot.
4. Trigger a detection request.
5. Observe that YOLO loads only when `get_engine(engine)` is first called.

## Expected Result

Model initialization policy should be intentional and explicit. If models differ, the reason should be documented and the tradeoff should be clear.

## Actual Result

The current code does this:

- `webapp/towerscout.py:1088-1091`
  - eager-loads EfficientNet at import time unless `TOWERSCOUT_LAZY_MODEL_INIT` is enabled
- `webapp/towerscout.py:291-297`
  - also exposes a lazy getter for EfficientNet
- `webapp/towerscout.py:155-172`
  - lazy-loads YOLO through `get_engine()`
- `webapp/towerscout.py:3177-3184`
  - preloads the default YOLO model only in non-`dev` startup
  - skips that preload in `dev`, so the tester does not see YOLO load until first detection

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log:
  - user tester observation reported on 2026-04-09
- Other evidence:
  - `webapp/towerscout.py:150`
  - `webapp/towerscout.py:155-172`
  - `webapp/towerscout.py:291-297`
  - `webapp/towerscout.py:1088-1091`
  - `webapp/towerscout.py:3177-3184`

## Triage Notes

- This is not necessarily a correctness bug by itself.
- The most likely current rationale is:
  - EfficientNet is treated as a single global secondary classifier used across detections
  - YOLO may vary by selected engine/model and is therefore loaded through the engine registry on demand
  - `dev` startup intentionally avoids preloading YOLO, likely to reduce boot cost during development
- Even if intentional, the current behavior is inconsistent enough to confuse testers and operators.
- This also means boot-time failures are asymmetric:
  - EfficientNet failures can happen immediately on startup
  - YOLO failures may wait until the first live detection request

## Retest Notes

- Retest owner: future implementer or documentation owner
- Retest date: pending
- Retest result: not applicable until behavior or docs change

## Resolution

Open as a design/operational clarity issue. Either document the current asymmetry clearly or align both model loaders behind the same lazy/eager policy.
