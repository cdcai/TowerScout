# Wiki and README Alignment

**Date**: October 20, 2026

**Tasks**: TASK-092 / TASK-089; local drafts only

## Completed

- Shortened README setup instructions into a Start Here section explaining the
  wiki's purpose, linking clearly labeled repository drafts, and retaining a
  maintained Quick Start fallback. Retained release authority, hash verification,
  unsigned-policy boundaries and the Docker/Podman Python distinction.
- Updated five wiki pages: Podman Guidance, Before You Install, Choose Your
  Setup, Install And First Run, and Local IT Administrator Guide.
- Added the 80-character package-root restriction, explicit 64-bit Python 3.12
  selection, version/bitness checks, and existing-installation preservation.
- Replaced global Compose-version readiness advice with the selected provider
  reported by TowerScout status after setup, plus actual workflow confirmation.

## Validation

- All 21 existing documentation and unsigned-support tests passed with the
  fixture-free invocation documented in the previous manual-integration record.
- All 15 wiki Markdown files inspected by a local link checker: 48 internal
  page/heading references resolve. README relative links resolve.
- Podman Python-selection and installer commands match the maintained Quick Start.
- Strict agent-work validator and whitespace checks passed.
- No external URL availability, GitHub wiki rendering or publication is claimed.

## Destination review: identified follow-up

| Surface | Observed state | Remaining action |
| --- | --- | --- |
| README and wiki release/manual/support links | Current fork destinations | Prepare and review official cdcai destinations as a coordinated adoption change; verify after publication. Preserve immutable historical links. |
| README provenance | Describes the current fork | Rewrite for the receiving repository while retaining origin and fork-work credit in the official adoption version. |
| `compose.yaml` | Fork `latest-cpu` fallback | Review source-development default versus digest-pinned official package behavior; change with relevant runtime/package checks. |
| `.env.example` | Fork `latest-cpu` image | Align with the selected official source/default policy and check consumers. |
| `scripts/package-release.ps1` | Explicit image/environment inputs, then fork fallback | Verify explicit official CPU/CUDA identities and fallback behavior; do not infer a new digest. |
| `container-publish.yml` | Derives GHCR namespace from executing repository | Verify package creation/linkage/visibility and exact build identity before dispatch. |
| `release-manifest.v1.json` | Template with empty artifact identities | Preserve template semantics; generated official manifests must contain actual qualified identities. |

This is an initial destination inventory, not an exhaustive adoption-diff review.
No runtime/default changes were made in this documentation slice.

## Publication checklist

1. Regenerate the staged fork wiki preview and hash inventory from the updated
   source. Earlier local rehearsal copies predate these edits and are stale.
2. Review the exact fork preview, authorize publication, then verify rendered
   navigation and anonymous access. Keep preview labeling and video status honest.
3. Prepare the distinct official cdcai wiki and README destination changes.
4. Once the official wiki exists and is checked, replace the README's draft
   navigation with the verified cdcai wiki Home link and remove the unpublished
   notice. Retain Quick Start/offline documentation access.
5. Add the final demo only after recording and checking it against qualified
   official artifacts. No finished video is implied by the placeholder.

No remote repository, wiki, registry or release was changed. Private-material
delivery, Chris's practice/receipt, official qualification and leadership report
remain open on the delivery plan.
