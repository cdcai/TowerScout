# TowerScout Windows Deployment Prioritization — Version 2

**Date:** September 21, 2026. **Baseline:** `9276084d91807906c53e00060670692b27e38483` in `J-Schulein/TowerScout`.

**Execution plan:** [Version 2 work breakdown](2026-09-21-windows-deployment-hardening-v2.md). **Review evidence:** [Static verification record](2026-09-21-windows-deployment-hardening-v2-verification.md).

**Amended by ADR-022 (2026-09-24):** The selected ML candidate is now
torch 2.10.0 / torchvision 0.25.0 with distinct `cpu` and `cuda128` artifacts.
ADR-022 supersedes this document's CUDA 12.6/torch 2.6.0 ML baseline only;
all package, device, provider, persistence, recovery, and independent-host
acceptance requirements remain in force.

**Version rule:** This pair supersedes the September 21 unversioned analysis/plan for the proposed deadline effort. Preserve those originals as history; do not execute their larger task list in addition to this one. Repository handoff files and skills still need the targeted alignment described in W00. Writing this revision does not change application behavior, task status, branches, PRs, or runtime state.

## 1. Decision and intended outcome

Use the existing PowerShell/Compose distribution path from an accepted `main` revision. Stop PR #67 implementation, reconciliation, and repeated review during this delivery window. Preserve its evidence and recommend closing it unmerged through the applicable authorization. It is not a prerequisite for starting, testing, or releasing this work. No automatic launcher resumption is scheduled.

The required outcome remains a downloadable Windows 11 AMD64 application that runs real inference on CPU and NVIDIA GPU through both Docker and Podman, with successful independent-machine reproduction. Scope reduction applies to implementation machinery and optional improvements, not to reporting untested profiles as supported.

**Main improvement over version 1: install and exercise an early package on Day 1, reuse existing qualification tools, and select only bounded fixes needed for the acceptance outcome.** Keep the final two days for independent reproduction and recovery. Do not wait until every hardening idea has been implemented before trying the download/setup path.

Seven days is a delivery target, not a verified duration. Machine access, approved execution policy, assets, provider accounts, build time, and actual regression results determine feasibility. W01 creates an explicit go/at-risk/blocked forecast on Day 1 and refreshes it on Day 3. A missed gate changes the forecast or final claim; it does not silently relax acceptance.

## 2. Non-negotiable acceptance

| Profile | Evidence required |
| --- | --- |
| Docker CPU | CPU image; actual YOLO and EfficientNet work on CPU; complete application workflow. |
| Docker NVIDIA | CUDA 12.6 image; both models actually work on CUDA; no CPU fallback. |
| Podman CPU | Approved Compose provider and intended machine/connection; actual YOLO and EfficientNet work on CPU. |
| Podman NVIDIA | Intended WSL2 machine, approved provider, NVIDIA CDI, both models on CUDA. |

For each row, repeat the downloaded workflow on an independent suitable Windows computer. A practical allocation is one CPU-only machine plus two different NVIDIA machines: repeat CPU profiles on the CPU-only host and one GPU host in explicit CPU mode; repeat GPU profiles on both GPU hosts. Include a Podman environment without Docker Desktop. These machines and organizational access have not been confirmed by this document.

Every qualified row must demonstrate download/checksums, ordinary-account extraction including a path with spaces, setup/import, real model execution, Google and Azure workflow checks, review/export, cancellation/error recovery, a successful next request, and persistence across stop/relaunch and reboot. Shared-script failure scenarios may be exhaustively injected once per relevant engine and smoke-checked in the remaining profiles; do not repeat every artificial fault eight times without a reason.

Preserve the eight named volumes, loopback binding, model hashes/trusted loading, TLS verification, provider-key redaction, model weights, thresholds, NMS, geometry, export semantics, 100 retained-tile package cap, and 50 MiB request-body limit. Keep `v0.1.2` immutable and cdcai adoption owner-gated. The selected baseline uses torch 2.6.0 / torchvision 0.21.0; do not introduce an ML/dependency migration as a shortcut.

The existing Podman provider installer needs Python. Document and test that runtime prerequisite; end users should not need an application source checkout, Git, Node, or a development environment. Do not add a new standalone provider distribution this week.

## 3. What changes from version 1

