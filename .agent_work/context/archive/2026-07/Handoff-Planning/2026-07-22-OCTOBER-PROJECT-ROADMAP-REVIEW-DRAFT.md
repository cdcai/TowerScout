# TowerScout Extended Project Roadmap - Reviewer/Planner Draft

**Prepared**: 2026-07-22

**Status**: REVIEW DRAFT - not yet an approved execution plan

**Planning window**: 2026-07-13 through 2026-10-31

**Hard project end**: 2026-10-31

**Operational closeout date**: 2026-10-30

**Pilot baseline**: fork-side `v0.1.2` at
`718a56485a59182f060a537e8f11d4ce71a1f0d4`

**Review requested from**: Reviewer / Planner

## Review Fields

- **Reviewer**:
- **Review date**:
- **Recommendation**: Approve / Approve with changes / Rework
- **Major schedule changes requested**:
- **Major scope changes requested**:
- **Risks or dependencies to add**:
- **Additional comments**:

## 1. Purpose

This document proposes a phased schedule for using the TowerScout project
extension through the end of October while preserving enough time for release
validation, cdcai ownership transfer, and final handoff.

It is intended for review and planning feedback. It does not select the next
implementation tasks, authorize changes to `cdcai/TowerScout`, or replace the
feedback-gated adoption decision. Specific task selection will occur in a later
planning iteration after this schedule and its capacity assumptions are
reviewed.

## 2. Confirmed Planning Facts

- The project has been extended through 2026-10-31. This is the hard end date.
- Because October 31 falls on a Saturday, 2026-10-30 is the operational
  completion and sign-off date.
- The validated `v0.1.2` pilot email was sent to the user group on 2026-07-13.
- Pilot feedback is maintained by the project lead in a fillable Word document
  outside the repository. Repository-based feedback intake and tracking are
  out of scope.
- The primary pilot support owner and backup contact are confirmed and have
  appropriate access.
- `TASK-088` is complete.
- `TASK-087` is paused after its merged non-mutating proof; later enablement is
  not automatically selected.
- `TASK-089` remains owner-gated. `cdcai/TowerScout` stays unchanged until
  feedback is reviewed and the owner explicitly approves an adoption baseline.
- The published `v0.1.2` assets are immutable. Any changed package must use a
  new version identity and proportionate validation.

## 3. Recommended Planning Approach

Use July through September as the primary decision and implementation window.
Protect October for stabilization, release validation, ownership transfer,
documentation, and contingency.

The recommended capacity assumption is:

- address any confirmed pilot blockers first
- complete ownership/adoption work when its external gates are satisfied
- select no more than one major improvement lane at a time
- add only bounded smaller work that does not threaten the September feature
  cutoff
- do not plan to complete the entire backlog before project end

This is intentionally conservative. Earlier release work showed that package,
runtime, provider, and clean-machine findings can expand validation time even
when the source change appears small.

## 4. Proposed Phases And Dates

| Phase | Dates | Status | Primary objective | Expected exit condition |
| --- | --- | --- | --- | --- |
| 1. Rebaseline And Pilot-Launch Closeout | July 13-July 22 | **COMPLETED** | Align all current plans to the October hard stop, record completed pilot/support facts, close Task-088, and merge the handoff documentation | Current sources use the October deadline; Task-088 is complete; no new work is selected; documentation is merged to `main` |
| 2. Pilot Stabilization And Decision Inputs | July 23-August 7 | Proposed | Preserve the validated pilot, respond only to actionable findings supplied by the project lead, and gather the information needed to select later work | Blocking findings are identified or ruled out; schedule/scope assumptions are reviewed; no silent change to `v0.1.2` |
| 3. Adoption Decision And Ownership Transition | August 10-August 28 | Proposed / owner-gated | Obtain the cdcai owner's adoption decision and execute the approved ownership transition only if all Task-089 gates are satisfied | Approved baseline is adopted and revalidated, or a documented decision is made to fix first or defer adoption |
| 4. Focused Improvement Window | August 31-September 25 | Proposed / scope not selected | Complete the approved improvement work while preserving release and handoff capacity | Selected work is feature-complete, tested, documented, and ready for final release-candidate validation |
| 5. Feature Freeze And Final Release Candidate | September 28-October 9 | Proposed | Stop feature growth, close release blockers, and validate the final candidate across affected package/runtime/provider surfaces | Final candidate is frozen; required automated and manual validation passes; release and support docs are current |
| 6. Final Acceptance And Handoff | October 12-October 23 | Proposed | Complete owner acceptance, publish the final approved release state, and transfer operational knowledge and remaining backlog | Owner can operate the repository/release path without depending on the current developer; final handoff package is accepted |
| 7. Contingency And Administrative Closeout | October 26-October 30 | Proposed | Resolve only final blockers, verify custody/access, and complete sign-off | No unresolved operational dependency remains; final status and ownership sign-off are recorded before project end |
| Official End | October 31 | **HARD DATE** | Project ends | No planned project work remains after this date |

