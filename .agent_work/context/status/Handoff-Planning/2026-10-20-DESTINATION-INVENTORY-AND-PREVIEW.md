# Destination Inventory and Refreshed Wiki Preview

**Date**: October 20, 2026

**Task**: TASK-089 / TASK-092

**Reviewed source**: `6066a9953629f9e6f9017d5c02f61bafc658d1f3`

## Completed review

Scanned all 887 tracked files, reading UTF-8 text for literal fork repository
and image references. Found 486 occurrences in 97 files:

| Review group | Occurrences | Disposition |
| --- | ---: | --- |
| Maintained user documentation | 44 | Review 23 files for coordinated official links/examples; preserve versioned history. |
| Runtime/package defaults | 4 | Change together with consumer and precedence checks, not as prose replacements. |
| Tests/agent references | 36 | Inspect fixture intent; update only expectations affected by the official change. |
| History/provenance/control records | 402 | Preserve historical identities; review current control wording individually. |

Counts describe literal-reference coverage, not a full private-artifact scan,
external-link availability check or authorization to replace every match.

## Runtime defaults identified

1. `.env.example`: default image value.
2. `compose.yaml`: fallback when no image is supplied.
3. `scripts/package-release.ps1`: explicit image, then environment, then fallback.
4. `scripts/lib/TowerScoutPodmanGpu.ps1`: explicit image, environment, package
   environment file, then fallback. Preserve digest joining and precedence.

The fourth location was missing from the initial destination list. Include it
in the coordinated official-default change. `container-publish.yml` already
derives the GHCR image namespace from the executing repository; this does not
prove package permissions or visibility. Manifest templates must remain
templates; generate official identities from actual qualified artifacts.

## Refreshed fork preview

The outgoing workspace's local `output/handoff/destination-review/` now contains:

- `review.html`: source review page with inventory counts and expandable pages.
- `reference-inventory.json`: complete file/line/reference inventory.
- `wiki-preview-6066a99/`: 14 wiki pages plus sidebar, each with a fork-preview banner.
- `wiki-preview-manifest.json`: exact source commit and original/staged SHA-256 values.

The intended rehearsal destination is `J-Schulein/TowerScout.wiki`, not cdcai.
Earlier `output/handoff/wiki-rehearsal/` copies are stale and must not be used.
The HTML review is a local source reader, not an emulation of GitHub rendering.

## Double checks

- All 15 source/staged hashes match; each transformation adds only the preview banner.
- All 48 internal wiki links/anchors resolve in the staged copy.
- All eight original-checkout preservation hashes still match.
- Strict agent-work validation and whitespace checks pass.
- No repository defaults, image identities, remote repositories or wiki content changed.

## Next execution steps

1. Prepare the coordinated official destination/default change, including all
   four fallback locations and applicable tests. Keep candidate evidence unchanged.
2. Review README provenance for the receiving repository and retain offline
   documentation access. Replace draft navigation only after the real wiki exists.
3. Before fork publication, inspect existing remote wiki content, confirm the
   exact destination and authorization, and check external manual/support links.
   The preview currently links to fork main manuals; local preparation changes
   are not yet on main, so verify content/version consistency before publication.
4. Publish only the reviewed rehearsal after authorization, then check actual
   GitHub rendering, sidebar, anonymous access and external links. This local
   preview does not establish any of those results.
5. Continue private-material inventory, receiving-owner practice/receipt,
   full adoption review and official artifact qualification.
