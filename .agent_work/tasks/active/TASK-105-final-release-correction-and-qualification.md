# TASK-105: Final Release Correction And Qualification

**Status**: IN_PROGRESS - RC9 independent-host evidence is accepted as a
strong four-profile pass on one NVIDIA host, but its fresh-install findings and
the remaining host allocation prevent a final release claim. Planning and
evidence intake are complete; bounded corrections are under local regression
review and have not been merged or qualified as a final candidate.
**Priority**: CRITICAL
**Type**: C (Runtime Correction / Release Qualification / Handoff)
**Estimated Effort**: 3-5 working days for implementation, review, builds, and
first-host qualification, plus the availability of the remaining independent
Windows hosts
**Owner**: `J-Schulein` until handoff; `cdcai` thereafter
**Working Candidate Identity**: The next unused `v0.1.3-rc.N`, selected only
after checking GitHub releases/drafts, Git tags, and GHCR tags; publish only as
an immutable, non-Latest fork prerelease
**Official Release Identity**: Selected with the `cdcai` owner at adoption;
the candidate name does not reserve or authorize `v0.1.3` final

## Objective

Resolve or explicitly disposition every RC9 independent-host finding, rebuild
the CPU and CUDA 12.8 artifacts from one accepted `main` source, qualify the
exact browser-downloaded package bytes, complete the required independent-host
allocation, and prepare an evidence-backed final-candidate transfer packet for
project handoff.

RC9 remains an immutable validation prerelease and evidence baseline. It is not
modified, relabeled, or promoted.

## User Outcome

A beginner who follows the supplied Windows instructions should not encounter
a false Podman GPU setup failure, an unexplained provider-installer failure, a
dangerous Docker/Podman recovery choice, a misleading readiness check, or a
silent missing export. The final release claim must be supported by the exact
public bytes and all required host/profile evidence.

## Requirements (EARS Notation)

- WHEN a fresh Podman GPU host does not already have the large CUDA image, THE
  GPU provisioning workflow SHALL avoid reporting CDI setup failure merely
  because the image pull exceeds a short probe timeout.
- WHEN a supplied `.cmd` wrapper is launched from Windows PowerShell 5.1 or a
  PowerShell 7 parent, THE provider installer SHALL use a compatible SHA-256
  implementation and SHALL not inherit an incompatible module path.
- IF provider installation fails after creating package-local staging state,
  THEN a normal documented retry SHALL safely recover without requiring an
  undocumented manual deletion or `-Force` discovery step.
- WHEN Docker Desktop and Podman are installed together, THE documentation
  SHALL warn users about startup order, SHALL say not to select **Reset to
  factory defaults**, and SHALL provide volume-preserving recovery steps.
- WHEN Podman readiness is checked, THE instructions SHALL verify the provider
  TowerScout actually selected rather than relying on an unrelated global
  `podman compose version` result.
- WHEN a cancelled request finishes too late for server-side interruption, THE
  frontend SHALL discard that cancelled request's results and SHALL permit the
  next request only when the shared detection slot is ready.
- WHEN users export CSV or KML, THE application SHALL initiate an explicit
  user-selected file download, use the correct media type, and avoid claiming
  success for an additional browser-blocked download.
- WHEN geocoding is limited, THE UI/log guidance SHALL accurately identify the
  attempted provider behavior and explain that some results may retain
  coordinates without a street address.
- WHEN the final Podman and GPU prerequisites are documented, THE manuals
  SHALL distinguish the tested rootless path, tested Python version, and the
  actually qualified GPU list from merely observed compatible alternatives.
- WHEN CPU and CUDA images are built from the same source, THE checked-in
  frontend bundle SHALL be reproducible or the only permitted difference SHALL
  be generated, declared, and verified before release.
- WHEN a Windows-only ZIP entry convention remains unchanged, THE project
  SHALL record that disposition as a support-boundary decision rather than
  implying cross-platform archive portability.
- BEFORE stable release, THE project SHALL pass the strict security gate while
  the ADR-024 residual policy is unexpired, or obtain a new written owner
  decision before any build or publication after October 31, 2026.
