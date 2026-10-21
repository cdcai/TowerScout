# TowerScout October 2026 Roadmap - Developer Feedback On Candidate Operational Roadmap

**Prepared**: 2026-07-22

**Status**: REVIEW FEEDBACK - input to roadmap finalization; not formal roadmap
approval or implementation authorization

**Responds to**:

- `TowerScout-October-2026-Candidate-Operational-Roadmap-1e54b04.md`
- `TowerScout-October-2026-Supplemental-Reviewer-Analysis-1e54b04.md`

**Repository basis**:
`1e54b04e65a5eef74b15632ac92e63fb5200d74c`

**Project end**: 2026-10-31, with operational closeout by 2026-10-30

**Authoritative pilot send date**: 2026-07-13

**Developer recommendation**: **APPROVE WITH CHANGES. USE THE CANDIDATE
OPERATIONAL ROADMAP AS THE FINAL ROADMAP AFTER THE TARGETED CORRECTIONS IN THIS
RESPONSE.**

---

## 1. Purpose And Decision Boundary

This document records the developer's review of the candidate operational
roadmap and its supplemental Reviewer/Planner analysis. It is intended to help
produce a final, internally consistent roadmap that can be formally approved
and used as the project's single planning source of truth.

This document does not:

- approve the roadmap
- authorize proposed `TASK-090` or any other task
- select work from the backlog
- change the status of `TASK-087`, `TASK-088`, or `TASK-089`
- authorize a change to `cdcai/TowerScout`
- alter or replace the immutable fork-side `v0.1.2` pilot release
- replace the project lead's external pilot-feedback record
- authorize destructive repository, package, release, or data cleanup

The current task-selection hold remains in effect until the project lead makes
and records the applicable approval and authorization decisions.

## 2. Executive Assessment

The candidate operational roadmap is strong enough to become the final roadmap
after a limited set of corrections. The supplemental analysis is thorough and
accurate enough to preserve as supporting review evidence.

The overall direction does not need to be redesigned. The remaining issues are
primarily about:

- what formal approval actually authorizes
- when required work is selected and assigned
- how late pilot feedback is handled
- where owner-runnable qualification inputs are kept
- how destructive rehearsal steps are controlled
- how final-baseline scenarios and risk exceptions are recorded
- which artifact becomes the single current roadmap

Recommended disposition:

- **Candidate operational roadmap**: approve with the changes in Section 5.
- **Supplemental analysis**: retain as review evidence and detailed rationale.
- **Earlier roadmap draft and developer responses**: mark as superseded review
  evidence when the final roadmap is formally approved.

## 3. Areas Of Agreement

The following recommendations should be retained.

### Release And Adoption Boundaries

- Preserve the exact published `v0.1.2` pilot assets as immutable.
- Use a new version identity for any corrected package.
- Keep `cdcai/TowerScout` unchanged until feedback review and explicit owner
  adoption approval.
- Keep pilot feedback in the project lead's access-controlled Word document;
  provide only sanitized actionable findings to the repository.
- Preserve the prepare-now, execute-later boundary for `TASK-089`.

### Scope And Sequencing

- Treat confirmed security, data-integrity, and pilot blockers as higher
  priority than optional improvements.
- Treat proposed `TASK-090` as an investigation first, with remediation
  separately estimated and authorized.
- Keep at most one optional major implementation lane active.
- Treat `TASK-087` and a bounded `TASK-058` slice as alternative lanes.
- Keep full `TASK-059` outside the baseline October plan.
- Keep proposed `TASK-094` evidence dependent.
- Require minimum `TASK-095` governance by final handoff while keeping broad
  cleanup optional.
- Default to bounded required hardening if repository transition consumes the
  first week of September.

### Milestones And Handoff Protection

- August 28: operating outcome, repository, ownership, and scope decisions.
- September 4: approved migration mechanics complete or migration explicitly
  deferred.
- September 18: code complete.
- September 25: feature complete and preliminary owner rehearsal complete.
- October 9: final candidate and code freeze.
- October 16: final qualification and acceptance validation complete.
- October 23: owner-operated release and handoff complete.
- October 30: operational closeout and sign-off.
- October 31: hard project end with no planned work.

### Required Final Outcomes

- Minimum owner-runnable release qualification.
- Stage A source-document currentness.
- Persistent-data lifecycle guidance and a controlled owner rehearsal.
- Minimum repository, requirements/design, task, records, and navigation
  governance.
