# TowerScout October 2026 Roadmap - Developer Response To Updated Comprehensive Review

**Prepared**: 2026-07-22

**Status**: REVIEW RESPONSE - input to the next planning iteration; not an
approved execution plan

**Responds to**: `TowerScout October 2026 Roadmap - Updated Comprehensive
Reviewer/Planner Assessment` based on repository commit `348c566`

**Roadmap baseline**:
`2026-07-22-OCTOBER-PROJECT-ROADMAP-REVIEW-DRAFT.md`

**Prior developer response**:
`2026-07-22-DEVELOPER-RESPONSE-TO-COMPREHENSIVE-ROADMAP-REVIEW.md`

**Project end**: 2026-10-31, with operational closeout by 2026-10-30

**Authoritative pilot send date**: 2026-07-13

**Developer recommendation**: **APPROVE THE UPDATED PHASE AND DATE FRAMEWORK
AFTER THE TARGETED CORRECTIONS IN THIS RESPONSE; THEN PRODUCE A SHORTER
OPERATIONAL ROADMAP FOR FORMAL APPROVAL**

---

## 1. Purpose And Decision Boundary

This document records the developer's second-round response to the updated
Reviewer/Planner assessment. It also incorporates the project lead's answers
to the decision questions that remained open after the first review.

This document is designed to help the Reviewer/Planner prepare the next
iteration. It does not:

- approve the roadmap or convert proposed work into committed scope
- authorize proposed `TASK-090` or any other implementation task
- authorize a change to `cdcai/TowerScout`
- replace the project lead's external pilot-feedback record
- alter or replace the immutable fork-side `v0.1.2` pilot release
- authorize destructive repository, release, or records cleanup

Implementation begins only after the applicable work is selected, authorized,
assigned, and given acceptance and validation criteria.

## 2. Executive Assessment

The updated assessment is the strongest roadmap iteration so far. I agree with
most of its analysis and recommend using its phase and date structure as the
basis for the approved roadmap.

The update successfully addresses most of the concerns from the first review:

- Phase 2 is smaller and more realistic.
- Required gates, required outcomes, candidates, and successor work are more
  clearly separated.
- The external Word feedback process remains outside `.agent_work`.
- The August 31-September 4 repository-transition rule is explicit.
- The release-qualification proposal is reduced to a minimum owner-runnable
  process rather than complete automation of every environment.
- Documentation work is staged.
- Requirements and design rebaselining is recognized as a handoff need.
- Supply-chain upgrades are no longer automatically bundled into one large
  task.
- The October 16 final-qualification milestone is restored.
- A preliminary owner rehearsal is included before October.
- The support snapshot remains evidence-dependent successor work.
- `TASK-087` and `TASK-058` remain alternative major lanes.
- Full `TASK-059` remains outside the baseline plan.

The updated assessment is comprehensive review evidence, but it is too long to
serve as the day-to-day execution plan. After the corrections below, the next
artifact should be a concise approved roadmap that links to detailed task
specifications and preserves only the decision history a future owner needs.

## 3. Important Technical Correction From The First Response

The updated Reviewer/Planner assessment is correct that the legacy custom-image
deletion route is part of an active application workflow. The first developer
response incorrectly described it as apparently unused.

The current flow is:

1. [`webapp/js/src/towerscout.js`](../../../../webapp/js/src/towerscout.js)
   submits a custom image to `/getobjectscustom`.
2. The frontend draws the image from `/uploads/` plus the browser-provided
   `image.name`.
3. After the image loads, the frontend calls `removeCustomImage(url)`.
4. That function sends a `GET` request to `/rm` plus the upload URL.
5. [`webapp/towerscout.py`](../../../../webapp/towerscout.py) deletes the
   corresponding file from the upload directory.

The route therefore cannot simply be removed without preserving the custom
image workflow. The proposed security-boundary investigation remains
justified, but it must cover both safe behavior and workflow compatibility.

The investigation should specifically address:

- HTTP method and request-forgery exposure
- canonical server-side filename or upload identifier handling
- resolved-path containment before deletion
- encoded and malformed path behavior
- deletion error handling and user-visible behavior
- the complete upload, display, detection, and cleanup journey

Upload validation currently sanitizes the submitted filename, while the
frontend reconstructs the later URL from the original browser-side
`image.name`. A safer design would have the upload response return the
canonical server-generated filename or identifier and require the frontend to
use that value. The investigation should confirm the exact behavior before a
remediation is designed.

This correction changes the proposed task from "validate and potentially
remove an unused route" to "validate and safely harden an active workflow."

## 4. Disposition Of Project Lead Answers

The following answers are now authoritative planning inputs.