- WHEN final-candidate readiness is claimed, THE project SHALL complete the v2 host
  allocation, including a CPU-only Windows host, two different NVIDIA Windows
  hosts, and a Podman environment without Docker Desktop installed.

## RC9 Finding Disposition

| ID | RC9 finding | Required disposition before stable release |
| --- | --- | --- |
| F1 | Fresh Podman GPU provisioning times out while pulling the CUDA image | Code fix plus a fresh/no-image regression. A short timeout may remain for a true readiness probe, but not for a first image pull. |
| F2 | Docker Desktop and Podman Desktop can race for the Docker pipe at login | Prominent coexistence and safe-recovery guidance. Never advise factory reset. Confirm the instructions on a mixed-runtime host. |
| F3 | PowerShell 7 parent can break `Get-FileHash` in the Windows PowerShell child | Wrapper isolation and/or .NET hashing fallback, tested from Windows PowerShell 5.1 and PowerShell 7. |
| F4 | Failed provider install leaves a directory that blocks the documented retry | Transactional staging/cleanup or safe incomplete-install replacement; ordinary `-Apply` retry must pass. |
| F5 | `podman compose version` may report Docker Desktop's provider instead of TowerScout's selected provider | Replace the readiness instruction with package-selected-provider evidence. |
| F6 | A late GPU cancel can finish on the server | Confirm the existing client discards the cancelled result; add a focused frontend regression. Treat remaining server work as bounded resource behavior, not a displayed success. |
| F7 | Edge can block the second download; KML uses the CSV media type | Provide separate explicit CSV/KML downloads, correct KML media type, retain dataset ZIP behavior, and update user guidance. |
| F8 | Geocoding limits and provider wording can confuse users | Correct provider wording and explain coordinate-only results without changing the rate limit solely to hide the observation. |
| F9 | Rootful Podman, Python 3.13, and missing GPU-list wording do not match the tested-support text | Keep rootless/Windows Python 3.12 as the supported tested path unless separately qualified; add the actual GPU qualification list and clarify observed-but-unclaimed alternatives. |
| F10 | CPU/CUDA bundle build dates differ; ZIP entries use Windows separators | Make the bundle timestamp reproducible if the bounded change passes bundle tests. Retain Windows ZIP separators only as an explicit Windows-package limitation unless a safe, independently tested packaging correction is selected. |

Every row must end as `fixed`, `verified_no_change`, or
`documented_and_owner_accepted`. None may silently disappear from closeout.

## Scope Boundaries

### In scope

- `scripts/lib/TowerScoutPodmanGpu.ps1` and focused Podman GPU tests.
- Provider installer wrappers/scripts, package-local staging behavior, and
  Windows PowerShell 5.1/PowerShell 7 compatibility tests.
- Focused Docker/Podman coexistence, provider-readiness, Python, GPU-support,
  geocoding, export, and troubleshooting documentation.
- Frontend cancellation and export behavior, source/bundle synchronization,
  and focused browser contracts.
- Reproducible frontend build metadata if it can be made deterministic without
  changing runtime behavior.
- Same-source CPU/CUDA security qualification, control ZIP assembly, browser
  download, four-profile testing, independent hosts, release evidence, and
  handoff preparation.

### Out of scope

- PR #67 or Task-087 launcher redesign.
- Task-058 background-job or general cancellation architecture.
- New map providers, model changes, thresholds, NMS, tiling, or ML dependency
  migration.
- Rootful Podman support unless separately selected and qualified.
- Python 3.13 support merely because one reviewer host succeeded with it.
- Signature-enforcing endpoint support outside ADR-023.
- Pip removal, Debian migration, baseline expansion, or residual-policy
  weakening.
- cdcai repository mutation before separate handoff authorization.

## Implementation Plan

### Phase 0 - Preserve evidence and freeze the correction list

- [x] Review the independent-host report as evidence, not instructions.
- [x] Validate the sanitized ZIP structure, JSON readability, internal
  manifest, artifact identities, and absence of obvious secrets.