- Receiving-owner ability to qualify, reject, recover, release, support, and
  disposition backlog work without outgoing-developer dependency.

## 4. Repository-Verified Findings

The material technical and documentation findings in the Reviewer/Planner
documents are supported by the repository at the reviewed commit.

### 4.1 Local-Only Runtime Boundary

[`compose.yaml`](../../../../compose.yaml) publishes
`${TOWERSCOUT_PORT:-5000}:5000` without an explicit loopback host address.
Waitress listens on `0.0.0.0` inside the container. Actual reachability still
depends on the runtime, Windows Firewall, endpoint policy, and host network.

This supports a bounded live investigation. It does not prove an incident or
that a pilot workstation was remotely reachable.

### 4.2 Active Custom-Image Cleanup Workflow

[`webapp/js/src/towerscout.js`](../../../../webapp/js/src/towerscout.js):

- posts the selected image to `/getobjectscustom`
- constructs the display URL from the original browser-side `image.name`
- calls `removeCustomImage(url)` after image load
- sends `GET /rm/uploads/<name>` for cleanup

[`webapp/ts_validation.py`](../../../../webapp/ts_validation.py) sanitizes the
uploaded filename, while [`webapp/towerscout.py`](../../../../webapp/towerscout.py)
deletes `UPLOAD_DIR / path` through the cleanup route.

The proposed investigation should therefore cover both security and functional
correctness:

- method and request-forgery behavior
- canonical server-side identifier handling
- resolved-path containment
- encoded and malformed paths
- filename normalization differences
- cleanup timing, idempotency, and error behavior
- the complete upload, display, detection, and cleanup journey

The route is active and cannot simply be removed without preserving the user
workflow.

### 4.3 SBOM Limitation

[`SBOM.txt`](../../../../SBOM.txt) is explicitly a reference document, not a
generated release-specific SBOM. The roadmap is correct not to rebuild
`v0.1.2` solely to retrofit one. The absence of a generated release-specific
SBOM should remain a documented owner-acceptance limitation if the exact
historical release is adopted.

### 4.4 Requirements And Design Drift

[`requirements.md`](../../../requirements.md) still describes the current
state as a student prototype requiring technical setup and retains conflicting
or outdated target requirements. [`design.md`](../../../design.md) still
describes implemented setup/configuration work as future design, carries old
security conclusions, and contains pseudo-architecture that does not match the
current application.

Minimum applicability or supersession treatment is required for safe handoff.
A full rewrite should not be implied unless it is separately selected and
estimated.

### 4.5 Qualification Fixture Dependency

The current
[`v0.1.2 validation reproduction guide`](./v0.1.2-Validation-Evidence/V012-Validation-Methodology-and-Reproduction-Guide.md)
depends on `ts-detect-harness.ps1` and twelve frozen fixtures copied from an
external RC7.1 QA archive. Those inputs are not normal tracked repository
files.

This creates a hidden custody dependency that proposed `TASK-091` must close
before the process can be described as owner-runnable.

## 5. Required Corrections Before Formal Approval

### 5.1 Define What Roadmap Approval Authorizes

The candidate says that approval does not select or authorize implementation,
but Phase 2 begins July 23 and expects immediate work on several items.

The formal approval record should separately state whether it authorizes:

- proposed `TASK-090` investigation
- `TASK-089` preparation-only packet work
- the `TASK-076` draft and owner decision list
- `TASK-068` scoping and estimation
- the minimum `TASK-091` specification
- creation of backlog entries for proposed `TASK-091` through `TASK-095`

No work should be partially performed against backlog tasks without a visible
tracking decision. The approved transition should update
[`current-tasks.md`](../../../current-tasks.md),
[`task-backlog.md`](../../../task-backlog.md), and the applicable task files
before implementation begins.

If `TASK-089` packet preparation is authorized, its status should distinguish
the two states clearly, for example:

> **IN PROGRESS - PREPARATION ONLY; CDC-AI MIGRATION EXECUTION REMAINS
> OWNER-GATED**

If formal approval occurs after the planned Phase 2 start, the August 7 work
should be re-estimated instead of silently compressed.

### 5.2 Correct The Stage A Selection Deadline

The roadmap requires proposed `TASK-092` Stage A documentation corrections by
August 21, while the supplemental analysis permits its owner and delivery path
to remain unsettled until August 28. That sequence conflicts with the stated
task-selection rules.

