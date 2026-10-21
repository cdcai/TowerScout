# Official Destination Implementation

**Date**: October 20, 2026

**Task**: TASK-089 / TASK-092; local adoption preparation

## Changes

- Updated current release, issue/support and manual URLs in 23 maintained
  documentation files to `cdcai/TowerScout`, including Markdown/HTML and wiki.
- Updated all four CPU-image defaults to `ghcr.io/cdcai/towerscout:latest-cpu`:
  `.env.example`, `compose.yaml`, `scripts/package-release.ps1`, and
  `scripts/lib/TowerScoutPodmanGpu.ps1`.
- Reworded README provenance to credit the original project and the fork's
  2026 work without describing the receiving repository as its own fork.
- Preserved explicit image and digest precedence. Historical fork fixtures
  remain to verify that an existing explicitly configured image is honored.
- Added official/fork parameterization to package staging and explicit-image/
  unconfigured-fallback checks to the Podman resolver regression.

No published release, tag, image or acceptance evidence was relabeled.
Candidate notes, RC5 addendum/handoff, manifest templates and the namespace-
deriving publication workflow remain unchanged. Official mutable defaults
are preparation values, not proof that those registry tags exist. Official
packages must use actual published, qualified digests.

## Verification

63 selected checks passed across the initial run and focused rerun:
documentation, unsigned support, workflow security ordering, manifest schema,
release package staging, mocked Podman GPU helpers and runtime hardening.
These are local/static/mocked checks, not official deployment qualification.

The first run passed 60 tests and failed three package cases because inherited
PowerShell module discovery could not locate `Get-FileHash`. Both namespaces
failed identically. The six package tests then passed with the process-local
standard Windows PowerShell module paths; no persistent setting changed.
Tests used `--noconftest -o addopts= -p no:cacheprovider`; these selected tests
do not need the shared application-runtime bootstrap.

Additional comparisons confirmed:

- All 27 selected destination files are free of active fork URLs/image defaults.
- Four runtime/default edits change only the namespace.
- Parsed Compose ports, volumes, environment and security fields are unchanged
  apart from the intended image fallback.
- Historical candidate documents, release manifest template and publishing
  workflow are unchanged.
- Strict agent-work validation and whitespace checks passed.

## Fork rehearsal handling

The maintained wiki now targets cdcai. A separately staged fork preview must
rewrite only its current release/support destinations to the fork and pin
manual links to the exact reviewed preparation commit. Keep a mapping and
source/staged hashes. Do not publish pointers to an unpublished source commit.

The existing local preview remains a previous-source snapshot. Generate the
new revision-labeled preview after this checkpoint. Its manual links become
publicly usable only after the reviewed source commit is available in the fork.
Confirm the intended public commit identity before pushing; current local
commits use an automatically inferred identity. Then verify source URLs and
obtain/confirm authorization for exact fork publication, inspect any existing
wiki content, and rehearse GitHub rendering. No cdcai mutation is part of that
fork rehearsal.

Actual official package/image availability, public destination checks, wiki
publication, source adoption, fresh security scans and real official-package
qualification remain pending. No push or publication occurred in this slice.
