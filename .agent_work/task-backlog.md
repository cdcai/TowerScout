# Task Backlog - Remaining Work

**Last Updated**: May 14, 2026
**Planning State**: Sprint 05 completed work has been removed from the backlog. Sprint 06 now follows an AGPL-compliant YOLO-enabled RC/pilot path: `TASK-069` sign-off is sufficient to merge PR #11 as the internal controlled AGPL-governed RC planning and compliance baseline, `TASK-072` is completed, and package docs/validation continue against the corrected compliance payload.
**Ordering Method**: The ordered backlog below is based on current project value, dependency shape, and the shortest credible path to a v1 local release that non-technical pilot users can install and run.

---

## Cleanup Notes

- Removed completed or current-task-only backlog entries for `TASK-051`, `TASK-052`, `TASK-054`, `TASK-055`, `TASK-056`, `TASK-057`, `TASK-062`, `TASK-063`, `TASK-064`, `TASK-025`, and `TASK-065`.
- Kept `TASK-029` in the backlog because it was not started.
- Archived the not-started `TASK-029` active task artifact under `.agent_work/context/archive/2026-05/not-started-task-artifacts/`; the backlog row below is now the planning source for that task until it is selected.
- Added release-readiness tasks for asset delivery, end-user package documentation, clean-machine UAT planning, runtime preflight, GPU/CUDA scope, provider-key release policy, and public-release asset/release-manifest hardening.
- Moved mobile responsiveness, NumPy 2 migration, Sprint 04 deferred quick wins, advanced filtering, performance dashboard, and user preferences out of the ordered release backlog. They remain visible in the parking lot / technical-debt register below.

---

## Ordered Remaining Backlog