| Prior question | Project lead answer | Roadmap disposition |
| ---: | --- | --- |
| 6 | The project lead owns severity and pilot-response decisions in coordination with the future `cdcai` repository owner. | **Resolved.** The developer or assigned security reviewer supplies the technical recommendation; the project lead decides the pilot response with the `cdcai` owner. |
| 10 | Pilot feedback is still pending. | **Resolved for now.** Keep proposed `TASK-094` as evidence-dependent successor work. Do not commit it without feedback showing a support-diagnostics need. |
| 19 | The `cdcai` repository owner will receive repository ownership. | **Mostly resolved.** The receiving owner is known. The roadmap still needs to record whether that owner will personally run release rehearsals or designate an operator. |
| 20 | All validation environments are available. | **Availability resolved.** The remaining need is to reserve or confirm their use by the applicable milestone dates; see Section 7. |
| 22 | The `cdcai` owner owns the final residual-risk decision. | **Resolved for project planning**, subject to any external organizational approval rules identified later. |
| 23 | Backlog transfer should be workable because the project lead works closely with the `cdcai` owner. | **Risk reduced but destination still open.** Select and record the durable destination by August 28. |
| 24 | The project lead owns `J-Schulein/TowerScout`. | **Resolved for the fork.** The project lead can authorize fork branches, tags, releases, packages, and `.agent_work` handling. The `cdcai` owner controls actions in `cdcai/TowerScout`. |
| 25 | July 13 is the authoritative pilot send date. | **Fully resolved.** Remove July 12/13 uncertainty from current plans and questions. Historical records may retain a correction note. |
| 26 | External organizational milestones are not yet known and will be discussed with the `cdcai` owner after the roadmap is more solid. | **Open but not Phase 2-blocking.** Confirm by August 28 whether privacy, records, security, compliance, procurement, or organizational acceptance steps apply. |

## 5. Corrections Needed Before Roadmap Approval

### 5.1 Resolve The `TASK-095` Classification Conflict

The updated assessment describes minimum governance and handoff cleanliness as
a required final outcome, but later places `TASK-095` in work to select based
on evidence. Those positions conflict.

Recommended correction:

- minimum `TASK-095` governance is required by final handoff
- optional cleanup beyond that minimum is evidence- and capacity-dependent
- the detailed task remains in the backlog until selected through the normal
  task lifecycle

The required minimum should cover source-of-truth navigation, current task and
backlog disposition, requirements/design applicability, records custody,
repository inventory, and final owner readability.

### 5.2 Make Mixed Required/Candidate Tasks Explicit

Several proposals contain a required planning or handoff outcome and a larger
optional implementation scope. The roadmap should classify each part
separately:

| Proposed task | Required portion | Candidate or successor portion |
| --- | --- | --- |
| `TASK-076` | Phase 2 provider-key policy draft and owner decision list | Full completion after required approvals |
| `TASK-068` | Phase 2 scope and estimate for release-critical Windows/package contracts | Selected implementation slice |
| `TASK-091` | Specification by August 7 and minimum owner-runnable qualification process by handoff | Broader automation across externally gated cells |
| `TASK-092` | Stage A currentness and applicability corrections | Stage B information-architecture restructuring |
| `TASK-093` | Lifecycle documentation and owner rehearsal | Destructive-operation tooling where evidence justifies it |
| `TASK-094` | None at present | Successor work only if pilot/support evidence shows a need |
| `TASK-095` | Minimum final governance and handoff cleanliness | Optional broader cleanup |

This distinction prevents a required planning deliverable from silently
authorizing the larger implementation task.

### 5.3 Reserve Capacity For Required Outcomes First

The project should select at most one optional major implementation lane. That
lane may be selected only after capacity is reserved for:

- security and pilot-blocker response when findings require it
- the minimum owner-runnable release qualification process
- Stage A documentation currentness corrections
- minimum governance and requirements/design rebaselining
- final qualification, owner rehearsal, migration or defer mechanics, and
  handoff

This is especially important because most development is expected to be
performed by one developer. Required closeout work cannot depend on an
optimistic assumption that optional feature work finishes early.

### 5.4 Tighten The Shortened-September Rule

If repository transition work is not complete until September 8, the default
should be bounded hardening rather than starting a major lane.

`TASK-087` or `TASK-058` should remain eligible only if all of the following are
already true:

- design and acceptance criteria are complete
- the work has been re-estimated against the remaining calendar
- required validation environments are reserved
- rollback or removal from the final candidate is practical
- September 18 code complete remains credible

If any condition is missing, use the time for mandatory security, release,
documentation, governance, and handoff work.

### 5.5 Separate `TASK-090` Investigation From Remediation

A one-to-three-day estimate is reasonable for bounded investigation and
severity classification. It is not yet a reliable estimate for remediation,
cross-runtime validation, packaging, and a new release.

The roadmap should therefore use two decisions:

1. authorize and complete the investigation
2. estimate and authorize remediation based on verified findings

