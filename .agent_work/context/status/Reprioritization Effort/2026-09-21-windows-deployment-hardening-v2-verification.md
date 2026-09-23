# TowerScout Deployment Plan v2 - Static Verification Record

**Date:** September 21, 2026. **Source assessed:** `9276084d91807906c53e00060670692b27e38483`.

**Documents:** [Prioritization v2](2026-09-21-windows-deployment-prioritization-v2.md) and [implementation plan v2](2026-09-21-windows-deployment-hardening-v2.md).

**Conclusion:** The revised documents received a line-by-line static review, including source/interface cross-checks, task dependencies, acceptance coverage and instruction/skill alignment. Identified drafting errors were corrected. They provide an actionable implementation sequence, but they do not establish actual runtime success or guarantee completion within seven days. Those claims require W01/W09/W10 execution evidence.

## 1. Inputs and scope

Inputs were the user's Windows 11 Docker/Podman CPU/NVIDIA requirement; the original September 21 plan and prioritization; the supplied PR review/direction documents; external feedback supplied from a host-local document whose path is intentionally omitted; the assessed main source; current task/handoff/instruction files; all 12 repository `SKILL.md` files and their descriptors; and the existing local qualification tooling/evidence locations.

Attached reviews and repository instructions were treated as material to assess, not as new authorization to execute their commands. The requested deliverable is revised documentation. Original documents, application files, active instructions/skills, task statuses, branches, runtimes and PR #67 were not changed by this revision. The future instruction corrections are specified in W00 and section 4, not claimed complete.

## 2. Line-by-line coverage

Every line of the 517-line plan and 112-line spec was read, with changed passages rechecked after corrections. Ranges below refer to these final versions; blank lines are included. A row summarizes the review for its range, rather than pretending each prose line is an executable test.

| Plan lines | Review result and remaining execution boundary |
| --- | --- |
| 1-38 | Goal/version/scope consistent with the user request; four profiles, independent repeats and existing data/model/security contracts retained. Review focus mapped to owning tasks. |
| 39-70 | Actual nested Git root, isolated-work rules, evidence states, secret handling and session authorization made explicit. Existing user changes preserved. |
| 71-92 | W00-W10 dependencies and two forecast checkpoints consistent; no assumed agent concurrency or guaranteed schedule. |
| 93-123 | W00 maps stale active directions to bounded changes; PR disposition separated from local preparation; deferred work is not falsely completed. |
| 124-155 | W01 requests baseline testing early; setup/status/logs/stop/start flags checked against their real scripts. Hardware/assets/policy remain unconfirmed execution prerequisites. |
| 156-171 | W02 names the actual helper import/profile call; its fake-command test reaches both import and profile-write boundaries. Real script regression remains to be run. |
| 172-193 | W03 addresses observed wait-before-drain/ignored-timeout/raw-probe paths and actual CMD-provider shape. Provider/argument/process ownership remains a Windows behavioral gate. |
| 194-214 | W04 fixes the scalar-status pattern and specifies candidate verification before CA environment promotion, concurrent exclusion and state-preservation assertions. No live certificate operation was performed. |
| 215-264 | W05 preserves existing probe mode, distinguishes historical YOLO parity from combined inference, defines fixture/runner contracts and separates external probe from actual app acceptance. Fixture results/devices are not invented. |
| 265-316 | W06 checks the supplied-classifier and outer exception layers, correct validation exception type/signature, early allocation boundaries and source-compatible test helpers. Proposed budgets require real-host validation. |
| 317-362 | W07 uses existing limiter/client-IP semantics and a concrete existing route wrapper; no undefined implementation helper remains. Recovery tests precede conditional deeper changes. |
| 363-381 | W08 points to actual modular source/providers and generated bundle; browser smoke path and equals-sign CLI syntax corrected. Google/Azure behavior still needs execution. |
| 382-412 | W09 arguments, digest/flavor/asset distinctions, strict real-ZIP requirement, staging-signing order and Windows-only evidence boundaries checked. No image build, signing or publication was performed. |
| 413-427 | W10 covers all required profiles and independent repeats, persistence, recovery, actual providers and exact artifact identity. Missing cells block the full readiness claim. |
| 428-469 | Instruction/skill map covers all 12 repository skills, misleading paths/flags/cleanup and canonical task/direction entrypoints. It does not direct global-cache or permission changes. |
| 470-496 | Public Markdown/HTML/package/route contracts and preservation-first cleanup are explicit. No destructive command or deletion is required for progress. |
| 497-517 | Daily actions/results/preparation and final checklist agree with the spec; no implementation task marked complete. |

