# Task Backlog - Main-Based Windows Delivery

**Last Updated**: October 21, 2026 (owner handoff preparation)
**Current Decision**: [ADR-021](./decisions/021-main-based-windows-deployment-deadline.md)
**ML Runtime Amendment**: [ADR-022](./decisions/022-cuda128-blackwell-ml-runtime.md)
**Windows Package Policy**: [ADR-023](./decisions/023-unsigned-windows-package-support-boundary.md)
**RC5 Security Boundary**: [ADR-024](./decisions/024-rc5-security-gate-and-residual-boundary.md)
**Candidate Acceptance**: [ADR-026](./decisions/026-rc5-bounded-candidate-acceptance.md)
**Immediate Plan**: [September 21 v2 implementation plan](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md)

The active board controls selected work. This backlog holds deferred,
conditional, and follow-on work. Task-087/096 launcher work is preserved but is
not a delivery prerequisite and has no automatic restart date. Task-087 PRs
#64/#67 are closed without merge; any restart begins from then-current `main`.

## Receiving-owner priorities

Chris accepted ongoing ownership after October 30. The outgoing lead owns
delivery preparation through closeout. The active board remains authoritative;
these groups organize the handoff rather than closing tasks.

| Priority | Owner / timing | Next action and completion condition |
| --- | --- | --- |
| Official delivery | Outgoing lead with Chris; target October 27 | Adopt reviewed source, pass official security/integrity/affected runtime checks, deliver wiki/video and owner packet, and record receipt. |
| Security follow-up (TASK-104) | Outgoing lead prepares; Chris maintains after closeout | Review the five exact residuals before October 31, 2026 23:59:59 UTC expiry; retain a documented fix or disposition before any publication relying on them. Never automatically renew. |
| ML bridge review (TASK-103) | Chris after closeout | Evaluate supported replacement and real-model/device regression evidence by January 31, 2027 or earlier ADR-022 trigger; record the decision. |
| Future improvements below | Chris selects | Prioritize a demonstrated user need, define a small acceptance condition, and open a fresh task before implementation. No automatic restart of deferred work. |

## Owner decision guide

These are planning estimates, not commitments from Chris or the separate model
team. Small means roughly 1-3 focused days, medium 1-2 weeks, and large multiple
weeks; unfamiliar environments, independent testing and review can add time.
Begin uncertain work with a bounded investigation, then estimate implementation.
The dated release/security obligations take precedence over optional work.

