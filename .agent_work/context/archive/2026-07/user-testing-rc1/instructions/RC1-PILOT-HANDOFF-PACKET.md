# RC7.1 Pilot / UAT Handoff Packet

Use this packet before sending TowerScout `v0.1.0-rc7.1` instructions to an
external tester. This packet is approved for tester use; assign the actual
tester/cohort during outreach.

## Handoff Status

- Packet owner: Jonathan Schulein / TowerScout release owner
- Prepared date: 2026-07-02
- Approved for tester use: `YES`
- Approver: Not required for RC7.1 packet approval
- Approval date: Not required for RC7.1 packet approval
- Tester/cohort: Assign during tester outreach
- Support contact: Jonathan Schulein (`bg90@cdc.gov`) or Chris Edens (`iek4@cdc.gov`)
- Support ownership transfers to cdcai at the final project handoff.

## Current Readiness Notes

RC7.1 publication and downloaded-artifact validation have passed. The release
replaces original RC7 for tester-facing validation and includes CPU/CUDA
Application Package ZIPs plus the shared Model & Data Package ZIP and checksum
sidecars. Release-owner Docker CPU validation and teammate Docker GPU
validation passed from downloaded release artifacts. The packet is approved for
tester use without requiring named tester/cohort, approver, or approval-date
fields before send. Confirm runtime prerequisites with each tester during
outreach.

Package-variant rules:

- Normal testers receive the CPU Application Package and checksum.
- Support-assigned GPU testers receive the CUDA 12.1 Application Package and
  checksum instead.
- Both variants use the same Model & Data Package ZIP and checksum from the
  same GitHub Release `Assets` section.
- Do not send both Application Package variants to a tester unless support is
  explicitly asking for comparison testing.
- The CPU Application Package is expected to reject `-Gpu on`. GPU validation
  requires the CUDA 12.1 Application Package and must not be counted as passed
  unless readiness reports `runtime.selected_device=cuda`.
- Podman remains support-assigned. If a connected Windows host has Podman but
  no approved Compose provider, instruct the tester to run
  `.\scripts\install-podman-compose-provider.cmd -Apply` before retrying setup.

## Required Release Values

- GitHub release URL:
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc7.1`
- Release tag: `v0.1.0-rc7.1`
- Accepted source ref: `1152c16fede6e852e37603a90d4ec9d9626c0e71`
- Selected Application Package variant:
  `[x] CPU default  [ ] CUDA 12.1 support-assigned`
- CPU Application Package ZIP:
  `towerscout-v0.1.0-rc7.1-cpu.zip`
- CPU Application Package checksum file:
  `towerscout-v0.1.0-rc7.1-cpu.zip.sha256`
- CUDA 12.1 Application Package ZIP, if support-assigned:
  `towerscout-v0.1.0-rc7.1-cuda121.zip`
- CUDA 12.1 Application Package checksum file, if support-assigned:
  `towerscout-v0.1.0-rc7.1-cuda121.zip.sha256`
- Model & Data Package ZIP:
  `towerscout-v0.1.0-rc7.1-assets-towerscout-v1-assets-2026-05-05.zip`
- Model & Data Package checksum file:
  `towerscout-v0.1.0-rc7.1-assets-towerscout-v1-assets-2026-05-05.zip.sha256`
- Expected CPU image reference from `IMAGE.txt`:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc7.1-cpu@sha256:14b6ef523f93a91bbcceef4163b2d100a3b8c3f0b32bfdc6b91c362694ae3d09`
- Expected CUDA image reference from `IMAGE.txt`:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc7.1-cuda121@sha256:95f1f3967294957543ed0c40e11531a5af2d56f2beb7723973596b952fc39ffd`
- Expected CPU package folder name after extraction:
  `towerscout-v0.1.0-rc7.1-cpu`
- Expected CUDA package folder name after extraction:
  `towerscout-v0.1.0-rc7.1-cuda121`
- CPU Application Package SHA-256:
  `bf104a1136722eee971302ce4bdc2ebc02ebb21031ee4d911dea908155336228`
- CUDA Application Package SHA-256:
  `507ca553aebf797218fccba61d821e262f06eb2e3801f0a73ef54230af524935`
- Model & Data Package SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`

