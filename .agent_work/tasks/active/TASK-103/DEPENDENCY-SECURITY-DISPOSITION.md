# TASK-103 Dependency Security Disposition

**Date**: 2026-09-24

The Task-098 closeout retained eight torch advisories against the qualified
torch 2.6.0 baseline. Moving to torch 2.10.0 clears seven of those eight
residuals according to the Task-103 implementation brief. The remaining
advisory stays visible and is governed by ADR-022's bridge exit triggers; it is
not silently dismissed or treated as permanent acceptance.

GitHub code scanning reported one medium-security alert on PR #86: alert #215,
`CVE-2025-3000`, affecting `torch==2.10.0`. Trivy rates this item LOW. The
vulnerable operation is `torch.jit.script`; TowerScout does not call that API,
and the shipped `newest.pt` model follows the standard PyTorch loader rather
than the vendored optional TorchScript branch. The alert is therefore
dispositioned as bridge risk rather than a false positive: torch 2.13.0 fixes
it, but the qualified CUDA 12.8 bridge is deliberately pinned to 2.10.0 under
ADR-022. Re-open and re-evaluate immediately if TowerScout begins scripting or
accepting TorchScript models, changes the shipped model format, or evaluates a
qualified torch version containing the fix. This is a technical reachability
and release-risk disposition, not a legal determination.

The exact published image is additionally subject to the committed accepted
Trivy baseline. `container-publish.yml` blocks every new CRITICAL/HIGH
`(VulnerabilityID, PkgName)` key and emits both machine-readable and written
delta dispositions; unchanged accepted-baseline findings remain auditable.

The committed stage-A baseline is
`.github/security/task103-trivy-baseline.v1.json` (SHA-256
`f18a4f2037573bb6f3280778fb694a8c1beb5e8c1313c47f10ac9cf507d31928`).
It records 396 unique keys from matching accepted CPU/CUDA scans made with
Trivy 0.69.3 and database timestamp `2026-09-24T19:02:16.063941580Z`, including
the source image IDs and raw-report hashes. The pilot narrative's earlier 392
count used an earlier vulnerability-database state; the normalized key set is
the enforceable baseline. A local dry run against both Task-103 candidate
images found 396 keys, zero new, and zero resolved. Only the workflow scans of
the exact published digests establish the H9 result.
