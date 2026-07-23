# TowerScout October 2026 Roadmap - Developer Response To Comprehensive Review

**Prepared**: 2026-07-22

**Status**: REVIEW RESPONSE - input to the next planning iteration; not an
approved execution plan

**Responds to**: `TowerScout Extended Project Roadmap - Comprehensive
Reviewer/Planner Assessment`

**Roadmap baseline reviewed**:
`2026-07-22-OCTOBER-PROJECT-ROADMAP-REVIEW-DRAFT.md`

**Project end**: 2026-10-31, with operational closeout by 2026-10-30

**Pilot baseline**: immutable fork-side `v0.1.2` at
`718a56485a59182f060a537e8f11d4ce71a1f0d4`

**Developer recommendation**: **APPROVE THE PHASE AND DATE FRAMEWORK WITH
REVISIONS; DO NOT ADOPT THE FULL PROPOSED WORK PORTFOLIO AS COMMITTED SCOPE**

---

## 1. Purpose And Decision Boundary

This document records the developer response to the comprehensive
Reviewer/Planner assessment and provides recommended answers to its Section 14
decision questions.

It is intended to support another planning iteration. It does not:

- select the next implementation task
- authorize any change to `cdcai/TowerScout`
- replace the project lead's external pilot-feedback record
- change or replace the published `v0.1.2` assets
- authorize destructive repository or records cleanup

Any approved implementation work must still be selected through the normal
task-planning process, assigned an owner, given acceptance criteria, and matched
to the required validation capacity.

## 2. Overall Assessment

The comprehensive review is directionally strong. Its governing strategy,
phase structure, adoption gates, feature cutoff, and October handoff protection
should be retained.

The review should not be converted into the execution plan verbatim. Its Phase
2 and Phase 3 portfolio contains enough security, policy, Windows automation,
release automation, documentation, data-lifecycle, governance, migration, and
architecture work to create several parallel projects. Calling the individual
items bounded does not make their combined workload bounded.

The approved roadmap should therefore retain the dates and risk controls while:

1. reducing the work committed before the August decision points
2. distinguishing required gates from candidate improvements
3. keeping unselected work in the backlog
4. preserving the external pilot-feedback boundary
5. requiring a minimum owner-runnable release qualification process without
   promising full automation of every environment-dependent validation cell
6. addressing stale current requirements/design context as part of handoff
   governance

## 3. Areas Of Agreement

The following recommendations should be accepted:

- Preserve the exact published `v0.1.2` assets and use a new version for any
  correction.
- Address confirmed pilot blockers, security issues, and data-integrity issues
  before optional improvement work.
- Keep `cdcai/TowerScout` unchanged until feedback review and explicit owner
  adoption approval.
- Use August 28 for the operating-outcome and repository-of-record decision.
- Use September 4 as the migration-completion-or-explicit-defer trigger.
- Use September 18 as the internal code-complete target.
- Keep September 25 as the feature-complete cutoff.
- Keep October 9 as the final-candidate/code-freeze date.
- Protect October from planned feature development.
- Treat `TASK-087` and `TASK-058` as alternative major lanes.
- Keep full `TASK-059` outside the baseline October plan.
- Require the receiving owner to demonstrate release, rejection/rollback,
  recovery, support, backlog, and handoff capability.
- Move unfinished lower-priority work to a durable owner backlog rather than
  compressing final validation and handoff.

## 4. Verified Immediate Security-Boundary Concern

The review correctly identifies a security-boundary concern that deserves
immediate bounded validation:

- [`compose.yaml`](../../../../compose.yaml) publishes
  `${TOWERSCOUT_PORT:-5000}:5000` without an explicit loopback host address.
- [`webapp/towerscout.py`](../../../../webapp/towerscout.py) starts Waitress on
  `0.0.0.0`.
- The same Flask module contains an apparently unused
  `/rm/uploads/<path:path>` route that deletes through `GET` without a visible
  final resolved-path containment check.

These static findings do not prove that a pilot workstation is remotely
reachable, that the deletion route is exploitable, or that an incident
occurred. They do establish that the intended local-only trust boundary should
not be assumed to be technically enforced without live validation.

Recommended handling:

1. Select an immediate security-validation task after roadmap approval.
2. Track the network-exposure and deletion-route findings independently within
   that task so each can receive its own severity and disposition.
3. Test representative Docker and supported Podman package paths, local browser
   behavior, non-default ports, and second-host reachability.
4. Determine whether the deletion route can be removed because no current
   caller has been identified. If retained, review HTTP method, path
   containment, local-browser/CSRF behavior, confirmation, and error handling.
5. Decide only after validation whether a new pilot patch is required.
6. Do not modify the published `v0.1.2` assets; any correction receives a new
   version identity.

## 5. Required Revisions Before Roadmap Approval

