# Data Licenses And Provenance

This file documents data-asset terms for the TowerScout YOLO-enabled release
track.

## US Census ZCTA Data

TowerScout repackages U.S. Census Bureau 2025 TIGER/Line(R) ZCTA shapefile data
and is not an original Census Bureau product. The data supports ZIP-code boundary
search. The current release asset manifest labels the data files under:

```text
data/tl_2025_us_zcta520/
```

Release packaging must include the manifest version, file sizes, and SHA-256
hashes from `webapp/asset_manifest.v1.json`. The asset bundle contract is in
`docs/release/release-asset-bundle-contract.md`.

Source: U.S. Census Bureau, *2025 TIGER/Line Shapefiles*, national 2020 ZIP
Code Tabulation Areas (ZCTAs), `tl_2025_us_zcta520`.
The [2025 technical documentation, sections 1.1-1.2](https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2025/TGRSHP2025_TechDoc.pdf)
states that these U.S. Government materials are not subject to U.S. copyright
under 17 U.S.C. 105 and may be reproduced. Census requests source attribution.
The application code license does not impose a new license on these data.

Census provides no warranty of positional or attribute accuracy. Boundaries
serve statistical purposes and are not legal land descriptions or determinations
of jurisdiction, ownership or entitlement. TIGER/Line is a registered Census
Bureau trademark; its use here identifies the source data, not endorsement.
Keep the supplied metadata with redistributed data. Original downloads are
available from the [Census TIGER/Line site](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html).

## Release Requirements

Every release that publishes data assets must include:

- The exact source dataset name and year.
- The asset manifest version and hashes.
- Any required public-domain, attribution, or usage notice supplied by the data
  source.
- Revocation notes for a defective or incorrectly labeled data asset.
