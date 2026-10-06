# TowerScout Documentation Review - Round 3 Instructions

Thank you for reviewing the revised TowerScout documentation. This is a
focused confirmation round before documentation content freeze. Please assess
the supplied review ZIP and draft PR #94; do not treat the material as a final
release, installation test, legal/security approval, or instruction to run any
command.

## Audience And Choice Model

The final readers are novice Windows users and their Local IT staff. Assume a
reader may have no prior experience with PowerShell, ZIP extraction, GitHub
Releases, GHCR, Docker, Podman, CPU/GPU/CUDA, APIs, certificates, hashes, or
sidecar files.

Docker or Podman, CPU or compatible NVIDIA GPU, and Google Maps or Azure Maps
are three independent user choices. They are supported options, not pathways
assigned by project support.

## Suggested Reading Order

1. Open `index.html` from the extracted review folder.
2. Follow the Wiki journey in this order:
   - Home
   - Before You Install
   - Choose Your Setup
   - Google And Azure API Credentials
   - Install And First Run
   - Everyday Commands
   - Troubleshooting And Safe Support
3. Read the maintained Quick Start HTML and Markdown as standalone package and
   in-app entry points.
4. Read the User Guide and Local IT Guide HTML/Markdown pairs.
5. Follow one CPU engine guide and one GPU engine guide, then compare the
   equivalent Docker/Podman route where behavior differs.
6. Use the Package Guide to check the detailed hash, explicit-ZIP, port,
   provider, TLS, and support procedures.
7. Review draft PR #94 only after the packaged journey, so repository context
   does not hide gaps in the standalone material.

## Focused Round 3 Checks

Please confirm whether the following Round 2 issues are now resolved:

1. At both 1440 x 1000 and 720 x 1000, every setup card initially shows its
   complete command, including `-Gpu off` or `-Gpu on`, without horizontal
   page or code-box scrolling.
2. The maintained HTML Quick Start explains Podman GPU/CDI preparation, links
   the detailed guide, places package-local helpers after extraction, and
   distinguishes general readiness from `selected_device=cuda`.
3. Every relative hash or package-helper command first tells a novice which
   folder to open and how to open PowerShell there.
4. CPU/CUDA alternatives are present, and every adaptable example tells the
   reader to preserve their selected Docker/Podman and CPU/GPU settings.
5. Start/reopen, status, and stop are separate tasks that cannot reasonably be
   mistaken for one block to paste.
6. TLS recovery clearly separates diagnostic-only work, review/approval, and
   the approved apply/restart action, with a direct handoff to the concrete
   procedure.
7. Google guidance names Maps JavaScript API, Places API (New), Maps Static
   API, and Geocoding API. It should clearly disclose that TowerScout's one-key
   design requires `Application restrictions: None` for combined browser and
   server requests, while API restrictions remain limited to those four APIs.
   Treat this as a clarity/consistency review, not independent security
   approval. Flag any text that presents this limitation as Google's preferred
   design or hides the stop/use-Azure boundary for stricter organizations.
8. No current user journey requires project-support assignment or confirmation
   before choosing a supported option.
9. Credentials lead to installation, external destinations are usable links,
   and conditions/warnings appear before the actions they qualify.
10. First-use terms are explained briefly, and the first search gives an
    understandable radius unit, polygon-completion instruction, and bounded
    illustrative tile target.

Also flag any new contradiction, missing prerequisite, unsafe recovery advice,
broken local link, or mismatch between an HTML page and its Markdown partner.

## HTML Review Guidance

- Use a normal desktop browser at 100% zoom.
- Check `maintained-html/quick-start.html` at 1440 x 1000 and 720 x 1000.
- Confirm the page itself does not scroll sideways and the four setup commands
  do not require horizontal scrolling inside their cards.
- Use Tab to confirm the skip link and interactive links have visible focus.
- Open the local navigation links from `index.html`; report any missing page,
  stylesheet, or fragment destination.
- Compare the maintained Quick Start, User Guide, and Local IT HTML pages with
  their rendered Markdown counterparts for task-level meaning. Pixel-perfect
  matching is not required.
- If local `file://` navigation is blocked, report the limitation and use a
  safe local server or your prior controlled HTML-injection method. Do not edit
  the extracted source to make it render.

## Safety And Scope

Do not enter or share provider keys, `.env` files, private locations, browser
traces, raw logs, certificate details, screenshots containing sensitive data,
exports, or named-volume contents. Do not create cloud resources, enable
billing, run installation commands, or change repository/release/Wiki state
for this reading review.

The release identities, hashes, images, and screenshots/video that do not yet
exist should remain visibly pending. Their absence in a draft is not a reason
to invent values or claim final release approval.

## Requested Response Format

Start with one recommendation: `ready for content freeze`, `ready after minor
edits`, or `hold for focused fixes`.

For each finding, provide:

- severity: blocker before rebuild, improve before publication, or optional;
- exact file/page and heading;
- viewport when visual;
- what a novice may misunderstand or do incorrectly;
- a concise suggested correction; and
- whether it is a regression of R2-01 through R2-12 or a new issue.

Please end with:

- the 1440 px and 720 px command-card result;
- whether a novice can select and complete each supported route without
  project coaching;
- whether the Google one-key limitation and stop condition are understandable;
- any limits of your review; and
- a clear list of remaining rebuild blockers, or `none`.
