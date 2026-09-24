# TASK-103 Dependency Security Disposition

**Date**: 2026-09-24

The Task-098 closeout retained eight torch advisories against the qualified
torch 2.6.0 baseline. Moving to torch 2.10.0 clears seven of those eight
residuals according to the Task-103 implementation brief. The remaining
advisory stays visible and is governed by ADR-022's bridge exit triggers; it is
not silently dismissed or treated as permanent acceptance.

The authenticated Dependabot-alert endpoint was not available to this session,
so alert-number-level closure must be reconciled after GitHub analyzes the
merged dependency graph. Publication evidence must record the resulting exact
alert inventory and must not claim all residuals closed until that refresh is
observed.

The exact published image is additionally subject to the blocking
CRITICAL/HIGH Trivy gate and written per-finding disposition artifact in
`container-publish.yml`.
