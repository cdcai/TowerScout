# TowerScout Windows Deployment Hardening Implementation Plan - Version 2

> **For agentic workers:** Use `superpowers:executing-plans` for sequential implementation when available. Use `superpowers:subagent-driven-development` only when the execution session authorizes that method. If neither skill is available, follow section 1. Steps use unchecked boxes because this is a plan, not an execution report.

**Goal:** Deliver a new main-based download that reproduces successful Windows 11 Docker/Podman CPU/NVIDIA operation on independent suitable computers, without merging PR #67.

**Architecture:** Retain the existing PowerShell/Compose package and single-process Flask/Waitress application. Correct specific deployment and application defects; reuse the existing external model probe and HTTP harness. Test an early package before completing all fixes, then qualify immutable candidate bytes.

**Tech stack:** Windows PowerShell 5.1 and CMD wrappers; Docker Desktop/WSL2; Podman/WSL2 with an approved Compose provider and NVIDIA CDI; Python, Flask/Waitress, PyTorch/torchvision, Pillow, aiohttp, pytest; JavaScript and Node/Puppeteer for development checks.

**Spec:** [Version 2 prioritization](2026-09-21-windows-deployment-prioritization-v2.md). **Static review:** [Verification record](2026-09-21-windows-deployment-hardening-v2-verification.md).

**Amended by ADR-022 (2026-09-24):** Task-103 owns the selected
torch 2.10.0 / torchvision 0.25.0 and `cuda128` migration. ADR-022 supersedes
the CUDA 12.6/torch 2.6.0 no-migration constraint below, but it does not relax
the four-profile, real-model, provider, recovery, or independent-host gates.

**Assessed baseline:** `9276084d91807906c53e00060670692b27e38483`, September 21, 2026. Main may subsequently move; select and record the execution baseline once. Reassess changed files before adopting a newer revision.

**Version/status:** This document and the v2 spec supersede the unversioned September 21 pair for the proposed deadline effort. Preserve the originals as history. This request authorizes documentation; it does not execute cleanup, change task status, close PRs, or deploy software. After implementation is authorized, continue within that scope without redundant per-task permission requests.

## Global constraints

- Windows 11 AMD64; Docker and Podman; CPU and NVIDIA GPU. All four profiles and independent-host repetition are required for the full readiness claim.
- Start from accepted main; do not merge, reconcile, rebase, extend, or repeatedly review PR #67 during this delivery window. Preserve its evidence. No automatic resumption is scheduled.
- GPU qualification requires actual YOLO and EfficientNet CUDA work. CPU fallback does not pass a GPU profile.
- Preserve all eight named volumes, loopback binding, provider-key redaction, TLS verification, and trusted-model hashes/loading.
- Preserve weights, thresholds, NMS, tiling/coordinate geometry, exports, the 100 retained-tile package default, and 50 MiB request-body limit.
- Keep the baseline ML pair: torch 2.6.0 / torchvision 0.21.0, with separate CPU and CUDA 12.6 images. No dependency, model, or precision migration this week.
- End users need no Git, Node, source checkout, or application development environment. The existing approved Podman provider requires Python; explicitly document and qualify that prerequisite.
- Keep published `v0.1.2` immutable and cdcai adoption owner-gated. Use new candidate identifiers; never relabel historical evidence.
- Keep health/readiness lightweight. `setup_required`, `degraded`, a selected device label, mocked model tests, and a successful HTTP status alone do not establish successful inference.
- Establish endpoint/signing policy on Day 1. A bypass-based run does not qualify a managed endpoint; do not disable protection or certificate checks to pass.
- Seven days is a conditional forecast. Unavailable hosts, assets, policies, or failed tests remain named blockers; they do not become passes through documentation.

## Review focus

1. Multiple engines, Podman connections, and fresh shells: operations address the chosen installation or fail before mutation. W03/W10.
2. Hanging/noisy children, CMD providers, spaces, and trailing backslashes: preserve arguments/status and bound owned-process cleanup. W03/W09.
3. Failed or simultaneous trust repair: retain the previous working bundle and configuration. W04/W10.
4. Mocked models, skipped EN work, wrong devices, or unrelated artifact bytes: qualification fails rather than issuing a misleading pass. W05/W09.
5. Cancellation/error plus another detection request: preserve ownership, progress, results, and recovery without deleting export inputs. W07/W10.

## 1. Execution protocol and working context

The assessment used a host-local nested checkout whose path is not authoritative. Treat the executing checkout and any surrounding user directories as non-disposable, then discover the current Git root:

```powershell
git rev-parse --show-toplevel
git status --short
git branch --show-current
git rev-parse HEAD
git worktree list --porcelain
```

Use an isolated authorized branch/worktree for implementation, preserving existing changes and untracked evidence. Do not run `git reset --hard`, `git clean -fdx`, force-delete branches, prune engines, or use Compose `down -v`. No cleanup is needed merely to read this plan.

For every coding slice, follow this sequence:

1. Read the task's files and immediate callers; use `rg` to locate symbols. Paths describe the assessed source, not permission to skip inspection.
2. State the observable failure and desired result in one sentence.
3. Add a focused behavioral regression and run it before the fix. A missing import, collection error, unavailable dependency, or platform skip is not the intended failure.
4. Make the narrow correction, preserving existing interfaces unless a change is specified here. Snippets below show contracts/patterns; retain surrounding exception and cleanup logic.
5. Run the listed focused checks and inspect exit codes and skips. Do not write tests that merely search for your new source string when behavior can be exercised.
6. Review the diff, update the task/evidence entry, and commit only the task's files when commits are authorized. Do not stage unrelated local evidence.
7. If two bounded attempts do not resolve a failure, preserve the reproducer and request focused capable review. Do not keep expanding architecture or silently weaken the gate.

Documentation-only changes need link/command/consistency checks, not invented application tests. Use the existing approved developer environment; inspect `tests/conftest.py` before running tests because it patches model loading and creates test state. Windows PowerShell 5.1 behavioral checks are mandatory for shipped scripts; PowerShell 7 alone is insufficient. All test children need an outer deadline. Long-running real work may have a larger declared deadline than a readiness probe.

Use one task board and one evidence index. Reuse existing active task ownership where appropriate; W identifiers below are work-package identifiers, not a second TASK-number system. Record `not_run`, `pass`, `fail`, `blocked`, or justified `not_applicable`, plus command/exit code, source revision, fixture/tool/artifact hashes, anonymous host ID, and next action. Required-platform skips are `not_run` or `blocked`.

Keep secrets, private AOIs, raw provider responses, certificates, and sensitive browser traces out of committed evidence. Never dump the live `.env` to diagnose configuration. Use synthetic configuration for tests and sanitized summaries for review. Verify the reported Azure-key rotation with its owner before publication; do not retrieve or reproduce the old key.

Record live-test scope before starting: host, engine, Podman machine/connection, Compose project, port, image, scratch directory, and permitted volume creation. Honor existing session authorization; do not ask repeatedly for work it covers. New external publication/signing/registry pushes and destructive cleanup use their applicable authorization. Status/setup/verification scripts can write configuration or start processes; inspect before treating them as read-only.

## 2. Sequence, ownership, and stop conditions

| Work | Dependency | Completion boundary |
| --- | --- | --- |
| W00 Direction/instructions | None | Future agents enter the v2 main-based work; historical work is preserved. |
| W01 Baseline/prerequisites | Start with W00; do not wait for all documentation edits | An actual early package attempt and named feasibility blockers. |
| W02 Dormant helper | W01 failure inventory | Helper-off launch/stop works without helper files/state. |
| W03 Runtime adapters/target | W01 selected profiles | Bounded commands with exact arguments and correct target. |
| W04 TLS repair | W03 adapter contract for final integration | Failure preserves prior trust; exit status is truthful. |
| W05 Qualification reuse | Start on Day 1 alongside fixes | Existing external tooling proves both models and exact candidate identity. |
| W06 Model/input failures | W01 fixtures; W05 informs real checks | Required-classifier failure is visible; allocation limits apply early. |
| W07 Admission/rate/recovery | W06; coordinate shared application file | Concurrent jobs are controlled; rate budgets and cancellation recover correctly. |
| W08 Google first use | W01 reproducible browser case | Correct request bounds on Google; Azure remains working. |
| W09 Candidate freeze/package | W02-W08 accepted; first consolidated review | Exact real archives/images and required Windows checks. |
| W10 Independent qualification | W09; baseline host preparation starts W01 | Four profiles repeat on independent hosts or release blockers are explicit. |

