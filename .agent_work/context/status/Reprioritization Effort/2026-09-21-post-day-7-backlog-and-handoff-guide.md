# TowerScout Post-Day-7 Backlog and Handoff - Suggested Implementation Plan

> **For agentic workers:** This is a suggested guide for selecting and updating work after the seven-day deployment effort. When execution is authorized, use `superpowers:executing-plans` if available and work through the selected tasks sequentially. Delegation requires the execution session's authorization. The unchecked steps below describe future work, not completed deliverables.

**Goal:** By October 30, leave a qualified application, clear user instructions, a usable owner operations guide, transferable release/support responsibilities, and a prioritized post-handoff backlog. October 31, 2026 is the hard project end.

**Architecture:** Retain the main-based PowerShell/Compose application and existing qualification tools. Finish bounded reliability gaps, then protect time for documentation, media, repository sanitization and owner-operated rehearsal. Keep one authoritative operational backlog at each stage of the transition.

**Tech stack and delivery surfaces:** Windows 11 AMD64; Docker/Podman; CPU/NVIDIA GPU; Windows PowerShell 5.1; existing Python/JavaScript checks; Markdown and manually maintained HTML; versioned images, ZIPs, and externally hosted video.

**Related requirements:** [Prioritization v2](2026-09-21-windows-deployment-prioritization-v2.md), [seven-day implementation plan](2026-09-21-windows-deployment-hardening-v2.md), and [its static verification record](2026-09-21-windows-deployment-hardening-v2-verification.md). This guide adds post-Day-7 planning and the requested handoff deliverables; it does not replace the four-profile acceptance requirements.

**Status and baseline:** Suggested September 21, 2026 guide, grounded in local source `9276084d91807906c53e00060670692b27e38483` and the existing backlog. Day-7 results are not yet known. Writing this guide does not update task status, sanitize files, record/publish a video, transfer ownership, or authorize external publication.

## Global constraints

- Finish any unpassed Day-7 deployment, data-integrity, or security gate before optional backlog work. Do not describe a partial matrix as the full Windows Docker/Podman CPU/NVIDIA result.
- Keep PR #67 and the Task-087 launcher deferred through project closeout; do not reinstate them as dependencies or automatically resume them after Day 7. Preserve their history and evidence.
- Preserve the tested command-based stop/start/TLS workflow, all eight named volumes, loopback binding, model identities, TLS verification, and provider-key redaction.
- Keep published `v0.1.2` immutable. Official cdcai adoption and publication remain owner-authorized; technical access alone does not imply approval.
- Freeze the final candidate on October 9. Afterward, change shipped behavior or packaged documents only for a release blocker or essential correctness correction, with a new artifact identity and affected requalification.
- Complete acceptance by October 16, owner-operated rehearsal by October 23, and operational closeout by October 30. Plan no remaining outgoing-developer dependency for October 31.
- Reserve the documentation/media/handoff time below before selecting optional technical work. If capacity falls short, cut optional work and revise the forecast rather than silently dropping handoff outputs.

## Review focus

1. A Day-7 result is mistaken for completion of owner-operated qualification: section 3 requires evidence reconciliation; section 5 requires the receiving owner to perform the work.
2. Public Markdown changes but the app still serves old HTML: section 6 checks both guide formats, package contents, image contents, and actual Help links.
3. A demo shows a different workflow or exposes credentials: section 7 binds the recording to the frozen candidate, checks every frame, and transfers source-media custody.
4. Sanitization deletes unique evidence or misses history/release assets: section 8 separates preservation, current-tree review, history/distribution review, and incident handling.
5. The owner inherits duplicate backlogs or inaccessible release accounts: sections 5 and 9 require one canonical backlog and demonstrated owner/backup access.

## 1. Planning assumptions and protected capacity

The calendar assumes Day 7 ends around September 27. September 28-October 30 contains 25 weekdays before considering holidays, leave or competing responsibilities. Confirm actual availability with the project lead and receiving owner at the start of this phase. If Day 7 slips, recompute capacity; do not slide the October 31 deadline automatically.

Use the following as a suggested allocation for one primary implementer. These are protected planning allowances, not validated effort estimates or promises. Receiving-owner/tester availability must also be booked; it cannot be replaced by the implementer marking their own work accepted.

