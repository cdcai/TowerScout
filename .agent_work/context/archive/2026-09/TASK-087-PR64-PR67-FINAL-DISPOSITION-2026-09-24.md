# Task-087 and PR #64/#67 Final Disposition

**Date**: September 24, 2026  
**Decision**: Close PRs #64 and #67 without merge; preserve exact history;
continue Windows delivery from accepted `main` under ADR-021.

## Why This Is Final

PR #67 is a 235-commit launcher and host-repair prototype based on a superseded
delivery direction. It is conflicted with current `main`, contains broad
planning and runtime changes, and has important gates that were never passed.
Merging or mechanically reconciling it would reintroduce a second release path
and make current acceptance harder to audit. PR #64 is an earlier Task-087
activation branch and is likewise superseded.

The decision is not a claim that the prototypes have no value. It separates
historical research from accepted product state. PR #63's bounded Gate 3 work
was already merged as `4b93cafc522f1315d382a46a37ba4f1c0ac785d6`;
the unmerged follow-on branches remain recoverable at their exact commits.

## Preserved Git Checkpoints

| Source | Exact commit | Durable archive tag |
| --- | --- | --- |
| Merged PR #63 final head | `91c1847a18714c64d3a9096f9e6cddb7cf1618e5` | `archive/task-087-pr63-final-20260924` |
| Draft PR #64 final head | `1b5156e3983bce3da2543539404ca9d9368780c0` | `archive/task-087-pr64-final-20260924` |
| Draft PR #67 final head | `93d22f2ce0551defb79c852e0e879947cc611521` | `archive/task-087-pr67-final-20260924` |
| Preimplementation checkpoint | `bfb4697edd6ab06412bdfae7fbda7c837c6ec650` | `archive/task-087-preimplementation-20260924` |

These annotated tags are pushed to `J-Schulein/TowerScout`. GitHub retains the
PR discussion and Actions history. A separately verified pre-cleanup bundle and
local document/artifact manifest provide disaster-recovery coverage outside the
working repository; they are not a second live planning source.

The external recovery set records:

- `TowerScout-pre-cleanup-20260924.bundle` with SHA-256
  `633D31F53F7C5F90042997246C6C5ABAAA3FFE1EFDBA0A5FF0B60E12B01FB106`
  and 94 refs;
- `stash-task-101-governance-transfer.patch` with SHA-256
  `6F4A3C9659FB7EAA3A5115634D2EF58D2B66D240DE791DF4323BF9452306B2B4`;
- a manifest of the separately preserved local-only documents and sanitized
  CI artifacts.

After verifying those records, the stale live stash, obsolete local branches,
defunct `migration/*` refs, and temporary pre-cleanup refs were removed. The
older intentional workstation-migration archive namespace and published release
tags were retained because they are unrelated historical recovery records.

## Review Findings Retained

The September 21 review identified nine areas that remain historical evidence,
not accepted behavior:

| Finding | Final treatment |
| --- | --- |
| F-1 exact runtime pins | Supportability concern; no current-release adoption. |
| F-2 missing Windows-native CI | Assurance gap remains unpassed. |
| F-3 launcher omitted from static gates | Quality-gate gap remains unpassed. |
| F-4 inaccurate mutation capability metadata | Merge-blocking defect remains unresolved in accepted product state because the branch is not merged. |
| F-5 runtime `Add-Type` dependency | Managed-endpoint risk remains unqualified. |
| F-6 unreachable launcher modules | Retained only in archived history. |
| F-7 dormant host-helper residue | Current release uses the bounded command path governed by Task-068. |
| F-8 deep-path/Python portability | Prototype-specific results remain historical. |
| F-9 branch size/reviewability | Resolved operationally by closing rather than reconciling the branch. |

Artifact-specific static checks and earlier Docker CPU demonstrations remain
valid only for the exact commits and packages they evaluated. They do not prove
current package readiness, signed distribution, managed-endpoint acceptance,
all-profile inference, provider readiness, or independent-host reproduction.

## Carry-Forward Boundary

- The authoritative task state and release plan live on accepted `main`.
- The current command-based setup/start/stop/TLS workflow remains the release
  path. Tasks 068, 091, 095, and 097 own its bounded qualification and fixes.
- No Task-087 branch is merged, rebased, or reused as a release prerequisite.
- A future owner may inspect an archive tag, but implementation must begin with
  a newly selected task and fresh branch from then-current `main`; useful code
  is reapplied deliberately with current tests and acceptance criteria.
- Closing the PRs and deleting their ordinary branch refs does not delete their
  tagged commits, GitHub discussion, or recorded evidence.

This record supersedes older instructions to keep PR #67 open, reconcile it,
or resume it after Task-101. Those statements remain historical context inside
the archived task record and PR discussion only.
