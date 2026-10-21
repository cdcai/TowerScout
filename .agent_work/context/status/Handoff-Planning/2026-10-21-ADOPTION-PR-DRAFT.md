# Adoption PR preparation text

**Submitted:** [cdcai draft PR #4](https://github.com/cdcai/TowerScout/pull/4).
This file retains the preparation text; the live PR and [submission receipt](2026-10-21-ADOPTION-SUBMISSION-AND-CHECKS.md) record current execution status.

**Target:** cdcai/TowerScout:main.
**Proposed source:** J-Schulein/TowerScout:chore/task-089-adoption-preparation.
**Source checkpoint:** approved PR #113 merged as `60ae1c9` and integrated
at `8b49f74`. The final submitted head and remote results belong in the PR
description and execution receipt. See the [dependency review](2026-10-21-PR113-DEPENDENCY-AND-ADOPTION-REVIEW.md).

## Proposed title

Adopt TowerScout Windows deployment, application improvements and owner guidance

## Proposed description

The original repository does not contain the fork's accumulated deployment,
provider, reliability and maintenance work. This adoption brings that reviewed
history into cdcai and prepares owner-controlled Windows Docker/Podman CPU/CUDA
distribution. It retains attribution to the original application and models.

The changes include application/provider improvements, container and Windows
package tooling, release/security checks, user and Local IT documentation,
version-controlled wiki sources, and maintained task/owner guidance. Preparation
aligns official destinations, incorporates accepted Podman installation limits,
organizes historical records and preserves deferred launcher work without
resuming it. The optional Codecov upload was removed; local coverage generation
and the existing artifact path remain. Approved PR #113 updates aiohttp to
3.14.4 and Pillow to 13.0.0, with matching security tests and the Pillow runtime
minimum. The model weights, detection thresholds and torch/torchvision pair
are unchanged.

Validation: exact fork v0.1.3-rc5 bounded acceptance is documented in ADR-026.
The preparation delta passed 63 selected checks again on October 21 (23.19 seconds),
strict task validation, and a verified 14-page fork wiki rehearsal. October 21
read-only checks confirmed cdcai ancestry, administrative access, enabled Actions
and allowlist compatibility. These are not new official-image/package acceptance.
The dependency PR passed blocking CI and 586 unit tests on each Python version.
The combined adoption rehearsal passed 144 selected tests on repeat. Existing
advisory integration failures and the initial local loopback reset remain
documented. Final adoption-head CI is required before merge.
A preparation-branch push alone does not trigger the main-only push workflow;
use a PR targeting main for CI, or explicitly approved validation dispatches.

Chris approved enabling cdcai Issues; the setting is now applied and verified.
Remaining official delivery: verify public support links, agree merge/build identities; verify package publication/public access; build and
qualify exact official artifacts; publish wiki/video separately; complete owner
practice and receipt. Current security exceptions expire October 31, 2026 at
23:59:59 UTC. Neither this PR nor its merge promotes Latest or renews exceptions.

## Review map

- Runtime/application: webapp and accepted TASK-105 / ADR-026 evidence.
- Distribution: Dockerfile, compose files, scripts, release contracts/notices.
- Automation: .github workflows and security policy; distinguish advisory CI
  reporting from enforced release gates.
- User materials: README, docs, paired HTML and wiki sources.
- Maintenance/history: .agents skills, .agent_work current board/backlog,
  decisions and preserved historical evidence.

Use a normal merge commit if the owner accepts the recommended history approach.
The latest cdcai main was an ancestor at preflight; recheck before merge. Do not
force-push, bulk-copy tags, remove unique evidence, or describe all accumulated
history as newly tested in this PR.
