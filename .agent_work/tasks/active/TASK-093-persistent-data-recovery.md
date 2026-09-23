# TASK-093: Persistent Data Lifecycle And Recovery Rehearsal

**Status**: SELECTED - runtime evidence pending W07/W10
**Priority**: HIGH
**Type**: C (Reliability / Recovery)

## Objective

Prove that setup, assets, sessions, review/export inputs, and other intended
state survive normal stop/relaunch, reboot, controlled failure, and rollback.

## Requirements

- WHEN TowerScout stops or its container is replaced, THE SYSTEM SHALL preserve
  all eight named volumes unless a separately confirmed destructive action is
  explicitly requested.
- WHEN detection is cancelled or fails, THE SYSTEM SHALL support a successful
  next request without publishing partial results or deleting successful
  export inputs.
- WHEN rollback/recovery is rehearsed, THE PROJECT SHALL use an isolated target
  and verify restored state before resuming use.

## Acceptance Boundary

Final evidence belongs to the exact W09 candidate. No `down -v`, volume prune,
or broad cleanup is part of this task.