| Work allocation | Reserved person-days | What the allowance covers |
| --- | ---: | --- |
| Remaining reliability, Windows automation, recovery and acceptance | 6 | Bounded fixes, useful regression automation, repeated-run testing, final evidence reconciliation. |
| Owner's guide and owner-operated rehearsals | 3 | Draft procedures, walkthrough, corrections and independent owner execution. |
| Public guides, in-app guides and external setup guide | 3 | Update existing material, synchronize formats and verify links/rendering against the candidate. |
| Replacement installation/demo clip | 2 | Storyboard/dry run, capture, editing, captions/transcript, review and custody transfer. |
| Repository and distribution sanitization | 2 | Early scoped audit/remediation plus a final pass; major history remediation is not assumed to fit this allowance. |
| Backlog reconciliation, post-handoff backlog and instruction alignment | 2 | Reclassify tasks, prepare owner-facing entries, consolidate authority and check agent entrypoints. |
| Adoption/access/publication preparation and closeout | 2 | Confirm custody/permissions, prepare or execute authorized transfer, verify final downloads and closeout. |
| Contingency | 5 | Blocker fixes, reruns, owner review delays and limited media/document corrections. |
| **Total** | **25** | Reduce optional scope if the available calendar is smaller. |

Owner's-guide drafting, access preparation and sanitization start in the first post-Day-7 week. Do not queue them behind every technical improvement. Do not schedule a large new feature merely because contingency has not yet been consumed.

## 2. Calendar and deliverable gates

| Window | Technical work | Protected documentation/handoff work | Exit and preparation |
| --- | --- | --- | --- |
| **September 28-October 2** | Reconcile Day-7 results; select bounded Windows automation/recovery gaps; begin repeated-run checks. | Inventory public/in-app guides; draft owner-guide outline and key procedures; first sanitization pass; draft post-handoff backlog; storyboard video. Confirm owners, access and intended publishing locations. | Prioritized board with named owners and remaining effort. Reserve acceptance/rehearsal sessions; obtain official release-identity and hosting decisions as early as possible. |
| **October 5-9** | Complete selected reliability changes and justified measured performance fixes; review candidate/security evidence. | Finish packaged/public/in-app guide content and owner-guide v1; resolve sanitization findings affecting shipped files; dry-run video; establish a stable video landing page/link if it will appear in packaged guides. | **October 9: freeze candidate source, images, packages, fixtures and shipped documentation.** Identify exact recording target and remaining owner decisions. |
| **October 12-16** | Independent acceptance on the frozen artifacts; finish required recovery/persistence checks. | Record and finish the install/demo clip against that workflow; captions/transcript and privacy review; verify public/in-app guide usability; owner reviews the guide; second sanitization check of candidate/transfer materials. | **October 16: acceptance complete; video and user documentation ready for approved distribution.** Owner-guide review comments and final rehearsal script ready. |
| **October 19-23** | Fix acceptance blockers only, with new identities and affected reruns. | Owner performs release/qualification/recovery/support rehearsal; correct guide gaps; finalize post-handoff backlog and custody map; review sanitized transfer set. | **October 23: owner-operated rehearsal complete.** Ready-to-execute adoption packet, named remaining exceptions and closeout checklist. |
| **October 26-30** | Verify final approved downloads/images and any transfer-related identity changes. | Complete authorized adoption/publication, final sanitization delta check, access and media custody transfer, backlog cutover, archival pointers and sign-off. | **October 30: operational closeout.** Either completed adoption or a fully documented migration-ready packet with adoption blockers and owners. |

If official naming, registry paths or packaging change after candidate acceptance, identify the changed bytes and rerun affected checks. Do not rename a candidate ZIP and treat it as verified official output. Resolve ownership and naming early enough to leave requalification time.

The finished video may be attached after October 9 to an already-approved stable external landing page without altering the frozen package. If the link is not ready before freeze, keep the packaged written guide complete and add the video link to the public repository afterward; do not silently modify frozen ZIPs or images just to add a link.

## 3. Suggested changes to the existing backlog

Start with [the current backlog](../../../task-backlog.md) and [active board](../../../current-tasks.md). Their old launcher-first dependencies and expired milestones need reconciliation. The v2 plan specifies the initial direction patch; this guide describes the continuing closeout work.

