# Repository Organization - Approved First Pass

**Date**: October 20, 2026

**Task**: TASK-089

**Scope**: User-approved O1/O2/O3, applied in the isolated local adoption-preparation branch.

## Applied changes

| Item | Change | Effect |
| --- | --- | --- |
| O1: Navigation | Refreshed `.agent_work/README.md`, `context/status/README.md`, and `context/status/Handoff-Planning/README.md` | Current board, acceptance, owner guidance and handoff records are easier to find; dated pilot records are identified as history. |
| O2: Current work | Updated `current-tasks.md`, `task-backlog.md`, and the current section of Task-089 | Chris's ownership/access agreement is recorded separately from pending adoption, official qualification, publication and receipt. Stale RC9 directions in current board sections are corrected. |
| O3: Historical organization | Moved four completed-sprint retrospectives into dated archive folders | Retrospective contents remain unchanged; references in three documents now point to the archived locations. |

All paths in this table are relative to `.agent_work/` unless stated otherwise.

## Four unchanged-content moves

Each source was under `context/analysis/`; its filename is unchanged.

| Retrospective | New folder |
| --- | --- |
| `SPRINT-05-RETROSPECTIVE-ANALYSIS-2026-05-08.md` | `context/archive/2026-05/analysis/` |
| `SPRINT-06-RETROSPECTIVE-ANALYSIS-2026-07-02.md` | `context/archive/2026-07/analysis/` |
| `SPRINT-07-RETROSPECTIVE-ANALYSIS-2026-07-23.md` | `context/archive/2026-07/analysis/` |
| `SPRINT-08-RETROSPECTIVE-ANALYSIS-2026-08-11.md` | `context/archive/2026-08/analysis/` |

Reference repairs are limited to `completed-tasks.md`, the July 23 archived
completed-task snapshot, and the July archived comprehensive handoff analysis.
Two affected retrospective links in the archived snapshot were already broken
before this pass; they now resolve correctly.

## Status boundaries

- Ownership, Administrative access, destination, delivery direction and proposed
  release name are agreed. Delivery targets October 27, with support October 28-30.
- Exact fork RC5 has bounded acceptance under ADR-026. This does not qualify
  changed official images or packages.
- Official adoption, security/integrity/affected runtime checks, wiki/video,
  private delivery and Chris's receipt remain pending.
- Security residual acceptance still expires October 31, 2026 at 23:59:59 UTC.
  The ADR-022 bridge review remains due January 31, 2027 or an earlier trigger.
- Task-087/096 launcher work remains deferred. No task was closed to simplify
  the folder structure. Task-089's earlier body is preserved below an explicit
  historical heading; other dated task histories remain in place.

## Verification and limitations

- Compared all 883 baseline tracked-file hashes: four byte-identical moves and
  nine approved text edits; all other baseline tracked content is unchanged.
- Verified all eight original-checkout preservation hashes remain unchanged.
- Verified the complete earlier Task-089 body is retained.
- Checked relative Markdown file/directory targets in changed documents against
  the baseline: zero new broken targets; new navigation targets resolve.
- Searched tracked Markdown for the four obsolete retrospective paths: none remain.
- Strict `validate_agent_work.py` and `git diff --check` pass.

The July 23 archived completed-task snapshot retains 29 unrelated pre-existing
broken relative targets. They are historical link debt, not introduced by these
moves; a broader historical-link repair is outside this first pass. This check
does not validate external URLs or Markdown heading anchors. No runtime tests
were needed for these planning/navigation edits.

No remote repository, release, registry, wiki or account was changed by this
organization pass. Root documentation, application/runtime files and further
archive consolidation remain outside this pass.
