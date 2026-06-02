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

As of the post-PR28 final package validation check on 2026-05-29, leave
`Approved for tester use` set to `NO` until the release owner selects the
tester cohort and explicitly approves this packet for send.

Resolved since the PR27 readiness check:

- The setup wrapper and UAT documentation were simplified for the first UAT
  cohort.
- The RC package version is moving to `v0.1.0-rc2` because `v0.1.0-rc1`
  already points to an older source ref.
- The owner-selected public Azure Maps smoke fixture was filled.
- Support contacts and provider-key handling expectations were filled.

Pending for the final `v0.1.0-rc2` handoff:

- Publish the corrected `v0.1.0-rc2-cuda121` image from the final source ref.
- Regenerate the `v0.1.0-rc2` Application Package ZIP and checksum.
- Rename or republish the unchanged Model & Data Package ZIP with the matching
  `v0.1.0-rc2` release filename.
- Validate the downloaded release assets through setup, asset import,
  readiness, Settings-linked docs, `/license`, and bounded Azure smoke.

Remaining before tester handoff:

- Select the tester/cohort.
- Owner/reviewer approve this packet for tester send.
- Confirm each tester has Docker Desktop/WSL 2 approval or an explicitly
  assigned Podman path.

## Required Release Values

- GitHub release URL:
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc2`
- Release tag: `v0.1.0-rc2`
- Accepted source ref: `PENDING final package validation`
- Application Package ZIP: `towerscout-v0.1.0-rc2.zip`
- Application Package checksum file: `towerscout-v0.1.0-rc2.zip.sha256`
- Model & Data Package ZIP:
  `towerscout-v0.1.0-rc2-assets-towerscout-v1-assets-2026-05-05.zip`
- Model & Data Package checksum file:
  `towerscout-v0.1.0-rc2-assets-towerscout-v1-assets-2026-05-05.zip.sha256`
- Expected image reference from `IMAGE.txt`:
  `PENDING final package validation`
- Expected package folder name after extraction: `towerscout-v0.1.0-rc2`

All four release files must come from the same GitHub release `Assets` section.
Do not ask testers to use the green GitHub `Code` button or GitHub's automatic
source-code ZIP/TAR.GZ downloads.

## Required Runtime Path

- Primary engine: `docker`
- Required launch mode: `-Gpu off`
- Supported default setup command:

```powershell
.\setup-towerscout.cmd
```

Tell testers to create one `C:\Users\<tester>\Documents\TowerScoutUAT`
working folder, copy the four downloaded release files from `Downloads` into
that folder, extract only the Application Package ZIP there, open PowerShell in
the extracted application folder, and run the command above. Setup finds the
Model & Data Package ZIP in the extracted folder or parent `TowerScoutUAT`
folder and verifies the `.sha256` sidecars.

If automatic ZIP discovery is ambiguous, provide a fully expanded command with
the tester's actual Windows user folder:

```powershell
.\setup-towerscout.cmd -PackageZip C:\Users\<tester>\Documents\TowerScoutUAT\<application-package-zip> -AssetZip C:\Users\<tester>\Documents\TowerScoutUAT\<model-data-package-zip>
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

Internal post-PR28 final-digest smoke evidence captured on 2026-05-29:

- Runtime path: published prerelease package, Docker Desktop, `-Gpu off`,
  image digest
  `sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158`.
- Application Package checksum:
  `e071f1ac773f993b3a8636cab4be0e476ee95086dfec6ff24beda8b8a6fb3142`.
- Package validation: refreshed app ZIP checksum matched the release sidecar;
  Model & Data Package checksum remained
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`;
  bootstrap preflight passed; the first run required an explicit image pull
  because the CUDA-capable image was not yet local; readiness reached
  `setup_required` with assets `ok`; in-container hash verification returned
  `asset_status=ok`.
- Docs/source validation: `/docs/project-overview.html`,
  `/docs/towerscout-user-guide.html`, `/docs/v1-rc1-quick-start.html`, and
  `/license` returned HTTP `200`.
- Estimate: `8` tiles, `44.0` seconds.
- Detection result: Azure search HTTP `200` with one result; detection HTTP
  `200`, `55` result records, `47` records with address data, and elapsed time
  about `59` seconds.
- Host note: validation used port `5006` to avoid possible `localhost:5000`
  conflicts on this workstation. Do not treat host-browser validation on
  `localhost:5000` as passed from this smoke.

Use a public/non-sensitive fixture. Do not ask testers to use a private
investigation AOI for the first smoke test.

## Tester Instructions To Send

Send these files or links to the tester:

- `docs/v1-rc1-quick-start.md`
- `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md`
- `.agent_work/user-testing/instructions/TESTER-ISSUE-REPORT-CHECKLIST.txt`

Include the filled release URL, filenames, setup command, fixture, and
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
- Setup or launcher output showing engine, port, and readiness state.
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