| Order | Task | Status | Type | Estimated Effort | Key Dependencies | Recommended Disposition And Rationale |
|---:|---|---|---|---|---|---|
| 1 | `TASK-072` Release Asset Bundle Contract | COMPLETED | C (Release Engineering / Asset Governance) | 1-2 days (8-16h) | `TASK-065`; current asset manifest | Completed in the active Sprint 06 lane. Defines exactly how model weights and ZIP-code data are bundled, versioned, checksummed, distributed, placed next to the release package, imported, verified, and matched to a TowerScout release. External asset ZIP publication now follows the `TASK-069` AGPL-compliant YOLO release posture and model-terms labeling. |
| 2 | `TASK-069` License And Release Policy Review | SIGN_OFF_RECORDED | C (Legal / Release Policy / Governance) | 0.5-1 day technical prep plus owner/legal review | `TASK-025`; `TASK-065`; owner/legal availability | Promoted to active Sprint 06 work for the controlled AGPL-governed YOLO-enabled RC direction. Sign-off is sufficient to merge PR #11 as the internal Sprint 06 RC baseline and does not constitute final public open-source approval. Deliver corrected YOLO AGPL attribution, release decision memo, model/data/provider terms, source-offer requirements, release control package compliance payload, image generic notices/OCI labels, and reviewer feedback material. |
| 3 | `TASK-071` End-User Release Package Documentation | NOT_STARTED | B/C (Documentation / User Enablement) | 1-2 days (8-16h) | `TASK-069`; `TASK-072`; release package shape | Add and keep second. Produce the package-based quick start and full user guide for the AGPL-compliant YOLO-enabled package, including what to download, where assets go, how to launch, how to configure provider keys, how to find source/license notices, how to validate success, and how to report problems. |
| 4 | `TASK-066` Release Candidate Validation Gate | NOT_STARTED | C (Release Engineering / Validation) | 1-2 days (8-16h) | `TASK-065`; `TASK-069`; `TASK-071`; `TASK-072`; agreed release package shape | Keep as the bridge between internal release readiness and external user testing. Prove the release ZIP, pinned image digest, checksums, release manifest, source/SBOM references, model notices, asset import, provider setup, TLS CA import, first-run restart behavior, and bounded detection from a clean user-facing path. |
| 5 | `TASK-073` Clean-Machine Pilot / UAT Execution Plan | NOT_STARTED | B/C (User Testing / Release Validation) | 0.5-1 day (4-8h) | `TASK-066`; draft user package docs | Add and keep. Define pilot tester instructions, acceptance checklist, environment capture, friction logging, issue-report workflow, success criteria, and support escalation before asking end users to test. |
| 6 | `TASK-077` Public Release Manifest And Asset Import Hardening | PARTIAL_IN_SCOPE | C (Release Engineering / Compliance) | 2-4 days full task; narrow slice in Sprint 06 | `TASK-069`; `TASK-072`; `TASK-066` validation evidence | Pull forward the narrow compliance-payload slice now: release manifest, source URL/ref, checksums, image digest, SBOM reference, model/data terms, and revocation notes. Leave staged allowlist-only asset activation as follow-up unless `TASK-066` shows it is release-critical. |
| 7 | `TASK-076` Provider API Key Exposure And Restriction Policy | NOT_STARTED | C (Security / Release Policy) | 0.5-1.5 days (4-12h) | Current setup/settings and provider-loading behavior; `TASK-069` alignment | Keep near-active. Browser map SDK keys are still exposed to the client through provider-loading routes, and AGPL does not change provider/API obligations. Decide and document whether v1 accepts this with strict provider-side key restrictions, referrer limits, quota controls, and user guidance, or whether further proxy/auth changes are required before wider distribution. |
| 8 | `TASK-074` Runtime Prerequisite Preflight | NOT_STARTED | B/C (Launcher / Supportability) | 1-2 days (8-16h) | `TASK-071`; launcher/runtime scripts | Add and keep as high leverage. Provide a user/support preflight that checks engine presence, Podman machine state, Compose provider, WSL/virtualization hints, port availability, disk space, asset presence, TLS bundle path, and provider setup state before or during launch. |
| 9 | `TASK-067` CI Release Gate Tightening | NOT_STARTED | C (CI / Release Engineering) | 1-2 days (8-16h) | `TASK-066` checklist | Keep. Once the release-candidate checklist exists, promote the highest-value digest, manifest, packaging, and launcher checks into CI or documented required/manual gates. Keep scope narrow and release-protective. |
| 10 | `TASK-068` Windows Test Portability And Script Validation | NOT_STARTED | B/C (Testing / Developer Experience) | 0.5-1 day (4-8h) | `TASK-065`; current release helper tests | Keep as a release-support follow-up. Decide whether PowerShell release-helper coverage stays Windows-only or gains explicit PowerShell Core coverage in CI. |
| 11 | `TASK-075` GPU / CUDA Support Decision | NOT_STARTED | C (Runtime Policy / Hardware Compatibility) | 0.5-1 day (4-8h) | Current CPU baseline; `TASK-051` CUDA audit | Add and keep as a decision gate, not an implementation promise. Decide whether v1 is explicitly CPU-only or whether GPU/CUDA support will be documented and validated under a specific install/runtime path. |
| 12 | `TASK-070` Restricted-Network Package Enhancements | NOT_STARTED | B/C (Release Engineering / Offline Support) | 1-3 days (8-24h) | `TASK-066`; normal connected release path validated | Keep, but after the normal connected release path is validated. This should not block v1 unless restricted-network support becomes a launch requirement. |
| 13 | `TASK-078` Permissive Apache-Only Runtime Migration | NOT_STARTED | C (ML Runtime / Release Policy) | TBD after PoC | `TASK-069`; current YOLO validation baseline | Later separate track for an Apache-compatible/permissive public release. Evaluate ONNX or another non-Ultralytics runtime, remove AGPL YOLO from the default runtime, and validate detector behavior before claiming an Apache-only package/image. This belongs with the later clean curated public release line, not the Sprint 06 RC gate. |
| 14 | `TASK-058` Background Detection Jobs And Durable Run State | NOT_STARTED | C (Architecture / Reliability) | 3-5 days (24-40h) | Release baseline stable; current progress/cancel contract understood | Keep as the highest-value post-release architecture work. Long-running detection should not stay bound to request/thread-local assumptions, but this should not preempt the release package path unless release work intentionally pauses. |
| 15 | `TASK-059` Backend Layer Decomposition And Logging Consolidation | NOT_STARTED | C (Architecture / Maintainability) | 3-5 days (24-40h) | `TASK-058` | Keep after `TASK-058`. Route/service boundaries should follow the actual job and state ownership model rather than be guessed first. |
| 16 | `TASK-027` Enhanced Error Handling | NOT_STARTED | A/B (Reliability / UX) | 1-2 days (8-16h) | Existing logging and support diagnostics | Keep. Better user-facing recovery, retry, and troubleshooting messages compound release-support value. Fold any still-relevant Sprint 04 deferred error-handler quick wins into this task. |
| 17 | `TASK-026` CPU Optimization | NOT_STARTED | C (Performance) | 2-3 days (16-24h) | Current inference baseline; release host assumptions | Keep. CPU-only performance matters for the selected local deployment baseline, but it should follow release-candidate validation so optimization starts from a stable package. |
| 18 | `TASK-029` Multi-Provider Fallback | NOT_STARTED | B (Reliability) | 2-3 days (16-24h) | Provider abstraction; improved error handling preferred | Keep, but not before release gates. Automatic fallback can improve reliability, but it must preserve provider provenance and avoid masking unsafe/no-key conditions. |
| 19 | `TASK-060` Frontend Build Modernization | NOT_STARTED | B (Frontend Infrastructure) | 1-2 days (8-16h) | Stable release branch or explicit modernization window | Keep. Manual ordered concatenation is maintenance risk, but changing the build pipeline is not necessary for the immediate release gate. |

