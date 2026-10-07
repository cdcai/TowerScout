# TASK-092: Documentation Currentness And Information Architecture

**Status**: IN_PROGRESS - all five review rounds are dispositioned,
`J-Schulein` approved the content freeze at `524ba37`, bounded post-freeze
reproducibility corrections landed at `f8e191d`, and PR #94 merged as
`fc97b32` with green post-merge CI. PR #95 merged the bounded project-state
reconciliation as `a24d369`; local image/package documentation parity passes,
and the same-source RC8 CPU/CUDA image digests are frozen after strict local
and exact-published-digest security qualification. Final screenshots/video,
live permission verification, digest-pinned control-ZIP identities, packaged
and running-image Help validation, publication, and final W09/W10 gates remain
**Priority**: HIGH
**Type**: C (Documentation / Release)
**Child Work Plan**:
[GitHub Wiki Information Architecture And Local IT Guide](./TASK-092/wiki-information-architecture.md)

## Objective

Make agent, user, package, and in-app guidance agree with the exact main-based
release path and its observed support limits.

## Requirements

- WHEN current delivery direction changes, THE PROJECT SHALL update active
  entrypoints without rewriting historical records.
- WHEN a candidate is frozen, THE PROJECT SHALL align Markdown, manually
  maintained HTML, package allowlists, and in-app Help with the tested bytes.
- IF a profile or workflow is untested, THEN documentation SHALL NOT claim it
  is supported.
- WHEN the Windows control package remains unsigned, THE PROJECT SHALL state
  the supported wrapper/policy boundary, official-hash verification procedure,
  managed-endpoint exclusions, and safe stop/escalation behavior consistently
  in repository, packaged, release, and external user material.
- BEFORE exact package bytes are frozen for independent testers, THE PROJECT
  SHALL align Markdown and manually maintained HTML and validate the commands
  against the candidate behavior.
- WHEN detailed online guidance is introduced, THE PROJECT SHALL use a hybrid
  documentation model: focused Wiki navigation and evergreen role-based
  guidance plus complete version-specific offline instructions in the release
  package.
- WHEN the same topic appears on more than one surface, THE PROJECT SHALL name
  one authoritative source and use links or generated copies rather than
  independently maintained duplicate instructions where practical.
- WHEN repository `docs/` content changes, THE PROJECT SHALL account for both
  distribution surfaces: the control ZIP packages those files and the
  Dockerfile copies them into the CPU/CUDA images for the in-app `/docs/`
  routes.
- BEFORE the Wiki or video is published, THE PROJECT SHALL confirm the durable
  repository/location, editing permissions, owner and backup, release/version
  labels, public accessibility, and custody at handoff.

## Acceptance Boundary

W00 covers active agent/task direction. W09 completes public/end-user manuals
against actual artifacts before the source, documentation-aligned CPU/CUDA
images, and control ZIPs are frozen and distributed. W10 independent testers
must use those shipped instructions unchanged; a later packaged or in-app
documentation edit creates changed ZIP/image bytes and requires new identities
plus affected reruns.

The Wiki improves navigation but does not replace the offline package guide.
The authoritative candidate record must display exact ZIP hashes before the
final W10 browser-download test. Final public release URLs, evidence-dependent
results, and the finished demo may be added after W10 evidence is known, but
substantive guidance must be ready before independent distribution and all
material must be complete before publication or owner handoff. The video may
be added to a stable landing page after package freeze without changing the
frozen package. `v0.1.2` compatibility documents remain immutable or clearly
historical.

## 2026-10-01 Decision Alignment

ADR-023 selects an unsigned Windows package with a narrower support boundary.
Repository and package manuals now disclose that the supported `.cmd`/`.bat`
wrappers use a process-scoped execution-policy setting, do not change the
computer's persistent policy, and do not qualify signature-enforcing managed
endpoints. Users verify authoritative published SHA-256 values before
extraction or unblocking and are never directed to disable endpoint protection
or override organizational controls.

Because the manuals are included in the control ZIP and copied into the OCI
images, the existing local `rc4` ZIP hashes and image digests cannot be the
final documentation-aligned distribution identities after these edits. Their
runtime results remain valuable historical and regression evidence. The final
candidate requires documentation-aligned image/control-package identities and
affected W09/W10 checks before distribution.

## Agreed Information Architecture