One owner edits shared PowerShell libraries at a time. One owner edits `webapp/towerscout.py` request lifecycle at a time. Coordinate the generated JavaScript bundle. Overlapping machine testing and implementation is useful when resources permit; this plan does not assume parallel agents.

Day-1 checkpoint: if assets, policy, machines, or baseline install cannot be established, mark the forecast at risk/blocked with owner and next check. Day-3 checkpoint: if corrected Docker/Podman rehearsal or real combined inference remains unresolved, revise the deadline forecast. Do not consume Days 5-6 with optional architecture work.

## 3. Work packages

### W00 - Establish one direction and correct agent entrypoints

**Files:** `.github/copilot-instructions.md`, both `.github/instructions/*.instructions.md`, `CONTRIBUTING.md`, `HANDOFF.md`, `.agent_work/{README.md,current-tasks.md,task-backlog.md,requirements.md,design.md}`, related active task files/status entrypoints, and the focused skill corrections in section 4. Proposed new files: root `AGENTS.md` and `.agent_work/decisions/021-main-based-windows-deployment-deadline.md`; confirm 021 is still unused before creating it.

**Consumes:** User direction to move away from PR #67, this v2 pair, current task ownership. **Produces:** a short current-direction pointer, one decision record, and an accurate active board; no release-readiness claims.

- [ ] Inventory status, worktrees, branches and untracked path names. Record assessed main and PR #67 head `93d22f2ce0551defb79c852e0e879947cc611521` as historical references; verify the PR head again only if actually dispositioning it. Preserve unique work before any later archive.
- [ ] Add the short current-direction text below to the existing handoff/board and link this pair. Do not duplicate the complete plan into each file.

```text
Current delivery direction: qualify a new release from accepted main for
Windows 11 Docker/Podman CPU/NVIDIA use. Execute the September 21 v2 plan.
PR #67 and Task-087 launcher work are deferred and are not release gates.
Preserve their history; do not merge, reconcile, or resume them this week.
Task status comes from the active board; acceptance comes from the v2 spec.
```

- [ ] Record the decision and its consequences. Recommend closing PR #67 unmerged under the applicable authorization; preparing the local decision does not require changing GitHub first. Preserve its commits/review evidence. Do not describe it as unrelated Git history: a common ancestor exists.
- [ ] Correct all repeated PR #67 merge/resume directives in `.github/copilot-instructions.md`, not only its first paragraph. Replace the single GPU-package assumption with the two-image CPU/CUDA contract. Update active Task-101's obsolete PR integration gate without claiming that gate passed.
- [ ] Keep completed security work completed, mark deferred launcher/UI/governance work accurately, and map current implementation to existing Tasks 091/092/093/097 and relevant owners. Task-097 acceptance must not depend on Task-087 or a new Task-096 Exit UI. Do not mark deferred tasks completed merely to satisfy a validator.
- [ ] Replace the blanket instruction to seek approval before every IMPLEMENT step with honoring the current session's authorized plan/scope. Preserve genuine external-action and scope-change boundaries. Replace requests for unabridged logs with sanitized evidence and private raw-log custody.
- [ ] Apply the release-critical skill corrections in section 4 now: wrong flags/paths, unowned cleanup, bypass-as-proof, and misleading qualification claims. Leave cosmetic rewrites alone. Create a short root `AGENTS.md` pointer, at most about 30 lines, linking the current board, v2 pair, and skill router; retain one authoritative instruction source for each subject.
- [ ] Run the strict validator and search active entrypoints for remaining conflicting direction. Historical documents may mention PR #67; a raw match is not automatically an error.

```powershell
python .agent_work/scripts/validate_agent_work.py
git grep -n -E 'PR.?67|Task.?087|TASK-087|launcher|IMPLEMENT' -- HANDOFF.md CONTRIBUTING.md .github .agent_work/current-tasks.md .agent_work/task-backlog.md .agents/skills
```

**Done:** A new agent can find the selected direction without reading historical reviews. Validator errors are resolved truthfully; no bulk deletion or global skill-cache modification. Finish the minimal direction patch early on Day 1; public manual alignment can finish with W09.

### W01 - Attempt the baseline package and establish feasibility immediately

**Files to read:** `scripts/{setup-towerscout.ps1,package-release.ps1,import-assets.ps1}`, `scripts/lib/TowerScoutPodmanComposeProvider.ps1`, `compose.yaml`, `compose.gpu.yaml`, `compose.gpu.podman.yaml`, `.env.example`, `docs/release/`, the July evidence/fixtures identified in W05. **Evidence:** use a new authorized private working directory for raw evidence and keep any durable sanitized index with Task-091 under `.agent_work/tasks/active/TASK-091/`; do not assume existing evidence is disposable.

**Produces:** baseline artifact inventory, host allocation, fixture contract, failure list, and Day-1 forecast. No new product behavior.

- [ ] Reserve one CPU-only host and two different NVIDIA hosts where possible. Repeat CPU profiles on two suitable hosts, and GPU profiles on both NVIDIA hosts. Include a Podman installation without Docker Desktop. Record Windows build, RAM, free disk, GPU/VRAM/driver, WSL, engine/provider versions, Python prerequisite, endpoint policy, and anonymous host IDs. Unconfirmed access is a blocker, not an assumed resource.
- [ ] Assign an owner to asset/model access, approved Google/Azure accounts, TLS certificates, signing if policy requires it, builds, and independent testing. Confirm whether downloaded unsigned scripts can run under the claimed policy. The target may require organization-approved signing; determine this before building final ZIPs.
- [ ] Select a new baseline candidate identifier and accepted main SHA. Obtain/build its CPU and CUDA images using the existing workflow and authorized publication route. Pin image digests; do not reuse a mutable tag or call an old `v0.1.2` ZIP evidence for current main. If builds consume Day 1, record the delay and perform the first package attempt as soon as available.
- [ ] Locate the authorized asset ZIP, confirm its SHA256 and model contract, and build a real control ZIP using W09's existing package arguments. Record that packaging does not create the asset ZIP. Fail asset provenance early instead of secretly mounting the developer's models.
- [ ] Download and extract to a user-writable path containing spaces. On an ordinary account, attempt setup immediately using explicit engine/GPU flags. Capture actual error category, command/exit status, and time to health/model-ready/first result. Do not use `-SkipAssetImport`, a source build, or developer-populated volumes as fresh-user proof.

```powershell
# Set these two paths to verified downloads on the authorized test host.
$downloadedAssetZip = (Resolve-Path -LiteralPath '.\downloads\towerscout-assets.zip').Path
$downloadedControlZip = (Resolve-Path -LiteralPath '.\downloads\towerscout-control.zip').Path
# Run from the extracted control package, not the source checkout.
.\setup-towerscout.cmd -Engine docker -Gpu off -Port 5000 -AssetZip $downloadedAssetZip -PackageZip $downloadedControlZip -TimeoutSeconds 180 -RestartWaitSeconds 180
.\scripts\status.cmd -Engine docker -Port 5000
.\scripts\logs.cmd -Engine docker -Tail 200
.\scripts\stop.cmd -Engine docker
.\start.bat -Engine docker -Gpu off -Port 5000
```

The two ZIP names above are local operator-selected names, not a promised release naming convention. Resolve them before changing working directory; keep the absolute paths in the same PowerShell session. Use `podman`/`on` only for the matching profile and image. `stop.cmd` has no `-Port` parameter. `status` initializes configuration and therefore is not a pure inspection command. Avoid `logs -Follow` in bounded automation.