| Task(s) | Suggested disposition after Day 7 | Remaining outcome to select |
| --- | --- | --- |
| **068 + 091** Windows portability and owner qualification | Required, limited to remaining gaps | Run Windows PowerShell 5.1 behavioral/real-ZIP checks; make the existing qualification tools reproducible by the owner. A CPU CI job does not establish GPU correctness. |
| **093** Persistent data and recovery | Required | Demonstrate backup/restore, upgrade/rollback and interrupted-operation recovery; run repeated detect/cancel/export cycles and check RAM/VRAM/disk growth. Preserve export inputs and named volumes. |
| **092** Documentation | Required with explicit child deliverables | Track public guides, in-app guides, external setup guide and installation video separately, each with owner, due date and acceptance evidence. |
| **095** Governance/handoff | Required with explicit child deliverables | Owner's guide, instruction/skill alignment, sanitization coordination, post-handoff backlog and custody review. |
| **089** Adoption/ownership | Prepare immediately; execute when authorized | Receiving and backup owners can access and operate repositories, packages, release tooling, assets, guides/video and support records. Final transfer follows owner qualification/approval. |
| **076 + 027** Provider-key guidance and errors | Required guidance; evidence-selected code fixes | Document provider-account/key ownership and restrictions; fix observed ambiguous errors without broad error-framework restructuring. |
| **097** Podman qualification | Complete only the remaining acceptance | Carry forward valid Day-7 evidence, add missing host/provider/policy coverage and rerun changed surfaces. Remove the 087/096 dependency; retain stop/start user outcomes. |
| **026** CPU optimization | Conditional before October 9 | Select only a measured supported-host bottleneck; verify output correctness and memory as well as timing. No model/precision migration. |
| **077** Manifest/import hardening | Conditional | Fix a demonstrated integrity/import/recovery gap remaining after v2 work. Avoid duplicate package-check frameworks. |
| **094** Support snapshot | Evidence-gated | Add a small redacted export only if actual support cases cannot be resolved with current status/logs and documented collection. |
| **070** Restricted-network enhancements | Conditional requirement, otherwise future work | Qualify the promised connected/managed-network path; add offline distribution only if explicitly required, with a revised effort forecast. |
| **087 / PR #67; 096** Launcher and browser Exit/helper | Deferred beyond project closeout | Preserve evidence; document the existing tested command-based lifecycle. Reconsider only through a future owner's new scope decision. |
| **058, 059, 060, 061, 078, 029, 028** Architecture/build/dependency migrations, provider fallback and mobile work | Post-handoff consideration | Preserve rationale and entry criteria. Do not promise implementation or convert them into October release gates. |

### Updating the board without duplicating work

- [ ] Review each relevant task against actual Day-7 evidence; classify it as complete, remaining closeout work, conditional, deferred, or superseded. Do not restart completed slices because an old estimate lists the whole task.
- [ ] Keep existing TASK identifiers. Use named child deliverables under 092/095 rather than inventing conflicting task numbers. Create a missing task file only when it is selected and assign its canonical location through the existing workflow.
- [ ] Replace expired dates and PR #67 dependencies in active entrypoints. Preserve completed security work and distinguish superseded branch-integration gates from tests that actually passed.
- [ ] For every selected item record owner, backup/reviewer, input evidence, deliverable path, due date, acceptance test and current blocker. A role without an assigned person is an unresolved assignment.
- [ ] Reconcile `HANDOFF.md`, `.agent_work` board/backlog/status pointers, the current roadmap and the v2 instruction/skill corrections. Keep history dated; do not rewrite it to imply the new direction was always in force.
- [ ] Run `python .agent_work/scripts/validate_agent_work.py` after tracking changes, inspect its exit status, and manually check links and conflicting directions. A validator pass does not establish semantic consistency.

## 4. Deliverable locations and responsibility

These locations are recommendations for future execution; this document does not create the listed deliverables. Confirm the receiving owner's preferred durable host before publishing media or transferring accounts.