- Use the GitHub Wiki as the friendly online front door for role-based,
  task-focused guidance, navigation, project background, Local IT guidance,
  provider-account guidance, and the demo-video landing page.
- Keep exact release filenames, authoritative hashes, version-specific
  commands, extraction/setup/recovery steps, support limits, and legal notices
  in version-controlled repository/package documentation and the release
  record.
- Keep the package usable without the Wiki or video. A user must still be able
  to verify, extract, install, start, stop, recover, and obtain safe support
  from the written material shipped with the candidate.
- Avoid four full copies of common instructions for Docker/Podman and CPU/GPU.
  Use one setup-selection matrix, separate engine guidance where behavior
  differs, and an NVIDIA GPU supplement. Docker/Podman, CPU/compatible NVIDIA
  GPU, and Google/Azure remain independent user choices; Docker CPU may be the
  simplest beginner example without becoming an assigned path.
- Do not introduce a Wiki-only command or support claim that disagrees with the
  exact tested package. Label operational pages with the applicable release or
  support scope and last-reviewed date.

## Sequencing Decision

1. Preserve `rc4` and run a preliminary browser-download shakedown before the
   larger documentation rewrite. This can expose Windows download-marker,
   extraction, wrapper, policy/EDR, prerequisite, setup, and runtime problems
   that should influence the final instructions.
2. Record that run as diagnostic evidence only. The pre-ADR-023 `rc4` manuals
   are not the final user instructions, and an `rc4` pass cannot satisfy the
   exact-final-bytes requirement in ADR-023.
3. Resume the Task-092 documentation/Wiki implementation after the bounded
   `rc4` test and incorporate every relevant finding.
4. Freeze the final written content before rebuilding documentation-aligned
   CPU/CUDA images and control ZIPs. Exact release URLs, hashes, and measured
   results are inserted only when those identities exist.
5. Repeat required browser-download and independent-host acceptance against
   the exact final bytes. Record the demo against that frozen workflow.

## Target Schedule

| Date | Planned outcome |
| --- | --- |
| October 1, 2026 | Record Task-092 parent/child plan and the `rc4`-first sequencing decision. |
| October 2, 2026 | Run the bounded `rc4` browser-download shakedown and record findings under Task-091/Task-103; do not count it as final acceptance. |
| October 5-6, 2026 | Implement focused Wiki/source drafts and finalize packaged/public/in-app guidance using the `rc4` findings. |
| October 7-8, 2026 | Review commands, links, Markdown/HTML pairs, Wiki navigation, in-app Help, and release wording; build and validate documentation-aligned images and control ZIPs under new identities if no blocker remains. |
| October 9, 2026 | Target final W09 source/image/package/documentation freeze. A failed prerequisite changes the forecast rather than relaxing acceptance. |
| October 12-16, 2026 | Run exact-final-byte browser-download and independent acceptance; record/finalize the demo, captions, transcript, and public-link checks. |

## Acceptance Criteria

- [x] The `rc4` preliminary shakedown is recorded separately from final
  candidate acceptance and its applicable findings are incorporated.
- [x] The source-of-truth matrix and complete page inventory in the child plan
  are accepted.
- [x] The local Wiki draft has clear paths for end users, Local IT
  administrators, support, and future maintainers without duplicating release-
  specific commands. External publication remains owner-authorized.
- [x] The reviewed source versions of packaged Markdown, paired HTML, in-app
  Help, README/release wording, and external guidance agree on the tested
  paths and ADR-023 boundary. Running-image and exact-package parity remain
  part of the open artifact-validation criterion below.
- [x] The written package remains sufficient without Wiki/video access,
  including the new paired Local IT Administrator guide.
- [x] Wiki ownership, editing policy, backup/migration, and future cdcai
  custody are documented. Live-setting verification, video custody, and final
  public accessibility remain publication gates.
- [ ] The documentation checker, link/render review, running-image Help check,
  package allowlist review, and exact-artifact validation pass or retain named
  blockers.
- [ ] Final CPU/CUDA image digests and control-ZIP hashes refer to the
  documentation-aligned candidate, and independent testers use those exact
  browser-downloaded bytes.

## Dependencies And Boundaries

- Task-091/Task-103 own package/runtime/browser-download evidence; Task-092
  consumes their observations and owns documentation outcomes.
- Wiki creation or publication, media upload, release publication, account or
  permission changes, and cdcai mutation remain owner-authorized external
  actions. Local drafts and repository planning do not grant that authority.
