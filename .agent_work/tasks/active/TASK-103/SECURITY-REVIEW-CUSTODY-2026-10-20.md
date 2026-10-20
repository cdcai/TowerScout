# October 7 second-opinion review: custody and current interpretation

The original local review `RC5-SECOND-OPINION-SECURITY-REVIEW-2026-10-07.md` is preserved outside this adoption
change set, together with its October 19 checkpoint copy.
SHA-256: `e3e2901440104cc15020e633227a81f64fab746e80cbd45478ffd9f645a794a1`.

It reviewed source `b0725e7` and explicitly disclaimed authorization and
acceptance. It also recorded missing original scan inputs and inability to
rescan the old candidate. Its verified/inferred/unverified labels belong to
that dated review, not to this reconciliation.

## Relationship to accepted work

- Dependency provenance and proposed removal of unused GDAL are addressed
  by [ADR-024](../../../decisions/024-rc5-security-gate-and-residual-boundary.md)
  and [TASK-104](../TASK-104-rc5-security-gate-and-residual-disposition.md).
- Fail-closed scan handling, severity escalation, residual-policy validation,
  and scan-before-push ordering have subsequent implementation and test
  records in TASK-104, `tests/unit/test_task103_trivy_delta.py`, and
  `tests/unit/test_container_publish_workflow.py`.
- The current publish-workflow test parses YAML and checks scan settings and
  ordering, superseding the review's statement that those checks were absent.
- The comparator still does not read `PkgPath`; this review does not mark
  that observation fixed. Current residual matching has additional identity
  constraints, but any claim that they fully address the historical collision
  concern needs focused review during official security qualification.
- The historical CUDA 12.6 baseline remains intentionally preserved under
  ADR-024; it is not evidence that CUDA 12.8 was never subsequently scanned.
  Do not regenerate the baseline to make a new candidate pass.
- This mapping is a source/record inspection, not a new test result or a
  claim that every October 7 recommendation is implemented. TASK-104's
  official security review should record the disposition of the remaining
  PkgPath/identity concern rather than silently dropping it.
- Current exact-candidate acceptance comes from ADR-026; fresh official
  security checks and the October 31 exception expiry remain binding.

## Handoff disposition

Retain the original as historical review material. Do not publish it as a
current security report or treat its embedded reproduction commands as
instructions to execute. Delivery to Chris belongs in the approved private
evidence packet after content review and destination confirmation. Custody
is local; receipt by Chris has not been established.