- [x] Record the sanitized evidence package by filename and SHA-256 without
  committing the binary ZIP or raw evidence.
- [x] Map all ten findings and the remaining host gaps into this task.
- [ ] Inventory GitHub releases/drafts, Git tags, and GHCR flavor tags, then
  select one completely unused `v0.1.3-rc.N` identity before immutable image
  dispatch. Update all package and release inputs before any build.

### Phase 1 - Add focused regressions before fixes

- [ ] Reproduce F1 with an absent CUDA image and a deliberately slow/fake pull;
  distinguish download time from the final bounded GPU smoke.
- [ ] Reproduce F3/F4 from both Windows PowerShell 5.1 and a PowerShell 7 parent,
  including a first failed install followed by ordinary `-Apply` retry.
- [ ] Add a provider-selection contract showing that TowerScout's package
  provider is authoritative even when global `podman compose version` resolves
  Docker Desktop Compose.
- [ ] Add a frontend late-cancel test proving a completed stale response is not
  processed or displayed.
- [ ] Add export tests for separate user actions, filenames, media types, and
  success/error messaging.
- [ ] Add a deterministic bundle-build assertion before changing generated
  metadata behavior.

### Phase 2 - Implement the bounded corrections

- [ ] Make Podman GPU provisioning pull-aware. Preserve fail-closed CDI/device
  validation and a real post-pull GPU smoke; do not convert failure into an
  unconditional warning.
- [ ] Isolate wrapper module lookup and use the existing safe hash fallback or
  equivalent .NET SHA-256 path in the provider installer.
- [ ] Download/install through a uniquely named staging directory and promote
  only after checksum and environment creation succeed. Remove only task-owned
  incomplete staging on failure.
- [ ] Make a normal retry idempotent for a partial package-local install while
  preserving the managed-cache path guard.
- [ ] Preserve the current cancellation request identity and stale-response
  guard; change production behavior only if the regression disproves it.
- [ ] Split CSV and KML into separate explicit download actions, pass the
  correct MIME type, revoke temporary object URLs, and keep dataset ZIP export
  unchanged.
- [ ] Correct geocoding provider wording without exposing provider responses or
  changing validated provider fallback behavior.
- [ ] Make bundle build metadata deterministic from a supplied/repository
  source timestamp if the generated bundle remains byte-consistent and all
  bundle guards pass.

### Phase 3 - Update user and support documentation

- [ ] Add the Docker-before-Podman startup order, **Quit** guidance, explicit
  warning against factory reset, and volume-preserving recovery steps.
- [ ] Replace raw `podman compose version` readiness claims with the selected
  provider line emitted by TowerScout setup/status.
- [ ] Explain fresh Podman GPU first-pull duration and the difference between
  CDI configuration, image download, and the final GPU smoke.
- [ ] Keep Python 3.12 and rootless Podman as the tested support boundary;
  describe Python 3.13/rootful observations only as unqualified.
- [ ] Add the actual tested NVIDIA GPU/architecture list to the release notes
  and ensure Quick Start links to a real section.
- [ ] Explain browser download controls and coordinate-only geocoding results.
- [ ] Update matching Markdown/HTML pages and verify in-app Help routes and
  links before candidate freeze.

### Phase 4 - Review and merge the corrections

- [ ] Use one focused runtime-installation PR for F1/F3/F4/F5 and their tests.
- [ ] Use one focused frontend/documentation PR for F2/F6-F10 and their tests,
  unless the first PR review identifies a safer single-PR boundary.
- [ ] Pass all focused Windows, frontend, package, documentation-link, security,
  and existing required CI checks.
- [ ] Run `git diff --check`, the agent-work quick check, and the strict
  `.agent_work` validator.
- [ ] Review automated comments individually and merge only after exact-head CI
  is green.

### Phase 5 - Freeze and publish the corrected final candidate

- [ ] Freeze one accepted `main` source commit after both correction PRs merge.
- [ ] Recheck ADR-024 residual versions, severities, fix availability, and
  expiry before dispatch. Any changed/new/expired finding blocks.