| Version 1 direction | Version 2 decision |
| --- | --- |
| Many broad tasks all labelled P0 | Small required corrections; conditional fixes driven by early acceptance; an explicit deferred list. |
| Final package first exercised around Day 4 | Day-1 baseline package; corrected rehearsal by Day 3; frozen candidate by Day 4 if evidence permits. |
| New in-image self-test CLI, fixtures, and report framework | Extend the existing external qualification probe and reuse the July harness/fixtures with corrected assertions. No new shipped model-test API/module. |
| New generic process library | Repair the existing bounded adapters and their callers; retain exact arguments, deadlines, and CMD-provider support. |
| Runtime profile propagated through ten scripts before qualification | Use explicit profile flags and existing configuration first. Bind/check the selected target; add persistence only for an observed lifecycle gap, without a new discovery framework. |
| Full cancellation/state-machine redesign | Minimal whole-job admission plus acceptance tests; repair reproduced cancellation/data-coherence failures narrowly. Defer broad restructuring. |
| Broad CI expansion before release work | Required Windows/ZIP/image verification first; add a small Windows CI job if it fits, without making unrelated legacy suites blocking. |
| Three integration reviewer checkpoints | Two consolidated reviews: corrected candidate before freeze, final evidence before publication. Risky changes can still receive an immediate focused review. |
| Large housekeeping pass | Day-1 instruction corrections and preservation inventory; physical cleanup and historical reorganization remain optional. |

## 4. Required, conditional, and deferred work

### Required corrections and proof

1. **Align agent direction and prerequisites (W00-W01).** Remove active PR #67 merge/resume gates; correct misleading skills; establish machines, assets, fixture provenance, policy, candidate identity, and baseline results.
2. **Remove dormant helper dependencies (W02).** Normal launch/stop must not import/write helper state when that path is disabled.
3. **Bound runtime commands and target the right installation (W03).** Correct ignored deadlines, output-drain stalls, unbounded engine/provider probes, and ambiguous Podman mutation. A target mismatch stops mutation, not just emits a warning.
4. **Preserve TLS state and truthful exit status (W04).** Scalar child status, unique candidate bundle, verify before configuration promotion, atomic update, prior trust retained, minimal concurrent-repair exclusion.
5. **Reuse qualification tooling honestly (W05).** Required-device execution, positive real EN work, output comparisons, artifact identity, and failure exit status. Keep ordinary health lightweight.
6. **Fix bounded application defects (W06-W08).** Propagate required-classifier failure; reject oversized candidate grids and decoded images early; isolate rate-limit budgets; guard overlapping detection work; correct Google first-use bounds and rebuild its bundle.
7. **Qualify exact artifacts and hand them over (W09-W10).** Real ZIPs/images, required Windows checks, independent reproduction, recovery, final documentation, and accurate release status.

### Conditional work: add only when evidence requires it

- Saved engine/GPU/port convenience beyond the explicit supported commands, if fresh-shell testing exposes an otherwise unmanageable selection problem.
- Targeted late-cancellation/session cleanup and provider deadline fixes when fault tests fail. Such a failure can block release; the broader redesign remains deferred.
- A blocking Windows CI job if available without delaying actual Windows verification.
- Resource/batch tuning only after a measured problem on the smallest supported host; rerun correctness afterward.
- Signing-stage support when the claimed deployment environment actually requires signing. Establish that dependency on Day 1; required signing cannot be waived to meet the date.

### Defer

PR #67/framework reuse; a new launcher or browser Exit helper; new runtime discovery/PE/Authenticode infrastructure; native recovery journals; new in-image self-test product surfaces; comprehensive cancellation/queue architecture; dependency/model/precision migrations; new provider packaging; throughput optimization without evidence; general formatting, skill-system redesign, branch deletion, and bulk archival.

## 5. Correct reuse of existing evidence

The local `v012-validation/harness/ts-detect-harness.ps1` and July fixture packet are useful starting points. They are outside the Git root and must be inventoried, hashed, checked for permitted use, and transferred deliberately to authorized test systems.

Their historical 53-detection parity exercises `/getobjectscustom`. On current main, that route invokes YOLO without the secondary classifier. The harness also geocodes before its `SkipLive` condition, records readiness device selection instead of proving every model's actual work, and catches live-provider errors without necessarily failing its process. Reusing it unchanged would overstate the evidence.

Extend `scripts/task098_ml_qualification.py` with an optional fixed-fixture combined-flow mode, preserving its existing synthetic mode. Use real production loaders and `detector.detect(tiles, events, run_id, crop_tiles=False, secondary=classifier, perf_metrics=metrics)` outside pytest mocking. Run it externally against the exact candidate image and imported assets. Require positive secondary candidates/batches and actual devices; preserve the original fixture parity as a separate YOLO-only comparison. Do not change the custom-image product route merely to make the test exercise EN.

