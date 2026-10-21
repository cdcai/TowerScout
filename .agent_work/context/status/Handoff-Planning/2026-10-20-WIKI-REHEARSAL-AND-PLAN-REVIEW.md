# Fork Wiki Rehearsal And Transition Plan Review

**Date:** October 20, 2026. **Tasks:** TASK-089 / TASK-092.
**Overall status:** Tuesday substantially complete, with specific follow-ups;
Wednesday preparation partly completed early. Official adoption has not occurred.
Delivery target remains October 27; October 28-30 remains the support buffer.

## Verified fork rehearsal

- Published [fork wiki preview](https://github.com/J-Schulein/TowerScout/wiki):
  14 pages and one sidebar, clearly labeled as preview documentation.
- Source: `ca24d6f351a505dc16d0ac4f407adc50eb034b03`, pushed to the fork's
  `chore/task-089-adoption-preparation` branch using the user-confirmed identity.
- Wiki commit: `5cb595273a00ee00d4627024be71758f9386de40`.
- Verified all 15 Git blob hashes against canonical UTF-8 source plus the
  recorded preview transformations; remote master matched the local commit.
- All 14 pages returned HTTP 200 anonymously and contained the preview and
  published-preview labels. All 48 relative page references resolved to known
  pages. This does not claim every external link or heading anchor was tested.
- Eight unique mapped repository destinations were checked before publication;
  manual links point to the exact published preparation commit.
- Browser review confirmed Home/sidebar and Podman guidance rendering.
  Publication labels and a Home punctuation encoding error were corrected,
  then published bytes were rechecked. The final Home screenshot was saved.
- Local evidence: `output/handoff/fork-rehearsal-ca24d6f/manifest.json`,
  `publication-preflight.json`, `publication-verification.json`,
  `published-wiki-home.png`, and refreshed `review.html` in the original workspace.
  These files are local evidence, not automatically delivered owner materials.
- No cdcai repository/wiki/image/release mutation. No runtime qualification or
  final video publication is established by this rehearsal. Official wiki
  source still targets cdcai; preview-only destination rewrites remain separate.

## Review against Tuesday's plan

Reviewed the Tuesday section of the local *TowerScout transition and closeout
plan* (`output/docx/towerscout-detailed-transition-plan.docx`) and its shared
source `output/handoff/build_transition_plan.py`, including later milestones.
The original plan remains the schedule baseline; the October 21 audience correction
separates the manager leadership report from Chris's packet. This record supplies actual
status without overwriting user checkmarks or rewriting historical plans.

| Planned action | Assessment | Evidence / remaining action |
| --- | --- | --- |
| Meet Chris; agree ownership, access, destination, delivery and release name | Core decisions complete | User-reported meeting; Administrative access previously verified. Agreed cdcai/TowerScout and proposed v0.1.3 title. Recheck exact identity availability before building. |
| Confirm registry/workflow access | Partial | Repository admin access is established. Verify effective Actions/package permissions, GHCR linkage and public access before official execution. |
| Classify repository and .agent_work | Complete for approved first pass | Local reconciliation, O1/O2/O3 organization and root/maintainer follow-up records exist; references checked and deferred history preserved. Private custody remains separate. |
| Draft owner-manageable backlog | Partial | Owner priorities, deadlines, triggers and retained task IDs are recorded. Finish plain-language item details, effort, dependencies and needed expertise; review priorities with Chris. |
| Make maintenance obligations explicit | Documented; detailed assignment confirmation pending | October 31 security expiry and January 31 ML review/earlier triggers recorded. General ownership is accepted; do not infer agreement on each advisory-monitoring, assessment, testing and release-approval responsibility. |
| Private evidence, provider accounts/billing and video hosting | Unconfirmed | Select approved email/SharePoint destination and custody; confirm whether provider accounts are owner-managed or user/site-managed, and identify any shared-account responsibility. Choose video host and test playback. |
| Follow-up meetings and action-list distribution | Unconfirmed | Attendance was reported feasible, but actual calendar bookings and distribution are not evidenced. Prepare/send only when instructed to send. |

**Tuesday closure:** Do not check every Tuesday item complete yet. The central
ownership milestone is achieved, cleanup preparation has progressed beyond
its initial proposal, and the remaining items can be closed during October 21
preparation without consuming the support buffer if handled promptly.

## Overall progress and next steps

1. **October 21 - finish readiness and owner decisions.** Close the open
   Tuesday items above; complete backlog details, private-delivery inventory
   and recording/owner-material drafts. Confirm report chronology and baseline
   evidence; an outline is not a completed leadership report.
2. **October 21 - finalize the adoption review package.** Compare fresh cdcai
   state with the prepared branch; preserve independent changes. Review the
   complete diff, CI, official destination inventory, merge/history approach,
   release identity and permissions. Prepare the PR and an explicit map of
   official changes to required tests and any justified evidence reuse.
3. **October 22 - review and adopt.** Use the planned owner review to approve
   the concrete scope and execution sequence. Open/review/merge through the
   agreed process, then build official CPU/CUDA images and pinned packages.
   Pass fresh security gates and record exact source/digests/checksums.
4. **October 23 - verify distribution and practice maintenance.** Check exact
   browser-downloaded official bytes, anonymous access and affected real
   runtime behavior; obtain required independent results. Practice a small
   Codex maintenance task with Chris. Test the video hosting arrangement.
5. **October 26 - release decision, demo and report.** Close actual blockers,
   obtain the recommendation decision, record the settled Docker/CPU workflow,
   and finish the leadership-report draft with evidence-backed comparisons.
6. **October 27 - deliver and confirm receipt.** Publish/verify official wiki
   and final video against the delivered release, finish owner guidance,
   prioritized backlog, maintenance calendar and private-material delivery;
   record Chris's acceptance and access to the final packet.
7. **October 28-30 - support and closeout.** Handle last-minute questions and
   corrections, confirm outstanding responsibilities, and end support on
   October 30. Do not treat October 31 security expiry as extended by handoff.

The fork preview, documentation integration, organization and destination
preparation advance Wednesday work. They do not complete official adoption,
image/package validation, owner practice, the demo, leadership report or
receipt. The schedule remains a target, not a verified forecast: build/security
failures or missing independent testing could require replanning.

## Consistency notes

The owner-maintenance guide's 30-minute practice is a focused exercise within
the transition plan's proposed 75-minute October 23 meeting, not a replacement
meeting duration. Confirm the calendar with Chris. Older dated records saying
no wiki publication occurred remain valid for their recorded slices; current
board/task summaries now distinguish completed fork rehearsal from pending
cdcai publication. The original checkout is preserved; current preparation
and this record live in the isolated adoption worktree.