- [ ] With separate owner authorization, dispatch CPU and CUDA 12.8 images with
  `push_latest=false`. Require local scan-before-login and exact-published-
  digest confirmation for both flavors.
- [ ] Assemble clean-source, digest-pinned CPU and CUDA control ZIPs using the
  selected `v0.1.3-rc.N` identity and reuse only the exact verified asset ZIP.
- [ ] Verify authoritative sidecars, all internal checksums, manifests,
  licenses/notices, forbidden-file inventory, Help parity, and package secret
  hygiene.
- [ ] With separate owner authorization, publish the selected `v0.1.3-rc.N` as an
  immutable, non-Latest GitHub prerelease. Do not upload mutable replacement
  assets.

### Phase 6 - Qualify the exact public bytes

- [ ] On the first host, browser-download the six public assets and verify the
  release-page SHA-256 values before extraction.
- [ ] Run the affected fresh-install tests first: Podman GPU with no local
  candidate image, provider installation from both shell parents, ordinary
  retry after an injected safe failure, selected-provider reporting, mixed-
  runtime recovery, exports, and late cancellation.
- [ ] Complete the full Docker CPU, Docker CUDA, Podman CPU, and Podman CUDA
  workflow against the exact downloaded packages: providers, managed TLS,
  ZIP lookup, real models/device, cancel/retry, controlled recovery, review,
  exports, stop/relaunch, and reboot.
- [ ] Run the fixed combined-model probe, explicit CUDA-unavailable negative,
  required shared-script faults, and warm performance checks where the v2 gate
  requires them.
- [ ] Repeat the required cells on a CPU-only Windows host, a second NVIDIA
  Windows host, and a Podman environment without Docker Desktop installed.
- [ ] Require ordinary-account, path-with-spaces, Mark-of-the-Web-preserving
  extraction and shipped instructions. Record deviations as gaps, not passes.
- [ ] Retain raw sensitive evidence privately; commit only sanitized summaries,
  hashes, counts, anonymous host IDs, and pass/fail status.

### Phase 7 - Final-candidate closeout and handoff

- [ ] Reconcile every matrix cell to the exact selected candidate source, image
  digests, package hashes, asset hash, documentation, and evidence references.
- [ ] Confirm the GitHub prerelease assets and tags have not changed since
  browser download. Any byte change requires new hashes and affected reruns.
- [ ] Complete release notes, support/rollback instructions, maintenance
  obligations, residual-expiry handoff, and cdcai transfer packet.
- [ ] At adoption, have the `cdcai` owner and project lead select the official
  tag/title and authorize the official build and publication. Do not relabel
  or promote the fork candidate as the official release.
- [ ] Build the official images/packages consistently for the selected
  identity, then repeat exact-public-byte integrity, security, and affected
  runtime checks before any stable/Latest claim. Carry candidate evidence
  forward only where the official delta is proven not to affect the result.
- [ ] Close Tasks 091/092/093/097/103/104/105 only when their actual remaining
  gates are reconciled; do not mark blocked or unrun cells complete.

## Automated Validation Minimum

- Focused Podman GPU, provider installer, bootstrap/Compose, Windows runtime,
  cancellation, export, frontend bundle, and documentation contract tests.
- Existing required Python and frontend CI suites for every touched surface.
- Release package/manifest, container workflow, dependency/Fiona, strict
  Trivy comparator, SBOM, and sensitive-file checks.
- Windows PowerShell 5.1 behavioral execution from a spaced path; PowerShell 7
  parent compatibility for shipped `.cmd` wrappers.
- `python .agent_work/scripts/validate_agent_work.py` and `git diff --check`.

## Release Acceptance Criteria

- [ ] Every F1-F10 row has a recorded disposition and evidence.
- [ ] All corrected code paths have focused regressions that failed before and
  pass after the change.
- [ ] Required CI passes at the accepted source commit.
- [ ] CPU and CUDA images share the accepted source label and pass local plus
  exact-digest security gates with zero blocking findings or escalations.