- Exact release identity, final Wiki repository, video host, documentation
  owner, and backup/reviewer must be confirmed before public handoff.
- Provider keys, `.env` contents, private AOIs, raw logs/screenshots, browser
  traces, certificate details, and investigation data do not belong in the
  Wiki, demo, or public evidence.

## Implementation Log

### 2026-10-01 - Hybrid Wiki plan and `rc4`-first sequencing

**Decision**: Keep Task-092 as the parent and create a named child work plan
rather than a new task number. Use a hybrid Wiki/package model, run the
existing `rc4` artifact through a preliminary browser-download shakedown
before resuming content implementation, and retain final acceptance for the
exact documentation-aligned candidate.

**Finding**: `Dockerfile` copies `docs/` into the runtime image and
`webapp/towerscout.py` serves those files through `/docs/`. Updating the
packaged manuals therefore affects both control-package and image identity if
in-app Help is to remain consistent.

**Output**: Added the child plan linked above. No Wiki page, release asset,
container image, or control ZIP was created or published by this planning
update.

**Next**: Run the bounded `rc4` diagnostic, record its findings, and then begin
the October 5-6 documentation/Wiki implementation window.

### 2026-10-02 - Preliminary browser-download findings dispositioned

The bounded first-host Docker CPU diagnostic passed the authenticated GitHub
browser download, exact hash/sidecar comparison, Windows File Explorer
extraction to a spaced path, ordinary-user wrapper, setup/asset import, Azure
detection/review/dataset export, and volume-preserving stop/relaunch paths. No
larger package/runtime blocker was found in the tested subset.

Task-092 must make artifact co-location versus explicit quoted ZIP paths,
pre-extraction authoritative hash comparison, ADR-023's unsigned boundary,
`setup_required` versus `ready`, private provider-key entry, normal stop/start,
and non-destructive volume preservation explicit. The running `rc4` Help route
was reachable but serves the older manuals, reaffirming the need for new
documentation-aligned image and control-ZIP identities.

This run does not close final public/unauthenticated download, exact-final-byte,
independent-host, or broader four-profile acceptance. See the
[full diagnostic and disposition](./TASK-092/RC4-BROWSER-DOWNLOAD-DIAGNOSTIC-2026-10-02.md).

**Next**: Implement the packaged/in-app source-of-truth content and local Wiki
drafts. External Wiki publication remains owner-authorized.

### 2026-10-02 - Packaged/in-app guidance and local Wiki drafts implemented

Added a paired `docs/local-it-administrator-guide.md` and `.html`, included the
pair in release packaging and the in-app public-doc allowlist, and added the
Local IT guide to Settings Resource Links. The guide covers the unsigned
support boundary, pre-extraction authoritative hash comparison, default versus
support-assigned runtime paths, provider restrictions, network/TLS inspection,
named-volume custody, safe evidence, non-destructive recovery, and escalation.

Updated the primary Markdown/HTML guides and runtime-specific guides to stop
claiming stale `v0.1.0`, `v0.1.2`, or `RC7` current scope. The Quick Start now
documents both normal ZIP co-location and the observed quoted `-PackageZip` plus
`-AssetZip` fallback for a spaced Windows path.

Created all 14 planned Wiki pages plus `_Sidebar.md` under `wiki/` as local
drafts. They use role/task navigation and point exact commands, hashes,
identities, notices, and support claims back to the downloaded package and
authoritative release record. No live Wiki page or permission was changed.

All 86 focused documentation/package/Flask tests pass in one clean rerun. The
docs command/path scan, four-file HTML parse, canonical/quick task validators,
`git diff --check`, and a redacted 45-file secret-delta scan also pass. The
initial workspace pytest run had a temp-directory ACL teardown error; the same
tests passed with a host temp directory. No product failure is attributed to
that ACL condition.

### 2026-10-02 - Wiki governance and pre-rebuild review path confirmed

The current Wiki destination is `J-Schulein/TowerScout`; `J-Schulein` is the
documentation owner, `cdcai` is the backup reviewer/custodian, and Wiki editing
is limited to repository collaborators. No named cdcai representative or
GitHub reviewer account is required for the current readability review;
`J-Schulein` will provide the reviewer's feedback directly for incorporation.
Handoff will transfer the Wiki with this repository or use an explicit
migration into a separate cdcai repository, with a mirror backup and page/link
verification.