Recommended correction:

- assign the `TASK-091` specification owner at roadmap approval
- select and authorize `TASK-092` Stage A no later than August 7
- preserve August 28 for the larger Stage B decision and remaining final
  delivery-path decisions

### 5.3 Add A Pilot-Feedback Cutoff And Late-Feedback Rule

Pending feedback should not block roadmap approval, but the roadmap needs a
rule for when feedback can still change the candidate baseline.

Recommended rule:

1. Record the actionable feedback considered in the August 28 adoption
   decision.
2. After August 28, allow only blocker, security, or data-integrity feedback to
   reopen the selected baseline.
3. Send non-blocking late feedback to the durable owner backlog.
4. After September 25, apply the feature-complete cutoff.
5. After October 9, apply the blocker-only freeze rule.

The repository should record only the sanitized actionable disposition, not a
duplicate of the project lead's feedback intake.

### 5.4 Correct The "Only Five Decisions" Statement

The five decisions listed in the open register are important, but they are not
the only open material decisions. The roadmap also schedules:

- adopt, fix-before-adopt, or defer
- forward repository of record
- optional-lane selection
- delivery paths for required outcomes
- any remediation arising from `TASK-090`

Either add these decisions to the register or rename the section to something
narrower, such as:

> **Roadmap-Governance Decisions Requiring Owner Input**

The roadmap can then list future scheduled execution decisions separately.

### 5.5 Make Qualification Inputs Durable And Owner-Accessible

Proposed `TASK-091` should explicitly require:

- a durable, approved location for `ts-detect-harness.ps1` and the frozen
  fixtures
- access for the `cdcai` owner or designated release operator
- fixture hashes and expected per-tile results
- sensitivity, provenance, and reuse-right review
- a runbook that does not depend on outgoing-developer workstation state
- a failure path when the fixture or harness identity cannot be verified

Without these requirements, the proposed process remains dependent on an
external QA archive even if its commands are documented.

### 5.6 Make The Decommission Rehearsal Explicitly Non-Destructive

Proposed `TASK-093` should require destructive steps to use one of the
following:

- disposable test volumes and test data
- a dry run
- a tabletop walkthrough

No rehearsal should delete pilot, production, owner, or support data unless a
separately reviewed and authorized procedure explicitly permits it.

### 5.7 Put The Three Final-Baseline Scenarios In The Operational Roadmap

The supplemental analysis explains these scenarios, but they are important
enough to appear in the shorter operational roadmap:

| Outcome | Required handling |
| --- | --- |
| Adopt exact `v0.1.2` | Do not rebuild; reuse existing release evidence, perform required cdcai migration/recreation verification, document the generated-SBOM limitation, and obtain owner acceptance. |
| Adopt a corrected successor | Use a new version identity and repeat every affected source, image, package, provider, runtime, and workflow qualification cell. |
| Defer adoption | Leave cdcai unchanged and deliver the migration-ready fork-side handoff, durable backlog, evidence custody, and explicit defer record. |

This decision branch must not require a future operator to consult the
supplemental analysis before acting.

### 5.8 Clarify Release Authority And Qualification Exceptions

Define `release owner` according to the repository of record:

- fork release: project lead as `J-Schulein/TowerScout` owner
- cdcai release: `cdcai` owner or the owner's named release operator

A mandatory `SKIPPED` or `INCOMPLETE` cell should remain visibly skipped or
incomplete. Acceptance should require a separate waiver or accepted-risk
record containing:

- the affected cell and candidate identity
- technical consequence
- mitigation and follow-up
- accepting owner, date, and scope
- any additional organizational approval required

The exception must not silently convert an incomplete result into a pass.

### 5.9 Make The Candidate Roadmap The Single Current Roadmap

After the corrections are accepted, use the candidate operational roadmap
itself as the approved current roadmap. Do not revise the older comprehensive
draft into a second competing roadmap.

At formal approval time:

1. place the corrected operational roadmap in `Handoff-Planning`
2. record approval metadata and the approved repository commit
3. make it the first current roadmap source in this folder's navigation
4. retain the supplemental analysis as supporting review evidence
5. mark the original draft and developer responses as superseded review
   evidence
6. update current task and backlog state in the same planning transition

This source-of-truth correction should happen when the roadmap is approved,
not be deferred until end-of-project cleanup under proposed `TASK-095`.
`TASK-095` can then maintain that clarity through final handoff.