- [ ] The selected candidate control ZIPs bind the exact image digests and pass internal
  and external checksum verification.
- [ ] Exact public browser-downloaded bytes pass all four profiles locally.
- [ ] The CPU-only host, two distinct NVIDIA hosts, and Podman-without-Docker
  allocation satisfy the v2 independent-host requirement.
- [ ] Both models execute on the required device; no CPU fallback passes a GPU
  profile.
- [ ] Provider, TLS, persistence, recovery, export, cancellation, Help, and
  reboot evidence is complete and sanitized.
- [ ] ADR-023 unsigned-package boundaries remain accurate.
- [ ] ADR-024 residuals are unexpired at build and publication, or a new
  written owner decision supersedes the expiry before publication.
- [ ] The fork candidate remains immutable and non-Latest.
- [ ] Official cdcai build/publication and any stable/Latest promotion have
  explicit owner approval and exact-byte evidence for the official artifacts.

## Stop Conditions

- Any new or changed HIGH/CRITICAL finding, severity escalation, incomplete
  scan, identity mismatch, or expired residual.
- Any need to overwrite an immutable image tag or published release asset.
- Podman GPU still reports failure solely because an ordinary first pull is
  slow, or provider installation/retry still needs an undocumented repair.
- A required exact-byte, profile, device, provider, recovery, export, reboot,
  or independent-host cell fails or is unavailable.
- Documentation and observed behavior disagree on a beginner's standard path.
- A proposed correction requires reopening PR #67/Task-087, weakening TLS or
  model/security controls, deleting volumes, or expanding the support boundary.

## Owner Actions

- Confirm the next available `v0.1.3-rc.N` identity before immutable image
  dispatch.
- Arrange or confirm access to the remaining CPU-only and second NVIDIA hosts;
  ensure one required Podman run has no Docker Desktop installation.
- Enter approved Google/Azure credentials during live tests when needed; no
  credentials enter repository evidence.
- Separately authorize CPU/CUDA GHCR dispatches, fork GitHub prerelease
  publication, the later official cdcai build/publication, and any cdcai
  repository mutation.
- If work approaches October 31, either complete publication before the
  residual expiry or approve a new evidence-backed security disposition.

## Evidence

- [RC9 independent-host sanitized evidence intake](./TASK-105/RC9-INDEPENDENT-HOST-EVIDENCE-INTAKE-2026-10-14.md)
- RC9 source report and sanitized ZIP remain outside the repository under the
  release owner's evidence custody.

---

## Implementation Log

### 2026-10-14 - Local correction checkpoint