### 5.1 Reduce Phase 2 Commitments

Phase 2 covers only July 23 through August 7. It should be limited to:

- immediate security-boundary validation and severity classification
- receiving actionable pilot findings supplied by the project lead
- completing the preparation-only `TASK-089` migration/handoff packet
- preparing the `TASK-076` provider-key policy draft and identifying required
  owner decisions
- scoping the release-critical portion of `TASK-068`
- defining the minimum viable `TASK-091` qualification process
- confirming receiving-owner and validation-environment availability
- preparing concise candidate backlog entries for later selection

Phase 2 should not promise completion of every proposed P1 task.

### 5.2 Preserve The External Feedback Boundary

The project lead maintains pilot feedback in an external fillable Word
document. Repository plans should accept an actionable summary from the project
lead; they should not create or maintain a second feedback-classification or
intake table in `.agent_work`.

### 5.3 Keep Candidate Tasks In The Backlog Until Selected

The normal TowerScout task lifecycle keeps unselected work in
[`task-backlog.md`](../../../task-backlog.md). Detailed Type B/C active task
files are created when work moves into the active plan.

Recommended disposition:

- Create/select the immediate security-validation task only after roadmap
  approval.
- Record the release-qualification, documentation, data-lifecycle, support
  snapshot, and governance proposals as candidate backlog items.
- Create detailed active task files only when each item is selected.
- Treat provisional task numbers as placeholders until availability is
  confirmed.

### 5.4 Narrow The Release-Qualification Commitment

The final project needs an owner-runnable qualification process, but complete
automation across Windows, Docker, Podman, CPU, GPU, providers, managed
networks, assets, and publishing is likely larger than the proposed two-to-four
day estimate.

The minimum required harness should:

- verify candidate source, tag, image, package, checksum, and asset identities
- inspect required and forbidden package contents
- run the deterministic CPU fixture and repeatability check
- compare readiness identity with expected release metadata
- produce a sanitized human-readable and machine-readable report
- mark externally gated validation cells as required, optional, skipped, or
  incomplete
- allow the receiving owner to reject a failed candidate without publication

GPU, live-provider, managed-network, and some Windows package execution may
remain controlled manual cells. The requirement is a reproducible owner-run
qualification process, not automation for its own sake.

### 5.5 Stage Documentation Work

Current documentation contains real release-identity drift. Correct current
applicability wording first, without replacing the distributed `v0.1.2`
package. Treat the broader four-part information architecture as separately
approved work.

Compatibility paths must remain until route, package, test, support, and
historical dependencies are deliberately dispositioned.

### 5.6 Add Requirements And Design Rebaselining

[`requirements.md`](../../../requirements.md) and
[`design.md`](../../../design.md) contain a mixture of current requirements,
historical target-state ideas, obsolete platform goals, and pseudo-designs that
do not match the implemented application.

Handoff governance should either update these files or clearly label the
current versus historical sections so the receiving owner does not mistake old
design intent for current supported behavior.

### 5.7 Preserve The October 16 Validation Milestone

Retain the original explicit milestones:

- October 9: final candidate and code freeze
- October 16: final qualification and acceptance validation complete
- October 23: final release and handoff complete
- October 30: operational closeout and sign-off

Schedule a preliminary owner rehearsal by September 18 or September 25 so
October is not the first time owner operability is tested.

## 6. Recommended Revised Phase Commitments

| Period | Recommended commitment | Exit condition |
| --- | --- | --- |
| July 23-August 7 | Security triage, actionable feedback supplied by project lead, `TASK-089` packet, `TASK-076` draft, environment/owner scheduling, and candidate scoping | Security findings classified; migration packet reviewable; owner decisions and environment gaps visible; no pilot or cdcai mutation |
| August 10-August 28 | Resolve confirmed security findings as required, approve bounded policy/test work, select adopt/fix/defer outcome, and select at most one Phase 4 lane | Operating outcome and forward repository known; selected lane has owner, acceptance criteria, validation, and stop conditions |
| By September 4 | Complete approved migration mechanics or explicitly defer | No ambiguous repository-of-record or namespace state remains for continued work |
| August 31-September 18 | Implement exactly one approved major lane, or bounded hardening when no major lane is justified | Code complete; tests pass; package/runtime/provider/ML validation inputs are ready |
| September 21-September 25 | Integration, package validation, documentation, support readiness, and selected-lane acceptance | Feature complete; selected work is accepted or removed from the final candidate |
| September 28-October 9 | Final-candidate qualification and freeze | Candidate identity fixed; required qualification cells pass; blocker-only change rule begins |
| October 12-October 16 | Final qualification and acceptance validation | Release, package, support, recovery, and known-risk evidence accepted |
| October 19-October 23 | Owner-operated release, rollback/reject, recovery, backlog, and handoff rehearsal | Receiving owner can operate without current-developer dependency |
| October 26-October 30 | Contingency and administrative closeout | Access, custody, task disposition, backlog, and sign-off complete |
| October 31 | Hard project end | No planned work or unresolved operational dependency remains with the outgoing team |

