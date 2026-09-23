# TASK-092: Documentation Currentness And Information Architecture

**Status**: SELECTED - W00 active entrypoints; W09 user documentation pending
**Priority**: HIGH
**Type**: C (Documentation / Release)

## Objective

Make agent, user, package, and in-app guidance agree with the exact main-based
release path and its observed support limits.

## Requirements

- WHEN current delivery direction changes, THE PROJECT SHALL update active
  entrypoints without rewriting historical records.
- WHEN a candidate is frozen, THE PROJECT SHALL align Markdown, manually
  maintained HTML, package allowlists, and in-app Help with the tested bytes.
- IF a profile or workflow is untested, THEN documentation SHALL NOT claim it
  is supported.

## Acceptance Boundary

W00 covers active agent/task direction. W09 completes public/end-user manuals
against actual artifacts. `v0.1.2` compatibility documents remain immutable or
clearly historical.