**Branch**: `feature/task-105-final-release-correction`, based on accepted
`main` at `9065fe77aa757aea32f22a8dd1d0dc7df83d43e9`. Existing uncommitted
Task-105 planning and RC9 evidence edits were preserved on the branch.
The bounded corrections are recorded as local commits `b3817c6` (Podman GPU
and provider installer) and `c3171db` (frontend, docs, and packaging note).
They have not been reviewed or merged; only the first commit has exact-head CI.
After explicit owner approval, both branches were pushed to the fork and
opened as draft PRs: [runtime/provider PR #109](https://github.com/J-Schulein/TowerScout/pull/109)
against `main` at `b3817c6`, and [frontend/docs PR #110](https://github.com/J-Schulein/TowerScout/pull/110)
against the runtime branch, containing frontend correction `c3171db` and the
approved Task-105 tracking files. All reported PR #109 exact-head
checks passed at `b3817c6`, including Python 3.11/3.12, frontend, Windows
helper, controller, Docker frontend stage, security, and Trivy; the build job
was skipped by workflow conditions. PR #110 reported no checks at initial
inspection because it is stacked on the runtime branch and CI targets PRs
against `main`. Neither PR has been reviewed or merged; PR #110 exact-head CI
remains open.

**Implemented for review**: F1 separates a missing GPU image pull from the
60-second CDI smoke; F3/F4 use .NET SHA-256, isolate the Windows PowerShell
module path, stage and verify the provider before promotion, and permit an
ordinary retry of managed partial state. F6 gained a late-response regression
and required no production change. F7 uses separate CSV/KML user actions and
correct media types. F8 corrects imagery/geocoding and coordinate-only
wording. F10 replaces the changing bundle date with a source fingerprint;
the Windows-only ZIP separator convention is documented. F2/F5/F9 received
focused coexistence, selected-provider, and tested-support instructions.

**Checks passed**: the isolated Windows PowerShell 5.1 provider install test
covered failure, normal retry, promotion, idempotence, and a CMD child with a
poisoned module path. Direct PowerShell GPU mocks covered dry-run, verify-only,
stale CDI, and missing-image pull timing. Focused Node export, cancellation,
bundle reproducibility, global-contract, debug-logging, and provider-state
checks passed. The documentation command checker, `git diff --check`, strict
agent-work validator, Python compile, and dirty-source local package/manifest
rehearsal passed. The rehearsal is not a release artifact.

**Gaps**: `pytest`, application Python dependencies, and PowerShell 7 are
unavailable in the current local environment. The real pinned provider wheel
could not be downloaded here; the installer regression used a synthetic local
wheel. Browser/Edge, fresh Podman GPU, mixed-runtime, exact candidate, strict
security, and independent-host runs remain open. The GitHub release list
still contains draft `v0.1.3-rc4`; the remote tag query found no matching
`v0.1.3-rc*` tag. GHCR package-version inventory returned HTTP 403 because the
current token lacks `read:packages`. No candidate identity is selected.

**Additional review**: The F4 regression now injects an existing partial
managed install and verifies that a normal retry succeeds while preserving
the former directory. The existing provider-selection test now simulates a
global Docker Desktop Compose result while TowerScout selects its configured
package provider. Both Windows behavioral checks passed. Legacy installer and
export documentation assertions were updated and passed as direct checks;
the complete Python suite still requires `pytest` and app dependencies.

**Host allocation**: The release owner reports that only this Windows machine
and the previous RC9 independent NVIDIA host are available. These can support
first-host and repeat independent-host work after publication, but cannot
establish the required CPU-only Windows host or a Podman host without Docker
Desktop installed. The second NVIDIA host cell may use the existing
independent host only after testing the exact corrected candidate bytes.
The v2 independent-host acceptance criterion therefore remains open.

**Next**: finish focused review and accepted-main integration, then recheck
security policy and exact identity before separately authorized CPU/CUDA
dispatch. A CPU-only host and Podman-without-Docker environment remain
unavailable for full qualification; repeat the second NVIDIA host only with
the corrected candidate.

### 2026-10-14 - Task activation and plan

**Objective**: Convert the RC9 independent-host findings into one bounded path
to an intended final release.

**Context**: RC9 passed all four profiles on the first host and one independent
NVIDIA host, but the reviewer reproduced first-use Podman GPU, mixed-runtime,
PowerShell/provider-install, provider-check, export, wording, and
reproducibility issues. The v2 CPU-only/second-NVIDIA/Podman-without-Docker
allocation remains incomplete.

**Decision**: Preserve RC9, implement and test the bounded corrections under
TASK-105, use the next available `v0.1.3-rc.N` identity as the immutable
non-Latest fork final candidate, and defer the official identity/build to the
cdcai adoption step required by ADR-017 and REL-003.

**Output**: Requirements, dispositions, phased implementation plan, acceptance
criteria, stop conditions, evidence custody, and owner actions recorded.

**Validation**: The quick and strict agent-work validators, relative Markdown
link check, and `git diff --check` passed after the associated board,
requirements, design, and evidence-index updates.

**Identity preflight**: The live fork release list on 2026-10-14 already
contained a draft `v0.1.3-rc4`; therefore no exact `v0.1.3-rc.N` value is
reserved by this planning step. Selection requires the full release/tag/GHCR
inventory immediately before dispatch.

**Next**: Add the focused failing regressions for F1, F3/F4, F6, F7, and bundle
reproducibility before changing production behavior.