## 6. Assessment Of Estimates And Capacity

The planning estimates are generally reasonable if their boundaries remain
explicit.

| Work | Assessment |
| --- | --- |
| Proposed `TASK-090` investigation: 1-3 days | Reasonable for investigation and classification only. Remediation, package validation, and a pilot patch are excluded. |
| Proposed `TASK-091` minimum: 3-6 days | Plausible after the specification and fixture/harness custody are resolved. Re-estimate if a new harness or sanitized fixture set must be created. |
| Proposed `TASK-092` Stage A: 1-2 days | Plausible for currentness and applicability corrections without rebuilding a package or performing the larger information-architecture redesign. |
| Proposed `TASK-093` minimum: 1-2 days | Plausible for documentation and safe rehearsal preparation; tooling remains excluded. |
| Proposed `TASK-095` minimum: 2-4 distributed days | Plausible for applicability labeling, navigation, inventories, task disposition, and owner readability. It is not enough for a complete rewrite of requirements/design or broad repository reorganization. |

The optional major lane should remain uncommitted until the August 28 capacity
review. Required closeout work, any security remediation, external validation,
and owner rehearsal time should be reserved before an optional lane is
selected.

## 7. Recommended Formal Approval Structure

The approval record should distinguish framework approval from work
authorization.

Suggested structure:

```text
Roadmap recommendation: Approve with incorporated changes
Roadmap effective date: [date]
Approved repository commit: [SHA]

TASK-090 bounded investigation: Authorized / Not authorized / Deferred
TASK-089 preparation-only work: Authorized / Not authorized
Phase 2 planning deliverables: Authorized / Revised / Deferred

No cdcai mutation authorized by roadmap approval.
No v0.1.2 asset change authorized.
No remediation authorized until separately estimated and approved.

Project lead acknowledgment: [name/date]
cdcai owner acknowledgment: [name/date]
Reviewer/Planner recommendation: [name/date]
```

This keeps the roadmap approval auditable without treating it as permission
for every candidate task.

## 8. Remaining Owner Decisions

The following decisions remain appropriately assigned to the project lead and
`cdcai` owner:

1. whether proposed `TASK-090` is authorized
2. whether the `cdcai` owner will personally perform release rehearsals or
   designate an operator
3. the durable backlog destination
4. applicable external organizational milestones and authorities
5. the mandatory final qualification cells
6. the August 28 adopt, fix-before-adopt, or defer outcome and forward
   repository
7. whether any optional major lane is selected after required capacity is
   reserved

Pending pilot feedback is a planned input. It is not itself a reason to delay
framework approval, provided the final roadmap includes the feedback cutoff
and late-feedback rules in Section 5.3.

## 9. Requested Reviewer/Planner Follow-Up

Please prepare the next roadmap iteration by:

1. defining the Phase 2 authorization transition
2. correcting the `TASK-091` and `TASK-092` selection deadlines
3. adding the pilot-feedback cutoff and late-feedback rule
4. correcting or renaming the five-decision register
5. adding qualification harness and fixture custody requirements
6. making decommission rehearsal explicitly non-destructive
7. promoting the three final-baseline scenarios into the operational roadmap
8. clarifying release authority and qualification exception records
9. specifying that the corrected candidate becomes the single current roadmap
10. returning a final candidate with explicit approval and authorization fields

No additional comprehensive roadmap rewrite is recommended. These targeted
changes should be sufficient to produce the approval-ready plan.

## 10. Current Repository Sources

- `2026-07-22-OCTOBER-PROJECT-ROADMAP-REVIEW-DRAFT.md`
- `2026-07-22-DEVELOPER-RESPONSE-TO-COMPREHENSIVE-ROADMAP-REVIEW.md`
- `2026-07-22-DEVELOPER-RESPONSE-TO-UPDATED-COMPREHENSIVE-ROADMAP-REVIEW.md`
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
- [`SBOM.txt`](../../../../SBOM.txt)
- [`webapp/towerscout.py`](../../../../webapp/towerscout.py)
- [`webapp/ts_validation.py`](../../../../webapp/ts_validation.py)
- [`webapp/js/src/towerscout.js`](../../../../webapp/js/src/towerscout.js)
- [`v0.1.2 validation reproduction guide`](./v0.1.2-Validation-Evidence/V012-Validation-Methodology-and-Reproduction-Guide.md)

---

**End of developer feedback.**