| Item | User problem and benefit | Priority / trigger | Effort and expertise | Dependencies and completion condition |
| --- | --- | --- | --- | --- |
| TASK-089 official delivery | Users need an owner-controlled, verified download and help location | Current delivery; target Oct 27 | Several focused days plus builds/host checks; release engineering with Chris's review | Reviewed source, permissions and security gates; complete official artifacts, guidance and confirmed receipt |
| TASK-104 security follow-up | Temporary exceptions must not silently become permanent | Before Oct 31 23:59:59 UTC; earlier fix/severity/exposure trigger | Small assessment; fix effort unknown until fresh scan; dependency/security expertise | Exact scan identities and policy; record tested correction or explicit bounded owner decision, otherwise hold affected publication |
| TASK-103 ML bridge review | Supported devices/dependencies must remain maintainable | By Jan 31, 2027 or earlier ADR-022 trigger | Small assessment; migration likely medium/large; ML/runtime expertise | Available supported stack and real-model/device evidence; documented decision and qualified replacement if selected |
| Future YOLO replacement | Evaluate whether new training/model improves detection | When Chris's separate development group supplies a candidate | Unknown until artifact review; ML evaluation plus application/runtime integration | Version/weights, provenance, permissions and evaluation set; meet the acceptance details below in a new scoped task |
| TASK-077 asset/import hardening | A demonstrated download or import failure prevents usable setup | Select only for a reproduced gap | Small/medium; packaging and integrity checks | Reproducible failure and asset contract; corrected import plus valid/invalid input regression evidence |
| TASK-027 error handling | A reproduced failure leaves users unable to recover or understand the next step | User-impacting issue outside existing selected tasks | Small/medium per defect; backend/frontend troubleshooting | Safe reproduction and owning component; clear error, recovery and successful next request |
| TASK-070 restricted-network support | Users at a confirmed target site cannot obtain prerequisites/assets | Only after site requirements and administrator support are known | Medium/large; deployment/network expertise | Approved distribution and update mechanism; end-to-end test in the named environment |
| TASK-094 support snapshot | Existing safe diagnostics cannot explain a real support case | Evidence-selected, not automatic telemetry | Small investigation, medium implementation; diagnostics/privacy expertise | Minimum necessary fields and redaction design; useful output verified to exclude credentials/private investigation data |
| TASK-026 CPU optimization | A measured bottleneck makes a supported workflow impractical | Only after representative timing and resource measurements | Medium investigation; ML/performance expertise | Repeatable baseline and correctness checks; measured improvement without output or memory regression |
| TASK-087 launcher / TASK-096 exit helper | Potential simpler startup/stop experience | Deferred; new owner-selected scope after delivery | Medium/large; Windows/runtime/frontend expertise | Preserve archived work; fresh branch from current main and explicit support scope; prove launch/stop/recovery without data loss |
| TASK-058 background jobs | Long work may justify a different execution model | Future architecture only after demonstrated need | Large; backend/concurrency expertise | Cancellation, admission and persistence design; tested recovery and state consistency |
| TASK-059 backend decomposition | Large modules can make safe maintenance harder | Future maintainability need | Large, staged; backend/testing expertise | Behavior baseline; small reviewed changes with unchanged external contracts |
| TASK-060 frontend modernization | Toolchain age may hinder builds and maintenance | Supported-tooling issue or owner-selected improvement | Medium/large; JavaScript/build expertise | Supported tool versions and module-order tests; reproducible generated bundle and browser checks |
| TASK-061 NumPy 2 migration | Dependency compatibility may eventually require migration | Separate dependency review; not this delivery | Medium/large; scientific Python/ML expertise | Compatible binary dependencies and models; real CPU/CUDA correctness and resource evidence |
| TASK-078 permissive runtime | A future distribution requirement may call for different licensing | Only after explicit product/licensing decision | Large; ML engineering and licensing review | Suitable replacement models/data and terms; reviewed notices and qualified behavior, not a label-only license change |
| TASK-029 provider fallback | Users may benefit from continuing after provider failure | Owner-selected need with provider-policy review | Medium/large; provider/state expertise | Credential, billing and failure semantics; tested transitions without stale state or unauthorized use |
| TASK-028 mobile UI | Smaller screens may make workflows difficult | Parking lot until target device/use case is chosen | Medium; UI/accessibility expertise | Supported workflow and viewport criteria; observed usability without desktop regression |

Known accepted findings remain in ADR-026 and TASK-105. Do not create duplicate
backlog entries or treat an accepted limitation as a verified correction.

## Future model replacement - owner-selected follow-on

The outgoing lead reports that a replacement YOLO model is being developed
with improved training data and possibly a newer YOLO version. This is future
work, not a current release gate or an accepted improvement claim.

- **Owner:** Chris selects and coordinates with the model-development owner.
- **Benefit to establish:** Better detection on representative imagery, with
  measured accuracy and acceptable runtime/resource use.
- **Trigger/dependencies:** Obtain the candidate model, version, weights,
  provenance, licensing/data permissions and evaluation evidence. Chris coordinates the separate development group. No repository or delivery
  timeframe exists yet; obtain artifacts and integration details when available.
- **Effort/expertise:** Estimate after inspecting the model; requires ML and
  application/runtime expertise. New YOLO versions may need more than a weights swap.
- **Completion:** Compare against current behavior on agreed evaluation data;
  verify preprocessing/output compatibility, CPU/CUDA execution, performance,
  packaging and notices; qualify a separately versioned release and preserve
  a return path to the prior model. Do not assume improved training data alone
  proves better field results.
- **Relationship to TASK-103:** Coordinate with the ML bridge review, but do
  not postpone its January 31, 2027 deadline or earlier triggers while waiting
  for a new model. Create a scoped implementation task when Chris selects it.

## Selected On The Active Board

