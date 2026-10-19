# TASK-105: Final Release Correction And Qualification

**Status**: IN_PROGRESS - Task-105 corrections merged through PRs #109 and
#110. The same-source CPU/CUDA `v0.1.3-rc5` images and immutable, non-Latest
prerelease passed publication and integrity gates. Browser-downloaded integrity,
File Explorer extraction, exact-package Docker CPU/CUDA installation, and
combined-model device probes pass on the first host. Podman CPU/CUDA setup,
combined-model probes, provider and browser workflows, exports, and shipped
lifecycle checks pass. The bidirectional engine switch and dataset restore
pass. All four first-host profiles now also pass reboot persistence, including
dataset restore and new exports. Independent-host four-profile operational
evidence has been reviewed; the owner confirms dataset restore and comparable
same-area live-model testing. Final finding dispositions and qualification
reconciliation were accepted October 19 under ADR-026 in reviewed commit
`33bd3a3`. Fork draft-PR publication is authorized; review/merge, official
adoption/qualification, and handoff remain open. Task-105 remains active.
**Priority**: CRITICAL
**Type**: C (Runtime Correction / Release Qualification / Handoff)
**Estimated Effort**: 3-5 working days for implementation, review, builds, and
first-host qualification, plus the availability of the remaining independent
Windows hosts
**Owner**: `J-Schulein` until handoff; `cdcai` thereafter
**Working Candidate Identity**: `v0.1.3-rc5`, immutable and non-Latest, from
accepted `main` `835cbb910573a931350c5b704d14496952d7ef87`
**Official Release Identity**: Selected with the `cdcai` owner at adoption;
the candidate name does not reserve or authorize `v0.1.3` final

