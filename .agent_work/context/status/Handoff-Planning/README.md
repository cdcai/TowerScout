# Handoff Planning - Current Navigation

## Read First

1. [`2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md`](./2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md)
   - canonical forward-development, qualification, release, and handoff plan
2. [`PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`](./PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md)
   - current rules for the unchanged `v0.1.2` pilot and cdcai feedback hold
3. [`PILOT-OPERATIONS-PACKET.md`](./PILOT-OPERATIONS-PACKET.md)
   - completed July 13 pilot distribution, support, and custody record
4. [`GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md`](../../analysis/GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md)
   - 62-alert dependency inventory, applicability, and Tasks 090/098 gate
5. [`.agent_work/current-tasks.md`](../../../current-tasks.md)
6. [`HANDOFF.md`](../../../../HANDOFF.md)

## Current Decision

- Keep the six `v0.1.2` pilot assets immutable.
- Develop owner-requested fixes in the fork under `v0.1.3-rc.N`.
- Do not publish `v0.1.3` final prematurely.
- Keep `cdcai/TowerScout` unchanged until the owner-qualified final candidate
  receives explicit adoption approval.
- Qualify Docker CPU, Docker GPU, Podman CPU, and Podman GPU.
- Complete Task-090 alert classification and Task-098 mandatory remediation
  before Task-087 resumes.
- Complete operational closeout by October 30, 2026.

## Active Validation Record

The frozen Pilot Package remains active while feedback is collected. Its
sanitized validation record remains under:

- [`v0.1.2-Validation-Evidence/`](./v0.1.2-Validation-Evidence/)

This evidence proves the Pilot Package; it does not certify a future candidate.

## Archived Planning And Release History

Superseded strategies, July 22 roadmap iterations, external reviews, and
v0.1.0-v0.1.2 publication checklists moved to:

- [`context/archive/2026-07/Handoff-Planning/`](../../archive/2026-07/Handoff-Planning/)

They are historical evidence only. Their dates, commands, and adoption
recommendations do not authorize current execution.