---

## Parking Lot / Technical-Debt Register

These items should not compete with the Sprint 06 release-readiness lane. Keep them visible for later planning, but do not treat them as ordered v1 release blockers unless new evidence changes their priority.

| Item | Status | Recommended Handling | Rationale |
|---|---|---|---|
| `TASK-028` Mobile Responsiveness | PARKED | Move to later field-use backlog | The v1 supported target is Windows 11 AMD64 local desktop use. Mobile/tablet improvement is useful later but not required before first local release validation. |
| `TASK-061` Coordinated NumPy 2 Runtime Migration | TECH_DEBT | Track in dependency maintenance register | Important eventually, but the current release baseline intentionally holds a NumPy 1.x stack. Do not mix this into Sprint 06 unless a security/support issue forces it. |
| Sprint 04 Deferred Quick Wins | MERGE | Fold into `TASK-027` or close if stale | Browser refresh warning and error-handler standardization should not survive as a standalone backlog item. |
| Advanced Filtering | PARKED | Revisit after pilot feedback | Valuable only if larger-result-set review becomes a confirmed user bottleneck. |
| Performance Dashboard | PARKED / RESHAPE | Reconsider as lightweight support diagnostics if needed | Current release needs actionable status/log/preflight output more than an in-app dashboard. |
| User Preferences | PARKED | Revisit after repeated-user workflow evidence | Setup and Settings already cover part of this value. Add preference surface only when pilot feedback shows real need. |

---

## Sprint 06 Selection Guidance

Do not automatically select this whole list for Sprint 06. A conservative Sprint 06 should close `TASK-065`, then execute a small release-readiness slice in dependency order:

1. `TASK-069` to settle the AGPL-compliant YOLO release posture and compliance payload.
2. `TASK-071` to write package-based end-user docs against that posture and the completed asset contract.
3. `TASK-066` to validate the package/docs/assets/source-notice path from a clean user-facing environment.
4. `TASK-073` to prepare external pilot / UAT execution after the internal release-candidate gate.
5. `TASK-076` to resolve provider-key exposure boundaries before broadening distribution.

`TASK-077` has a narrow compliance-payload slice in Sprint 06. `TASK-074`, `TASK-067`, and `TASK-068` are high-value follow-through if capacity remains or if `TASK-066` exposes friction that should be automated before external testing.

If the release path pauses, `TASK-058` is the best next architecture investment. It should precede `TASK-059`.

---

## Historical Performance Snapshot

| Sprint | Duration | Outcome | Notes |
|---|---:|---|---|
| Sprint 01 | February 4-18, 2026 | Complete | Foundation, memory, and UX work |
| Sprint 02 | February-March 2026 | Complete | Architecture work |
| Sprint 03 | March 11-18, 2026 | Complete | Legacy feature restoration and Google Maps API migration |
| Sprint 04 | March 19-April 6, 2026 | Complete | Setup/settings, performance investigation, cleanup, detection stabilization |
| Sprint 05 | April 7-May 8, 2026 | Closeout | Runtime determinism, local YOLO ownership, smoke baseline, release hardening, OCI packaging, launcher MVP |

---

## Related Documentation

- [Current Tasks](./current-tasks.md)
- [Completed Tasks](./completed-tasks.md)
- [Sprint 05 Retrospective Analysis](./context/analysis/SPRINT-05-RETROSPECTIVE-ANALYSIS-2026-05-08.md)
- [Sprint 06 Plan](./context/status/SPRINT-06-PLAN.md)
