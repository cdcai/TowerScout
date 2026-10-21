# ADR-020: Task-101 Node And Puppeteer Security Baseline

**Status**: Accepted
**Date**: August 19, 2026
**Task**: `TASK-101: extract-zip Advisory Assessment And Release-Gate Disposition`
**Scope**: Frontend dependency security, maintained Node baseline, Puppeteer
compatibility, CI browser acquisition, and Docker frontend builds

## Decision

1. Set the frontend tooling engine policy to Node `>=22.12.0`. Use the
   maintained Node 22 line in GitHub Actions and the Docker frontend stage so
   later Node 22 security patches are not frozen by an exact image tag.
2. Pin `puppeteer@25.8.0` exactly. Accept its locked
   `puppeteer-core@25.8.0` and `@puppeteer/browsers@3.2.1` graph, which no
   longer contains `extract-zip`.
3. Preserve `package-lock.json` as the reproducible install contract and use
   `npm ci`. Do not use an npm override, forced downgrade, audit-threshold
   reduction, or alert dismissal to hide the advisory.
4. In the two Task-087 browser jobs, set the supported
   `PUPPETEER_SKIP_DOWNLOAD=true` control and retain the exact
   `playwright@1.62.0` Chromium install as the single intentional browser
   acquisition source.
5. Treat CommonJS loading, bundle reproducibility, focused dependency and CI
   contracts, Task-087 browser/host-helper jobs, and Docker frontend/full
   builds as required compatibility evidence.

## Context

Dependabot alert `#76` reported high-severity `GHSA-jmr9-qjv8-65gv` /
`CVE-2026-56876` in the development-only graph
`puppeteer@24.19.0 -> @puppeteer/browsers@2.10.8 -> extract-zip@2.0.1`.
No patched `extract-zip` release was available. The dependency is absent from
the shipped Python runtime and normal-user Windows package, but maintained
browser-install tooling could execute the affected extraction path and the
blocking frontend audit correctly rejected the graph.

Puppeteer 25.8.0 requires Node 22.12 or newer and replaces that dependency
path with `@puppeteer/browsers` 3.2.1. Task-101 therefore crosses both a
Puppeteer major boundary and the historical Node 18 tooling baseline.

## Options Considered

1. Dismiss or risk-accept alert `#76` because the graph is development-only.
2. Mask the vulnerable transitive package with an npm override or forced
   downgrade.
3. Keep Puppeteer 24 and wait for a patched `extract-zip` release.
4. Upgrade Puppeteer and every maintained Node/build baseline together, then
   run the proportionate compatibility matrix.

## Rationale

Option 4 removes the vulnerable package rather than hiding it, restores the
blocking audit, and keeps TowerScout on a maintained Node line. Exact
Puppeteer and lockfile versions make the security outcome reviewable, while
the Node 22 aliases allow maintenance patches within the supported major.
Keeping one pinned Playwright Chromium source avoids redundant browser
downloads and makes the Task-087 jobs' executable source explicit.

## Impact

- Developers and CI need Node 22.12 or newer for frontend tooling.
- The Docker frontend stage now resolves a maintained Node 22 image.
- CommonJS Puppeteer consumers remain supported and are covered by an explicit
  CI smoke assertion.
- Task-087 remains paused. PR #72 and default-branch dependency reconciliation
  later passed; this decision still does not resume Task-087. Resumption
  requires semantic integration into PR #67 and green checks at that branch's
  new exact head, in that order.
- ADR-016 Decision 2 is superseded only for its Node minimum. Its tracked
  `package-lock.json` and `npm ci` reproducibility policy remains authoritative.

## Validation And Review

Local Task-101 validation on August 19, 2026 established a clean isolated
install, zero high-severity npm audit findings, the exact selected graph,
global `extract-zip` absence, CommonJS loading, focused regression contracts,
frontend bundle equivalence, and successful Docker frontend/full builds.
PR #72 CI/CD run `32300398378` and Task-087 compatibility run `32300398377`
passed at implementation head `a87ab53`. Final-head runs `32308971393` and
`32308971392` then passed at `820b649`, and PR #72 squash-merged as `0cc189c`.
Exact-main runs `32310281115` and `32310281051` passed; alert `#76` closed as
fixed with no dismissal metadata. PR #67 integration/validation remains the
separate acceptance gate recorded in Task-101.

Review this decision when Puppeteer raises its Node minimum, TowerScout changes
browser acquisition tooling, Node 22 leaves maintenance, or a new critical/high
advisory affects the selected graph.
