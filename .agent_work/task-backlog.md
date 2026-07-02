# Task Backlog - Remaining Work

**Last Updated**: July 2, 2026
**Planning State**: Sprint 06 is closed through the validated `v0.1.0-rc7.1` tester-facing package set. `TASK-087` is selected as active Sprint 07 work and is tracked in `current-tasks.md`, not in the backlog.
**Ordering Method**: Remaining work is ordered by release/pilot risk first, then post-release architecture and maintenance value.

---

## Cleanup Notes

- Removed completed Sprint 06 release-readiness entries from the ordered backlog: `TASK-065`, `TASK-066`, `TASK-067`, `TASK-069`, `TASK-071`, `TASK-072`, `TASK-073`, `TASK-074`, `TASK-075`, `TASK-079`, `TASK-080`, `TASK-081`, `TASK-082`, `TASK-083`, `TASK-084`, `TASK-085`, and `TASK-086`.
- Selected `TASK-087` as active Sprint 07 work.
- Kept follow-on release support, policy, restricted-network, architecture, and performance tasks visible for future selection.
- Kept parked field-use and technical-debt items separate from ordered release/pilot work.

---

## Ordered Remaining Backlog

| Order | Task | Status | Type | Estimated Effort | Key Dependencies | Recommended Disposition And Rationale |
|---:|---|---|---|---|---|---|
| 1 | `TASK-076` Provider API Key Exposure And Restriction Policy | NOT_STARTED | C (Security / Release Policy) | 0.5-1.5 days (4-12h) | Current setup/settings and provider-loading behavior; release-owner policy input | Pull forward before broader distribution if provider-key ownership, restriction, quota, and support expectations remain informal. Browser map SDK keys are client-visible by design, so the release needs clear provider-side restrictions and user/support guidance. |
| 2 | `TASK-068` Windows Test Portability And Script Validation | NOT_STARTED | B/C (Testing / Developer Experience) | 0.5-1 day (4-8h) | Current Windows launcher/import/TLS helper scripts; `TASK-087` helper proof findings | Pull forward if Sprint 07 exposes helper or PowerShell behavior that should be covered by repeatable Windows-first validation rather than manual evidence only. |
| 3 | `TASK-077` Public Release Manifest And Asset Import Hardening | PARTIAL_FOLLOW_UP | C (Release Engineering / Compliance) | 1-3 days depending on scope | Current package manifest/checksum flow; asset import helper; release evidence | Keep as a follow-up for staged/allowlist-only asset activation or additional manifest hardening if pilot feedback shows import risk. The narrow compliance payload was substantially addressed during Sprint 06 package work. |
| 4 | `TASK-070` Restricted-Network Package Enhancements | NOT_STARTED | B/C (Release Engineering / Offline Support) | 1-3 days (8-24h) | Normal connected package path validated; pilot restricted-network requirements | Pull forward only if restricted-network or offline preload support becomes a launch requirement. RC7.1 remains a connected package path with support-managed exceptions. |
| 5 | `TASK-078` Permissive Apache-Only Runtime Migration | NOT_STARTED | C (ML Runtime / Release Policy) | TBD after PoC | `TASK-069`; current YOLO validation baseline | Later public-release track. Evaluate ONNX or another non-Ultralytics runtime, remove AGPL YOLO from the default package/image, and validate detector behavior before claiming an Apache-compatible package. |
| 6 | `TASK-058` Background Detection Jobs And Durable Run State | NOT_STARTED | C (Architecture / Reliability) | 3-5 days (24-40h) | Release baseline stable; current progress/cancel contract understood | Highest-value post-release architecture work once pilot blockers are handled. Long-running detection should eventually move away from request/thread-local assumptions. |
| 7 | `TASK-059` Backend Layer Decomposition And Logging Consolidation | NOT_STARTED | C (Architecture / Maintainability) | 3-5 days (24-40h) | `TASK-058` preferred first | Keep after durable job/state ownership is clear. Route/service boundaries should follow the actual job and state model rather than be guessed first. |
| 8 | `TASK-027` Enhanced Error Handling | NOT_STARTED | A/B (Reliability / UX) | 1-2 days (8-16h) | Existing logging, setup, provider, and support diagnostics | Keep as a release-support improvement. Fold still-relevant Sprint 04 deferred error-handler quick wins into this task. |
| 9 | `TASK-026` CPU Optimization | NOT_STARTED | C (Performance) | 2-3 days (16-24h) | Stable package/runtime baseline; representative CPU benchmarks | Keep after pilot feedback unless CPU performance becomes a confirmed tester blocker. Optimization should start from the validated package path, not source-only assumptions. |
| 10 | `TASK-029` Multi-Provider Fallback | NOT_STARTED | B (Reliability) | 2-3 days (16-24h) | Provider abstraction; improved error classification preferred | Keep, but do not pull before policy/error-handling clarity. Automatic fallback must preserve provider provenance and avoid masking unsafe/no-key or quota conditions. |
| 11 | `TASK-060` Frontend Build Modernization | NOT_STARTED | B (Frontend Infrastructure) | 1-2 days (8-16h) | Stable release branch or explicit modernization window | Keep as maintenance. Manual ordered concatenation is a risk, but changing the build pipeline is not necessary for the immediate pilot path. |