| Deliverable | Existing/proposed location | Responsible roles | Target |
| --- | --- | --- | --- |
| Owner's guide | **Proposed:** `docs/maintenance/owners-guide.md` | Maintainer drafts; receiving owner and backup perform procedures. | Outline October 2; v1 October 9; accepted rehearsal October 23. |
| Post-handoff backlog | **Proposed:** `docs/maintenance/post-handoff-backlog.md` | Project lead reconciles; receiving owner accepts priorities/custody. | Draft October 2; reviewed October 23; canonical cutover by October 30. |
| Installation/demo video reference and transcript | **Proposed:** `docs/installation-video.md`; video/source project in an owner-controlled approved location | Recorder/editor produces; independent tester and owner review. | Storyboard October 2; dry run October 9; final October 16. |
| Sanitization summary | **Proposed:** `.agent_work/tasks/active/TASK-095/repository-sanitization-summary.md`; sensitive findings kept privately | Maintainer performs scoped audit; designated owner verifies dispositions. | Early pass October 2; candidate pass October 16; final delta October 30. |
| Public repository guides | Existing `README.md`, `CONTRIBUTING.md`, `docs/` guide/support/release files | Documentation maintainer; independent installer reviews. | Packaged content October 9; external link verification October 16. |
| In-app guides | Existing `docs/{quick-start,user-guide,project-overview}.html` and paired `.md`, Help/resource links | Documentation maintainer; application tester verifies served pages. | Shipped content October 9; frozen-app acceptance October 16. |
| External setup guide | Existing owner-held guide; durable versioned destination recorded in handoff | Project lead/documentation owner | Content agrees with frozen workflow by October 16; custody October 23. |

Public owner documentation contains roles and safe procedures. Credentials, recovery codes, personal contacts and private infrastructure details belong in approved access-controlled records referenced by their purpose, not copied into Git.

## 5. Owner's guide: responsibilities and tested how-to procedures

The receiving owner should be able to answer: what am I responsible for, what do I check regularly, how do I make a safe change, and how do I recover or obtain help? Write this for a maintainer unfamiliar with this conversation and without a required AI tool subscription.

### Required content

| Chapter | Include | Acceptance exercise |
| --- | --- | --- |
| Ownership and service boundary | Primary/backup roles; supported profiles/versions; who approves releases, model changes and residual risks; support intake; escalation and response expectations agreed by the owner. | Owner names the responsible role for a failed install, leaked key, bad release and provider outage. |
| Repository and access | Repository/registry/media/document ownership; permissions needed for review, CI and publication; where private credential recovery is administered; contributor workflow and applicable review controls. | Primary and backup demonstrate their own access; no dependency on the departing developer's personal account/token. |
| Prepare a maintenance environment | Known tool versions and setup steps; source checkout; relevant tests; differences between ordinary user prerequisites and developer/operator prerequisites. | Owner prepares or verifies the environment using the guide and runs a focused check. |
| Qualify and publish a release | Select source/version, run required checks, produce CPU/CUDA images and real ZIPs, bind digests/checksums/assets, qualify four profiles, review notices/SBOM, approve/publicize the exact artifacts. | Owner performs an authorized rehearsal and identifies the exact source/image/ZIP/evidence relationship. Do not publish just to satisfy a rehearsal. |
| Roll back and recover | Stop the intended installation, preserve data, identify backups, restore to an isolated target, select a known-good release, verify recovered settings/session/export data, resume support. | Owner restores and verifies a backup and rehearses rollback without deleting production volumes. |
| Security and dependencies | Triage current alerts; separate shipped and development exposure; approved patch/requalification process; incident contacts; key rotation; model hashes and trusted-loader constraints. | Owner triages a synthetic advisory/key-exposure scenario, with no live secret in the exercise. Historical alert counts are not presented as today's status. |
| Providers, assets and models | Account/billing/quota ownership, key restrictions, authorized CA handling; asset provenance and custody; opt-in Model Upload Key administration and approved hash changes; feature disabled by default. | Owner explains normal user setup versus restricted administrative model changes and locates the relevant tested procedures. |
| Routine operation and documentation | Status/log collection, provider/TLS diagnosis, capacity/disk checks, data retention agreed with the owner; how Markdown/HTML, packages and video references are updated together. | Owner diagnoses a seeded failure and collects a sanitized support report. |
| Backlog and release decisions | Canonical backlog, severity/priority rules, verification evidence, first maintenance review and what remains intentionally deferred. | Owner selects one future item and describes its entry criteria, tests and rollback boundary. |

