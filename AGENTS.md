# TowerScout Current Delivery Direction

Start with these sources, in order:

1. `.agent_work/current-tasks.md`
2. `.agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-prioritization-v2.md`
3. `.agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2.md`
4. The relevant route selected by `.agents/skills/towerscout-skill-router/SKILL.md`

For the active ML runtime migration, also read
`.agent_work/decisions/022-cuda128-blackwell-ml-runtime.md` and
`.agent_work/tasks/active/TASK-103-cuda128-blackwell-ml-runtime.md`.
For Windows package distribution and execution-policy claims, also read
`.agent_work/decisions/023-unsigned-windows-package-support-boundary.md`.
For the active RC5 security correction and publication ordering, also read
`.agent_work/decisions/024-rc5-security-gate-and-residual-boundary.md` and
`.agent_work/tasks/active/TASK-104-rc5-security-gate-and-residual-disposition.md`.
For the final RC9-finding correction and `v0.1.3-rc.N` candidate qualification, also
read `.agent_work/decisions/025-two-host-final-candidate-qualification.md` and
`.agent_work/tasks/active/TASK-105-final-release-correction-and-qualification.md`.
For the accepted exact `v0.1.3-rc5` candidate, also read
`.agent_work/decisions/026-rc5-bounded-candidate-acceptance.md` and its linked
closeout record and operations addendum.

Current delivery direction: qualify a new release from accepted `main` for
Windows 11 Docker/Podman CPU/NVIDIA use. PR #67 and the Task-087 launcher
redesign are deferred and are not release gates. Preserve their branches,
commits, reviews, and evidence; do not merge, reconcile, extend, or resume them
during this delivery window.

Task status comes from the active board. Acceptance comes from the v2
prioritization document as amended by ADR-022, ADR-023, ADR-024, ADR-025, and
ADR-026 for the exact RC5 candidate.
ADR-025 requires four corrected-candidate profiles on this Windows NVIDIA host
and the separate independent NVIDIA host; it does not claim CPU-only or
Podman-without-Docker coverage. ADR-026 records owner-approved RC5 evidence
substitutions, installation restrictions, and known-issue dispositions; it does
not automatically qualify changed candidates or official cdcai bytes, or
authorize their publication. Static checks, health endpoints, and mocked model tests
do not establish deployment readiness; record actual package, model, device,
provider, persistence, recovery, and independent-host results.

The Windows control package is intentionally unsigned under ADR-023. Support
only environments where the user and organization permit the supplied
process-scoped wrapper path. Do not claim compatibility with endpoints that
require trusted Authenticode signatures, WDAC/AppLocker approval, or other
organization-specific allowlisting. Do not advise disabling protection or
changing persistent execution policy. Final package proof must use the exact
browser-downloaded bytes and authoritative published SHA-256 values.

Within the current session, honor the user's authorized implementation scope
without asking again for each routine step. External publication, account
changes, signing, and destructive cleanup retain their normal authorization
boundaries.
