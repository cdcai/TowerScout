# RC1 Pilot / UAT Handoff Packet

Use this packet before sending TowerScout V1 RC1 instructions to an external
tester. Fill in the exact release, artifact, fixture, and support details for
the pilot run. Do not send this packet until all required values are complete.

## Handoff Status

- Packet owner: Jonathan Schulein / TowerScout release owner
- Prepared date: 2026-05-29
- Approved for tester use: `NO`
- Approver:
- Approval date:
- Tester/cohort:
- Support contact: Jonathan Schulein (`bg90@cdc.gov`) or Chris Edens (`iek4@cdc.gov`)

## Current Readiness Notes

As of the final package validation check on 2026-05-29, leave
`Approved for tester use` set to `NO` until the release owner selects the
tester cohort and explicitly approves this packet for send.

Resolved since the PR27 readiness check:

- The `v0.1.0-rc1` prerelease exists with all four package assets uploaded and
  is now published.
- The final Application Package was regenerated from accepted source ref
  `baa5ccc053184d4a24389a436f6d7c2168238c1e`.
- The final GHCR image was published from that same source ref and pinned in the
  package by immutable digest.
- The downloaded release assets passed checksum verification.
- Docker Desktop package-path validation from the downloaded release
  assets passed through bootstrap, asset import, readiness, Settings-linked
  docs, and `/license`.
- The prerelease was published for `v0.1.0-rc1`.
- The owner-selected public Azure Maps smoke fixture was filled.
- Support contacts and provider-key handling expectations were filled.
- Internal provider setup plus bounded detection smoke passed against the final
  published digest from inside the RC container.

Remaining before tester handoff:

- Select the tester/cohort.
- Owner/reviewer approve this packet for tester send.
- Confirm each tester has Docker Desktop/WSL 2 approval or an explicitly
  assigned Podman path.

## Required Release Values

- GitHub release URL:
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc1`
- Release tag: `v0.1.0-rc1`
- Accepted source ref: `baa5ccc053184d4a24389a436f6d7c2168238c1e`
- Application Package ZIP: `towerscout-v0.1.0-rc1.zip`
- Application Package checksum file: `towerscout-v0.1.0-rc1.zip.sha256`
- Model & Data Package ZIP:
  `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip`
- Model & Data Package checksum file:
  `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip.sha256`
- Expected image reference from `IMAGE.txt`:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda121@sha256:36f452a5da0d9f3fa17f5b0f90802873cb40b1a433596048e4e9437e6f51d746`
- Expected package folder name after extraction: `towerscout-v0.1.0-rc1`

All four release files must come from the same GitHub release `Assets` section.
Do not ask testers to use the green GitHub `Code` button or GitHub's automatic
source-code ZIP/TAR.GZ downloads.

## Required Runtime Path

- Primary engine: `docker`
- Required launch mode: `-Gpu off`
- Supported command:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -AssetZip .\towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip
```

If the release ZIPs remain in Downloads, provide a fully expanded command with
the tester's actual Windows user folder:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -PackageZip C:\Users\<tester>\Downloads\TowerScout-v0.1.0-rc1\<application-package-zip> -AssetZip C:\Users\<tester>\Downloads\TowerScout-v0.1.0-rc1\<model-data-package-zip>
```

Only provide a Podman command if support explicitly assigned the Podman path and
confirmed the Podman machine plus Compose provider are running.

## Required Smoke-Test Fixture

- Fixture name: `RC1 Azure 200 West Street 150 m smoke`
- Provider to use: Azure Maps
- Public/non-sensitive location description:
  `200 West Street, New York, NY 10282`
- Search text or navigation instruction:
  search for `200 west st, New York, NY 10282`
- Shape type: circle
- Circle radius: `150 meters`
- Expected tile range: about `8` tiles
- Whether zero detections is acceptable: No; towers should be detected.
- Expected outcome: detection completes, the map and right-hand review panel
  update, and tower records display address/provider metadata when geocoding
  succeeds.

Internal final-digest smoke evidence captured on 2026-05-29:

- Runtime path: published prerelease package, Docker Desktop, `-Gpu off`,
  image digest
  `sha256:36f452a5da0d9f3fa17f5b0f90802873cb40b1a433596048e4e9437e6f51d746`.
- Estimate: `8` tiles, `48.23` seconds.
- Detection result: HTTP `200`, `55` total records, `8` tile records, `47`
  cooling-tower records, `47` records with address data, and elapsed time about
  `43` seconds.
- Host note: this smoke used internal container requests because this
  workstation had a conflicting local host process on `localhost:5000`. Do not
  treat host-browser validation on this workstation as passed from that URL.

Use a public/non-sensitive fixture. Do not ask testers to use a private
investigation AOI for the first smoke test.

## Tester Instructions To Send

Send these files or links to the tester:

- `docs/v1-rc1-quick-start.md`
- `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md`
- `.agent_work/user-testing/instructions/TESTER-ISSUE-REPORT-CHECKLIST.txt`

Include the filled release URL, filenames, bootstrap command, fixture, and
support contact from this packet in the tester message.

Provider-key expectations:

- Some testers may be provided a key, but support should not assume every
  tester already has one.
- Testers may use an owner-provided key or an approved organization-managed key.
- Testers must not send API keys, full `.env` files, or provider portal
  screenshots with account, subscription, billing, quota, or key details back
  to support.

## Support Evidence To Request If Blocked

Ask only for support-safe evidence:

- Tester name or role.
- Date/time and time zone.
- Exact failed step.
- Exact command.
- Exact error text.
- Windows version.
- Docker Desktop version and whether Docker Desktop was running.
- WSL 2 status if known.
- Release URL or release tag used.
- Package filenames used and checksum pass/fail result.
- `Get-Content .\IMAGE.txt` output.
- Bootstrap or launcher output showing engine, port, and readiness state.
- `.\scripts\status.cmd -Engine docker` output, or the selected engine.
- Provider used, fixture name, tile estimate/count, and whether detection
  reached the right-hand review panel.
- Reviewed/redacted screenshot only if it does not show API keys, private AOIs,
  raw provider responses, tile/map URLs, or sensitive local data.

Do not ask for provider keys, full `.env` files, raw logs, raw detection API
JSON, tile/map URLs, private AOI screenshots, browser network traces, cached
provider responses, exported datasets, named-volume contents, local CA bundles,
certificates, or provider portal screenshots unless the site has an approved
handling procedure. Tile/map URLs and raw API responses can contain provider
credentials.

## Final Pre-Send Check

- [x] Exact release URL/tag is filled in.
- [x] Accepted source ref is filled in and matches `SOURCE.txt` plus
      `release-manifest.v1.json`.
- [x] Exact Application Package filename is filled in.
- [x] Exact Model & Data Package filename is filled in.
- [x] Checksum filenames are filled in.
- [x] Smoke-test fixture is filled in.
- [x] Support contact is filled in.
- [ ] Tester has Docker Desktop/WSL 2 approval or an explicitly assigned Podman
      path.
- [x] Provider-key ownership/restriction expectations are confirmed.
- [ ] Tester/cohort is filled in.
- [ ] Owner/reviewer has approved this packet for tester send.
- [ ] Approval date is filled in.
