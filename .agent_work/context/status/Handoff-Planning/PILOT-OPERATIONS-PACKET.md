# TowerScout v0.1.2 Pilot Launch And Custody Record

**Prepared**: 2026-07-12

**Pilot sent**: 2026-07-13

**Record updated**: 2026-07-22

**Baseline**: `v0.1.2` at `718a56485a59182f060a537e8f11d4ce71a1f0d4`

**Release**: `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`

**Status**: COMPLETE

This record confirms that the validated pilot was distributed and that its
support and evidence custody prerequisites were satisfied. It does not
authorize changes to `cdcai/TowerScout`.

## Completed Launch Conditions

- [x] The pilot email was sent to the user group on 2026-07-13.
- [x] The email identifies the fork-side `v0.1.2` release as the pilot source
  and does not present the unchanged cdcai repository as the pilot download.
- [x] The primary pilot support owner and backup contact are confirmed.
- [x] Both support contacts have appropriate access.
- [x] Feedback is captured by the project lead in a fillable Word document
  outside this repository.
- [x] Feedback intake and tracking are not duplicated in `.agent_work`.
- [x] The six published and validated assets remain immutable:
  - `towerscout-v0.1.2-cpu.zip`
  - `towerscout-v0.1.2-cpu.zip.sha256`
  - `towerscout-v0.1.2-cuda121.zip`
  - `towerscout-v0.1.2-cuda121.zip.sha256`
  - `towerscout-v0.1.2-assets-towerscout-v1-assets-2026-05-05.zip`
  - `towerscout-v0.1.2-assets-towerscout-v1-assets-2026-05-05.zip.sha256`

Contact names, addresses, and the feedback document are intentionally not
stored in this public repository. They remain in the sent communication and
access-controlled project records.

## Durable Evidence Custody

- [x] Stable release and six assets: the public `v0.1.2` GitHub Release.
- [x] Source identity: tag `v0.1.2` and commit shown above.
- [x] User setup: `docs/quick-start.md` and packaged HTML equivalent.
- [x] First-line support: `docs/package-guide.md`.
- [x] Handoff and accepted risks: `HANDOFF.md`.
- [x] Validation summary and reproduction guide:
  `v0.1.2-Validation-Evidence/` in this folder.
- [x] Pilot/adoption decision:
  `PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`.
- [x] Deferred adoption preparation:
  `.agent_work/tasks/active/TASK-089-cdcai-migration-execution.md`.
- [x] Confirmed support contacts have appropriate access to continue support
  without depending solely on the current developer.

## Ongoing Boundaries

- The project ends 2026-10-31; operational closeout is 2026-10-30.
- The project lead will provide actionable feedback from the external Word
  document when development action is needed.
- Any changed package receives a new version identity. Never replace the
  published `v0.1.2` bytes.
- `cdcai/TowerScout` remains unchanged until feedback review and explicit owner
  approval of an adoption baseline.
- Task-089 moves from preparation to execution only after that approval.