If a pilot patch is required, that work becomes the primary implementation
lane and displaces optional major work as needed. The published `v0.1.2`
artifacts remain immutable; a correction receives a new version identity.

### 5.6 Remove Pilot-Date Uncertainty

July 13 is authoritative. Current Phase 2 plans, next-action lists, decision
questions, and deadline tables should use that date without requesting further
confirmation. Historical documents may preserve the former discrepancy and
its resolution.

### 5.7 Use Planning Language That Cannot Be Mistaken For Git Instructions

Replace ambiguous labels such as "Commit now" with planning-specific terms:

- **Approve as current roadmap commitments**
- **Required by final handoff**
- **Candidate work requiring selection**
- **Successor backlog unless evidence changes**

This avoids confusing a scope decision with a source-control commit.

## 6. Recommended Decision And Ownership Model

| Decision or responsibility | Recommended owner |
| --- | --- |
| Pilot finding severity and pilot-response decision | Project lead, in coordination with the `cdcai` owner |
| Technical and security recommendation | Developer or specifically assigned technical/security reviewer |
| Adoption baseline and future repository of record | `cdcai` owner, in coordination with the project lead |
| Final project-level residual-risk acceptance | `cdcai` owner |
| Fork archive, retention, releases, packages, and cleanup | Project lead as `J-Schulein/TowerScout` owner |
| `cdcai` repository archive, retention, releases, and cleanup | `cdcai` owner |
| Final operational acceptance | `cdcai` owner and the designated release operator, if different |
| Pilot feedback custody and actionable summaries | Project lead |
| Release implementation and validation evidence | Developer or assigned release operator |

The roadmap should distinguish the person who provides technical advice from
the person authorized to accept the resulting risk. It should not invent a
separate formal security-review role if the project does not have one.

## 7. Environment Availability And Scheduling

The project lead confirmed that all environments are available. The phrase
"by what dates" means the roadmap should reserve or confirm access when the
environment is needed, not re-question whether it exists.

Recommended scheduling assumptions:

| Date | Environment or participant need |
| --- | --- |
| By August 7 | Docker, supported Podman path, local-browser test, and second-host reachability for proposed `TASK-090` investigation, if authorized |
| By August 28 | Managed-network, GPU, live-provider, and Windows package environments required by the selected implementation lane are reserved or confirmed on demand |
| By September 25 | Selected-lane validation is complete in all mandatory cells |
| By October 16 | Final candidate has completed the approved qualification matrix |
| September 18-25 | Receiving owner or designated operator completes a preliminary release/handoff rehearsal |
| By October 23 | Receiving owner or designated operator completes the final owner-run release, reject/rollback, recovery, support, and backlog workflow |

If every environment is available on demand, the approved roadmap can simply
record "no known availability blocker" and identify the owner responsible for
calling each validation cell.

## 8. Required And Candidate Scope Recommendation

### Approve As Current Roadmap Commitments

- preserve the immutable `v0.1.2` pilot baseline
- accept actionable pilot findings from the project lead without duplicating
  feedback intake in the repository
- complete the preparation-only `TASK-089` adoption and migration packet
- perform required security/pilot-blocker work after explicit authorization
- define and deliver the minimum owner-runnable release qualification process
- correct current documentation applicability and release-identity drift
- complete minimum governance, requirements/design rebaselining, validation,
  owner rehearsal, and final handoff
- decide the operating outcome and repository of record by August 28
- complete approved migration mechanics or explicitly defer by September 4

### Candidate Work Requiring Selection

- a bounded `TASK-068` Windows/package contract implementation slice
- `TASK-076` completion after the policy draft receives required decisions
- broader `TASK-091` automation beyond the minimum owner-runnable process
- `TASK-092` Stage B information-architecture restructuring
- one major implementation lane: `TASK-087` or a bounded `TASK-058` slice
- `TASK-027` as a bounded fallback only when recovery evidence justifies it

### Successor Backlog Unless Evidence Changes

- proposed `TASK-094` sanitized support snapshot
- full `TASK-059` UI/backend decoupling
- broad cleanup beyond minimum `TASK-095` governance
- enhancements that do not directly protect adoption, final release quality,
  owner operability, or the October handoff

## 9. Remaining Decisions

Only the following material planning questions remain open:

1. **Authorization of proposed `TASK-090`:** Is the bounded investigation
   authorized once the roadmap is approved? This response recommends it but
   does not infer authorization.
2. **Receiving operator:** Will the `cdcai` owner personally perform the
   preliminary and final release rehearsals, or designate another operator?
3. **Durable backlog destination:** Will adopted work move to `cdcai` Issues or
   another `cdcai`-approved tracker? If adoption is deferred, should the final
   owner backlog remain version-controlled in the fork with a portable copy?
4. **External organizational milestones:** Do privacy, records, security,
   compliance, procurement, or acceptance steps apply? Confirm with the
   `cdcai` owner by August 28.
