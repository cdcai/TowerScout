# UT-012: Frontend Build Still Depends On Manual Ordered Concatenation

**Status**: TRIAGED
**Severity**: LOW
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The frontend build system still relies on a custom Node script that concatenates source files in a hard-coded order and overwrites `webapp/js/towerscout.js`. This is not currently a known user-facing blocker, but the senior engineer is right that it is a fragile build contract compared with a modern module-aware bundler. The April 13 review also noted a smaller related cleanup: `webapp/build.js` still keeps `towerscout.original.js` under the served `webapp/js/` tree, and Flask's generic `/js/<path>` route will serve it if requested.

## Environment

- OS: any
- Python: not relevant
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not relevant
- GPU or CPU path: not relevant

## Reproduction

1. Inspect `webapp/build.js`.
2. Observe that the build contract depends on a strict manually maintained module order.
3. Observe that the script overwrites the generated `webapp/js/towerscout.js` bundle directly.
4. Observe that `BACKUP_FILE` points at `webapp/js/towerscout.original.js`, which sits under the served JS tree.

## Expected Result

Frontend builds should ideally be handled by a modern bundler that resolves dependencies explicitly and provides better safety, tooling, and reproducibility.

## Actual Result

The current build path uses:

- a custom build script at `webapp/build.js`
- a hard-coded `MODULE_ORDER` list
- direct concatenation into `webapp/js/towerscout.js`
- a backup contract that leaves `towerscout.original.js` in the same served directory

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/build.js`
  - `webapp/js/towerscout.js`

## Triage Notes

- This captures senior engineer critique item 6.
- This is a maintainability and tooling issue more than an immediate reliability defect.
- Keep the full bundler migration deferred to `TASK-060`.
- Removing or relocating `towerscout.original.js` from the served JS tree is a smaller cleanup that can happen earlier if that file is touched.

## Retest Notes

- Retest owner: not applicable
- Retest date: not applicable
- Retest result: not applicable

## Resolution

Still open. Revisit the build-system modernization after the backend runtime contract and Docker baseline are stable, but treat `towerscout.original.js` cleanup as a low-risk follow-up rather than part of a full bundler migration.