## 5. Phase 1 Completion Record

Phase 1 was completed through PR #49 and merged to `main` as
`bce9dab585e839f9adead32b9aee38410d046ae7`.

Completed outcomes:

- [x] Replaced the former July 15 contingency with the hard October 31 end date.
- [x] Established October 30 as the operational closeout date.
- [x] Recorded the July 13 pilot email as sent.
- [x] Recorded the external fillable Word feedback method.
- [x] Confirmed primary and backup support coverage and appropriate access.
- [x] Removed `.agent_work` responsibility for feedback intake and tracking.
- [x] Confirmed durable public/repository custody of the release assets,
  checksums, validation summaries, handoff guidance, and known findings.
- [x] Marked Task-088 complete.
- [x] Marked Task-087 paused/deferred pending a future planning decision.
- [x] Kept Task-089 deferred and owner-gated.
- [x] Selected no new backlog work.
- [x] Passed repository CI, both agent-work validators, documentation checks,
  and the 57-test Flask route suite.

## 6. Phase 2 Decision Boundary

Phase 2 is not a commitment to a specific implementation task. Its purpose is
to protect the pilot baseline and create enough evidence for the next planning
decision.

During this phase:

- the project lead remains the source of actionable pilot feedback
- reported blockers, security/data-integrity concerns, supportability gaps, and
  non-blocking improvements should be distinguished before scope is selected
- `v0.1.2` remains unchanged
- any necessary package correction receives a new version
- the Reviewer/Planner should confirm whether the remaining dates and capacity
  assumptions are realistic

Phase 2 exits when there is enough information to approve the next work slice,
not merely because August 7 arrives.

## 7. Adoption And Repository-Ownership Gate

The recommended target for an initial adoption recommendation is August 21.
September 4 is the recommended latest internal decision point if the project
is to complete a normal cdcai adoption, subsequent development, and owner
operating period before final closeout.

Task-089 execution still requires:

- pilot feedback review
- explicit cdcai-owner approval of the version to adopt
- confirmed repository, Actions, and package-publish permissions
- an approved durable backlog destination
- an approved image copy/rebuild and validation path

If those gates are not satisfied, the schedule must use the documented defer-
adoption path rather than forcing a late repository change.

## 8. Scope Selection Rules For Phase 4

Specific planned work is intentionally left open for Reviewer/Planner input.
When work is selected, apply these rules:

1. Confirmed release blockers and security/data-integrity findings come first.
2. Work required for safe cdcai ownership or sustainable support comes before
   optional feature development.
3. Select at most one major improvement lane at a time.
4. Prefer work with clear acceptance criteria and validation available before
   September 25.
5. Do not start a major change whose package/provider/ML validation cannot
   reasonably finish before the feature cutoff.
6. Keep unrelated cleanup and broad modernization outside a selected work
   slice.
7. Move incomplete lower-priority work into the final owner backlog rather
   than compressing October validation and handoff.

## 9. Hard Milestones And Stop Rules

