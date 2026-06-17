# RC1 Pilot / UAT Handoff Packet

Use this packet before sending TowerScout V1 RC1 instructions to an external
tester. Do not send it until the release URL is final, the tester/cohort is
selected, and the release owner approves the packet.

## Handoff Status

- Packet owner: Jonathan Schulein / TowerScout release owner
- Prepared date: 2026-06-17
- Approved for tester use: `NO`
- Approver:
- Approval date:
- Tester/cohort:
- Support contact: Jonathan Schulein (`bg90@cdc.gov`) or Chris Edens (`iek4@cdc.gov`)

## Current Readiness Notes

RC6 package generation, CPU runtime validation, Podman CPU validation,
CPU-package GPU guardrail validation, Docker GPU validation, Podman GPU CDI
validation, and public-safe evidence preparation have passed. Leave
`Approved for tester use` set to `NO` until the official `v0.1.0-rc6` GitHub
release is published, downloaded-release verification passes, the tester cohort
is selected, and the owner/reviewer approves this packet.

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
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc6`
  (pending official publication)
- Release tag: `v0.1.0-rc6`
- Accepted source ref: `12daa5536f580f76d063559e86b9a474451bc54b`
- Selected Application Package variant:
  `[x] CPU default  [ ] CUDA 12.1 support-assigned`
- CPU Application Package ZIP:
  `towerscout-v0.1.0-rc6-cpu.zip`
- CPU Application Package checksum file:
  `towerscout-v0.1.0-rc6-cpu.zip.sha256`
- CUDA 12.1 Application Package ZIP, if support-assigned:
  `towerscout-v0.1.0-rc6-cuda121.zip`
- CUDA 12.1 Application Package checksum file, if support-assigned:
  `towerscout-v0.1.0-rc6-cuda121.zip.sha256`
- Model & Data Package ZIP:
  `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip`
- Model & Data Package checksum file:
  `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip.sha256`
- Expected CPU image reference from `IMAGE.txt`:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cpu@sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd`
- Expected CUDA image reference from `IMAGE.txt`:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cuda121@sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0`
- Expected CPU package folder name after extraction:
  `towerscout-v0.1.0-rc6-cpu`
- Expected CUDA package folder name after extraction:
  `towerscout-v0.1.0-rc6-cuda121`
- CPU Application Package SHA-256:
  `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d`
- CUDA Application Package SHA-256:
  `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603`
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
.\setup-towerscout.cmd -PackageZip C:\Users\<tester>\Documents\TowerScoutUAT\towerscout-v0.1.0-rc6-cpu.zip -AssetZip C:\Users\<tester>\Documents\TowerScoutUAT\towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip
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

## RC6 Validation Basis

- Final CPU Docker package smoke passed.
- Final CPU Podman package smoke passed with an approved package-local
  `podman-compose` provider.
- Final CUDA Docker CPU-fallback smoke passed.
- CPU package `-Gpu on` failed closed before container startup with
  package-aware CUDA-package guidance.
- Docker GPU and Podman GPU CDI validation passed on the support GPU host with
  readiness `selected_device=cuda`.
- Google and Azure provider detection both completed on CUDA in the support GPU
  validation pass.
- Public-safe GPU validation summary:
  `.agent_work/context/analysis/TowerScout-rc6-gpu-validation-evidence-emailsafe/TowerScout-rc6-gpu-validation-evidence/PUBLIC-SUMMARY.md`.

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

- [ ] Official `v0.1.0-rc6` release URL/tag is published and verified.
- [x] Accepted source ref is filled in and matches `SOURCE.txt` plus
      `release-manifest.v1.json`.
- [x] Selected default Application Package variant is filled in.
- [x] Exact selected Application Package filename is filled in.
- [x] Exact Model & Data Package filename is filled in.
- [x] Checksum filenames are filled in.
- [ ] The four selected release assets are uploaded to the GitHub release.
- [ ] Downloaded release assets have passed Docker Desktop runtime validation.
- [x] CUDA package readiness reports `runtime.selected_device=cuda` for the
      support GPU validation basis.
- [ ] Provider setup and bounded Azure smoke passed for the official
      downloaded release path.
- [x] Smoke-test fixture is filled in.
- [x] Support contact is filled in.
- [ ] Tester has Docker Desktop/WSL 2 approval or an explicitly assigned Podman
      path.
- [x] Provider-key ownership/restriction expectations are confirmed.
- [ ] Tester/cohort is filled in.
- [ ] Owner/reviewer has approved this packet for tester send.
- [ ] Approval date is filled in.
