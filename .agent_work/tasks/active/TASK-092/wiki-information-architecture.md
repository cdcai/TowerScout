# Task-092 Child Work Plan: GitHub Wiki Information Architecture And Local IT Guide

**Status**: IN_PROGRESS - local Wiki drafts plus packaged/in-app Local IT
guidance implemented; owner/permission review, publication, final identities,
and running-image validation remain
**Parent**: [TASK-092 Documentation Currentness And Information Architecture](../TASK-092-documentation-currentness.md)
**Priority**: HIGH
**Planned implementation window**: October 5-8, 2026
**Target documentation/artifact freeze**: October 9, 2026
**Final usability and video target**: October 16, 2026

## Purpose

Create a simpler online documentation experience without making installation
depend on an internet-only or mutable Wiki. Reduce independently maintained
duplication, add a dedicated Local IT Administrator path, and make ownership
and version scope clear enough for project handoff.

## Selected Model

Use a hybrid model:

- The GitHub Wiki is the online navigation and evergreen guidance layer.
- Version-controlled repository/package documents remain authoritative for
  exact release commands, filenames, hashes, offline installation, recovery,
  support boundaries, and notices.
- The authoritative release record owns exact downloads, public SHA-256
  values, image digests, supported environment results, and known limitations.
- In-app Help comes from the documentation baked into the exact OCI image and
  must agree with the package/release guidance.
- The written package must remain sufficient when the Wiki or video is
  unavailable.

This approach improves discovery without maintaining two independent copies of
every command. A future owner may automate publication from repository
Markdown, but a new synchronization system is not a pre-freeze requirement.

## Source-Of-Truth Matrix

| Information | Authoritative location | Wiki treatment |
| --- | --- | --- |
| Exact release downloads and public SHA-256 values | GitHub release record | Link to the applicable release; do not copy mutable values broadly. |
| Exact version-specific install, setup, start, stop, recovery, and verification commands | Versioned `docs/` files shipped in the control ZIP | Explain the task and link to the applicable versioned guide/section. Stable common wrappers may be summarized only when kept consistent. |
| In-app Help | `docs/*.html` and paired Markdown baked into the exact OCI image | Link users to the running app or versioned repository copy; verify the image serves the intended version. |
| Setup selection and role-based navigation | Wiki | Canonical Wiki content with release-scope labels and links to exact instructions. |
| Provider account/key overview | Wiki plus `PROVIDER_TERMS.md` and versioned setup docs | Keep evergreen account concepts together; link to current Google/Microsoft instructions and never publish keys. |
| Local IT preparation and support boundary | Wiki Local IT Administrator Guide | Canonical role-based overview; link to release-specific commands and ADR-023-safe procedures. |
| Demo video, transcript, and written walkthrough | Stable Wiki landing page; media in an owner-approved durable location | Link/thumbnail rather than depending on a Wiki-native inline player. |
| License/model/data/provider obligations | Release/package notices | Provide a short index and links; do not rewrite legal/compliance text independently. |
| Historical pilot instructions | Preserved versioned compatibility pages/releases | Label historical; do not blend with the current candidate path. |

## Planned Wiki Pages

| Page | Audience and purpose | Key content | Priority |
| --- | --- | --- | ---: |
| **Home / Start Here** | All readers | Plain-language purpose, role selector, current release scope, links for end users, Local IT, support, and maintainers. | Required |
| **Before You Install** | End users and Local IT | Windows/runtime/browser/disk/network/provider prerequisites, unsigned-package boundary, and stop/escalation conditions. | Required |
| **Choose Your Setup** | End users and support | Simple Docker CPU, Docker GPU, Podman CPU, and Podman GPU matrix. CPU is default; GPU and Podman are support-assigned. | Required |
| **Install And First Run** | End users | Download selection, authoritative hash verification, extraction, model/data package, Setup Wizard, readiness, and a small first detection. Link to exact versioned commands. | Required |
| **Google And Azure API Credentials** | End users and Local IT | What a provider key is, provider choice, ownership/billing/restrictions, browser-visible SDK key warning, official provider links, and no-key-sharing rule. | Required |
| **Everyday Commands** | End users and first-line support | One canonical index for start, stop, status, logs, restart, asset import, TLS diagnostics, and data-preserving recovery, with links to exact release commands. | Required |
| **Docker Guidance** | Docker users and Local IT | Docker Desktop/WSL 2 preparation, CPU default, engine-specific lifecycle, troubleshooting, and links to exact package instructions. | Required |
| **Podman Guidance** | Podman users and Local IT | Podman machine/connection, approved Compose provider, Python prerequisite, CPU/GPU distinctions, and target-safe troubleshooting. | Required |
| **NVIDIA GPU Setup** | GPU users and Local IT | GPU eligibility, Windows driver/WSL/container prerequisites, CDI for Podman, CUDA verification, disk expectations, and no-silent-fallback rule. This supplements rather than repeats installation. | Required |
| **Troubleshooting And Safe Support** | End users and support | Readiness, assets, ports, Compose/provider, TLS, provider validation, policy blocks, recovery, safe evidence, and escalation. | Required |
| **Local IT Administrator Guide** | Site IT and security staff | Purpose/architecture, prerequisite approval, unsigned-package boundary, integrity verification, network/TLS, data custody, support procedures, and unsupported environments. | Required |
| **Demo Video And Written Walkthrough** | New users, trainers, and handoff owner | Stable landing page, linked video, version/date, chapters, captions, transcript, privacy review, and equivalent written steps. | Required landing page; final media follows frozen candidate |
| **Releases And Supported Versions** | All readers and support | Current versus historical release, support matrix, known limitations, and direct link to the authoritative release record. | Required |
| **Licensing, Privacy, And Provider Terms** | Users, Local IT, and maintainers | Short index to authoritative notices, sensitive-data reminders, provider responsibilities, source/SBOM location, and public-health data handling boundaries. | Required |

