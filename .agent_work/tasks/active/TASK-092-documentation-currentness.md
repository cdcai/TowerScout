# TASK-092: Documentation Currentness And Information Architecture

**Status**: IN_PROGRESS - `rc4` findings are dispositioned; packaged/in-app
Local IT guidance and the complete local Wiki draft set are implemented and
focused tests pass. Owner/permission review, final release identities, running-
image Help validation, publication, and final W09/W10 gates remain
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
  differs, and an NVIDIA GPU supplement. CPU remains the normal/default path.
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
- [ ] The source-of-truth matrix and complete page inventory in the child plan
  are accepted.
- [x] The local Wiki draft has clear paths for end users, Local IT
  administrators, support, and future maintainers without duplicating release-
  specific commands. External publication remains owner-authorized.
- [ ] Packaged Markdown, paired HTML, in-app Help, README/release wording, and
  external guidance agree on the tested paths and ADR-023 boundary.
- [x] The written package remains sufficient without Wiki/video access,
  including the new paired Local IT Administrator guide.
- [ ] Wiki/video ownership, edit permissions, version labels, accessibility,
  backup/migration, and future repository custody are documented.
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

**Next**: Review content/ownership, confirm Wiki destination/permissions and
future backup owner, finalize release-note wording, then freeze content and
build new documentation-aligned image/control-ZIP identities. Validate in-app
Help from those exact images before any final package/browser claim.