- [ ] Freeze a small permitted fixed-image set with hashes and settings. Confirm that at least one image produces a real YOLO candidate in the existing EN confidence band; do not alter thresholds to manufacture that result. Record YOLO-only and combined expected outputs separately.
- [ ] Before candidate results, declare tolerances from repeated baseline runs: counts, normalized boxes, confidences/EN scores, and ordering treatment. Sort corresponding detections deterministically for comparison; do not hide missing detections with loose tolerances. Keep CPU and CUDA baselines distinct if measured numeric variation requires it. If no stable permitted fixture exercises EN, W05 remains blocked until one is obtained.
- [ ] Measure cold startup/model load and one warm-up plus three measured warm runs on the same host/settings. Record median time, peak host/container memory, GPU memory, workload size, and errors. Synchronize CUDA before/after measured inference. Flag more than 10% warmed-median slowdown for explanation/retest, not immediate speculative optimization. No supported minimum hardware claim until the smallest claimed host passes.

**Done:** Baseline failure list distinguishes installation, policy, provider, inference, and test-harness faults. Required fixes have owners; optional improvements are deferred. An unavailable external prerequisite is explicitly reflected in the seven-day forecast.

### W02 - Remove the disabled host-helper dependency

**Modify:** `scripts/launch.ps1`, `scripts/stop.ps1`. **Tests:** extend `tests/unit/test_task_087_host_helper.py` and adjacent launcher tests; add `tests/unit/test_windows_runtime_behavior.py` for Windows subprocess cases (proposed file shared with W03/W04).

**Contract:** When the helper is off, normal launch/stop does not dot-source its module, write its profile, or require ACL operations. When enabled, preserve the explicitly supported existing path; do not reactivate it for this release.

- [ ] Reproduce with a temporary copy of the necessary scripts and fake engine commands: remove the helper module in the copy, leave the helper disabled, and run launch/stop under `powershell.exe`. Assert no helper file access/profile creation and no missing-module failure. Cover both failing preflight and successful fake preflight followed by a controlled fake Compose failure, so execution reaches the profile-write location without starting a real container.
- [ ] Gate the helper import and `Save-TowerScoutHostHelperLaunchProfile` call using the actual existing enablement condition. The current launch import is unconditional; stop also imports outside its guarded cleanup. Keep the condition and imports close to their call sites.
- [ ] Exercise enabled-path behavior with a fake helper in the sandbox, plus disabled-path launch/stop on a real package during W09. Assert scalar nonzero engine failures remain nonzero.

```powershell
python -m pytest tests/unit/test_task_087_host_helper.py tests/unit/test_task_075_launcher_gpu.py tests/unit/test_windows_runtime_behavior.py -q
```

**Caution:** Do not delete all helper code, unrelated tests/workflows, web routes, or PR history. This is removal of a dormant dependency, not a launcher redesign.

### W03 - Repair existing process boundaries and bind the runtime target

**Modify:** `scripts/lib/{TowerScoutBootstrap.ps1,TowerScoutCompose.ps1,TowerScoutPodmanGpu.ps1,TowerScoutPodmanComposeProvider.ps1}` and only affected launch/setup/status/logs/stop callers. **Tests:** `test_windows_runtime_behavior.py`, `test_task_074_bootstrap.py`, `test_podman_gpu_enablement.py`, `test_task_075_launcher_gpu.py` under `tests/unit/`.

**Existing interfaces to retain:** `Invoke-TowerScoutPodmanCommand -Arguments <string[]> -TimeoutSeconds <int>`; `Invoke-TowerScoutPodmanGpuCommand`'s declared timeout; `Invoke-TowerScoutCompose -Engine <auto|docker|podman> -ComposeArguments <string[]> -Build -Gpu <off|auto|on> -PodmanMachineName <string>`. Preserve return shapes used by callers; add optional deadlines only after auditing consumers. Do not create a generic native-process framework.

- [ ] Inspect the current adapters before reusing them. The Podman/bootstrap process paths wait before draining redirected output; enough output can deadlock. The GPU adapter ignores its declared timeout, and engine/provider/Compose probes still have raw unbounded native calls.
- [ ] Extend `test_windows_runtime_behavior.py` with owned fake children: stdout and stderr each exceed pipe capacity; child returns 7 after output; child hangs; child spawns a hanging grandchild; executable/path/arguments contain spaces; arguments include an empty string and a trailing backslash. Compare received arguments exactly and assert bounded completion, exit-status propagation, and cleanup of only owned PIDs.
- [ ] Include the real approved provider shape: a `.cmd` wrapper invokes `.venv\Scripts\podman-compose.exe` with `%*`. Do not assume `System.Diagnostics.Process` can directly execute a CMD wrapper with `UseShellExecute=false`. Implement/reuse a separately tested batch invocation path; reject ambiguous quoting rather than concatenating unchecked shell text.
- [ ] Repair the existing adapters to drain both streams while running and keep bounded retained output. Use asynchronous reads or the existing compatible mechanism with verified Windows PowerShell 5.1 behavior; continue draining after the retention cap. Starting `ReadToEndAsync` alone removes the pipe stall but does not bound retained memory. Avoid PowerShell event callbacks on threads without a runspace. Do not wait for exit before starting the reads. Capture final status once, terminate the owned process tree on expiry, then bound cleanup/drain time too.
- [ ] Preserve the existing 30-second short-probe default where applicable. Distinguish short readiness probes from image pulls/imports/builds, which need a larger configured outer deadline and progress. Do not impose a 15/30-second limit on a large download. Treat `logs -Follow` as streaming interactive behavior, not a hung probe.
- [ ] Route the currently unbounded engine `info`, provider-version, Podman Compose-version and GPU-discovery calls through corrected boundaries. Audit error consumers so timeout/nonzero does not become an empty success or a fallback to another engine.
- [ ] On setup, resolve and record the explicit engine, package root/project, and for Podman the selected machine, connection, and rootful/rootless mode. Use existing configuration where possible; if it cannot hold that binding, add a small versioned target record to package state, without credentials. Validate the record before mutation. Do not create a ten-script profile/discovery subsystem.
- [ ] Invoke Podman operations with the selected connection/machine explicitly where supported. If a Compose provider cannot select that target, compare its effective target to the recorded one and fail before mutation on mismatch. An informative warning is insufficient. Never silently switch the user's global connection/default machine/rootful mode.
- [ ] Add fake-command sequence assertions: both engines installed but explicit Podman chosen; current default points elsewhere; selected machine missing/stopped; connection changed in a new shell. On mismatch assert zero `up`, `down`, import, repair, or stop calls. On matching target assert lifecycle operations use that target. Test actual non-default connection behavior on Podman in W09.

```powershell
python -m pytest tests/unit/test_windows_runtime_behavior.py tests/unit/test_task_074_bootstrap.py tests/unit/test_podman_gpu_enablement.py tests/unit/test_task_075_launcher_gpu.py -q
```

**Review trigger:** If CMD quoting, process-tree ownership, or provider target selection cannot be demonstrated by the fixture and actual provider, obtain focused review. Do not substitute new C#/Win32 infrastructure, change defaults globally, or declare an untested provider supported. A saved engine/GPU/port convenience profile is optional unless an observed lifecycle failure requires it.

### W04 - Make TLS repair transactional enough to preserve working trust

**Modify:** `scripts/repair-provider-tls.ps1`, `scripts/import-tls-ca.ps1`; touch the existing environment writer only as narrowly needed. **Tests:** Windows behavior module from W02/W03 and existing provider-TLS tests. **Interfaces:** retain existing flags, including `-CertificatePath` and verification-provider choices; do not dot-source a top-level script that initializes configuration during a unit test.

- [ ] Add a fake import command that writes two diagnostic lines and exits 7. Through the repair wrapper assert exactly integer 7 is interpreted as status and the outer process fails. Repeat exit 0 and paths with spaces under Windows PowerShell 5.1. This regression addresses output captured together with a returned exit code.
- [ ] Keep diagnostics on the host stream and return only the captured scalar status in `Invoke-TowerScoutImport`:

```powershell
& $importCommand @arguments | Out-Host
$importExitCode = $LASTEXITCODE
return [int]$importExitCode
```