---

## Active Elsewhere

| Task | Active Location | Notes |
|---|---|---|
| `TASK-087` Host-Side TLS Repair Control Plane | `.agent_work/current-tasks.md`; `.agent_work/tasks/active/TASK-087-host-side-tls-repair-control-plane.md` | Selected as Sprint 07 active work. Starts with helper transport and security proof before product UI integration. |

---

## Parking Lot / Technical-Debt Register

These items should not compete with Sprint 07 unless tester feedback changes their priority.

| Item | Status | Recommended Handling | Rationale |
|---|---|---|---|
| `TASK-028` Mobile Responsiveness | PARKED | Move to later field-use backlog | The v1 supported target remains Windows 11 AMD64 local desktop use. |
| `TASK-061` Coordinated NumPy 2 Runtime Migration | TECH_DEBT | Track in dependency maintenance | Important eventually, but the current release baseline intentionally holds a NumPy 1.x stack. |
| Sprint 04 Deferred Quick Wins | MERGE | Fold into `TASK-027` or close if stale | Browser refresh warning and error-handler standardization should not survive as standalone backlog items. |
| Advanced Filtering | PARKED | Revisit after pilot feedback | Valuable only if larger-result-set review becomes a confirmed user bottleneck. |
| Performance Dashboard | PARKED / RESHAPE | Reconsider as lightweight support diagnostics if needed | Current release support needs actionable status/log/preflight output more than an in-app dashboard. |
| User Preferences | PARKED | Revisit after repeated-user workflow evidence | Setup and Settings already cover part of this value. Add preference surfaces only when pilot feedback shows real need. |

---

## Historical Performance Snapshot

| Sprint | Duration | Outcome | Notes |
|---|---:|---|---|
| Sprint 01 | February 4-18, 2026 | Complete | Foundation, memory, and UX work |
| Sprint 02 | February-March 2026 | Complete | Architecture work |
| Sprint 03 | March 11-18, 2026 | Complete | Legacy feature restoration and Google Maps API migration |
| Sprint 04 | March 19-April 6, 2026 | Complete | Setup/settings, performance investigation, cleanup, detection stabilization |
| Sprint 05 | April 7-May 8, 2026 | Complete | Runtime determinism, local YOLO ownership, smoke baseline, release hardening, OCI packaging, launcher MVP |
| Sprint 06 | May 11-July 2, 2026 | Complete | V1 RC package path validated through RC7.1; `TASK-087` selected for Sprint 07 |

---

## Related Documentation

- [Current Tasks](./current-tasks.md)
- [Completed Tasks](./completed-tasks.md)
- [Sprint 06 Retrospective Analysis](./context/analysis/SPRINT-06-RETROSPECTIVE-ANALYSIS-2026-07-02.md)