The four files sent to a normal tester are the CPU Application Package ZIP,
the CPU checksum, the shared Model & Data Package ZIP, and the shared checksum.
All four release files must come from the same GitHub release `Assets`
section. Do not ask testers to use the green GitHub `Code` button or GitHub's
automatic source-code ZIP/TAR.GZ downloads.

## Required Runtime Path

- Primary engine: `docker`
- Required default launch mode: `-Gpu off`
- Supported default CPU setup command:

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
.\setup-towerscout.cmd -PackageZip C:\Users\<tester>\Documents\TowerScoutUAT\towerscout-v0.1.0-rc7.1-cpu.zip -AssetZip C:\Users\<tester>\Documents\TowerScoutUAT\towerscout-v0.1.0-rc7.1-assets-towerscout-v1-assets-2026-05-05.zip
```

Only provide GPU commands if support explicitly assigned the CUDA 12.1
Application Package:

```powershell
.\setup-towerscout.cmd -Engine docker -Gpu auto
.\setup-towerscout.cmd -Engine docker -Gpu on
```

Only provide Podman commands if support explicitly assigned the Podman path. If
the Podman machine is present but no approved Compose provider is available,
have the tester run:

```powershell
.\scripts\install-podman-compose-provider.cmd -Apply
```

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

Use a public/non-sensitive fixture. Do not ask testers to use a private
investigation AOI for the first smoke test.

## RC7.1 Validation Basis

- Official RC7.1 prerelease is published and replaces original RC7 for
  tester-facing validation.
- CPU Application Package and shared assets were downloaded by the release
  owner and validated through the Docker CPU package path.
- CUDA 12.1 Application Package path was validated by a teammate on a Docker GPU
  host.
- CPU and CUDA package ZIP structure checks passed; release manifest and
  `SHA256SUMS.txt` checks passed before publication.
- Package hygiene scans found no blocked runtime/support/secret/cert/cache/
  session/log/upload/temp artifacts in the CPU or CUDA Application Package ZIPs.
- CPU package remains the normal tester default; CUDA is support-assigned.
- Podman remains support-assigned. RC7.1 includes Podman TLS CA import fallback
  fixes, but use Podman only when support assigns it and prerequisites are ready.
- Prior RC6 Docker GPU and Podman GPU CDI validation remains historical support
  context; RC7.1 tester-facing validation is based on the downloaded RC7.1
  artifacts above.

## Tester Instructions To Send

Send these files or links to the tester:

- `.agent_work/user-testing/instructions/TowerScout_V1_RC1_UAT_User_Guide.docx`
- `docs/quick-start.md`
- `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md`
- `.agent_work/user-testing/instructions/TESTER-ISSUE-REPORT-CHECKLIST.txt`
  issue report form

Include the filled release URL, filenames, setup command, fixture, and support
contact from this packet in the tester message.

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
- Selected Application Package variant: CPU or CUDA 12.1.
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

- [x] Official `v0.1.0-rc7.1` release URL/tag is published and verified.
- [x] Accepted source ref is filled in and matches `SOURCE.txt` plus
      `release-manifest.v1.json`.
- [x] Selected default Application Package variant is filled in.
- [x] Exact selected Application Package filename is filled in.
- [x] Exact Model & Data Package filename is filled in.
- [x] Checksum filenames are filled in.
- [x] The four selected release assets are uploaded to the GitHub release.
- [x] Downloaded RC7.1 package paths passed release-owner CPU and teammate GPU
      validation.
- [x] CUDA package support-assigned Docker GPU process was validated by a
      teammate from downloaded RC7.1 artifacts.
- [x] Smoke-test fixture is filled in.
- [x] Support contact is filled in.
- [x] Runtime prerequisite handling is documented; confirm Docker Desktop/WSL 2
      approval or an explicitly assigned Podman path per tester during
      outreach.
- [x] Provider-key ownership/restriction expectations are confirmed.
- [x] Tester/cohort can be assigned during outreach; it is not a packet approval
      blocker.
- [x] Packet is approved for tester send.
- [x] Approval date field is not required for RC7.1 packet approval.