- [ ] Use a uniquely named candidate certificate/bundle. Copy/build it using existing container-copy and verification helpers, then verify the selected provider against that candidate before touching active `.env` values. `VerifyProvider none` is not acceptance evidence. A candidate failure must leave the existing bundle and environment bytes unchanged.
- [ ] Protect the short repair transaction using one package-scoped exclusive lock or equivalent; a second repair reports busy without changing either candidate's active state. Re-read/check the original environment bytes before promotion to detect an unrelated concurrent edit.
- [ ] Update only `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` after successful verification. Preserve unrelated keys, comments, encoding and line endings; reject duplicate active keys rather than guessing. Write a same-directory temporary file and atomically replace/rename as supported, keeping a rollback copy only for the bounded transaction and removing it afterward. Do not create a persistent full `.env` backup or a general recovery journal.
- [ ] Leave the previously working bundle available until adoption is confirmed. If promotion fails, keep prior configuration; if restart/adoption fails, report that state and retain the previous paths for explicit rollback. Do not claim automatic running-container adoption just because `.env` was updated.
- [ ] Fault cases: missing certificate; nonzero copy/build; invalid candidate; verification timeout; denied environment write; changed environment during transaction; second simultaneous repair; interruption before promotion; failed restart after promotion. Assert original bytes/paths and bundle usability where promotion has not succeeded, not just an error string. Run a successful repair and subsequent recovery using approved certificates on a qualified host.

**Caution:** Application CA repair cannot fix registry-pull or VM trust failures. Route those to the engine/organization instructions. Never use `verify=false`, skip hash/trust checks, or export a user's certificate contents into evidence.

### W05 - Extend existing external qualification; do not build a new product self-test

**Modify:** `scripts/task098_ml_qualification.py`. **Proposed new operator tools:** `scripts/qualify-candidate.ps1`, `scripts/qualification/ts-detect-harness.ps1`. **Proposed tests:** `tests/unit/test_candidate_qualification_contract.py`. **Read:** `scripts/task098-qualify-ml.ps1`, `webapp/{ts_yolov5.py,ts_en.py,ts_events.py,ts_performance.py}`, `tests/conftest.py`.

**Reusable operator inputs:** Obtain the authorized July harness and fixture packet from the release/model owner's evidence custody rather than assuming sibling directories beside the checkout. Record their absolute host paths only in private execution notes and bind committed evidence to sanitized identifiers and hashes. Confirm existence, permissions, fixture provenance and hashes. Preserve originals; copy only sanitized authorized tooling into the proposed repository path. Private/large fixtures remain an operator input, not an image layer or public commit.

**Known traps:** The July harness performs geocoding before `SkipLive`, catches live-provider failures, and records counts without enforcing the complete acceptance contract. Its 53-detection parity uses `/getobjectscustom`, whose current YOLO call omits `secondary`; this is not combined-model proof. Its `Invoke-RestMethod -Form` use needs PowerShell 7 for the operator or a deliberate compatibility adaptation, while shipped user scripts still require 5.1. Its 65-second sleep masks shared rate-limit coupling, and its 8-second fixture spacing can exceed a real 10/minute custom-upload limit.

The existing `task098-qualify-ml.ps1` wrapper accepts `Profile`, `TorchVersion`, `TorchvisionVersion` and `OutputDirectory`, builds through Docker, and mounts developer model files. It has no `Engine`, `Image` or `Digest` parameter and cannot certify the downloaded candidate unchanged. Retain it for its original developer use; the thin runner below addresses that specific gap.

**Proposed tool contracts (implement these before invoking them):**

```text
qualify-candidate.ps1
  -Engine docker|podman -Gpu off|on -PackageRoot <extracted directory>
  -FixtureManifest <absolute JSON path> -OutputDirectory <new directory>
  Exit 0 only for a complete successful report; otherwise nonzero.
  No build flag, image override, or developer-model path.

task098_ml_qualification.py
  Existing no-argument synthetic mode remains compatible.
  New: --fixture-manifest <path> --output <path>
  Device policy still comes from TOWERSCOUT_DEVICE before model imports.
```