The existing Task-098 PowerShell wrapper builds a Docker image from source and mounts developer model files. It cannot certify downloaded packages unchanged. W05 specifies the small replacement invocation and its boundaries. A separate probe process does not prove the app process loaded its models; retain the real live map workflow in final acceptance.

Baseline and candidate comparisons use the same frozen fixture bytes, models, host allocation, and settings. Record declared output tolerances before candidate results. Use one warm-up and three measured warm runs, with synchronized CUDA timing. Investigate more than 10% warmed-median degradation and memory/timeout problems separately. Do not turn the historical count 53 into the expected combined-model count or require invariant live-provider detections.

## 6. Instructions and skills are part of the critical path

The audit found active PR #67 directions in handoff, task tracking, and repeated sections of `.github/copilot-instructions.md`; nonexistent paths and unsupported commands in skills; a blanket per-task approval instruction; source-build commands presented as release checks; and unconditional Compose cleanup that can target unowned state.

W00 provides a file-by-file correction matrix. Preserve the useful skill routing rule: choose one primary skill, adding focused secondary checks only when relevant. Correct stale references and scope commands; do not run every skill, rewrite global plugin caches, or remove safeguards. No root `AGENTS.md` was found; a short proposed pointer file makes the current direction discoverable without duplicating the entire guide.

The new documents alone cannot prevent future agents following old entrypoints. Complete the small direction patch first, then move into baseline testing. The current task board remains the assignment source; this v2 pair holds requirements and execution detail; the decision record explains the change; historical evidence remains historical.

## 7. Daily actions, results, and preparation

| Day | Actions | Expected result or honest checkpoint | Prepare for next day |
| --- | --- | --- | --- |
| 1 | W00 direction/skill patch; W01 machine/policy/asset inventory; attempt baseline package setup immediately; begin W05 fixture/probe reuse. | One active direction, named external blockers, observed setup failures, baseline artifact identities. No readiness claim yet. | Freeze required fix list, assign owners, reserve all host sessions, prepare isolated regression fixtures. |
| 2 | W02/W04/W06/W08 small fixes; W03 bounded adapters and targeting; fix rate-limit coupling. Start real combined-fixture execution as soon as possible. | Focused regressions pass; first-use/model/TLS errors are understood; prototype qualification works or its blocker is explicit. | Select only remaining acceptance blockers; prepare corrected Windows package rehearsal. |
| 3 | Finish W03/W05/W07; test corrected setup on Docker and Podman; exercise cancellation, recovery, and export; first consolidated review. | A corrected rehearsal package and go/at-risk/blocked forecast. Failures have owners and bounded remedies. | Freeze scope; queue final image builds, signing if required, and package verification. |
| 4 | W09 integrate accepted fixes, freeze source, build CPU/CUDA images, create/verify real archives, run required Windows checks and baseline comparisons. | Candidate inventory binds exact source, images, ZIPs, assets, fixtures, and tooling; no unreviewed product changes. | Distribute exact candidate bytes to independent testers; restore fresh test targets. |
| 5 | W10 required profiles and independent-host repetition; Google/Azure workflows; first-use and actual-model evidence. | Completed matrix cells reference downloaded hashes; remaining failures are explicit. | Reserve time for affected reruns, reboot/persistence and managed-network tests. |
| 6 | Complete repetition, persistence, TLS/recovery and interruption checks; fix only release blockers with a new candidate identity when bytes change. | Mandatory cells pass or named blockers prevent release; support/rollback instructions are exercised. | Assemble final evidence and inventory; independent tester reviews instructions. |
| 7 | Second consolidated review; reconcile final hashes and limitations; complete handoff; publish only under applicable authorization. | Deployment-ready only if every required gate passes; otherwise deliver the exact qualified subset and remaining blockers. | Preserve rollback/evidence custody and a clearly deferred backlog. |

This sequence assumes implementation and testing can overlap when people/machines are available. It does not assume parallel agents or unlimited working hours. If one implementer cannot finish the bounded corrections by Day 3, revise the delivery forecast rather than compress independent testing into a token final check.

## 8. Verification boundary

This revision is grounded in source and instruction/skill inspection at the stated commit and the external feedback supplied by the user. Its companion verification record describes the static checks actually performed. Planning review can establish coherent instructions and known dependencies; only execution can establish model results, target-machine compatibility, timing, and delivery readiness.

The final claim must name tested profiles/hosts and artifact hashes. Missing hardware, keys, approved certificate handling, signing access, or provider availability are external blockers with owners. They are not completed tests. A smaller successful result remains useful but does not replace the user's four-profile independent-reproduction objective.