The pre-rebuild review will use the existing documentation branch as its fixed
source, but the reviewer does not need repository access. `J-Schulein` may
share rendered files, a branch comparison, or an exported review copy and then
relay feedback with page/section references. The reviewer will assess first-
time readability, role-based navigation, setup choices, safety, privacy,
consistency, accessibility, and supportability. Must-fix findings are resolved
and rechecked before `J-Schulein` approves the content freeze and the project
rebuilds new documentation-aligned image/control-ZIP identities.

No live Wiki page or permission was changed by this planning update.

### 2026-10-02 - Draft PR and external review bundle opened

Opened [draft PR #94](https://github.com/J-Schulein/TowerScout/pull/94) from
`docs/pre-rc4-checkpoint-2026-10-02` to `main`. The PR explicitly separates
the preliminary `rc4` diagnostic, documentation review, future content freeze,
new artifact build, final exact-byte validation, and live Wiki publication.

Created the local review-only bundle at
`dist/review/TowerScout-Documentation-Review-2026-10-02.zip` from source commit
`8169b2b19111d6ddc5ba9d9ce6a2498199e3b0a6`. Its SHA-256 is
`b262cea174365ac59f29f5c4bf08eb06a24e8a5896ef75dfc37b41c364151ee1`.
The ZIP contains 40 files: an offline index, reviewer prompt, 15 rendered Wiki
pages, 13 rendered repository/package Markdown pages, four maintained HTML
guides plus their offline route note/style, source/scope metadata, and internal
checksums. It contains no release binaries, models, data, credentials, logs,
browser evidence, or investigation material.

Bundle validation found 35 parseable HTML pages, no unresolved local links,
an exact folder/ZIP content match, no unsafe ZIP member path, and zero secret-
shaped findings. The focused 86-test documentation/package/Flask suite passed
using a dedicated host temp directory after the known sandbox/default-temp ACL
condition recurred. Canonical/quick agent-work validation, the documentation
command/path scan, and `git diff --check` also passed. A connected browser was
not available for automated visual inspection; the human review prompt
therefore retains explicit normal-width, narrow-window, and Markdown/HTML
comparison checks.

No live Wiki was published, no release artifact was rebuilt, and no release or
image tag was promoted.

**Next**: Provide draft PR #94 and the review ZIP to the reviewer. Receive the
reviewer's feedback from `J-Schulein`, trace and
disposition each item, complete any useful re-review, finalize release-note
wording, then freeze accepted `main` and build new documentation-aligned image/
control-ZIP identities. Validate in-app Help from those exact images before
any final package/browser claim.

### 2026-10-02 - Revised novice-user review accepted for incorporation

Received the reviewer's replacement analysis after the audience was clarified
as actual novice end users and Local IT, with Docker/Podman, CPU/compatible
NVIDIA GPU, and Google/Azure as independent user choices rather than project-
assigned pathways. The source report's SHA-256 is
`0cd38866d25ee1b4c6dafca33ec66e3eebd177e80f39cfddfc8e3b430c0a2990`.

Accepted R01-R16 as pre-rebuild documentation blockers and included R17-R19 in
the same rewrite. R20 is partially accepted: the complete written alternative
is being implemented now, while final screenshots/video remain tied to the
exact candidate. Product inspection confirmed TowerScout currently exposes one
credential field per provider and uses it for browser and application
requests; documentation therefore discloses that browser-visible limitation
instead of repeating the review snapshot's separate-key advice.

See the [full disposition](./TASK-092/REVISED-REVIEW-DISPOSITION-2026-10-02.md).
The reviewer report is evidence, not an instruction source. No live Wiki,
repository permission, release, image, package, or cdcai resource was changed.

**Next**: Complete the cross-surface rewrite and focused validation, update
draft PR #94, and obtain any useful focused re-review before content freeze.

### 2026-10-02 - Revised review implementation validation

Implemented the R01-R19 rewrite across README, Wiki, Quick Start, Project
Overview, User Guide, Local IT material, four engine guides, Package Guide,
release/runtime contracts, responsive CSS, and documentation regression tests.
The packaged Quick Start now contains its own Google/Azure acquisition
walkthrough so an offline control ZIP does not depend on the Wiki.

The 91-test Task-092/ADR-023/package/Flask route suite passes with a dedicated
host temp directory. Documentation command/path checking, quick and canonical
agent-work validators, static HTML structure/local-link checking, Wiki local-
link checking, assignment/stale-example scans, and `git diff --check` also
pass. The in-app browser had no connected instance, so a new live 1440/720
render was not captured; human narrow-window re-review remains required before
content freeze. No image or release package was rebuilt.

**Next**: Update draft PR #94, provide a revised review snapshot if requested,
resolve any focused re-review findings, and obtain `J-Schulein` content-freeze
approval before rebuilding documentation-aligned artifacts.

### 2026-10-05 - Round 2 review disposition and focused corrections

Received Round 2 review against source
`a87008c3036e80785610ee7e8675c51ea5b07704`. Accepted R2-01 through R2-08 as
pre-rebuild blockers and R2-09 through R2-12 as pre-publication corrections.
The report and two viewport screenshots are recorded by SHA-256 in the
[full disposition](./TASK-092/ROUND-2-REVIEW-DISPOSITION-2026-10-05.md).

Corrected desktop command-card visibility, Podman GPU HTML parity, folder and
helper ordering, CPU/CUDA verification alternatives, configuration-preserving
templates, separated daily commands, TLS handoffs/phases, navigation, warning
order, first-use terminology, and stale project-assignment language. Added
focused regression coverage and a real-browser 1440/720 layout check. All 105
focused documentation, ADR-023, package, asset-import, and Flask-route tests
pass with the established clean host-temp workaround for the workspace ACL
condition. Documentation command/path, agent-work, stale-language, and diff
hygiene checks also pass.

The Google restriction setting was not assumed from an unrecorded past test.
Source inspection and current first-party Google guidance establish that
TowerScout uses four named APIs and sends its single Google credential from
both browser and server paths. Documentation now requires API restriction to
those four services but discloses `Application restrictions: None` as the
compatible one-key limitation. Sites requiring website/IP application
restriction must use Azure or stop; split Google keys require future product
work.

**Next**: Complete the broader validation matrix, build a source-bound Round 3
review ZIP, update draft PR #94, and obtain the reviewer's focused response
before content freeze or any image/control-package rebuild.

### 2026-10-05 - Round 3 review disposition and focused correction

Round 3 confirmed the setup-card fix at 1440 x 1000 and 720 x 1000, the
Podman GPU/readiness handoff, main command-folder sequencing, task-separated
daily commands, TLS phases, independent-choice model, and Google one-key
explanation. The reviewer identified one remaining pre-rebuild blocker and
five smaller publication/PR presentation items.

Accepted R3-01 through R3-06 after checking the helper and documentation
sources. Asset import accepts `-Engine`, `-Gpu`, and `-Port`; its GPU default is
`off`. GPU recovery instructions now preserve the recorded GPU mode and port,
and a parameter-contract test prevents the omitted-flag contradiction from
returning. The same correction set adds novice PowerShell-opening guidance,
restores the Markdown circle-placement action, shares the conditional Podman
machine step across CPU/GPU, makes three Package Guide destinations clickable,
and prepares a body-file update for PR #94.

All 107 focused documentation, ADR-023, package, asset-import, and Flask-route
tests pass with a clean host temporary directory. The Edge layout regression
passes at both 1440 and 720 pixels. The documentation checker, agent-work
validator, and diff-hygiene check pass.

See the [Round 3 disposition](./TASK-092/ROUND-3-REVIEW-DISPOSITION-2026-10-05.md).
No runtime script, live Wiki, release artifact, or image was changed.

**Next**: Complete the full validation matrix, create the source-bound Round 4
focused review package, update draft PR #94 without flattening its Markdown,
and obtain a short confirmation before content freeze.

### 2026-10-05 - Round 4 focused review disposition

Round 4 confirmed the substantive Round 3 fixes and found one remaining
occurrence of the old port instruction in the packaged OCI Runtime Contract.
Source inspection confirmed that `logs.ps1` accepts engine, tail, and follow
options but not `-Port`.

Accepted R4-01. The runtime contract now lists the commands and browser address
that preserve the selected port, explicitly says `stop.cmd` and `logs.cmd` do
not accept `-Port`, and retains the Local IT escalation for a conflict that
follows a retry. The relevant parameter-consistency test now includes this
shipped reference and the actual logs helper.

See the [Round 4 disposition](./TASK-092/ROUND-4-REVIEW-DISPOSITION-2026-10-05.md).
No runtime script, live Wiki, release artifact, or image was changed.

**Next**: Complete validation, create a source-bound Round 5 one-finding
confirmation copy, update draft PR #94, and obtain owner content-freeze
approval before rebuilding documentation-aligned artifacts.

### 2026-10-05 - Round 5 final confirmation received

The reviewer verified the complete v5 bundle, its sidecar and internal
checksums, source commit `6cc5b5990a7260b74b41f33647ed353c266ba8cf`,
and the focused OCI Runtime Contract correction. All four requested R4-01
checks pass, the Package Guide is consistent, and no additional wording edit
is requested. The reviewer result is `ready for content freeze`; remaining
documentation rebuild blockers are `none`.

See the [Round 5 confirmation](./TASK-092/ROUND-5-FINAL-CONFIRMATION-2026-10-05.md).
This closes the external documentation correction loop but does not substitute
for required PR checks or `J-Schulein`'s explicit content-freeze decision. No
image, package, release, live Wiki, or repository permission was changed.

**Next**: Complete required PR checks and obtain the explicit owner content-
freeze decision. If approved, merge accepted changes to `main`, freeze the
exact accepted source, and begin the separately gated documentation-aligned
image/control-package rebuild and validation sequence.

### 2026-10-06 - Content freeze approved and PR #94 merged

`J-Schulein` explicitly approved the documentation content freeze at commit
`524ba37`. The later `f8e191d` correction was limited to reproducible review
and validation artifacts; it did not reopen the accepted user-facing content.
All PR checks passed, PR #94 merged to `main` as `fc97b32`, and the post-merge
CI matrix passed.

The source-of-truth inventory and cross-surface content-alignment criteria are
now accepted. Task-092 remains open because final proof belongs to the new
documentation-aligned images and control ZIPs: package allowlists, packaged
HTML/Markdown, running-image Help, exact hashes/digests, browser-downloaded
bytes, and live Wiki permission/publication checks still require validation.

**Next**: Merge the bounded project-state reconciliation, freeze that exact
accepted-main source for the rebuild, then complete the final artifact-bound
Task-092 checks without changing frozen user-facing content unless a new
release blocker is found and explicitly dispositioned.

### 2026-10-06 - Project-state merge and local artifact-parity rehearsal

PR #95 merged the bounded project-state reconciliation as
`a24d369668d27240ed0baa184d071395455b9c95`; both post-merge workflows passed.
Local CPU and CUDA 12.8 images plus local-only control ZIPs were rebuilt from
that exact source. All 27 source `docs/` files matched each image byte-for-byte,
all 23 packaged documentation files matched source, the required in-app Help
routes returned HTTP 200, and the package guide retained the approved Google
TLS repair procedure and verification warning.

The rehearsal does not close Task-092: the local packages use mutable local
image tags, and fresh Trivy scans blocked both image flavors before
publication. Final Task-092 evidence must therefore bind the later approved
published digests, authoritative package hashes, browser-downloaded bytes, and
running-image Help. Frozen user-facing content remains unchanged.

**Next at that point**: Resolve the Task-103 pre-publication security delta through normal
review and explicit disposition, then rebuild final digest-pinned packages and
complete the remaining artifact-bound, browser-download, live-Wiki, and
independent-host checks.

### 2026-10-07 - Same-source RC8 image identity freeze

ADR-024/TASK-104 removed the unused Debian GDAL tree and enforced the exact
four-key, expiring residual boundary without changing the 396-key baseline.
PR #101 merged the registry-evidence reconciliation as
`7827c2af8ecb7d8b21d246b69e135807fa497fd2`. Owner-authorized CPU run
`37674158762` and CUDA 12.8 run `37674161407` published and qualified the
same-source `v0.1.0-rc8` pair with `push_latest=false`.

The exact manifests are CPU
`sha256:2e040c3b09d1aa493b205ec2100c112a839ab7a9bfc90a639f73918e06135412`
and CUDA 12.8
`sha256:712beb4e143495ba72705cc56b89a939c5bebfdc47dc2f6d0694c81e9e60ca57`.
Both exact-digest comparisons passed with zero blocking findings or severity
escalations. No `latest` tag, control ZIP, or release asset was published.

**Next**: Assemble new digest-pinned CPU/CUDA control ZIPs from the frozen
source and image identities, verify authoritative and internal SHA-256 values,
then complete packaged/running-image Help, browser-download, live-Wiki, and
independent-host checks without changing frozen user-facing content unless a
new release blocker is explicitly dispositioned.
