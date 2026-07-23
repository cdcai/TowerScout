# UT-008: `towerscout.py` Remains A High-Risk Monolith For Runtime And Deployment Changes

**Status**: TRIAGED
**Severity**: MEDIUM
**Reporter**: Senior engineer critique / engineering validation
**Owner**: Unassigned
**Opened**: 2026-04-10
**Last Updated**: 2026-04-14

## Summary

The senior engineer's "God object" critique remains directionally correct. On commit `a2160dc` from April 13, 2026, `webapp/towerscout.py` grew again and now sits at 3,309 lines. The same file still owns startup behavior, request routing, ML orchestration, session management, temp-file cleanup, dataset import/export, and provider setup. This is not the highest-priority user-facing bug by itself, but it increases the risk of fixing Sprint 05 runtime issues in conflicting ways because too many concerns converge in one module.

## Environment

- OS: any
- Python: any supported runtime
- Branch: current repo state on 2026-04-14
- Commit: `a2160dc`
- Guide used: senior-engineer-review-2026-04-13.md
- Provider used: not specific
- GPU or CPU path: both

## Reproduction

1. Inspect `webapp/towerscout.py`.
2. Measure the file length and note that it remains a multi-thousand-line module.
3. Observe that the same file owns global runtime setup, Flask session configuration, detection orchestration, progress routes, custom-image detection, and dataset import/export.

## Expected Result

High-risk runtime concerns should be separated enough that Sprint 05 fixes can be made in bounded layers without repeatedly editing one monolithic file.

## Actual Result

`webapp/towerscout.py` currently centralizes several unrelated responsibilities, including:

- global startup and runtime initialization
- session configuration
- frontend/static serving routes
- main detection orchestration
- progress and abort routes
- custom-image detection and dataset/export paths later in the file

The file spans 3,309 lines in the current checkout.

## Artifacts

- Artifact folder: none
- Screenshot: none
- Terminal log: none required
- Other evidence:
  - `webapp/towerscout.py`

## Triage Notes

- This captures senior engineer critique item 1.
- The architectural concern is stronger now than it was in the earlier April 10 triage because the file has continued to grow.
- This issue increases change risk for `UT-003`, `UT-009`, `UT-011`, and `UT-015` because they all require edits in the same module.
- Keep this routed to `TASK-059`; it should influence how near-term fixes are sliced, but it should not preempt more urgent bounded pre-Docker cleanup.

## Retest Notes

- Retest owner: not applicable
- Retest date: not applicable
- Retest result: not applicable

## Resolution

Still open. Prefer targeted extraction after the current pre-Docker cleanup and Docker baseline are stabilized rather than turning this into a broad Sprint 05 refactor.
