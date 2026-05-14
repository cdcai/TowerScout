# Data Licenses And Provenance

This file documents data-asset terms for the TowerScout YOLO-enabled release
track.

## US Census ZCTA Data

TowerScout uses US Census TIGER/Line ZCTA shapefile data for ZIP-code boundary
search. The current release asset manifest labels the data files under:

```text
data/tl_2025_us_zcta520/
```

Release packaging must include the manifest version, file sizes, and SHA-256
hashes from `webapp/asset_manifest.v1.json`. The asset bundle contract is in
`docs/release-asset-bundle-contract.md`.

## Release Requirements

Every release that publishes data assets must include:

- The exact source dataset name and year.
- The asset manifest version and hashes.
- Any required public-domain, attribution, or usage notice supplied by the data
  source.
- Revocation notes for a defective or incorrectly labeled data asset.