5. **Mandatory qualification cells:** The technical minimum can be proposed by
   the developer, but the `cdcai` owner should confirm which environment and
   workflow cells are mandatory for final acceptance.

Pending pilot feedback is an expected input, not a planning blocker. The
roadmap should include a controlled response path without assuming what the
feedback will contain.

## 10. Recommended Form Of The Approved Roadmap

The updated assessment should be preserved as review evidence. It should not
become the daily operating document in its current comprehensive form.

The final approved roadmap should be shorter and contain:

1. settled facts and non-negotiable boundaries
2. phase dates, milestones, and exit conditions
3. required outcomes versus candidate and successor scope
4. named decision owners and due dates
5. the minimum change-to-validation matrix
6. stop, descope, and late-change rules
7. a concise open-decision register
8. accepted, modified, and deferred review recommendations

Detailed acceptance criteria, commands, test cases, and implementation notes
should live in the applicable backlog or task documents. The approved roadmap
should still include enough decision history that the future owner does not
need both external review documents to understand why the plan was chosen.

## 11. Recommended Phase And Milestone Framework

| Period | Recommended focus | Required exit |
| --- | --- | --- |
| July 23-August 7 | Bounded security investigation if authorized, actionable feedback supplied by project lead, `TASK-089` packet, policy/test specifications, environment and owner scheduling | Findings classified; migration packet reviewable; required decisions and validation needs visible; no unauthorized pilot or `cdcai` mutation |
| August 10-August 28 | Required security response, bounded policy/release work, operating-outcome decision, backlog destination, external-milestone check, and at most one Phase 4 lane selection | Adopt, fix-before-adopt, or defer outcome approved; future repository known; selected work has owner, acceptance, validation, estimate, and stop rules |
| By September 4 | Approved migration mechanics or explicit defer | No ambiguous repository-of-record or namespace state remains |
| August 31-September 18 | One approved major lane only when the start gate is met; otherwise mandatory hardening and handoff work | Code complete; required tests pass; removal/rollback remains practical |
| September 21-September 25 | Integration, package validation, documentation, support readiness, and preliminary owner rehearsal | Feature complete; selected work accepted or removed; owner operability gaps known |
| September 28-October 9 | Final-candidate qualification and freeze | Candidate identity fixed; required qualification cells pass; blocker-only change rule begins |
| October 12-October 16 | Final qualification and acceptance validation | Release, package, support, recovery, and known-risk evidence accepted |
| October 19-October 23 | Owner-operated release, reject/rollback, recovery, backlog, and handoff rehearsal | Receiving owner can operate without outgoing-developer dependency |
| October 26-October 30 | Contingency and administrative closeout | Access, custody, task disposition, backlog, and sign-off complete |
| October 31 | Hard project end | No planned work or unresolved operational dependency remains with the outgoing team |

## 12. Requested Reviewer/Planner Follow-Up

Please use this response to prepare the next roadmap iteration and:

1. correct the active custom-image deletion-route description
2. resolve the `TASK-095` classification conflict
3. split required deliverables from candidate implementation for mixed tasks
4. make the shortened-September start gate explicit
5. separate proposed `TASK-090` investigation and remediation estimates
6. normalize the pilot date to July 13
7. replace ambiguous "commit" terminology
8. incorporate the settled ownership and environment answers
9. retain only the five open decisions in Section 9
10. produce a concise candidate approved roadmap in the format described in
    Section 10

The next iteration should state clearly that acceptance by the
Reviewer/Planner is not itself implementation authorization. After the roadmap
is approved, the project lead can select the first Phase 2 task through the
normal task-planning process.

## 13. Current Repository Sources

- `2026-07-22-OCTOBER-PROJECT-ROADMAP-REVIEW-DRAFT.md`
- `2026-07-22-DEVELOPER-RESPONSE-TO-COMPREHENSIVE-ROADMAP-REVIEW.md`
- `PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`
- [`current-tasks.md`](../../../current-tasks.md)
- [`task-backlog.md`](../../../task-backlog.md)
- [`TASK-087`](../../../tasks/active/TASK-087-host-side-tls-repair-control-plane.md)
- [`TASK-088`](../../../tasks/active/TASK-088-stable-release-and-handoff-closeout.md)
- [`TASK-089`](../../../tasks/active/TASK-089-cdcai-migration-execution.md)
- [`HANDOFF.md`](../../../../HANDOFF.md)
- [`requirements.md`](../../../requirements.md)
- [`design.md`](../../../design.md)
- [`compose.yaml`](../../../../compose.yaml)
- [`webapp/js/src/towerscout.js`](../../../../webapp/js/src/towerscout.js)
- [`webapp/towerscout.py`](../../../../webapp/towerscout.py)

---

**End of second-round developer response.**