| Task | Current outcome |
| --- | --- |
| `TASK-105` | Preserve accepted RC5 evidence; complete official adoption, changed-artifact qualification, and handoff under ADR-026 |
| `TASK-104` | Preserve merged security controls; run fresh official checks and record residual follow-up before expiry |
| `TASK-103` | Preserve accepted CPU/CUDA bridge evidence; qualify affected official runtime and hand off ADR-022 maintenance review |
| `TASK-095` | W00 direction, task-control, evidence, and eventual handoff alignment |
| `TASK-091` | W01/W05/W09/W10 owner-runnable package and model qualification |
| `TASK-097` | Podman CPU/GPU target, provider, CDI, and independent-host qualification |
| `TASK-092` | Frozen/merged content; validate packaged, running-image, Wiki, and exact-artifact documentation surfaces |
| `TASK-093` | Persistence, cancellation/error recovery, reboot, rollback, and repeated-run evidence |

Tasks 068, 099, and 101 are completed and moved to the completed-task record.
Task-101's former PR #67 integration gate is superseded, not passed.
RC9 independent-host findings remain owned by TASK-105 and must not be
duplicated as generic backlog work. Their current dispositions come from
ADR-026 and the RC5 closeout: tested correction, verified no-change decision,
or explicitly accepted limitation. Preserve each disposition; do not silently
drop a finding or reopen it solely from an older status snapshot.


## Guidance Completed Through Task-092

`TASK-076` provider-key exposure and restriction guidance is incorporated in
the frozen documentation merged through PR #94. The manuals explain credential
ownership, browser visibility, API scoping, quotas/monitoring/rotation, and the
current Google one-key application-restriction limitation. No separate code
task is selected unless final package testing reveals a new ambiguity.

## Required Or Evidence-Selected Follow-On Work

| Priority | Task | Status | Entry criterion / required outcome |
| ---: | --- | --- | --- |
| 1 | `TASK-077` Public Release Manifest And Asset Import Hardening | EVIDENCE_SELECTED | Select only for a demonstrated manifest/import/integrity gap in W01/W09 |
| 2 | `TASK-027` Enhanced Error Handling | CONDITIONAL | Select only a reproduced user-facing release blocker not owned by W02-W08 |
| 3 | `TASK-070` Restricted-Network Package Enhancements | CONDITIONAL | Select only if the claimed deployment environment requires offline/restricted distribution |
| 4 | `TASK-094` Evidence-Gated Support Snapshot | EVIDENCE_GATED | Add only if current sanitized status/log procedures cannot resolve real support cases |
| 5 | `TASK-026` CPU Optimization | CONDITIONAL | Select only for a measured supported-host bottleneck; preserve outputs and memory limits |

## Explicitly Deferred Beyond The Delivery Window

| Task | Disposition |
| --- | --- |
| `TASK-087` / PRs #64/#67 | Archived and closed without merge. Preserve the tagged history and [final disposition](./context/archive/2026-09/TASK-087-PR64-PR67-FINAL-DISPOSITION-2026-09-24.md); any future reconsideration requires an owner-selected task and a fresh branch from current `main`. |
| `TASK-096` User-Initiated Exit And Container Stop | Preserve for a future owner decision. Use the tested command-based lifecycle now. |
| `TASK-058` Background Detection Jobs | Future architecture; current work permits only minimal whole-job admission and reproduced recovery fixes. |
| `TASK-059` Backend Layer Decomposition | Future architecture; not a one-week release gate. |
| `TASK-060` Frontend Build Modernization | Maintenance after release unless the current build itself blocks acceptance. |
| `TASK-061` Coordinated NumPy 2 Migration | Future dependency track; no dependency/model migration this week. |
| `TASK-078` Permissive Apache-Only Runtime Migration | Future release track. |
| `TASK-029` Multi-Provider Fallback | Future product work after provider policy/error behavior is stable. |
| `TASK-028` Mobile Responsiveness | Parking lot. |

Also deferred: a new launcher, browser Exit helper, generic native-process
framework, new runtime-discovery or recovery-journal architecture, new in-image
self-test product surfaces, provider repackaging, speculative throughput work,
and bulk historical cleanup.

## Owner-Gated Work

| Task | Boundary |
| --- | --- |
| `TASK-089` cdcai Adoption And Ownership Transfer | Ownership, access, direction and name agreed October 20; preparation active. Reviewed source adoption, package permissions, official qualification, publication and receipt remain. |

## Post-Day-7 Planning

Use the [suggested post-Day-7 guide](./context/status/Reprioritization%20Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md)
only after reconciling actual W00-W10 results. Finish unpassed deployment,
data-integrity, and security gates before optional backlog work. Maintain one
canonical active board and preserve task-ID history.
