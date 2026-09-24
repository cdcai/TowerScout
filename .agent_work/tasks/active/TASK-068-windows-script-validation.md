# TASK-068: Windows Test Portability And Script Validation

**Status**: IN_PROGRESS - W02 merged as `8976222`; no-blocker review and
exact-head CI complete; final W09 clean-package repetition remains
**Priority**: CRITICAL
**Type**: B (Windows Runtime Reliability)
**Owner**: Active delivery implementer; independent reviewer validates

## Objective

Keep the normal Windows package lifecycle independent of dormant helper code
while adding focused Windows PowerShell 5.1 behavioral coverage for release
paths exposed by W01-W04 and W09.

## Requirements

- WHEN host-helper review is disabled, THE SYSTEM SHALL launch and stop without
  importing the helper module, writing helper profiles, or requiring helper ACL
  operations.
- WHEN host-helper review is explicitly enabled, THE SYSTEM SHALL preserve the
  existing review-session behavior without enabling it by default.
- IF engine preflight or Compose execution fails, THEN THE SYSTEM SHALL return
  a truthful nonzero status without requiring dormant helper files.
- WHEN the packaged application is stopped and relaunched, THE SYSTEM SHALL
  preserve all eight named volumes.

## Acceptance Criteria

- [x] Missing helper module does not control helper-disabled launch or stop.
- [x] Command-free preflight fails for the engine reason, not helper import.
- [x] Fake Compose exit `7` remains exit `7` for launch and stop.
- [x] Enabled review-session cleanup remains covered by the adjacent runtime
  matrix.
- [x] Real packaged Docker CPU setup/start/stop/relaunch passes under Windows
  PowerShell 5.1 with helper review disabled.
- [x] All eight named volumes survive packaged stop and relaunch.
- [x] Independent review and required CI pass at the exact fix head.
- [ ] Final clean-source candidate package repeats the same behavior in W09.

## Dependencies

- ADR-021 accepted-main Windows delivery direction.
- Task-091 real-package artifact and runtime evidence.
- W09 final clean-source package identity for release acceptance.

## Implementation Plan

1. Reproduce only evidence-selected Windows package failures.
2. Add focused behavioral regressions before each bounded script correction.
3. Preserve enabled helper and existing command-based lifecycle contracts.
4. Repeat normal packaged setup/start/stop on the changed scripts.
5. Require independent review and exact-head CI before acceptance.

---

## Implementation Log

### 2026-09-22 - Dormant Helper Dependency

**Objective**: Remove the disabled helper module from normal launch and stop.

**Context**: A real accepted-main control ZIP completed sidecar checks and
hash-verified asset import, then endpoint antivirus blocked unconditional
parsing of `scripts/lib/TowerScoutHostHelper.ps1`. The helper review flag was
off, so normal launch had no reason to load that module.

**Decision**: Gate helper import and every helper state operation on the
existing explicit review-enable environment condition. Keep the helper code,
enabled behavior, PR history, and review-only surface intact.

**Execution**: Updated `scripts/launch.ps1` and `scripts/stop.ps1`. Added a
Windows sandbox regression with no helper module, no-engine preflight, fake
Compose exit `7`, and both launch/stop entrypoints. Committed the bounded code
  slice as `08674db` on `fix/task-068-dormant-helper-dependency`. Independent
  review found no blockers; follow-up `fa5ce83` suppresses a misleading
  deferment message when review is disabled but a stale controlled-operation
  flag is present.

**Output**: Helper-disabled package launch and stop no longer parse the blocked
module or write helper state. Explicit review mode still imports and uses it.

**Validation**:

- Pre-fix regression: failed at the missing helper import with exit `1`.
- Post-fix changed-boundary tests: `2/2` passed.
- Adjacent launcher/package/manifest tests: `9/9` passed.
- Blocking Flake8, PowerShell parser, editor diagnostics, and diff checks: pass.
- Real patched package setup/start/stop/relaunch: pass with eight volumes
  preserved.
- Independent read-only implementation review: no blockers.
- PR #75 checks at `08674db`: all required CI/CD, Windows host-helper,
  Task-087 controller, security, Docker frontend, and Trivy jobs passed.
- Exact-head PR #75 checks at `fa5ce83`: all required CI/CD, Windows
  host-helper, Task-087 controller, security, Docker frontend, and Trivy jobs
  passed.
- Full legacy helper test file: blocked by endpoint antivirus parsing the
  explicitly enabled helper module; this is retained as a review/CI gap.

**Next**: Obtain review/merge disposition for PR #75, then repeat from a clean
source package in W09.

### 2026-09-23 - W02 Merge Checkpoint

**Objective**: Close the W02 review gate without overstating final-package
acceptance.

**Execution**: PR #75 squash-merged to `main` as `8976222`. Its required checks
passed before merge.

**Validation**: PASS for the bounded helper-disabled lifecycle correction.
Final W09 clean-source package setup/start/stop/relaunch remains required.

**Next**: Reuse the merged fix in the frozen W09 candidate and repeat the
eight-volume preservation proof.

---

## Validation Results

**Status**: PARTIAL PASS - implementation, first-host package behavior,
independent review, and exact-head CI pass; final clean-source packaging remains.