## 7. Responses To Section 14 Decision Questions

### Roadmap Approval

| # | Question | Recommended answer |
| ---: | --- | --- |
| 1 | Approve the roadmap structure with the proposed phase/date changes? | **Yes, with revisions.** Retain the structure and dates, reduce Phase 2 commitments, and keep unselected tasks as candidates. |
| 2 | Use August 28 for the repository/operating decision and September 4 for migration completion or defer? | **Yes.** The August 28 outcome may be adopt, fix-before-adopt, or explicit defer. |
| 3 | Approve September 18 code complete, September 25 feature complete, and October 9 freeze? | **Yes.** These dates preserve integration and handoff margin. |
| 4 | Protect October from planned feature work? | **Yes.** October is for qualification, stabilization, owner acceptance, handoff, and contingency. |

### Newly Identified Tasks

| # | Question | Recommended answer |
| ---: | --- | --- |
| 5 | Create the local-only runtime and legacy route task as an immediate security/adoption gate? | **Yes, as an immediate validation gate.** It blocks adoption until the boundary is understood, but it is not a confirmed vulnerability or automatic pilot-patch decision. |
| 6 | Who owns severity and pilot response? | **Recommended roles:** project/release owner decides pilot response; cdcai owner approves adoption consequences; security reviewer advises severity. Named individuals remain to be confirmed. |
| 7 | Require an automated release-qualification harness? | **Yes, in minimum viable form.** Require deterministic identity/content/CPU checks, structured reporting, and owner execution; keep external cells controlled and explicit. |
| 8 | Approve the four-part user-documentation information architecture? | **Yes, conceptually and in stages.** Correct stale identity wording first; perform broader restructuring only when approved and capacity permits. |
| 9 | Implement reset/decommission tooling or require only lifecycle documentation and rehearsal? | **Require lifecycle documentation and rehearsal.** Implement only minimum safe tooling justified by identified gaps and approved destructive-operation controls. |
| 10 | Implement the sanitized support snapshot? | **Not yet.** Keep it in the successor backlog unless pilot/support evidence demonstrates diagnostic friction. |
| 11 | Create a separate governance/handoff-cleanliness task? | **Yes, narrowly.** It must complete even if adoption is deferred; focus on source-of-truth, retention, status consistency, repository inventory, and owner navigation. |

### Existing Tasks

| # | Question | Recommended answer |
| ---: | --- | --- |
| 12 | Complete `TASK-076` during Phase 2? | **Approve the work, but not unconditional completion.** Produce the draft and decision list in Phase 2; completion may require provider/security/release-owner approval. |
| 13 | Expand `TASK-068` to Windows/package contracts and CI promotion? | **Yes, in stages.** Implement release-critical script/package contracts first; promote checks only after they are reliable. |
| 14 | Which `TASK-077` items are required? | Require candidate-image scanning, a release-specific SBOM, a vulnerability-exception record, base-image digest recording/pinning with refresh guidance, and default-on asset verification if live validation supports it. Move from Node 18 when producing a new final build if validation passes. Do not rebuild `v0.1.2`. |
| 15 | Keep torch/YOLO trust work separate unless selected as the major lane? | **Yes.** It requires dedicated ML, CPU/GPU parity, package, and security validation. |
| 16 | Treat `TASK-087` and `TASK-058` as alternative major lanes? | **Yes.** Do not run them as parallel major tasks. |
| 17 | Keep full `TASK-059` after accepted `TASK-058` and outside the baseline plan? | **Yes.** Permit only extraction necessary to implement an approved `TASK-058` slice safely. |
| 18 | Use `TASK-027` as the bounded fallback lane? | **Yes, conditionally.** Select it only after mandatory security, ownership, release, and handoff work, and shape it around demonstrated recovery problems. |

### Ownership And Validation

| # | Question | Recommended answer |
| ---: | --- | --- |
| 19 | Who is the receiving owner/operator? | The cdcai owner should be the primary receiving operator, with the confirmed support owner as backup/observer. Named participant and availability require confirmation. |
| 20 | Which validation environments are available and when? | Not established by repository evidence. Confirm Windows, Docker, supported Podman, CPU, GPU, managed-network, provider, and receiving-owner availability before lane selection. |
| 21 | Which qualification cells are mandatory? | Use the minimum matrix in Section 8 below, then obtain release-owner approval for the final matrix. |
| 22 | Who can accept residual risks? | Recommended roles are cdcai owner for operational/repository risk, release owner for publication, security owner for security, compliance owner for license/compliance, provider account owner for key/quota risk, and data/system owner for decommissioning. Named authorities require confirmation. |
| 23 | What is the final backlog destination? | Prefer approved cdcai Issues. Otherwise use a version-controlled owner backlog in the final repository of record plus a portable final backlog export. Owner approval is required. |
| 24 | Who can delete or archive repository/project records? | cdcai owner for cdcai objects, fork owner for fork objects, and project/records owner for `.agent_work`. Prefer archive/supersede/document over deletion. Named authority requires confirmation. |