- [ ] Draft chapters from the actual v2 procedures and accepted candidate, linking existing maintained instructions instead of copying long command sequences into multiple manuals.
- [ ] For each how-to include prerequisites/permissions, inputs, exact version-appropriate commands or UI steps, expected results, verification, failure/rollback steps and evidence location. Clearly label examples; no live credentials or invented digests.
- [ ] Agree a realistic owner maintenance cadence: review support/security notifications during active use; periodically check access, backups and resource growth; rerun qualification for relevant release changes. Record the accepted cadence rather than promising unattended maintenance that does not exist.
- [ ] Have the receiving owner and backup walk through the guide before October 16, then perform the critical procedures by October 23. Record unprompted completion, assistance required, corrections and remaining blockers.
- [ ] Confirm ownership of external accounts, source media, guides and test fixtures; a successful document handoff without usable access is incomplete.

## 6. Public-facing and in-app guides

### Scope and source map

- Public repository: `README.md`, `CONTRIBUTING.md`, `docs/quick-start.md`, `docs/package-guide.md`, `docs/user-guide.md`, `docs/project-overview.md`, all four Docker/Podman CPU/GPU guides, and relevant `docs/support/` and `docs/release/` pages.
- In-app: `docs/quick-start.html`, `docs/user-guide.html`, `docs/project-overview.html`, their CSS/assets and the Help/resource links in `webapp/templates/towerscout.html`. The app currently serves these through `/docs/`; `webapp/towerscout.py` controls `PUBLIC_DOC_FILES`.
- Packaging: `scripts/package-release.ps1` explicitly lists shipped documentation. App route allowance, control-ZIP inclusion and runtime-image inclusion are separate checks; editing a repository file alone proves none of them.
- Compatibility: retain `docs/v1-rc1-quick-start.{md,html}`, `docs/v1-rc1-package-guide.md`, and `docs/towerscout-user-guide.{md,html}` as accurate historical pointers unless a deliberate reviewed compatibility change is needed.
- External setup guide: update its version/download references and operating steps using the same accepted workflow. Record owner, storage location, editing access and which public link is current.

### Required execution and acceptance

- [ ] Map each common user journey to one primary guide: choose/download the right package, verify/extract/import assets, choose engine/device, configure providers, perform first detection, review/export, cancel/recover, stop/relaunch, obtain help.
- [ ] Remove active PR #67 launcher assumptions and stale version/CUDA/package claims. State the actual supported profiles and prerequisites, including the approved Podman Compose-provider/Python requirement. Distinguish immutable pilot instructions from the new release.
- [ ] Synchronize each Markdown/HTML pair manually; there is no maintained HTML-doc generator in the current workflow. `node webapp/build.js` regenerates JavaScript, not these guides.
- [ ] Keep in-app instructions focused on user tasks and actionable recovery. Put maintainer responsibilities, source/build internals and backlog discussions in the owner's guide. Do not add an owner-guide route or new frontend framework just to deliver documentation.
- [ ] Verify all three actual in-app Help links, navigation anchors, CSS and relevant downloads on the running candidate. The existing docs route rejects nested paths: a new `docs/maintenance/` page cannot be assumed available through `/docs/maintenance/`. Prefer repository links for owner-only material.
- [ ] Test repository-rendered links separately from app-served HTML links. Root-relative `/docs/` URLs are intended for the running app and may not work by double-clicking an extracted HTML file; document supported viewing rather than claiming offline file viewing was tested when it was not.
- [ ] Inspect the final ZIP and runtime image for the intended guide versions. If changing an allowlist or route, run the relevant assertions in `tests/unit/test_flask_routes.py` and `tests/unit/test_release_package_script.py`; extend only for an actual changed contract. A pure prose change needs link/rendering/workflow review, not artificial source-string tests.
- [ ] Have an independent user follow the installation and in-app first-use guide without undocumented help. Record each point of confusion and resolve discrepancies before acceptance. Ensure the written guide remains usable without the video.

**Done:** Public repository, external setup guide, shipped package and running-app Help all describe the same accepted workflow and support limits. Their different rendering/link contexts have actually been checked.

## 7. Recreate the installation and demo clip

**Suggested format:** One concise primary clip, roughly 4-6 minutes, using the documented Docker CPU default, with brief chapters or companion inserts showing the Podman and NVIDIA differences. Use the owner-selected primary profile if changed before storyboarding. Four full duplicate videos are unnecessary; the written guides still cover all four profiles.