| Date | Milestone | Stop rule |
| --- | --- | --- |
| August 7 | Pilot decision-input checkpoint | Do not select major work without sufficient evidence and Reviewer/Planner agreement |
| August 21 | Target adoption recommendation | Do not treat technical access as adoption approval |
| September 4 | Recommended latest adoption decision | If approval is still unavailable, use the defer-adoption handoff path rather than a rushed migration |
| September 25 | Feature complete | Do not begin new major implementation after this date |
| October 9 | Final candidate and code freeze | Accept only release blockers, security/data-integrity fixes, or explicitly approved closeout corrections |
| October 16 | Final acceptance validation complete | Unresolved non-blocking work moves to the owner backlog |
| October 23 | Final release and handoff complete | Remaining week is contingency, not planned feature work |
| October 30 | Operational closeout and sign-off | All access, custody, ownership, release, and documentation checks must be complete |
| October 31 | Official project end | No unfinished operational dependency may rely on the current project team |

## 10. Handoff Deliverables To Preserve Across All Phases

- source and release identity for every adopted version
- release assets, checksums, image digests, and validation summaries
- setup, troubleshooting, support, and recovery guidance
- accepted risks and known findings
- final backlog with dependencies and recommended disposition
- repository, Actions, release, and package ownership/access record
- reproducible release and validation instructions
- explicit record of what was completed, deferred, or not approved
- fork preservation as the pilot/provenance archive after any cdcai adoption

The external fillable Word feedback document remains under the project lead's
custody and should be transferred according to the project's access-controlled
handoff process; it should not be committed to this repository.

## 11. Principal Schedule Risks

| Risk | Effect | Recommended control |
| --- | --- | --- |
| Pilot feedback arrives late or identifies a release blocker | Adoption and improvement work may shift | Preserve schedule buffer and use a new version for any package correction |
| cdcai adoption approval or permissions arrive late | Ownership transition is compressed | Use September 4 as the internal decision point and retain the defer-adoption path |
| Too many backlog items are selected | October release/handoff work is crowded out | Limit work in progress and select one major lane at a time |
| A source change expands package or provider validation | Nominal task estimates become unreliable | Reserve explicit validation time and stop feature growth September 25 |
| October is treated as normal development time | Final release and ownership transfer become fragile | Enforce feature freeze and protect October for stabilization/handoff |
| Sensitive feedback or support material enters the repository | Privacy/security exposure | Keep the Word document and contact details in access-controlled project records |

## 12. Questions For Reviewer/Planner

Please provide input on the following:

1. Is the overall July-to-October phase structure realistic?
2. Should October remain protected primarily for stabilization and handoff?
3. Are August 21 and September 4 reasonable adoption decision points?
4. Is one major improvement lane at a time the correct capacity limit?
5. Is September 25 an appropriate feature-complete cutoff?
6. Is October 9 an appropriate final candidate/code-freeze date?
7. Are any required ownership, release, security, compliance, or acceptance
   milestones missing?
8. Which decisions require cdcai-owner approval versus project-team approval?
9. What evidence should be required before selecting the Phase 4 scope?
10. What changes should be made before this draft becomes the approved plan?

## 13. Requested Review Output

The Reviewer/Planner should return:

- approve / approve with changes / rework recommendation
- revised phase dates, if any
- capacity and sequencing concerns
- required decision owners
- missing dependencies or handoff deliverables
- requested changes to the hard milestones or stop rules
- guidance for the next iteration in which specific work will be selected

After review, this document should either be revised into the approved roadmap
or archived as a superseded draft. It should not silently become the execution
plan without a recorded approval decision.

## 14. Related Current Sources

- `PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`
- `PILOT-OPERATIONS-PACKET.md`
- `.agent_work/current-tasks.md`
- `.agent_work/task-backlog.md`
- `.agent_work/tasks/active/TASK-088-stable-release-and-handoff-closeout.md`
- `.agent_work/tasks/active/TASK-089-cdcai-migration-execution.md`
- `HANDOFF.md`
