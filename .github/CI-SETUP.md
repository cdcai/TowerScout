# Temporary TowerScout CI setup

This setup installs validation before the application adoption. It changes no
application file, container publish workflow, image, release, tag or wiki.

Both workflows run **manually only**. Each job checks out the same reviewed
source in `J-Schulein/TowerScout`:

`8682b8e6b31a4425ab626da557f58bff97076de7`

The fixed source supplies the tests/scripts that do not yet exist on cdcai
main. Credentials are not persisted by checkout. There is no arbitrary source
input, package-write permission, registry login or image push. The full Docker
build is blocking and produces a runner-local CPU-default image only.
Security reports are retained as artifacts instead of uploaded to code scanning,
so results from the pinned source are not attributed to the setup commit. The
setup workflows need only contents:read and no security-events write permission.

## What a successful setup run means

It validates the pinned source using the installed workflow definitions and
destination runner/policy environment. It does **not** validate the old cdcai
application, automatically satisfy PR #4 checks, or qualify a public release.
Record the workflow revision, checked-out source, run IDs, skips and advisory
findings separately. The existing formatting/type/Bandit/integration/SARIF
advisories remain; a green summary does not mean those advisory commands passed.

## Activation and adoption sequence

1. Review the setup diff and fork rehearsal before approving this setup merge.
2. After merging setup, run both workflows in cdcai and inspect every required
   job, including the full Docker build and the Windows contracts.
3. Incorporate the new cdcai base into the adoption branch. Resolve these two
   temporary workflow files back to normal PR/main triggers and checkout of
   the proposed merge revision. Retain the blocking full build. Remove this
   temporary setup note in the adoption change after recording the setup proof.
4. Run normal cdcai checks on the latest adoption PR revision. Configure the
   observed nine required job names, require independent approval, and verify
   failed/missing checks prevent merging. Only then consider adoption approval.

Do not treat a manual setup run on an earlier pinned source as evidence for a
later adoption revision. The normal workflows must test the actual updated PR.
No privileged pull_request_target trigger is used. Publishing remains separate.

## Rollback

Before adoption, a reviewed revert of this setup removes only these new files.
After adoption, evaluate a new forward fix instead of reverting the modern
application to the old code. Preserve the pre-adoption ZIP, Git mirror and
settings audit; never restore by blindly force-pushing a mirror.