### Fact Normalization

| # | Question | Recommended answer |
| ---: | --- | --- |
| 25 | Is the pilot distribution date July 12 or July 13? | Use July 13 provisionally because current repository sources consistently record Monday, July 13. Confirm against the sent-email timestamp before final approval. |
| 26 | Are external milestones missing? | No additional milestone is evidenced in the repository. The project lead must confirm privacy/records transfer, compliance, organizational acceptance, security, procurement, or other external requirements. |

## 8. Recommended Minimum Change-To-Validation Matrix

| Change category | Minimum required validation |
| --- | --- |
| Planning or `.agent_work` only | Agent-work validators, link/status/current-source checks, `git diff --check`, and receiving-owner readability review |
| User documentation not yet packaged | Link and route checks, Markdown/HTML freshness or equivalence check, nontechnical-user review, and support review |
| Packaged documentation or Settings links | Documentation checks plus package-content tests, Flask allowlist/route tests, fresh-package resource check, and new package identity if distributed |
| Provider-key policy only | Document checks plus provider/security/release-owner approval |
| Provider, Setup, or Settings behavior | Unit, route, frontend contract, redaction, affected real-provider setup, and browser smoke |
| Compose, launcher, or local-runtime behavior | Script/package contracts, Docker CPU, applicable supported Podman path, readiness, non-default port, local browser, and second-host reachability |
| Legacy deletion-route hardening | Route tests for path/method/encoded forms plus the normal upload/delete user journey and security review |
| `TASK-087` enablement | Existing Gate 1-4 tests, redaction, duplicate/reconnect handling, managed-network validation, Docker CPU/CUDA, and Podman only when included |
| `TASK-058` durable jobs | Job state, concurrency, cancellation, restart/recovery, API compatibility, CPU package workflow, provider, result review, and export regression |
| Dependency, base-image, or ML changes | Image build and scan, SBOM, dependency tests, deterministic CPU repeatability, and GPU/per-tile parity when affected |
| Release packaging or manifest | Fresh build, package contents, checksums, asset import, readiness identity, deterministic smoke, and fresh-consumer verification |
| cdcai adoption | Fresh cdcai clone, public image pull, recreated package/release smoke, source traceability, and explicit cdcai-owner approval |

## 9. Decisions Requiring Project Or Owner Input

The following Section 14 questions cannot be closed from repository evidence:

- **6**: named severity and pilot-response owner
- **10**: whether actual pilot/support evidence justifies the support snapshot
- **19**: named receiving operator and rehearsal availability
- **20**: available validation environments and dates
- **22**: formally authorized risk acceptors
- **23**: approved final backlog destination
- **24**: authority over destructive repository/archive actions
- **25**: authoritative pilot send date
- **26**: external organizational milestones

Question **21** has a technical recommendation in this document, but its final
mandatory-cell matrix still requires release-owner approval.

## 10. Requested Reviewer/Planner Follow-Up

Please respond with:

1. acceptance or requested changes to the revised phase commitments
2. agreement or disagreement with the reduced Phase 2 boundary
3. disposition of the immediate security-validation recommendation
4. disposition of each candidate task: required gate, bounded candidate,
   conditional backlog, or successor backlog
5. revised effort and capacity assumptions, including validation time
6. named decision owners and due dates where available
7. changes to the minimum qualification matrix
8. answers or routing guidance for the unresolved questions in Section 9

After this feedback is received, the project can prepare a concise approved
roadmap, update the backlog without prematurely activating unselected work, and
select the first authorized Phase 2 task.

## 11. Current Repository Sources

- `2026-07-22-OCTOBER-PROJECT-ROADMAP-REVIEW-DRAFT.md`
- `PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`
- [`current-tasks.md`](../../../current-tasks.md)
- [`task-backlog.md`](../../../task-backlog.md)
- [`TASK-087`](../../../tasks/active/TASK-087-host-side-tls-repair-control-plane.md)
- [`TASK-088`](../../../tasks/active/TASK-088-stable-release-and-handoff-closeout.md)
- [`TASK-089`](../../../tasks/active/TASK-089-cdcai-migration-execution.md)
- [`HANDOFF.md`](../../../../HANDOFF.md)
- [`requirements.md`](../../../requirements.md)
- [`design.md`](../../../design.md)

---

**End of developer response.**
