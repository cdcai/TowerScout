# TowerScout Current Delivery Direction

Start with these sources, in order:

1. `.agent_work/current-tasks.md`
2. `.agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-prioritization-v2.md`
3. `.agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2.md`
4. The relevant route selected by `.agents/skills/towerscout-skill-router/SKILL.md`

For the active ML runtime migration, also read
`.agent_work/decisions/022-cuda128-blackwell-ml-runtime.md` and
`.agent_work/tasks/active/TASK-103-cuda128-blackwell-ml-runtime.md`.

Current delivery direction: qualify a new release from accepted `main` for
Windows 11 Docker/Podman CPU/NVIDIA use. PR #67 and the Task-087 launcher
redesign are deferred and are not release gates. Preserve their branches,
commits, reviews, and evidence; do not merge, reconcile, extend, or resume them
during this delivery window.

Task status comes from the active board. Acceptance comes from the v2
prioritization document as amended by ADR-022. Static checks, health endpoints, and mocked model tests
do not establish deployment readiness; record actual package, model, device,
provider, persistence, recovery, and independent-host results.

Within the current session, honor the user's authorized implementation scope
without asking again for each routine step. External publication, account
changes, signing, and destructive cleanup retain their normal authorization
boundaries.