| Segment | Show | Avoid |
| --- | --- | --- |
| Choose/download | Tested version, CPU versus CUDA package, separate assets, prerequisites and verified download location. | Old pilot/PR #67 UI mixed into the new instructions. |
| Extract/setup | Ordinary-account spaced path, checksum/asset steps and actual supported setup entrypoint. Label shortened download/wait footage. | Developer-preseeded model files, source builds or hidden manual fixes presented as normal setup. |
| Configure | Where users enter their own authorized provider settings; expected validation/readiness. Pause recording for actual credential entry. | Recording a real key and relying solely on later blur, private AOIs or personal account details. |
| Demonstrate success | A small permitted search, completed detection, review and export. Explain CPU/GPU confirmation appropriate to the profile. | Treating health alone or CPU fallback as GPU proof; claiming the video certifies all profiles. |
| Stop/recover/help | Tested stop/relaunch path and where to find in-app guides and safe support instructions. | Showing an unimplemented browser Exit control or destructive cleanup. |

- [ ] By October 2, write the script/shot list and choose a permitted demonstration area, neutral desktop/profile and recording location. Define the primary profile, version and which differences need inserts.
- [ ] Dry-run by October 9 on the actual package workflow. Fix confusing instructions before final capture. Prepare placeholder/example screens for credential entry; never record private values in raw footage.
- [ ] After freeze, record against the inventoried candidate, then add readable captions, transcript and chapter markers. Identify version/profile and qualify any shortened waits. If the final published identity changes, review every version/download reference and recapture affected portions.
- [ ] Review every frame and the audio/captions for keys, personal paths, notifications, account details, private imagery and misleading steps. Check permitted use of imagery/music/assets. Keep necessary raw media in approved private storage.
- [ ] Have an independent tester compare the clip to the written guide and repeat the demonstrated path. Verify the intended audience can access the approved hosting link without the outgoing developer's account.
- [ ] Transfer the finished video, transcript/captions, editable project, permitted source assets and editing/hosting permissions to the receiving owner. Record custody in the owner's guide. Publish only under the applicable authorization.

**Done by October 16:** A reviewed replacement clip and written fallback are ready for distribution, with owner-controlled source/editing custody by October 23. A slide-only walkthrough or footage of an old candidate does not satisfy the installation demonstration.

## 8. Sanitize the repository and handoff materials

Sanitization means controlling what is exposed and transferred while retaining needed source, attribution and evidence. It does not mean indiscriminately deleting history, models, user data, or all `.agent_work` files.

### Scope to record before scanning

Record the intended source revision, branches/tags/history being transferred, public documentation, release assets, relevant CI artifacts, container images and external media/evidence. Distinguish public repository contents, private operational records and local user state. A clean working tree alone is not a completed sanitization review.

- [ ] **Early inventory, by October 2:** inventory path names and custody; identify tracked/untracked/ignored material, private fixtures, screenshots/traces, logs, certificates, keys, `.env` files, personal paths/contact details and undocumented external assets. Do not dump their contents into the chat or a public report.
- [ ] **Use controlled scans:** scan the intended transfer set with approved tooling that redacts values and records path/category/status privately. Review history and artifacts separately from the current tree. A secret-like variable name or synthetic test key is not automatically a leaked credential; triage findings before changing tests/docs.
- [ ] **Account for the existing scanner:** `.agents/skills/towerscout-secret-and-provider-key-safety/scripts/scan_for_sensitive_terms.py` recursively reads files including `.env`, prints matching line snippets, and returns 0 even when it finds matches. Do not run it on a live working directory into a shared transcript or interpret exit 0 as clean. Prefer an approved redacting scan of an isolated transfer copy with findings kept private.
- [ ] **Remediate current content:** replace private examples with synthetic data, remove accidental sensitive artifacts from the intended public set, correct ignore/allowlist rules and verify tests/docs still work. Ignoring a file does not remove it from Git history. Preserve license notices, attribution, required lockfiles and asset provenance.
- [ ] **Handle actual credentials distinctly:** notify the authorized owner through the approved process and arrange revocation/rotation; removing a visible string does not invalidate an exposed credential. Record confirmation without recording the value. For historical exposure, prepare a scoped remediation proposal; history rewriting, force pushes and destructive branch deletion require explicit coordination/authorization and are not routine cleanup.
- [ ] **Preserve evidence:** retain unique PR #67/release/test evidence in the appropriate controlled archive; publish a sanitized summary/pointer where suitable. Do not delete untracked qualification evidence, user data or parent-folder documents because they appear temporary. If archiving requires a move, verify exact resolved paths, reparse points, intended boundaries and destination copies/hashes first.
- [ ] **Candidate pass, by October 16:** inspect the source transfer set, actual ZIPs, relevant image contents/layers and approved media/report outputs. Confirm private configuration, raw traces, recordings and model payloads are absent from places they should not be distributed. Check all newly added guide examples.
- [ ] **Final delta pass, by October 30:** repeat the scoped review for changes since the candidate pass; verify the sanitized destination material and intended audience access. Record reviewed revisions/artifacts, methods, finding categories, dispositions, exclusions and reviewer. Do not claim inaccessible/unreviewed history or external assets were checked.