## Local IT Administrator Guide Outline

1. TowerScout purpose: identify possible cooling towers from aerial/satellite
   imagery to support public-health investigation and planning; results still
   require human review.
2. Runtime shape: local Windows workstation, Docker or Podman, loopback-served
   browser application, digest-pinned OCI image, and separate model/data asset
   package.
3. Supported deployment matrix and who assigns non-default paths.
4. Windows 11 AMD64, WSL/virtualization, engine, browser, disk, network,
   Python-for-Podman-provider, and NVIDIA prerequisites.
5. Administrator-required versus ordinary-user steps.
6. ADR-023: unsigned scripts, supplied `.cmd`/`.bat` wrappers, process-scoped
   execution-policy behavior, organization approval boundaries, and prohibited
   advice to weaken protection.
7. Authoritative release-page hash verification before extraction/unblocking.
8. Required outbound destinations, proxy/TLS inspection, site CA process,
   local ports, and loopback-only exposure, after exact endpoints are verified.
9. Google/Azure key ownership, billing, API/referrer restrictions, browser SDK
   visibility, monitoring, and safe handling.
10. Persistent named volumes, potentially sensitive configuration/log/session/
    upload/export data, backup/recovery, and non-destructive stop/relaunch.
11. Safe diagnostic commands and what support may request.
12. Information that must not be shared publicly: provider keys, `.env`, raw
    logs/screenshots, private AOIs, browser traces, certificate details,
    cached responses, exported investigation data, and local identifiers.
13. Supported versus unsupported environments and escalation checklist.
14. Upgrade, rollback, uninstall, and custody expectations without destructive
    volume cleanup.

## Demo Video Plan

GitHub's Wiki documentation describes images and links but does not provide a
dependable contract for an embedded third-party video player. GitHub also notes
that embedded YouTube HTML does not render in GitHub Markdown. Use a stable
Wiki landing page with a linked thumbnail instead of making inline playback a
requirement.

The landing page must include:

- Applicable TowerScout version/image/package identity.
- Recording date and duration.
- Accessible thumbnail and descriptive link.
- Captions and transcript.
- Chapters/timestamps when the host supports them.
- Written steps that work without the video.
- Privacy review confirmation and no visible keys, AOIs, investigation data,
  local identifiers, or sensitive logs.
- A stale-video warning or replacement link when the demonstrated workflow no
  longer matches the current release.

References:

- [GitHub Wiki documentation](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
- [Editing Wiki content](https://docs.github.com/en/communities/documenting-your-project-with-wikis/editing-wiki-content)
- [GitHub Markdown/non-code rendering limitations](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files)
- [Attaching files on GitHub](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files)

## Wiki Ownership And Handoff

- Restrict editing to designated collaborators unless the future owner makes a
  deliberate different decision.
- Name a primary documentation owner and backup/reviewer.
- Record the Wiki repository URL, clone/backup procedure, page inventory,
  sidebar/navigation convention, media source location, and update checklist.
- Add `Applies to`, `Last reviewed`, audience, and support-scope metadata to
  operational pages.
- A formal repository transfer carries the Wiki, but adoption through a
  separate repository or fork may require an explicit Wiki migration. Do not
  assume cdcai adoption automatically moves this fork's Wiki.
- Verify public accessibility without a privileged session before linking the
  Wiki from release/package material.
- Publishing pages, changing GitHub permissions, uploading media, or mutating
  another repository remains owner-authorized external work.

References:

- [Changing Wiki access permissions](https://docs.github.com/en/communities/documenting-your-project-with-wikis/changing-access-permissions-for-wikis)
- [Transferring a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository)

## `rc4` Preliminary Shakedown Before Documentation Implementation

### Purpose

Use the already-qualified `rc4` package to find large problems likely to
persist into the documentation-aligned candidate before final prose and images
are frozen. Preserve `rc4`; do not treat it as discarded output.

### Valuable observations

- Browser download and Windows downloaded-file marker behavior.
- Authoritative-test-record/sidecar/local SHA-256 comparison procedure.
- File Explorer extraction to a user-writable path containing spaces.
- Ordinary-user `.cmd`/`.bat` wrapper behavior under the unsigned support
  boundary.
- SmartScreen, Defender/EDR, publisher, WDAC/AppLocker, or organization-policy
  stop/escalation behavior.
- Docker/Podman prerequisites, setup, asset import, readiness, provider/TLS,
  bounded detection, stop/relaunch, and persistence problems.
- Confusing user steps that should change the final package, Wiki, IT guide, or
  demo script.

### Evidence boundary

- Label the run `rc4 preliminary browser-download diagnostic`; it is not the
  final ADR-023 clean-machine pass.
- Use an approved browser-accessible test location; do not publish `rc4` as a
  release or alter external assets without authorization.
- Use a supplemental ADR-023-safe test sheet because the packaged `rc4`
  manuals predate the decision.
- A failure may reveal a release blocker. A pass lowers risk but does not
  replace final testing of the exact documentation-aligned bytes.
- Final acceptance still requires authoritative published hashes, the exact
  downloaded marker, ordinary-user execution, and required independent-host
  Docker/Podman CPU/NVIDIA evidence.

## Release Rebuild Impact

As of October 1, the intended application/runtime behavior is unchanged from
`rc4`; the known package-allowlist changes are documentation. However:

- `scripts/package-release.ps1` includes the changed manuals in both control
  ZIPs.
- `Dockerfile` copies `docs/` into both runtime images.
- `webapp/towerscout.py` serves those baked files through the in-app `/docs/`
  routes.
- Rebuilding changes generated version/source/timestamp/manifest/checksum
  metadata and control-ZIP hashes.
- Keeping the old `rc4` images would leave pre-ADR-023 in-app guidance while
  the extracted package contains new guidance. Do not accept that drift by
  accident.

The planned final freeze therefore covers source, documentation-aligned CPU
and CUDA images, control ZIPs, asset references, Wiki/release links, and all
generated identities. `rc4` runtime results remain the regression baseline,
but the required affected W09/W10 checks bind to the new identities.

## Work Sequence

| Step | Target | Exit condition |
| --- | --- | --- |
| 1. Preliminary `rc4` shakedown | October 2 | Diagnostic findings recorded without claiming final acceptance. |
| 2. Reconcile findings | October 5 morning | Every applicable finding is assigned to package docs, Wiki, runtime, support, or no-action with rationale. |
| 3. Draft/refactor content | October 5-6 | Required Wiki/source pages and packaged Markdown/HTML content complete enough for review. |
| 4. Review and validation | October 7 | Commands, links, HTML rendering, package allowlist, in-app routes, ADR-023 language, and secret/privacy safety reviewed. |
| 5. Rebuild documentation-aligned artifacts | October 7-8 | Clean-source CPU/CUDA images and control ZIPs have new exact identities; manifests/checksums pass. |
| 6. W09 freeze | October 9 | Source, images, ZIPs, shipped docs, Wiki landing links, fixtures, and test procedure frozen or blockers/forecast recorded. |
| 7. W10 and media | October 12-16 | Exact browser-downloaded candidate passes applicable independent-host gates; demo/captions/transcript and public links reviewed. |

## Acceptance Checklist

- [x] Preliminary `rc4` findings are dispositioned in
  [the diagnostic record](./RC4-BROWSER-DOWNLOAD-DIAGNOSTIC-2026-10-02.md).
- [ ] Wiki destination, edit permissions, owner, backup, and migration/backup
  procedure are confirmed.
- [ ] Required pages have content owners, release scope, and last-reviewed
  metadata.
- [x] Page navigation starts from user role and intended task.
- [x] CPU/default versus support-assigned GPU/Podman paths are unmistakable.
- [x] One authoritative command/source location is named for every repeated
  topic.
- [x] Local IT guidance covers prerequisites, integrity, unsigned execution,
  network/TLS, data custody, support evidence, and escalation.
- [x] Provider guidance states ownership/restriction obligations and never
  implies browser SDK keys are secret from the browser.
- [x] Video page has an accessible written alternative and privacy-safe media
  plan.
- [x] Packaged guidance is complete without Wiki/video access.
- [ ] Markdown/HTML pairs, in-app routes, package contents, and running-image
  Help agree.
- [ ] Documentation-aligned CPU/CUDA images and control ZIPs receive new
  identities and pass the affected release gates.
- [ ] Final public links and authoritative hashes are verified without a
  privileged session before distribution.

## Deliberately Deferred From This Child Plan

- A new documentation framework or broad GitHub Pages implementation.
- An automated Wiki synchronization pipeline unless manual maintenance proves
  unworkable and the future owner accepts the added system.
- A wholesale removal of packaged/offline guides before final acceptance.
- Re-recording the final demo before the exact candidate is frozen.
- Publishing, changing repository permissions, transferring ownership, or
  mutating cdcai without explicit authorization.
