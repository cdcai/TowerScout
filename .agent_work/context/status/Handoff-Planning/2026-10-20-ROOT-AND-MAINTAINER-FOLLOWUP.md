# Root Organization and Maintainer Guidance Follow-up

**Date**: October 20, 2026

**Task**: TASK-089; local preparation only

## Outcome

All 31 tracked root files remain in place. The repository map now lists every
file in a functional group and explains why its path is retained. No further
root relocation is recommended for this handoff. The earlier O1/O2/O3 archive
and navigation work remains unchanged.

The notices are copied by Dockerfile line 56 and used by the release packaging
script and notice/manifest tests. `package.json` invokes `validate_stage_0.sh`.
Startup, Compose and tool configuration paths remain established interfaces.
Local `.env` and `debug.log` are private material; their contents were not read
or copied into this review.

## Corrections applied

- HANDOFF now records Chris's accepted ownership, access, destination and title,
  delivery target October 27, and outgoing support end October 30. The October
  31 security expiry is distinguished from the support deadline. Historical
  pilot sequencing no longer appears as the current adoption hold.
- CONTRIBUTING distinguishes ordinary squash merges from the one-time adoption
  history/provenance review, and distinguishes policy from enforced settings.
- GitHub repository instructions no longer treat completed Tasks 066/067 as
  future gate decisions. Current CI marks full-image build advisory while the
  separate frontend-stage build is blocking; release acceptance remains separate.
- The owner guide now supplies a 30-minute maintenance exercise and concrete
  receipt criteria. It does not repeat Chris's existing application training.

## Skills and workflow review

The preceding preparation pass already reviewed all 12 skills, updated the
router/release gate and sanitized-input warning, and corrected Copilot guidance.
This follow-up rechecked skill metadata/descriptors and four workflow YAML
files, inspected current directions and fork references, and compared the CI
policy correction with actual workflow fields. No additional skill installation,
skill rewrite, workflow mutation or remote settings change is needed for this
slice. Existing historical fork/candidate references retain their provenance.

## Verification

- All 31 tracked root files retained; no moves or deletions.
- Relative Markdown file targets in edited root/navigation guidance resolve.
- All 12 skill headers/invocation descriptors and four workflow files parse.
- Strict agent-work validator and whitespace checks pass.
- No runtime/build/package files changed; no runtime qualification is claimed.

## Remaining work in execution order

1. Integrate accepted Podman short-path/Python guidance into the canonical
   manuals and paired HTML/served Help. Check the generation process first.
2. Review official destination/default references across package scripts,
   manifests and documentation; retain historical provenance intentionally.
3. Review the full incoming adoption diff for private artifacts and finish the
   private-material index, backlog dispositions and receiving-owner receipt plan.
4. Review and obtain publication authorization for the concrete fork wiki
   preview, then inspect rendering and navigation. No wiki is live from this work.
5. Verify execution-time repository/package permissions, public commit identity,
   security-review follow-up, complete-diff checks and adoption merge approach.
6. Complete authorized cdcai adoption, official builds and qualification before
   public recommendation; finish video, report and owner delivery.

Some dated requirements/design and task records retain earlier planning dates.
The active board controls current timing; the official documentation review must
distinguish historical text from current user instructions rather than replacing
all dates or fork URLs indiscriminately.