**Done:** No known unresolved sensitive-content exposure remains in the approved transfer scope, required evidence/source remains available to its owner, and a sanitized summary explains exactly what was checked. An unexpected substantial incident displaces optional work and may require a revised handoff forecast.

## 9. Create a useful post-handoff backlog

The post-handoff backlog is a maintenance decision aid, not a promise that every unfinished idea will be implemented. It must distinguish known defects, operational chores, conditional improvements and speculative redesigns.

- [ ] Draft `docs/maintenance/post-handoff-backlog.md` by October 2 using existing TASK IDs and links to retained context. Keep `.agent_work/task-backlog.md` authoritative during current execution; clearly label the owner-facing draft as a proposed successor so there are not two live assignment boards.
- [ ] For each carried item include: ID/title; observed problem and affected profiles; user impact; reproduction/evidence reference; existing workaround; severity and suggested priority; recommended next action; dependencies/entry criteria; acceptance checks; risks; rough effort confidence; proposed responsible role; and last-reviewed date.
- [ ] Keep resolved items out of the active future queue, with links to completion evidence where useful. Explain why deferred architecture work is deferred. Sensitive findings go through the owner's private process; use a sanitized public summary when appropriate.
- [ ] Seed the first maintenance review with continuing dependency/provider monitoring, periodic access/backup/qualification checks, measured performance issues, and any outstanding support findings. Carry Tasks 026/027/068/070/076/077/094 only to the extent that work remains. Tasks 058/059/060/061/078/029/028 remain optional decisions with explicit justification gates; PR #67 has no automatic restart date.
- [ ] Review with the receiving owner by October 23. Agree the first 30/60/90-day priorities without committing staff/time that have not been allocated. If the owner prefers GitHub Issues, migrate through an approved scoped process and choose that destination as canonical; do not maintain duplicate independently edited copies.
- [ ] By October 30, switch `HANDOFF.md`, the owner's guide and task/instruction entrypoints to the agreed canonical maintenance backlog. Archive the dated outgoing board or leave a clear read-only pointer. Verify all links and preserve task-ID history.

**Done:** The receiving owner can choose the next task without reading this conversation, knows what is deliberately out of scope, and has one current location to update status.

## 10. Closeout checklist and rules for the executing agent

- [ ] Reconcile Day-7 outcomes and selected backlog work; no leftover release gate is hidden in the post-handoff queue.
- [ ] All six requested additions have evidence: replacement video, owner's guide, post-handoff backlog, repository sanitization, public-facing guides and in-app guides.
- [ ] Shipped guides match the final accepted artifacts; any later package/image change has a new identity and affected checks rerun.
- [ ] Primary and backup owners have demonstrated needed access and critical operating procedures. Open adoption decisions have a named owner and explicit next action.
- [ ] A sanitized custody index identifies source, image/ZIP hashes, model/fixture provenance, qualification evidence, guide/video versions and storage locations. Private credentials remain outside it.
- [ ] Current task/instruction/skill entrypoints agree with the main-based direction; old PR #67 gates and expired dates do not control new agents.
- [ ] Final sign-off identifies completed acceptance, known limitations, approved residuals and the canonical maintenance backlog. If adoption remains unapproved, deliver the migration-ready packet without changing cdcai.

Keep changes narrow. Do not start a launcher, job queue, site redesign, new documentation generator or dependency migration to complete these deliverables. Read existing interfaces before copying commands; especially preserve the real `stop.cmd` arguments and package/asset identity distinctions documented in v2. Within a session that authorizes the work, do not request repeated permission for routine steps; retain the applicable boundaries for publication, account changes and destructive actions.

This guide was checked against the existing backlog, handoff tasks, guide files, documentation routes, package allowlist and scanner behavior. Its dates and effort allocations are recommendations. Actual Day-7 results, owner availability and execution evidence determine whether the schedule holds.
