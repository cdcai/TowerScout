# UT-017: `seaborn` Is Unpinned In The Runtime Requirements Without Clear Runtime Use

**Status**: READY-FOR-RETEST
**Severity**: MEDIUM
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The original issue was accurate when it was opened: `seaborn` was unpinned in the runtime manifest. On commit `a2160dc`, `webapp/requirements.txt` now pins `seaborn==0.13.2`, so the immediate resolver-drift problem is fixed. The remaining question is whether `seaborn` belongs in the runtime manifest at all, which is a narrower follow-up than the original unpinned dependency issue.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not relevant
- GPU or CPU path: not relevant

## Reproduction

1. Inspect `webapp/requirements.txt`.
2. Confirm that `seaborn` is now version-pinned.
3. Search `webapp/` for active `seaborn` imports and compare that with notebook usage under `Model/`.

## Expected Result

The runtime requirements file should contain only validated runtime dependencies, and those dependencies should be pinned or intentionally range-bounded.

## Actual Result

The current evidence now shows:

- `webapp/requirements.txt` pins `seaborn==0.13.2`
- code search still does not show an active direct `seaborn` import in `webapp/`
- notebook artifacts under `Model/` still reference `seaborn`, which suggests the runtime-placement question remains worth revisiting later

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/requirements.txt`
  - `Model/w210_model_NB.ipynb`
  - `Model/w210_model_NB_v2.ipynb`

## Triage Notes

- This captures senior engineer critique item 11.
- The immediate pinning concern is resolved.
- This issue remains separate from `UT-005`, which is about coordinated NumPy-stack compatibility rather than one package's placement in the runtime manifest.

## Retest Notes

- Retest owner: future dependency owner
- Retest date: pending
- Retest result: pending

## Resolution

Engineering review on April 14, 2026 found that commit `a2160dc` resolves the original unpinned dependency problem. Keep this in `READY-FOR-RETEST` for the next fresh-install validation, and treat any later runtime-manifest pruning as separate follow-on work rather than a reason to reopen the original issue.
