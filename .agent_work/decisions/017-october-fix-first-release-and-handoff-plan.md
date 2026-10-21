# ADR-017: October Fix-First Release And Handoff Plan

**Status**: Accepted
**Date**: July 23, 2026
**Decision Owners**: Project lead and cdcai owner

## Decision

Keep `v0.1.2` unchanged as the active Pilot Package while developing and
qualifying a new fix-first candidate in `J-Schulein/TowerScout`.

Use `v0.1.3-rc.N` for immutable fork-side candidates. Do not publish
`v0.1.3` final automatically. Before the official release, the cdcai owner and
project lead will select the official cdcai tag and display title, then build
the official image/package consistently under that identity.

Keep `cdcai/TowerScout` unchanged until the owner-qualified final candidate is
explicitly approved for adoption.

Required final-package profiles are Docker CPU, Docker GPU, Podman CPU, and
Podman GPU. Required owner fixes include Task-087 universal provider TLS repair,
Task-096 Exit/Stop, and Task-097 Podman final-path qualification.

## Context

The cdcai owner does not want the currently used official repository
overwritten before pilot feedback and final qualification. The project is
extended through October 31, 2026, but operational closeout must finish by
October 30. Owner-requested fixes and runtime validation must proceed while the
existing pilot remains stable.

## Options Considered

1. Adopt `v0.1.2` immediately.
   - Rejected because the owner wants feedback and fixes before replacing the
     official baseline.
2. Wait for all pilot feedback before any development.
   - Rejected because it wastes the extension window and delays known required
     fixes.
3. Fix first in the fork, qualify a new candidate, then adopt.
   - Accepted because it protects current users and preserves development time.

## Rationale

The accepted path separates three identities:

- immutable Pilot Package
- iterative development candidates
- owner-approved official cdcai release

This prevents accidental pilot mutation, premature official publication, and
version mismatches while leaving enough time for owner testing and handoff.

## Impact

- Task-087 is reselected and expanded to both Google and Azure across Docker
  and Podman application-provider TLS.
- Tasks 096 and 097 are new mandatory work.
- Task-058/059 are conditional stretch work.
- Final cdcai release naming is intentionally deferred until the official
  build.
- Task-095 governance work begins immediately and continues through handoff.

## Review

Review this ADR only if the owner changes the repository hold, required runtime
matrix, hard end date, or final release authority.
