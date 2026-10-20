# Local work and evidence reconciliation

**Date:** October 20, 2026
**Scope:** Seven pre-existing modified tracking/evidence files and the untracked October 7 security review, using the verified October 19 preservation manifest.
**Baseline:** Accepted fork main `d21c3b207949b6a49f13acae84a451ef0c74cad6`; preparation branch `chore/task-089-adoption-preparation`.
**Result:** All eight inputs dispositioned. Original files unchanged. No remote writes, runtime tests, new security scan, or task closure.

## What was unique

- W09 contained an unpublished RC9 inventory, exact image/package identities, and progression from RC8.
- W10 contained 495 added lines and 10 removed lines relative to accepted main: four detailed RC9 first-host profiles, Docker/Podman reboot records, and independent-host intake.
- Four task files supplied October 14 progress updates; their current-status wording predates October 19 RC5 acceptance.
- The backlog added TASK-105 and a rule against losing or duplicating independent-host findings. The preparation branch already had the current TASK-105 row; its unique ownership rule is now retained.
- The untracked second opinion is a dated review at `b0725e7`, not current vulnerability evidence.

## File dispositions and original identities

| Input | Disposition | Original SHA-256 |
| --- | --- | --- |
| `task-backlog.md` | Merged unique finding-ownership rule with existing owner priorities | `c9bcb523580aec29733f605368f7e4dd877edf98855c4085c2fbb247a537d8eb` |
| `TASK-091-owner-runnable-release-qualification.md` | Updated current status; preserved local October 14 status and remaining body | `05133ab7eef664c19da3e7b8f72c956fca6e8a28fdcc0e9887f86c291d38822d` |
| `TASK-092-documentation-currentness.md` | Updated current status; preserved local October 14 status and remaining body | `5ee8b71775ce227aee9d03554ad1ba4888b1c2c708168ca542879215f11bd7a9` |
| `TASK-093-persistent-data-recovery.md` | Updated current status; preserved local October 14 status and remaining body | `88ce3497b4cd4628c3dae6d65aea832e1e21131b619df6c4f26b0ae39d3f1271` |
| `W09-EVIDENCE-INDEX.md` | Retained full historical body with current-acceptance banner | `3730bd855c740e6fe102368d7c767a786fdb0c628c9a0378f6e58624ff3e6569` |
| `W10-LOCAL-FIRST-HOST-EVIDENCE-INDEX.md` | Retained full historical body with current-acceptance banner | `ae3ea048c20d3e85642b9ccafdb91631464333e312641a6542f8d60ebd6beb91` |
| `TASK-104-rc5-security-gate-and-residual-disposition.md` | Updated current status; preserved local October 14 status and remaining body | `08b137a3c51f00060497b1a33ea7dadd54e839ea8fde49c3b12d10d00de25e14` |
| `RC5-SECOND-OPINION-SECURITY-REVIEW-2026-10-07.md` | Retained original locally; added custody/interpretation note | `e3e2901440104cc15020e633227a81f64fab746e80cbd45478ffd9f645a794a1` |

## Evidence limits preserved

The RC9 detailed records are historical assertions retained from the original
local summaries, not independently rerun in this session. Later accepted
main summarizes the same RC9 progression; RC5 acceptance is separately
anchored in ADR-026 and its closeout. Raw evidence is not recreated from
hashes, and missing original raw outputs remain missing.

W09/W10 bodies are retained without edits under an explicit historical
heading. Older pending-host language does not reinstate superseded gates.
Four task headers now distinguish accepted fork qualification from remaining
official documentation, security, runtime-delta, recovery, and receipt work.
All tasks remain open.

## Other local material

- New October 19-20 planning records, report outline, inventories, and meeting
  notes remain local handoff preparation. They are not automatically copied
  wholesale into the adoption PR.
- Existing review and historical source worktrees are preserved. They were
  listed, not deleted or declared redundant. Their unique commits require
  separate retention review before cleanup.
- `output/`, local release artifacts, private fixtures/logs, models, and
  volumes remain excluded from this reconciliation. The handoff inventory
  tracks their separate custody decisions.

## Validation and next step

Validated all eight original hashes, full W09/W10 body preservation, and
the four historical task statuses and bodies. Added relative links resolve;
strict agent-work structure and whitespace checks pass. TASK-104 now links
the retained security review's package-path/identity question for explicit
disposition during official security review. This is not a new scan finding.
No application tests were run for these record-only changes.

Next: complete repository organization and owner-backlog review, then finish
official documentation and release destinations. The private evidence
destination and Chris's receipt remain outstanding handoff actions.
