# Destination setup before adoption - October 21, 2026

**Tasks:** TASK-089 / TASK-104. **State:** setup PR #5 merged as `87ca900`
with Chris's approval relayed by the user. Destination setup validation passed;
updated adoption-head validation and required-check enforcement remain pending.
Application adoption PR #4 remains draft and requires separate approval.

## Sequence correction

The user approved the revised setup-first sequence after the audit found no
registered cdcai workflows, no main protections, and disabled Dependabot and
secret protections. Draft adoption PR #4 stays parked until destination CI
and protections are demonstrated. Fork-only CI is not destination acceptance.
Fork final preparation head `e4adaf0` passed blocking CI runs `39642065995`
and `39642065993`; those results precede the full-build ratchet below.

## Bounded workflow change

- CI's existing full Docker build now runs on pull requests and is blocking.
- It waits for the Python, frontend, frontend-container and security jobs.
- The build is runner-local; it logs into no registry and publishes no image.
- A manual CI trigger supports repeatable setup validation.
- Existing Black, mypy, Bandit, integration and SARIF advisory behavior is
  unchanged. The strict vulnerability gate remains blocking.
- This CPU-default build does not qualify official CPU/CUDA images, model
  execution, downloaded packages or the required two-host workflows.

## Initial destination workflow setup

Prepare a separate branch from exact cdcai main containing only the two
validation workflows and a setup explanation. Copy the reviewed job bodies,
but use manual-only triggers and pin every checkout to one exact reviewed
adoption commit in J-Schulein/TowerScout, with persisted credentials disabled.
This avoids running new tests against cdcai's old application or importing
the application merely to install CI. No publish workflow is included.

Rehearse these exact setup files on the fork before asking for setup merge
approval. Record workflow-file revision and tested-source revision separately:
bootstrap results validate the pinned source and must not masquerade as
normal PR #4 checks. cdcai execution remains pending until the approved setup
merge. There is no privileged pull_request_target execution path.

After the setup merge, merge that cdcai base into preparation without rewriting
history. Resolve the two workflow files back to normal PR/main triggers and
normal checkout of the tested merge revision, retaining the blocking full
build. Rerun destination and fork checks on the resulting exact head/base.

## Repository settings and verification

The user authorized proceeding with the reviewed sequence. Prepare/read back
each payload and retain the pre-change settings. Enable Dependabot alerts,
secret scanning and push protection. Keep the selected-Actions allowlist,
read-only default workflow token and external-contributor approval policy.
Disable unneeded workflow-created PR approval capability.

The initial rule required one independent GitHub approval. On October 21,
2026, the user authorized using Chris's verbal approval instead. Verified
cdcai main now requires zero approving GitHub reviews and does not require
independent approval of the latest push. The PR requirement, stale-review
dismissal, conversation resolution, no force-push/deletion and administrator
enforcement remain. Record the user's confirmation of Chris's approval and
approved scope before a cdcai merge; do not invent approval or a GitHub review.
The settings change itself approves no merge. The before/after receipt is
`output/handoff/destination-readiness-audit/review-policy-amendment.json`
in the original local workspace.
Required status checks must be added after real destination executions make
their exact names available; do not claim the intermediate rule enforces CI.
No linear-history rule: the adoption must retain historical ancestry.

The proposed nine required jobs are frontend-test, Docker frontend stage,
test (3.11), test (3.12), security, Full Docker build, Production controller
contracts, Production controller e2e (simulated helper), and Windows host-helper
contracts. Verify failed/missing checks block merging and preserve the real
advisory dispositions. Recheck check identities and GitHub Actions provenance.

Enable automatic Dependabot security PRs once normal CI is active and the
adopted manifests are on main; enabling them against the old application would
generate obsolete update PRs while source adoption is pending. Alerts remain
visible during this staging period. This timing is deliberate, not completion.

Package creation/inheritance/public access remains unverified; the current
credential lacks read:packages for inventory. Establish it before official
publication. A release approval environment requires a corresponding workflow
reference and a reviewed owner policy; it is not established by an empty
environment setting alone. No release environment is claimed configured here.

## Dependency-graph follow-up

The source pins on fork main are aiohttp 3.14.4 and Pillow 13.0.0. Two native
October 6 submissions still report aiohttp 3.14.3/Pillow 12.3.0, explaining the
stale inventory associated with alerts #77/#78/#79. The underlying GitHub
scheduling reason remains unknown. Root and webapp scopes must both refresh.

A separate fork-main branch changes comments only in requirements-dev.txt and
webapp/requirements.txt to request native resubmission after approved merge.
Dependency specifiers must remain identical. PR #69 established the same
root-refresh mechanism previously. Preserve the existing Low torch alert;
do not dismiss alerts or submit an artificial replacement detector.

Completion requires current native submissions, corrected inventory without
the obsolete aiohttp entry, #77/#78/#79 marked fixed, and review of any new
findings. Merge any approved refresh commit into preparation and recheck CI.

## Completion boundaries

No setting, PR, run or merge is complete merely because this plan names it.
The execution receipt/PR descriptions must record actual results. Setup merge,
fork graph-refresh merge, adoption merge, official publication and release
qualification are separate checkpoints. Historical candidate evidence and
Chris/manager packet separation remain preserved.

## October 21 execution and adoption integration

Chris's approval for the exact setup PR #5 was relayed by the user. The merge
`87ca900` preserves the approved setup tree. The pre-adoption ZIP checksum was
reverified before merge; the Git mirror and settings audit remain preserved.
Destination runs `39669780901` and `39669784666` passed all nine jobs, including
the full Docker build, while checking out exact fork source `8682b8e`.
Each Python job passed 586 unit tests with 162 skipped and five subtests passed.
The same five advisory integration failures and formatting/type/Bandit findings
remain. Setup runs are not acceptance of the updated adoption PR or release.

Fork PR #115 merged as `55b3330`. Post-merge runs `39661712534` and
`39661712581` passed, including the real full build. Native graph run
`39661728819` refreshed both root and webapp submissions. GitHub now reports
aiohttp 3.14.4 and Pillow 13.0.0; alerts #77/#78/#79 are fixed without dismissal.
The separate Low torch alert #58 remains open.

The authorized integration brings both main revisions into preparation without
rewriting history. Restore the two temporary setup workflows to the exact
normal reviewed workflows from `8682b8e`, remove `.github/CI-SETUP.md`, and
preserve PR #115's two manifest comments. No runtime/dependency version change
is intended. Fresh fork and cdcai PR checks on the resulting head/base are
required. Configure the nine observed job names with GitHub Actions provenance
and up-to-date-branch enforcement; record the actual settings readback and
required-check results separately before claiming this checkpoint complete.

Keep fork PR #114 draft: it supplies the already-pushed preparation branch to
cdcai PR #4, and its official image defaults precede publication. Merging fork
main is not a prerequisite. No application adoption, image/release/wiki
publication or independent qualification is implied by this integration.