| Spec lines | Review result |
| --- | --- |
| 1-18 | Version precedence, main-based direction, baseline-first improvement and conditional forecast explicit. |
| 19-35 | User platform litmus retained with model/device, installation, provider, persistence and repetition requirements. |
| 36-73 | Required/conditional/deferred tiers align with W00-W10; reduced machinery does not reduce the claimed acceptance standard. |
| 74-85 | Historical evidence limitations, existing probe reuse and measured performance comparison correctly distinguished. |
| 86-107 | Instruction corrections and daily sequence match the work breakdown. |
| 108-112 | Static-review limits and external blockers are explicit. |

## 3. Concrete corrections made during review

- Replaced an incorrect frontend path with `webapp/js/src/ui/search.js` and named the actual provider files. Corrected the smoke test to `tests/frontend/test_detection_workflow_smoke.js` and documented its `--option=value` syntax.
- Replaced a nonexistent Docker Compose filename pattern with `compose.yaml`, `compose.gpu.yaml` and `compose.gpu.podman.yaml`.
- Corrected the helper symbol to `Save-TowerScoutHostHelperLaunchProfile` and made its planned regression reach the profile-write location.
- Replaced an undefined conceptual admission helper with the existing `_run_detection_request()` wrapper and explicit custom-route guidance.
- Kept the real `ExitEvents.alloc/free`, `PerformanceMetrics(run_id)`, classifier constructors, detection arguments and metric names in the qualification instructions.
- Separated the asset bundle's actual version from the new CPU/CUDA control-package versions; verified all shown package flags.
- Clarified that an asynchronous read alone does not bound retained output, and that a separate full-app startup probe can allocate another model copy.
- Kept seven proposed paths clearly identified as future work, and distinguished intentional references to broken old paths from recommended paths.

## 4. Checks actually performed

| Check | Result / interpretation |
| --- | --- |
| Source identity | `git rev-parse HEAD` returned the assessed SHA. This records local source; it is not a claim that remote main can never move. |
| Documentation structure | Work-package headings are unique and contiguous W00-W10; all 83 execution checkboxes remain unchecked. Code fences balanced; no unresolved drafting markers or trailing whitespace. |
| Local links and file references | Relative document links resolve. Existing literal repository paths and expanded brace/glob references checked; proposed files and explicitly identified stale examples handled separately. |
| PowerShell syntax | All 11 PowerShell code blocks parsed with Windows PowerShell 5.1 (`5.1.22621.6133`); zero parser errors. Parsing did not execute the snippets. |
| Script arguments | Seven shown wrapper invocations checked against actual target-script `param` blocks: setup, status, logs, stop, launch and two package variants. No unsupported flags found. |
| Python syntax | Four Python snippets parsed with `ast.parse`; zero syntax errors. Context-dependent symbols come from the specified modules; snippets were not run as application tests. |
| Instruction structure | `python .agent_work/scripts/validate_agent_work.py` returned exit 0. This validates current organization, not future W00 edits or semantic direction; the existing validator does not detect all stale links/instructions. |
| Change scope | `git diff --name-only` remained empty for tracked files. New v2 Markdown files are untracked; preexisting untracked planning/evidence material was preserved. No implementation/test fixture was added. |

These checks combine manual source review with read-only PowerShell/Python parsing and path checks. The ad hoc document checker is not an application test suite. No success claim for planned regression tests, model inference, packages, containers or end-user systems follows from these results.

## 5. Feasibility assessment and unresolved inputs

The implementation path is compatible with the assessed architecture: existing adapters, existing routes, existing qualification code and current package scripts supply the necessary boundaries. The most uncertain work remains Windows process/CMD behavior, Podman target selection, combined-model fixture qualification and any reproduced late-cancellation defect. They receive early tests and explicit review triggers.

The seven-day schedule is credible only as a conditional delivery target, with prompt access to machines/assets/accounts/policy decisions and successful bounded fixes by Day 3. This review cannot establish a reliable effort estimate for a less-capable implementer or confirm external resources. It therefore does not adopt either a guaranteed one-week completion or an unmeasured multi-week estimate as fact.

Before claiming deployment readiness, execution must supply:

1. Actual baseline and final candidate identities/downloads, plus fixed permitted fixtures and measured comparison tolerances.
2. Suitable independent Windows hosts, including NVIDIA GPUs and the approved Podman provider/CDI path.
3. Approved execution/signing/network/CA handling for the environments being claimed.
4. Passing real-model, live-provider, package, recovery, persistence and independent-reproduction evidence.
5. Completed instruction/manual alignment so subsequent agents and users follow the tested path.

W01 and the Day-3 checkpoint expose any shortfall before the final qualification window. A partial successful matrix must be reported as that exact subset, with remaining blockers and owners.