**RC5 publication checkpoint (2026-10-14)**: PR #109 merged as `08ac8ef` and
PR #110 as `835cbb9`; accepted source is
`835cbb910573a931350c5b704d14496952d7ef87`. Authorized CPU and CUDA
publish runs `38609314677` and `38609372836` passed local and exact-published-
digest security checks with baseline 396, candidate 79, five accepted residuals,
zero blockers, and zero severity escalations. The pinned image digests are CPU
`sha256:833dbe0d0097ffcc9e52dcf39d64f25cf503c3c9ffc806f55c42b60e452845d5`
and CUDA
`sha256:df0f30ac1bed4514d50c5b11eeac4ea64e38e6575bb209448fea4c53e5347890`.
The clean-source control ZIP hashes are CPU
`dfcc653eef4d0c9666604d6455797c123b757d92d4507ad1d451032f5cdd7a8f`
and CUDA
`c418e1948ed2719cd8c3678b612addccf468a139aafc97f99d3f4bd7676974d0`;
the shared asset ZIP is
`00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
All three sidecars and internal control-package checksums passed. The first
publication reported `isImmutable=false`; with separate owner approval, that
release and tag were removed, repository release immutability was enabled,
and the identical six bytes were republished. GitHub now reports
`isImmutable=true`, `isPrerelease=true`, and the accepted source tag; `v0.1.2`
remains Latest. All six assets downloaded through GitHub CLI from the first
publication matched its published sizes and SHA-256 values; the immutable
replacement reports the same six hashes and sizes, and `gh release verify`
validated GitHub's signed release attestation for the accepted source and all
six assets. This is a public-byte
integrity check, not the required browser-download/Mark-of-the-Web proof. The first-host
Podman CPU `-VerifyOnly` rehearsal passed release manifest and both ZIP
checksums, then stopped because C: had 11.65 GB free against the shipped
15 GB minimum. After deduplicating task-owned staging, C: had 12.39 GB free.
No runtime profile is credited as a pass from that rehearsal.

**RC5 first-host checkpoint (2026-10-14)**: The owner freed space, then used a
browser to download all six immutable release files. Every file's size and
SHA-256 matched the current GitHub release record and the three sidecars;
the downloaded ZIPs retained `ZoneId=3`. File Explorer extraction into a path
with spaces retained `ZoneId=3` on the CPU/CUDA entry scripts and manifest.
Both control folders passed release-manifest and 74 internal checksum checks.
The exact CPU and CUDA packages passed `-VerifyOnly`, fresh Docker image pull,
asset import and hash verification, and launch on ports 5315/5316 with their
pinned digests and CPU/CUDA device policies. Docker CPU had a Google TLS error;
the guided repair selected the previously approved host CA, applied normal TLS
verification, and passed the shipped volume-preserving stop/start. The same CA
and repair path passed for Docker CUDA. Invalid test keys reached Google and
Azure over normally verified TLS in both profiles. The owner reports that
Google and Azure are configured in Docker CPU. The fixed 12-tile combined
YOLO/EfficientNet fixture passed in each image: 54 detections and expected
outputs, with both models on CPU for CPU and CUDA for CUDA. The published CPU
image also passed an explicit CUDA-required/unavailable negative probe.
Private raw logs and probe JSON stay under ignored `dist/task105-rc5-evidence`.
The owner then reported live Google and Azure model runs in both Docker CPU and
CUDA browser sessions and successful download controls. The host's Downloads
folder held two new parseable CSV files (38 and 44 rows), two valid KML files
(24 placemarks each), and two dataset ZIPs (26 entries each, both CRC-clean).
No exported coordinates or contents enter repository evidence. Both apps
reported both provider-configured booleans, and a public-place forward geocode
used the requested provider in each of the four app/provider combinations.
A public ZIP lookup returned HTTP 200 and an invalid ZIP then valid retry gave
HTTP 400 then 200 on both ports. The served app's four local Help pages were
byte-identical to each profile's extracted package pages. Docker CUDA's full
combined probe passed one warm-up and three measured runs at a 2.633402-second
median, 4.71% faster than the earlier same-host RC4 baseline with identical
fixture tile hashes and final normalized results. Its identity/kernel and
injected-secondary-failure/clean-follow-up probes passed. Docker CPU's same
one-warm-up/three-measured combined probe passed at a 49.606243-second median,
1.21% faster than the earlier same-host RC4 baseline with identical fixture
tile hashes and final normalized results. The owner reports CUDA browser
cancel/retry and ZIP navigation succeeded. Both profiles then passed their
shipped volume-preserving stop/start; readiness, exact digest, intended device,
eight original named volumes, both provider configured booleans, asset checks,
and Google/Azure normal TLS status persisted. The owner refreshed both browser
sessions, found the review state usable, downloaded fresh dataset archives, and
restored results through each app's `Restore Dataset` control. Three new ZIPs
observed after relaunch opened and passed CRC checks (14 entries each); raw
archive contents remain private. Reboot, Podman, and independent-host cells
remain open; these Docker profiles are not yet full acceptance passes.

The owner then extracted separate Podman CPU/CUDA copies using File Explorer
from the same verified browser downloads, preserving `ZoneId=3` and a path
with spaces. Both passed all 74 internal checksums and release manifests.
Docker Desktop was closed before the rootless Podman runs. The fresh Podman
CPU and CUDA images pulled successfully; the first CUDA pull completed without
a false CDI timeout. Each package selected its verified package-local Compose
provider, imported the asset bundle, and reached the intended CPU or CUDA
device at the pinned digest. A guided CA repair used the same previously
approved host CA as Docker, verified normal Google TLS, and survived shipped
stop/start. The fixed 12-tile YOLO/EfficientNet probe passed on both Podman
profiles with 54 detections, expected normalized results, and the intended
device for both models. Podman CUDA also passed its Task-103 identity/kernel,
one-warm-up/three-measured combined, and injected classifier failure followed
by a clean run. Its four served Help pages were byte-identical to the exact
extracted package pages. Normal Google/Azure TLS transport from both restarted
containers passed without keys or disabled verification (Google HTTP 200,
Azure HTTP 401 without credentials). The Podman CPU one-warm-up/three-measured
combined probe passed at a 44.923575-second median; Podman CUDA's median was
2.508349 seconds. All four Docker/Podman combined probes used the identical
frozen tile hashes and passed their expected outputs. Browser workflows remain
open, so neither Podman profile is yet a full
acceptance pass.

The host's default `python` resolves to Python 3.14.7. The shipped Podman
Compose installer initially failed because the pinned PyYAML 6.0.2 wheel is
not available for that interpreter. Installed Python 3.12.10 was then selected
through the shipped helper's `-Python` option; an ordinary retry installed the
approved package-local provider, with no force or manual deletion. The user
guide calls for Python 3.12 but its example invokes the default `python` and
does not show interpreter selection. This host-specific prerequisite deviation
and documentation gap remain open for disposition; it is not a clean beginner
default-path pass. Private provider logs and wheel evidence remain ignored.

The owner configured both approved providers through each Podman app without
sharing keys. Both `/api/config/status` responses show Google and Azure
configured; a public-place forward geocode selected the requested provider in
all four Podman app/provider combinations. Both public ZIP lookup endpoints
returned HTTP 200 on retry after a 25-second first-request timeout while the
apps were under initial-use workload. Direct browser model and export behavior
then passed owner observation on both Podman profiles with
Google and Azure: maps loaded, bounded model searches and result views worked,
and the separate CSV/KML/dataset controls downloaded files. Three new CSVs
(42, 43, and 43 data rows), three XML-valid KMLs (22, 31, and 27 placemarks),
and three dataset ZIPs (26 entries each, CRC-clean) were independently found
in Downloads. The exact association between these three export sets and the
four app/provider searches was not collected; per-provider export coverage is
not inferred. The owner confirmed Podman CUDA browser cancel/retry, with
cancelled results excluded and a successful next request, and public ZIP
navigation. Both Podman profiles then passed their shipped volume-preserving
stop/start: the original eight named volumes in each, both provider configured
booleans, assets, intended CPU/CUDA device, pinned digest, and normal
Google/Azure TLS persisted. After refresh, the owner observed that the prior
in-memory result view was no longer visible, as expected; restoring previously
downloaded datasets worked without error. A new post-restart download from
each app was then verified. Reboot remains open.
The owner confirmed fresh post-restart downloads on both Podman apps; two new
CSVs (29 data rows each), two XML-valid KMLs (13 and 10 placemarks), and two
dataset ZIPs (14 entries each, CRC-clean) were independently found. Both RC5
Podman containers stopped via their shipped scripts without volume removal.
The rootless Podman machine stopped, Docker Desktop started cleanly, and both
previously tested RC5 Docker packages restarted through their shipped scripts.
Each Docker profile retained all eight named volumes created before the switch,
both provider configured booleans, assets, intended device, exact digest, and
normal Google/Azure TLS. The old RC9 Podman containers were still running
before the machine stop and have `always` restart policy. The owner confirmed
Docker CPU/CUDA browser dataset restore, review controls, and fresh downloads;
two dataset ZIPs (27 entries each, CRC-clean), one XML-valid KML, and one CSV
were independently found after the switch. Docker browser recovery passed.
The shipped Docker stops and Docker Desktop quit then succeeded. The rootless
Podman machine restarted; its RC9 containers did not auto-start despite the
`always` policy, so the two existing containers were explicitly started and
returned healthy without changing their volumes. The shipped RC5 Podman starts
then passed. Each RC5 profile retained its exact original eight named volumes,
both configured providers, assets, intended device, exact pinned digest,
selected package-local Compose provider, and normal Google/Azure TLS. The
owner refreshed both RC5 Podman apps and confirmed dataset restore and review
controls work after the full engine round trip. At this checkpoint, reboot and
independent-host qualification remained open.

**RC5 first-host reboot checkpoint (2026-10-14)**: Windows rebooted after the
bidirectional engine switch. Docker Desktop started cleanly, and both exact
RC5 Docker packages started through their shipped scripts. CPU and CUDA each
retained the original eight named volumes, both provider-configured booleans,
assets, intended device, pinned digest, and normal Google/Azure TLS. The owner
refreshed both apps, restored previously downloaded datasets, used the review
controls, and downloaded new files without error. Two new dataset ZIPs (27
entries each) opened and passed CRC checks. The shipped Docker stops and Docker
Desktop quit succeeded. The rootless Podman machine appeared running, but its
Windows client socket refused connections; a normal machine stop/start restored
the connection without deleting containers or volumes. Both exact RC5 Podman
packages then started through their shipped scripts, selected the intended
CPU/CUDA devices and pinned digests, and retained their original eight named
volumes, both configured providers, assets, and normal Google/Azure TLS. The
owner refreshed both Podman apps, restored datasets, used review controls, and
downloaded new files without error. Two new dataset ZIPs (27 entries each)
opened and passed CRC checks. The two retained RC9 containers were explicitly
started and returned healthy. This host's four-profile reboot-persistence gate
passes. The Python 3.12 selection deviation remains recorded; no CPU-only or
Podman-without-Docker claim follows from these results. The exact RC5
independent-host four-profile run remains required.
The owner then repeated browser cancel/retry and public ZIP lookup on the
Podman CPU and Docker CPU apps. Both reported cancelled results excluded from
the map/list, successful next search, and ZIP map navigation. The previously
recorded CUDA checks cover the same changed behavior on both engines. Docker
CPU/CUDA were restored via shipped scripts and finished ready and healthy,
with the correct device/digest, both configured providers, and eight named
volumes each. The Podman machine is stopped while Docker Desktop runs.

**Independent-host clarification (2026-10-16)**: The owner confirms thorough
dataset download/restore testing passed on the independent host, supplementing
the supplied report's "not covered" entry. The repeated same-area NYC searches
are credited as comparative live-model evidence. See the
[RC5 evidence intake](./TASK-105/RC5-INDEPENDENT-HOST-EVIDENCE-INTAKE-2026-10-16.md)
for verified artifact identities, extract integrity, provenance, test methods,
and remaining finding dispositions. The real-model and restore results are
credited without claiming a frozen-fixture benchmark absent from the packet.

## Objective

**October 19 closeout review**: The
[qualification matrix](./TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md)
reconciles the two-host results, owner restore confirmation, F1-F10/N1-N14
dispositions, dated scans, and unchanged public identities.
[ADR-026](../../decisions/026-rc5-bounded-candidate-acceptance.md) records the
short-path/Python support restrictions and the explicit independent probe
exception. The [operating addendum](../../../docs/release/rc5-operations-addendum.md)
and [cdcai packet](../../../docs/release/task105-cdcai-handoff.md) are prepared
for review. The owner approved bounded acceptance of reviewed commit `33bd3a3`
and separately authorized this fork branch and draft PR. These are separate
supplements, not changed RC5 bytes. Review/merge, cdcai adoption, and official
build/publication remain pending actions.

Resolve or explicitly disposition every RC9 independent-host finding, rebuild
the CPU and CUDA 12.8 artifacts from one accepted `main` source, qualify the
exact browser-downloaded package bytes, complete the ADR-025 two-host
independent run, and prepare an evidence-backed final-candidate transfer packet for
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
- WHEN final-candidate readiness is claimed, THE project SHALL complete the
  ADR-025 host allocation: all four corrected-candidate profiles on this
  Windows NVIDIA host and on the separate independent NVIDIA host. CPU-only
  and Podman-without-Docker environments SHALL remain outside the tested claim.

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

- [x] Freeze one accepted `main` source commit after both correction PRs merge.
- [x] Recheck ADR-024 residual versions, severities, fix availability, and
  expiry before dispatch. Any changed/new/expired finding blocks.
- [x] With separate owner authorization, dispatch CPU and CUDA 12.8 images with
  `push_latest=false`. Require local scan-before-login and exact-published-
  digest confirmation for both flavors.
- [x] Assemble clean-source, digest-pinned CPU and CUDA control ZIPs using the
  selected `v0.1.3-rc.N` identity and reuse only the exact verified asset ZIP.
- [x] Verify authoritative sidecars, all internal checksums, manifests,
  licenses/notices, forbidden-file inventory, Help parity, and package secret
  hygiene.
- [x] With separate owner authorization, publish the selected `v0.1.3-rc.N` as an
  immutable, non-Latest GitHub prerelease. Do not upload mutable replacement
  assets.

### Phase 6 - Qualify the exact public bytes

- [x] On the first host, browser-download the six public assets and verify the
  release-page SHA-256 values before extraction.
- [ ] Run the affected fresh-install tests first: Podman GPU with no local
  candidate image, provider installation from both shell parents, ordinary
  retry after an injected safe failure, selected-provider reporting, mixed-
  runtime recovery, exports, and late cancellation.
- [x] Complete the full Docker CPU, Docker CUDA, Podman CPU, and Podman CUDA
  workflow against the exact downloaded packages: providers, managed TLS,
  ZIP lookup, real models/device, cancel/retry, controlled recovery, review,
  exports, stop/relaunch, and reboot.
- [x] Reconcile the fixed combined-model probe, CUDA-unavailable negative,
  shared-script faults, and warm performance evidence: first-host exact-image
  reports pass; independent evidence reuse is approved under ADR-026. No
  independent frozen-fixture/warm report is claimed.
- [x] Repeat all four corrected-candidate functional profiles on the separate RC9
  independent NVIDIA Windows host, including explicit CPU mode for both CPU
  profiles and focused browser checks for the changed export/cancel flows.
  See the closeout matrix for the short-path deviations and formal-probe
  evidence reuse separately approved by the owner under ADR-026.
- [ ] Require ordinary-account, path-with-spaces, Mark-of-the-Web-preserving
  extraction and shipped instructions. Record deviations as gaps, not passes.
- [ ] Retain raw sensitive evidence privately; commit only sanitized summaries,
  hashes, counts, anonymous host IDs, and pass/fail status.

### Phase 7 - Final-candidate closeout and handoff

- [x] Prepare reconciliation of every matrix cell to the exact selected candidate source, image
  digests, package hashes, asset hash, documentation, and evidence references.
  The owner approved the acceptance exceptions under ADR-026 on October 19.
- [x] Confirm the GitHub prerelease assets and tags have not changed since
  browser download. Any byte change requires new hashes and affected reruns.
- [x] Prepare release notes, support/rollback instructions, maintenance
  obligations, residual-expiry handoff, and cdcai transfer packet.
  Draft-PR publication is authorized; review/merge and named maintenance-custodian
  acceptance remain pending.
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
- [ ] This Windows NVIDIA host and the separate independent NVIDIA host each
  pass all four exact-byte corrected-candidate profiles under ADR-025; the
  CPU-only and Podman-without-Docker environments are not claimed as tested.
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
- Arrange the corrected-candidate run on this host and the separate RC9
  independent NVIDIA host; record Docker/Podman coexistence on the available
  machines and keep CPU-only/Podman-without-Docker claims out of the release.
- Enter approved Google/Azure credentials during live tests when needed; no
  credentials enter repository evidence.
- Separately authorize CPU/CUDA GHCR dispatches, fork GitHub prerelease
  publication, the later official cdcai build/publication, and any cdcai
  repository mutation.
- If work approaches October 31, either complete publication before the
  residual expiry or approve a new evidence-backed security disposition.

## Evidence

- [RC9 independent-host sanitized evidence intake](./TASK-105/RC9-INDEPENDENT-HOST-EVIDENCE-INTAKE-2026-10-14.md)
- [RC5 independent-host run sheet](./TASK-105/RC5-INDEPENDENT-HOST-RUN-2026-10-14.md)
- [RC5 independent-host evidence intake and owner clarification](./TASK-105/RC5-INDEPENDENT-HOST-EVIDENCE-INTAKE-2026-10-16.md)
- [RC5 qualification closeout and finding dispositions](./TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md)
- [Accepted bounded candidate decision](../../decisions/026-rc5-bounded-candidate-acceptance.md)
- RC9 source report and sanitized ZIP remain outside the repository under the
  release owner's evidence custody.

---

## Implementation Log

### 2026-10-14 - Owner narrows the host allocation

The release owner directed final-candidate testing on this Windows machine
and the prior RC9 independent Windows machine, following the same four-profile
pattern. [ADR-025](../../decisions/025-two-host-final-candidate-qualification.md)
supersedes the additional CPU-only host and Podman-without-Docker installation
gates. This changes the prospective candidate claim only; the RC9 intake and
earlier gate assessments below remain historical. Each host must test the
corrected exact downloads. No candidate or stable readiness is inferred from
the old RC9 results, and untested environments stay outside the claim.

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

**Host allocation at this checkpoint (superseded by ADR-025 above)**: The
release owner reports that only this Windows machine
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