- [ ] Freeze a manifest with `schema_version: 1`, `required_device` (`cpu` or `cuda`), `tiles` (objects with `path` and `sha256`), `model_sha256` (keys `yolo` and `en`), `expected_detections` (one list per input tile using the detector's result fields), and `tolerances` (keys `box_abs`, `confidence_abs`, `secondary_abs`). Require exact per-tile count and class correspondence; compare the named numeric fields after deterministic ordering. Store baseline source and image in `baseline_identity`. Keep profile-specific manifests explicit. Validate paths stay inside the fixture root; reject missing/hash-mismatched files. Populate these data from W01, never from the candidate's own output.
- [ ] Extend the existing Python probe with the optional combined mode, preserving its original synthetic checks. Load actual `/app/webapp/model_params/yolov5/newest.pt` and `/app/webapp/model_params/EN/b5_unweighted_best.pt` through `YOLOv5_Detector(str(yolo_path))` and `EN_Classifier()` and their trusted loading. Use `ExitEvents()` and `PerformanceMetrics(run_id)`, allocating/freeing the event in `try/finally`. Build each tile as `{"filename": str(validated_tile_path)}`. Validate manifests before imports/loads; the existing module imports may need to move behind argument/device setup.

```python
# Core call inside the new mode after manifest/hash/device validation.
events.alloc(run_id)
try:
    detections = detector.detect(
        tiles, events, run_id, crop_tiles=False,
        secondary=classifier, perf_metrics=metrics,
    )
finally:
    events.free(run_id)
```

- [ ] Record `model_device`, `secondary_classifier_device`, `secondary_classifier_candidate_count`, and `secondary_classifier_batches` from the actual run. Require positive secondary candidates and batches. Inspect actual model parameter/input devices at forward execution using narrowly scoped instrumentation/hooks if existing telemetry only proves configured labels; remove hooks afterward. Require both observed devices to match the requested profile. Do not replace inference with fabricated detections in this combined mode.
- [ ] Use one warm-up and three measured warm runs; create fresh per-run metrics/detection input objects because classification appends scores. Synchronize CUDA for timing. Compare actual output to the manifest, recording separate YOLO-only historical parity if run. Enforce every mandatory check; never emit `passed: true` merely because inference returned.
- [ ] Extend the existing report with a versioned combined section: tool/fixture/model hashes, required/observed devices, candidate/batch counts, per-run outputs and comparisons, timing/memory, individual check results, and overall pass. The outer runner records inspected image digest, package hashes and source identity; an environment variable containing an expected identity is not independent proof of it. Missing fields fail report validation.
- [ ] Implement the thin external runner using the extracted package's Compose library/configuration and W03 target checks. Use the exact pinned image and the assets actually imported by setup. Mount the operator probe/fixtures read-only and its dedicated evidence directory writable. Do not mount the developer's model directory or rebuild an image. Do not call the legacy `_startup_probe` during combined mode: importing the full app in another process can load another model copy; measure actual app startup separately. Keep fixtures/probe out of the release-image payload.
- [ ] Rehearse the existing providers' `compose run --rm --no-deps --entrypoint python` path early. Add only the required volume/environment arguments with array-based quoting. Stop only the test-owned service before a separate probe loads both models, to avoid a second full GPU model allocation; relaunch that service afterward. Reuse the intended named asset volumes without deleting or recreating them. If provider semantics differ, fix that bounded invocation and test both engines rather than assuming Docker behavior on Podman.
- [ ] Adapt the copied HTTP harness: `SkipLive` must avoid all provider calls including geocoding; required live failures must affect the process exit code; assertions must check terminal success/results/export, not just HTTP 200; selected-device readiness remains informational. Keep upload pacing within its legitimate per-operation quota after W07; remove only workarounds for unrelated map traffic consuming the upload quota.
- [ ] Add report-contract tests with complete synthetic report objects: reject wrong device, zero EN candidates/batches, changed model/fixture/image identity, missing comparison results, output outside tolerance and child nonzero status. These tests validate the evaluator, not actual models. Retain legacy no-argument mode coverage. Then run the new probe outside pytest on CPU and CUDA; mocked pytest loading is not real-model evidence.

**Done:** Both real models work on the required device using frozen permitted images and imported assets, with truthful nonzero failure status. Final acceptance still requires the live map route in the actual app process; an external probe alone does not establish that the app loaded both models.

### W06 - Propagate classifier failure and reject excessive allocation early

**Modify:** `webapp/{ts_yolov5.py,ts_maps.py,ts_validation.py,towerscout.py}`. **Tests:** extend `tests/unit/{test_yolov5_secondary_metrics.py,test_validation.py,test_runtime_hardening.py,test_task_081_route_hardening.py}`. Split model-error and input-limit corrections into separate focused commits.

**W06a: required secondary classification.** `secondary=None` intentionally supports YOLO-only callers; preserve it. Candidates outside the existing confidence band legitimately bypass EN; preserve their scores. A supplied secondary classifier that fails must fail the detection job rather than accept its candidates silently.

- [ ] Add this regression to the existing secondary-metrics module, which already provides `_FakeModel` and `_FakeEvents`; add the shown imports. Run it before fixing both exception layers.

```python
import pytest
from ts_errors import ProcessingError


def test_required_secondary_failure_is_not_swallowed(tmp_path):
    tile_path = tmp_path / "tile.jpg"
    Image.new("RGB", (8, 8), "white").save(tile_path)
    detector = object.__new__(YOLOv5_Detector)
    detector.model = _FakeModel()
    detector.batch_size = 4
    detector.device_label = "cpu"

    class BrokenSecondary:
        device_label = "cpu"
        batch_size = 8

        def classify(self, image, detections, batch_id=0):
            raise RuntimeError("synthetic classifier failure")

    with pytest.raises(ProcessingError) as caught:
        detector.detect(
            [{"filename": str(tile_path)}], _FakeEvents(), "failure-test",
            secondary=BrokenSecondary(),
        )
    assert caught.value.details["operation"] == "secondary_classifier"
```

- [ ] Replace the secondary catch-and-continue with a typed failure and propagate it through the outer per-tile/batch catch. Preserve `operation="secondary_classifier"`; do not overwrite it with a generic operation during wrapping. Preserve recognized resource/OOM handling without allocating enough real memory to crash the test host.
- [ ] Add success/YOLO-only/noncandidate/OOM cases using the existing fakes. Preserve the current CUDA guard through tensor conversion and its release before secondary work; existing guard tests must still pass. Through the map route assert an error response and successful next request, not a partial successful result.

**W06b: allocation guards.** Candidate-grid count is distinct from the 100 retained-tile cap, and decoded pixels are distinct from compressed-body size. Add `TowerScoutValidator.MAX_CANDIDATE_TILES = 4096`, `MAX_IMAGE_PIXELS = 16000000`, and `MAX_IMAGE_EDGE = 8192` alongside its existing constants. These are proposed initial budgets, not measured hardware guarantees. Validate them against permitted baseline workloads and the smallest claimed host before freeze; any adjustment must be recorded and boundary-tested. No new user-facing configuration surface is necessary this week; tests can monkeypatch these constants.

- [ ] Extend the signature to `Map.make_tiles(self, bounds, overlap_percent=5, crop_tiles=False, max_candidate_tiles=None)`. Existing non-request callers retain compatibility; every production request caller passes the validator's candidate budget. After computing `nx`/`ny`, reject their product above that cap before constructing the tile list or making provider calls. Preserve current return tuple and geometry.
- [ ] Raise `ts_validation.ValidationError("Selected area exceeds the candidate tile limit. Select a smaller area.", field="bounds")`, matching the existing route handling; `ts_errors.ValidationError` has a different constructor and is not an interchangeable import. Pass the same candidate budget through `_build_tiles_for_request`, `estimate_detection_tiles`, and `_run_detection_request`; enforce it before model initialization.
- [ ] At uploaded-image open, validate dimensions/pixel product before full decode, conversion, copying, or model execution. Convert Pillow decompression-bomb conditions to the existing validation response. Preserve the body limit. The error should tell the user to choose a smaller area/image without exposing server paths.
- [ ] Test candidate cap and cap+1 using small configured test limits and spies that assert zero enumeration/provider/model calls on rejection. Test a narrow polygon over a huge bounding grid, not only a large retained result. Test image pixel/edge equality and one above, corrupt headers, and a compressed large-dimension fixture without allocating a huge image in the test process. Confirm an ordinary accepted image/map retains existing output.

```powershell
python -m pytest tests/unit/test_yolov5_secondary_metrics.py tests/unit/test_ts_en_classifier.py tests/unit/test_validation.py tests/unit/test_runtime_hardening.py tests/unit/test_task_081_route_hardening.py -q
```

**Caution:** Do not change model thresholds, force CPU fallback for required-CUDA mode, or add broad workload optimization. Reject before expensive work; an exception after allocation does not meet the guard's purpose.

### W07 - Isolate rate budgets, admit one detection job, and verify recovery

**Modify:** `webapp/{towerscout.py,ts_validation.py}`; change `ts_events.py`, `ts_progress.py`, `ts_maps.py` only if a reproduced lifecycle failure needs it. **Tests:** existing `tests/unit/{test_rate_limiter_hardening.py,test_progress_tracker.py,test_flask_routes.py,test_provider_http.py}`; proposed `tests/unit/test_detection_admission.py` for deterministic overlapping requests.

**W07a: scoped limits.** Keep the existing bounded/thread-safe `RateLimiter` implementation and quotas. Change its call-site key from a bare IP to a stable operation scope plus IP, separating map/provider/service traffic, geocoding, estimate, detection, custom image, and uploads. Do not key by an arbitrary run ID or increase quotas to hide coupling.

```python
# Call-site pattern; retain that route's existing numeric quota/window.
rate_limiter.is_allowed(
    f"custom-image:{client_ip}", max_requests=10, window_seconds=60
)
```

- [ ] Add route tests that perform enough allowed map fetches to exceed the custom route's smaller quota, then assert the first valid custom request is still accepted. Assert its own 11th request in the same 60-second window is rejected; verify unrelated operation windows do not prune each other's histories. Use a controlled clock, synthetic provider/images/models and fresh limiter; do not mock `is_allowed` to always return true. Preserve bounded key count and concurrent-limit tests.
- [ ] Audit every `rate_limiter.is_allowed` call and assign the same stable key to equivalent work. Validate provider/service before including them in the scope. Avoid a new generic rate-limit framework.

**W07b: whole-job admission.** The current deployment uses one Waitress process. Add one process-wide nonblocking detection lock shared by map and custom-image routes, separate from the existing GPU guard. This contract is not a multi-process distributed queue.

```python
# Module-level lock; import threading if not already imported.
detection_job_lock = threading.Lock()


@app.route('/getobjects', methods=['POST'])
def get_objects():
    if not detection_job_lock.acquire(blocking=False):
        return jsonify(error="Detection is already running.", code="DETECTION_BUSY"), 429
    try:
        return _run_detection_request()
    finally:
        detection_job_lock.release()
```

This replaces the existing `get_objects` wrapper; do not register a second route. Wrap the existing custom-image body with the same acquire/`try/finally` pattern, without reacquiring in `_run_detection_request`. Keep cheap custom-image validation before admission, but move session-ID creation and all event/progress/temp/session mutation after acquisition. Release after owned cleanup. Health, progress and abort endpoints remain outside this lock. Preserve the route's existing `_get_client_ip()` logic for rate-limit keys.

- [ ] Use `threading.Event` barriers in a test worker with its own Flask test client to hold the first map request inside a fake detector. Issue a second map/custom request with another client; assert 429/`DETECTION_BUSY`, no second detector call and no progress/event/session overwrite. Release the barrier and assert success. Repeat first-job failure and cancellation; assert a following request acquires the lock and succeeds. Avoid arbitrary sleeps and shared test clients across threads.
- [ ] Allocate a cancellation event before exposing its progress record, closing the current early-cancel race. Exercise cancellation during download, during inference boundaries, and immediately before final result publication; inspect actual behavior before larger edits. Native model calls may finish their current batch before cancellation is observed; document measured bounds instead of promising immediate interruption.
- [ ] Assert interrupted/failed work does not publish partial results or leave session metadata pointing to deleted files. Preserve successful tile/result files needed for review/export. If late cancellation reveals current metadata writes occurring before terminal success, stage only those new fields until the success decision; do not rewrite the whole session architecture or attempt to restore files already removed by unrelated operations.
- [ ] Exercise slow/broken provider and missing-response scenarios. Existing aiohttp timeouts are not a single guaranteed whole-job deadline across retry waves. Record actual cancellation/deadline behavior. If acceptance fails, make the smallest bounded cancellation fix, explicitly await owned tasks before closing the event loop, and handle `asyncio.CancelledError` intentionally; a generic `except Exception` may not catch it. Keep ordinary network error classifications distinct from cancellation.

```powershell
python -m pytest tests/unit/test_rate_limiter_hardening.py tests/unit/test_detection_admission.py tests/unit/test_progress_tracker.py tests/unit/test_flask_routes.py tests/unit/test_provider_http.py -q
```

**Done:** Rate isolation, single-job ownership, failure/cancel recovery and next-request success are demonstrated. A reproduced cancellation/data-loss failure blocks release until narrowly fixed. A full queue/cancellation redesign remains deferred; do not schedule it merely because this task touches the lifecycle.

### W08 - Correct Google first-use bounds and regenerate the bundle

**Modify:** `webapp/js/src/ui/search.js`; read `webapp/js/src/providers/{GoogleMap.js,TSMap_base.js,AzureMap.js}` for the boundary/viewport contract and edit them only if required. Regenerate `webapp/js/towerscout.js`. **Tests:** extend `tests/frontend/test_setup_wizard_validation_contract.js` and `tests/frontend/test_detection_workflow_smoke.js`; retain `tests/integration/test_task_064_provider_state_manager.js` coverage.

- [ ] Reproduce Google detection on first use with no drawn boundary. In `buildDetectionPayload`, bounds are currently read before adding the viewport boundary; Google can return an invalid empty union. Assert the outgoing payload has valid viewport bounds on the first click, not only after a retry.
- [ ] Select/create the fallback viewport boundary before reading request bounds, using the existing provider contract. Preserve explicit user polygons and selection state; do not switch providers or silently use stale bounds. Retain Azure's working viewport behavior.
- [ ] Add deterministic cases for Google empty-boundary first use, explicit Google polygon, Azure empty-boundary behavior, and provider switch. Verify bounds numerically and assert no duplicate boundary addition on repeat submission.
- [ ] Rebuild the checked-in JavaScript bundle and run focused contracts. Then run authorized real Google/Azure smoke, including cancellation, using a sanitized fixture and the test's existing supported options (`--provider=google` or `--provider=azure`, `--fixture=path`, `--base-url=url`, `--browser-path=path`, `--cancel-smoke`). The value-bearing options require the equals-sign form. Do not print a private local fixture or network trace to discover its secrets.

```powershell
node webapp/build.js
node tests/frontend/test_setup_wizard_validation_contract.js
node tests/frontend/test_global_contract.js
node tests/frontend/test_debug_logging_contract.js
node tests/integration/test_task_064_provider_state_manager.js
```

**Done:** Source and bundle match; first-use Google succeeds and Azure remains working. `node webapp/build.js` builds JavaScript, not the hand-maintained documentation HTML.

### W09 - Freeze, build and verify exact downloadable artifacts

**Files:** `.github/workflows/container-publish.yml`, `scripts/package-release.ps1`, `docs/release/`, relevant package tests, public manuals in section 5. Modify packaging/workflow only for a demonstrated artifact gap. Preserve existing required CI gates; a new small Windows job is optional if manual Windows verification is properly recorded.

**Consumes:** Accepted W02-W08 changes, W05 qualification tooling, first consolidated review. **Produces:** candidate inventory linking source SHA, CPU/CUDA image digests, control/asset ZIP hashes, internal manifests, fixture/tool hashes and Windows-check results.

- [ ] Finish the first consolidated review by Day 3, focused on process/target boundaries, TLS preservation, model errors, admission and harness truthfulness. Resolve release blockers; defer unrelated refactoring. Freeze an accepted source commit before final image builds.
- [ ] Use the existing image workflow's `pytorch_flavor` values `cpu` and `cuda126`, with explicit candidate tag and `push_latest` disabled. Registry pushes are publication actions. Record actual resolved digest for each variant and confirm its source label, dependency versions and expected flavor; a tag string is insufficient. Local-only rehearsal is useful but does not establish another computer can download the image.
- [ ] Set package variables from the actual inventory: `$releaseId`, `$packageOutputRoot`, `$cpuImageReference`, `$cpuDigest`, `$cudaImageReference`, `$cudaDigest`, `$assetBundleVersion`, `$assetZipSha256`. Set `$packageOutputRoot` to a new directory under ignored `dist/`, such as `dist/$releaseId`, so the CPU output cannot dirty the tracked worktree before the CUDA package clean-tree check. Each image digest must be `sha256:` plus 64 lowercase hex characters; asset SHA256 is 64 hex characters, optionally prefixed `sha256:`. Keep CPU and CUDA output identities distinct.

```powershell
.\scripts\package-release.cmd -Version "$releaseId-cpu" -OutputDir $packageOutputRoot -Image $cpuImageReference -ImageDigest $cpuDigest -PytorchFlavor cpu -AssetBundleVersion $assetBundleVersion -AssetBundleSha256 $assetZipSha256
.\scripts\package-release.cmd -Version "$releaseId-cuda126" -OutputDir $packageOutputRoot -Image $cudaImageReference -ImageDigest $cudaDigest -PytorchFlavor cuda126 -AssetBundleVersion $assetBundleVersion -AssetBundleSha256 $assetZipSha256
```

These are existing arguments. Assign variables from verified artifacts before execution; do not paste fabricated digests or assume the existing asset bundle version equals the new control-package version. Keep the script's clean-tracked-source gate; do not use `-Force`, `-NoZip`, or exception flags as final release proof.

- [ ] If endpoint policy requires signed scripts, sign only the approved staging files before internal `SHA256SUMS` generation and final ZIP creation. Verify signed bytes against the policy on the target host. Do not sign the source checkout and bypass its clean-tree gate, or modify a ZIP after recording its checksum. Failure to obtain required signing blocks that claimed environment.
- [ ] Inspect the explicit package file allowlist. Include any new runtime file needed by W03/W04 and all required guides/notices. External qualification tools need not be user-package contents. Inspect a real ZIP: sidecar SHA256, internal `SHA256SUMS`, release manifest, CPU/CUDA flavor/digest, asset contract and actual scripts/docs. Reject `.env`, credentials, private evidence, model payloads in the control ZIP, unrelated developer state and unexpected executables. Warning-only helper output is not a blocking gate unless the caller enforces its result.
- [ ] Execute package scripts on Windows PowerShell 5.1 from a spaced path, including unavailable engine/provider, a noisy/hanging child, helper-off launch, scalar TLS failure and matching/mismatched Podman target. Rehearse Docker and actual approved Podman provider setup/import/status/logs/stop/relaunch. Reopen a fresh shell before lifecycle checks. Never run unconditional `compose down` against an unverified project.
- [ ] Run focused artifact tests and the repository's existing required checks for touched areas. New meaningful Windows tests must run on Windows and report their result; platform-skipped CI does not satisfy them. No wholesale audit suppression, lint reformat, or dependency update to obtain green output.

```powershell
python -m pytest tests/unit/test_release_package_script.py tests/unit/test_release_manifest_schema.py tests/unit/test_container_publish_workflow.py tests/unit/test_import_assets_script.py tests/unit/test_license_notices.py tests/unit/test_windows_runtime_behavior.py tests/unit/test_candidate_qualification_contract.py -q
```

- [ ] Run baseline-versus-candidate W05 comparisons on the same host with frozen inputs, then complete the user-manual changes in section 5. Record any >10% warmed-median slowdown and determine whether it is repeatable/caused by the fix. Do not relax model correctness to recover speed.
- [ ] Freeze distribution bytes and make exactly those downloads available to authorized independent testers. If code, signed bytes, image, package, model, or fixtures change later, issue a new identity and rerun affected gates; explain unaffected evidence rather than copying a blanket pass.

**Done:** A clean checkout can reproduce the packaging procedure, and independent testers receive the exact inventoried downloads. Passing unit tests or creating a directory with `-NoZip` is not a downloadable-release result.

### W10 - Reproduce the installation and hand over evidence

**Files/evidence:** four-profile matrix, sanitized evidence index, tested support/rollback instructions, current board and public-doc status. Store raw sensitive evidence privately. **Consumes:** W09 immutable artifacts and W01 reserved machines/accounts.

- [ ] For each profile, record first host and independent repeat host, artifact/download hashes, image digest, model/fixture/tool hashes, versions, declared settings, result and evidence reference. Example allocation: Docker CPU and Podman CPU on `cpu-a` plus explicit-CPU `gpu-a`; Docker NVIDIA and Podman NVIDIA on `gpu-a` plus `gpu-b`. Isolate projects/ports and do not run competing profiles simultaneously when that distorts resource measurements.
- [ ] A tester follows only the shipped instructions on an ordinary account: download, verify, extract, setup with asset import, open UI, configure authorized provider, perform real map detection, review and export. No source checkout, developer model mount, preloaded application volumes, or undocumented manual repair is allowed in a fresh-install pass. Existing engine prerequisites can be installed through the documented approved procedure.
- [ ] In every profile, run the external fixed combined probe, then the live Google/Azure workflow in the actual app process. Record both model devices and positive EN work for the fixed case, expected output comparisons, startup/warm performance and memory. Provider-dependent live counts may vary; assert valid terminal outcome/review/export rather than forcing the historical count 53.
- [ ] On each host/profile exercise cancellation, a controlled recoverable error, and next-request success; stop/relaunch from a new shell and reboot. Confirm intended engine/target, assets, provider setup, sessions and export inputs persist. An explicit GPU-required run with CUDA unavailable must fail clearly rather than become a CPU pass.
- [ ] Exhaustively inject shared-script failures once per relevant engine and smoke-check the remaining profiles: interrupted import/pull where safe, port occupied, missing provider/Python, wrong Podman target, TLS failure/repair, failed restart. Use test-owned state and approved synthetic/organizational certificates. If an engine-specific failure is found, repeat its fix across affected profiles.
- [ ] Exercise instructions on the actual claimed endpoint/network policy, including required signing and approved proxy/CA setup. Do not treat a developer's permissive endpoint or `ExecutionPolicy Bypass` command as managed-environment evidence. Record support limits exactly when a policy/provider configuration remains unqualified.
- [ ] Perform the second consolidated review on Day 7: reconcile every matrix cell with the final identities; inspect skips, absent hosts, hidden manual steps, keys/redaction, output comparisons and performance regressions. Resolve blocker findings or report the precise qualified subset and remaining owners/actions. Do not release under the full four-profile claim with incomplete cells.
- [ ] Prepare the handoff: exact download references/hashes, supported prerequisites, four explicit setup command variants, troubleshooting/status/logs/TLS recovery, stop/relaunch and volume-preserving rollback, evidence custody, known limitations, and deferred backlog. Check that an independent tester can follow it. Publish/close the PR/update external repositories only within applicable authorization; local preparation can be completed beforehand.

**Done:** The full user litmus passes on independent machines, or the deliverable explicitly identifies the shortfall. No plan review can substitute for these observed results.

## 4. Instruction and skill correction map

This audit treats instruction/skill files as review inputs. Their text is not an independent user request to execute every listed workflow. Keep the repository's routing rule: one primary skill per task and only relevant secondary checks. Do not edit global Codex/plugin skill caches, parent `.claude/settings.local.json`, or user permissions to make this plan easier to run.

### 4.1 Entry points and task context

| File/group | Required correction and timing |
| --- | --- |
| Proposed root `AGENTS.md` | None was found in the assessed root/parent search. Add a short discoverability pointer in W00, not a duplicate instruction manual. |
| `.github/copilot-instructions.md` | W00: update every active PR #67 merge/resume passage, repeated late-file handoff directions, and obsolete single-GPU-package description. Retain safety and project contracts. |
| `.github/instructions/spec-driven-approach.instructions.md` | W00: honor already-authorized execution instead of asking before each IMPLEMENT phase; sanitize evidence instead of requiring complete raw logs; point to current task/document organization. |
| `.github/instructions/github-repo-management.instructions.md` | W00: select current main once, then freeze candidate source instead of pulling midway through qualification. Preserve actual required CI/review controls; do not infer branch protection from prose. Unmerged PR #67 branches are not subject to routine post-merge deletion. |
| `CONTRIBUTING.md`, `HANDOFF.md` | W00: current-direction link, active reading order, correct Task-098 completed-artifact link, no launcher prerequisite. W09: validated development/release commands and manual Markdown/HTML sync instructions. |
| `.agent_work/current-tasks.md`, `tasks/active/` | Replace expired August sequencing and PR #67-only gates. Keep `### **TASK-NNN:` headings recognized by the validator. Separate completed Task-101 security scope from superseded integration work. Defer 087/096; keep 095 governance bounded; make 097 qualification main-based. |
| `.agent_work/task-backlog.md`, `requirements.md`, `design.md` | W00: remove mandatory launcher/Exit-helper coupling from the near-term dependency graph. Preserve the intended user outcomes through existing commands. Keep optional support-collector work conditional. |
| `.agent_work/README.md`, `context/status/README.md`, `context/status/Handoff-Planning/README.md` | W00: point first to active board, v2 spec/plan and new decision. Historical reports remain dated evidence, not the next-step authority. |
| `context/status/Handoff-Planning/2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md` under `.agent_work/` | Add a concise current-week override/link; preserve October milestones and historical sequence. Do not rewrite history as if it used v2 all along. |
| `PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md` in the same directory | Remove current PR #67 dependency while preserving immutable pilot artifacts and the cdcai owner's adoption decision. |
| `.agent_work/decisions/017-*`, `020-*` | New scoped decision 021 explains supersession; retain older decisions. Do not merge a branch to recover an absent ADR-019 reference; correct/link the actual available decision when relevant. |
| `docs/internal/codex-skills/{README.md,SKILLS_MANIFEST.md}` | Keep the intentional skill inventory; identify repository copies as maintained source. Avoid blanket instructions to overwrite global skill copies, which would create divergent authority. |

### 4.2 All 12 repository skills

Paths below are under `.agents/skills/`; inspect the matching `agents/openai.yaml` descriptor for consistency when editing its skill. No descriptor or skill-framework redesign is needed.

| `SKILL.md` directory | Finding and bounded disposition |
| --- | --- |
| `towerscout-skill-router` | Keep one-primary routing. Link current direction and distinguish reading a skill during an audit from activating all of its procedures. |
| `towerscout-agent-work-hygiene` | Keep organization/redaction rules. Its quick wrapper can return success despite a strict validation failure; require the actual `python .agent_work/scripts/validate_agent_work.py` exit/result. Deferred work must not be moved to completed just to appease the validator. |
| `towerscout-container-windows-runtime` | Remove unsupported `stop.cmd -Port`; correct examples. Separate developer Compose-build checks from downloaded-package qualification. Remove unconditional `down` cleanup against an unverified target; clean up only owned resources and retain volumes. Bypass examples cannot establish endpoint compatibility. |
| `towerscout-release-candidate-gate` | Same command/ownership corrections. Fix `docs/release-asset-bundle-contract.md` to `docs/release/release-asset-bundle-contract.md`. Replace `-NoZip -Force` as release evidence with strict real-ZIP invocation including image/digest/flavor/assets. A warning-only checker needs enforced result checks. |
| `towerscout-end-user-docs-check` | Fix the same asset-contract path. Its advisory checker does not prove links/flags work. Identify configuration-writing/status/probe commands so document inspection does not unexpectedly run them. |
| `towerscout-release-compliance-review` | Fix the asset-contract path; preserve notices/licenses and report unresolved ownership/legal questions without inventing approval. No broad legal-document rewrite. |
| `towerscout-secret-and-provider-key-safety` | Replace nonexistent `AGENTS.md/security.md` with the security guidance in `.github/copilot-instructions.md` and `tests/unit/test_error_sanitization.py`. Avoid raw diff/scanner output exposing keys; summarize findings without values. Confirm reported key rotation through its owner. |
| `towerscout-ml-runtime-safety` | Explain pytest's mocked model loading, the historical custom-image YOLO-only case, actual-device/positive-EN requirements and external qualification boundary. Preserve hashes, trusted loading and supported checkpoint semantics. |
| `towerscout-browser-provider-smoke-triage` | Do not automatically dump `detection-workflow.local.json`, private AOIs or raw traces. Use authorized sanitized fixtures and interpret real 429/provider errors instead of treating every failure as test flakiness. |
| `towerscout-frontend-bundle-guard` | Keep source/bundle checks. Clarify that `node webapp/build.js` does not regenerate manual HTML docs and shell-specific checks need their actual shell. No unrelated bundle/source refactor. |
| `towerscout-provider-state-review` | Keep provider/state/race contracts. Limit tests to changed behavior and relevant cancellation/first-use cases; this release is not a general provider-state redesign. |
| `towerscout-ci-quality-ratchet` | Keep small ratchets and existing required checks. Do not make all legacy advisory suites blocking, install unrelated tooling, or run every skill by default. |

Prioritize misleading active instructions on Day 1; finish descriptive clarifications with W09. Link the direction once rather than pasting all eleven work packages into every skill.

## 5. Documentation and local repository cleanup

### 5.1 Documents to finish before candidate handoff

- `README.md`: distinguish the immutable published pilot from the new main-based candidate; link actual current downloads only after available, and claim only tested profiles.
- `docs/{quick-start,user-guide,project-overview}.md` and matching `.html`: update installation/profile selection, prerequisite/provider setup, model readiness, recovery and current direction together. HTML is manually maintained; update paired files deliberately and check rendered links.
- `docs/{docker-cpu,docker-gpu,podman-cpu,podman-gpu}-user-guide.md`: show four explicit command variants, correct CPU/CUDA 12.6 images for the new candidate, Podman provider/Python prerequisite, target selection, lifecycle/TLS commands and tested support limits. Keep historical CUDA 12.1 pilot statements clearly historical.
- `docs/package-guide.md`, `docs/release/` and support guides: align asset/control ZIP contract, SHA256/digests, Windows policy/signing where applicable, approved CA instructions, volume-preserving rollback and dormant helper status. Check the exact stopped/ready/error behavior against W10. Preserve `docs/v1-rc1-package-guide.md` as an accurate compatibility pointer.
- Preserve compatibility documents/routes such as `docs/v1-rc1-quick-start.{md,html}` and `docs/towerscout-user-guide.{md,html}` as clear pointers unless an authorized compatibility change is required. Check both the package allowlist and `webapp/towerscout.py` documentation route allowlist; they are different contracts.
- Parent-folder Word/PowerPoint/HTML review material remains user-owned historical evidence. Inventory titles/versions and add a new handoff reference if needed; do not silently overwrite or treat it as Git scratch space.

### 5.2 Preservation-first cleanup instructions

Cleanup is not a prerequisite for writing fixes. Perform only the direction/visibility work early; archive physically only when useful and authorized. Never print secret files to classify them.

| Material | Disposition |
| --- | --- |
| PR #67 branch/worktrees, review documents, unique commits | Record branch names/SHAs and unique work; preserve before optional archival. An upstream marked gone or a failed ancestry check after squash is not proof the branch is disposable. Recommend PR closure separately. |
| Active/completed/deferred task files | Use the canonical board and truthful lifecycle state. Completed artifacts go under completed; deferred launcher work belongs in backlog/archive with a pointer, not completed. Update links with any move. |
| Misplaced legacy evidence, `.agent_work/tmp/task098-qualification` | Inventory/hash and preserve unique results. Relocate durable sanitized indexes under `.agent_work/tasks/active/TASK-091/` and raw sensitive contents to the authorized private evidence directory; do not delete unique results merely because they are untracked or under tmp. |
| `dist/` and historical RC ZIP/checksum sets | Record artifact identity and evidence dependency; archive exact sets together only after verifying the destination copy. Do not run blanket build-output deletion. |
| `.env`, certificates, models, datasets, uploads, sessions and container volumes | Preserve. No raw-content inventory, overwrite, volume prune or removal as housekeeping. Use synthetic or isolated state for tests. |
| Parent `TowerScout` documents, validation folders, user downloads | Outside the Git root; preserve originals and authorized provenance. Do not recursively move the parent as though it were repository build output. |
| Generated bundles/HTML and notices | Regenerate/sync only their documented outputs. Preserve compatibility files and notices unless a reviewed change says otherwise. |

Before any optional recursive move/delete, resolve the exact absolute source/destination, verify they remain within the expressly intended workspace/target, check for junctions/reparse points, preview using native PowerShell `-LiteralPath`/`-WhatIf`, and verify retained copies/hashes first. Do not pass enumerated PowerShell paths into CMD deletion commands. No bulk destructive cleanup command is part of this plan.

## 6. Daily handoff schedule

| Day | Actions | Expected result | Prepare for next day |
| --- | --- | --- | --- |
| 1 | W00 minimal direction/skill patch; W01 baseline download/setup; start W05 fixture/probe reuse. | One active direction, actual baseline failures, named host/policy/asset owners and forecast. | Reserve hosts, freeze fixtures/tolerances and required fix list; prepare isolated regressions. |
| 2 | Small W02/W04/W06/W08 corrections; W03 adapters; W07 rate isolation; first real combined probe. | Focused regressions and early model evidence, or explicit blockers. | Prepare corrected Windows package rehearsal and remaining blocker list. |
| 3 | Finish runtime/qualification/admission work; Docker/Podman rehearsal, cancellation/export/recovery; first review. | Corrected rehearsal and refreshed go/at-risk/blocked forecast. | Freeze scope and queue CPU/CUDA builds, required signing and packaging. |
| 4 | W09 freeze source, verify real archives/images, required Windows checks and baseline comparisons. | Exact candidate inventory and ready-to-follow manuals. | Distribute identical bytes and prepare independent clean targets. |
| 5 | W10 four profiles, independent repetition, actual models and Google/Azure review/export. | Completed matrix cells with hash-bound evidence. | Schedule remaining cells, reboot/persistence, network/policy and recovery checks. |
| 6 | Finish reproduction/recovery; fix only blockers and rerun affected gates under new identities. | Required gates pass or remaining blockers are explicit. | Assemble final evidence, rollback/support packet and tester instruction review. |
| 7 | Second consolidated review, final identity reconciliation and handoff; authorized publication. | Full readiness only if all gates pass; otherwise precise qualified subset and blocker owners. | Preserve evidence/rollback custody and deferred backlog for subsequent work. |

Do not trade independent testing for optional polish. If the required fixes consume more time than available, change the forecast and explain the remaining gap. The plan is structured to discover that early; it does not guarantee a seven-day result.

## 7. Agent completion checklist

- [ ] W00-W10 evidence agrees with the v2 spec and the current board; no old v1 tasks were added merely because their files remain present.
- [ ] No PR #67 dependency, silent CPU fallback, mocked real-model pass, unowned cleanup, bypass-based endpoint claim or unverified candidate identity remains in the claimed outcome.
- [ ] Actual Windows 5.1/package/provider behavior, both model devices and independent-host repetition are documented; required skips are not passes.
- [ ] Final public docs, instruction entrypoints and skill commands agree with the tested direction; historical records remain distinguishable.
- [ ] Final report lists tested artifacts/profiles, performance comparison, outstanding limits/blockers and next owner/action. It never says deployment-ready solely because static review or unit tests passed.
