# TowerScout Documentation Review - Round 4 Focused Instructions

Thank you for performing this short confirmation review. This round is limited
to the six Round 3 findings. It is not installation testing, security/legal
approval, content-freeze approval, or final release qualification.

## Review Boundary

The readers remain novice Windows users and their Local IT staff. Docker or
Podman, CPU or compatible NVIDIA GPU, and Google Maps or Azure Maps are
independent user choices.

Do not run commands, enter provider credentials, create cloud resources, or
change repository/release/Wiki state. Do not include keys, `.env` contents,
private locations, raw logs, browser traces, certificate details, exports, or
volume contents in feedback.

## Focused Reading Order

1. `rendered-docs/docker-gpu-user-guide.html`, especially **Stop, Restart,
   Status, And Logs** and the degraded asset-recovery command.
2. `rendered-docs/podman-gpu-user-guide.html`, covering the same sections.
3. `rendered-docs/package-guide.html`, especially **Manual Asset Staging And
   Import**, Podman port recovery, and **Assets Missing Or Corrupt**.
4. Maintained and rendered Quick Start prerequisite sections.
5. Rendered Markdown User Guide **Circle Search**.
6. Wiki **Before You Install** and **Everyday Commands**.
7. Package Guide issue, release, and Azure authentication links.
8. Draft PR #94's rendered description.

## Required Confirmation

Please confirm:

1. GPU asset-recovery examples include the selected `-Gpu` mode and active
   `-Port`.
2. The Package Guide clearly says asset import accepts `-Engine`, `-Gpu`, and
   `-Port` and tells readers to use the non-secret setup record.
3. No current text says asset import lacks a GPU option or tells readers to add
   `-Port` to `logs.cmd` or `stop.cmd`.
4. The first PowerShell instruction tells a novice how to open a normal
   Windows PowerShell window.
5. Markdown circle instructions place the circle on the map before estimating
   tiles.
6. The conditional Podman machine check applies visibly to both CPU and GPU.
7. The three Package Guide destinations are clickable and descriptively named.
8. PR #94 renders with headings, paragraphs, bullets, and numbered steps—not
   as one continuous line.

The previously passing 1440/720 setup cards and Google explanation do not need
another broad audit. Please report a regression if one is obvious, but this
round should not restart settled design decisions without new evidence.

## Requested Response

Begin with `ready for content freeze`, `ready after minor edits`, or `hold for
focused fixes`.

For each remaining issue, provide the exact page/heading, reader impact,
suggested correction, and whether it blocks rebuild. End with an explicit list
of remaining rebuild blockers, or `none`, plus the limits of the review.
