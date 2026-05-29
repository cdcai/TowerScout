# RC1 Pilot / UAT Handoff Packet

Use this packet before sending TowerScout V1 RC1 instructions to an external
tester. Fill in the exact release, artifact, fixture, and support details for
the pilot run. Do not send this packet until all required values are complete.

## Handoff Status

- Packet owner:
- Prepared date:
- Approved for tester use: `NO`
- Approver:
- Tester/cohort:
- Support contact:

## Current Readiness Notes

As of the final handoff check on 2026-05-29, leave `Approved for tester use`
set to `NO` until the final release artifacts are published and verified.

Known pending items:

- GitHub Releases does not yet list a published V1 RC1 release.
- The existing local `dist\towerscout-v0.1.0-rc1.zip` was generated before the
  latest Task-073 documentation/handoff updates and should not be used as the
  final tester package.
- The previously validated image digest
  `sha256:55aabd73a0cbdb76a1d48f427e9fe74dcab63ed87f2a15d32d9709de3ce1a232`
  came from an earlier source ref. Because the container image serves the
  Settings Resource Links docs from `/app/docs`, the final package should use a
  newly built/published image digest from the accepted release source ref, or
  owner/reviewer acceptance should explicitly record any image-docs drift.
- A local validation Model & Data Package candidate exists at
  `dist\task074-merged-package\towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip`,
  but it is not a published GitHub Release asset.

Do not send this packet externally until these notes are resolved or explicitly
accepted by the release owner.

## Required Release Values

- GitHub release URL:
- Release tag:
- Accepted source ref:
- Application Package ZIP:
- Application Package checksum file:
- Model & Data Package ZIP:
- Model & Data Package checksum file:
- Expected image reference from `IMAGE.txt`:
- Expected package folder name after extraction:

All four release files must come from the same GitHub release `Assets` section.
Do not ask testers to use the green GitHub `Code` button or GitHub's automatic
source-code ZIP/TAR.GZ downloads.

## Required Runtime Path

- Primary engine: `docker`
- Required launch mode: `-Gpu off`
- Supported command:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -AssetZip .\<exact-model-data-package-zip>
```

If the release ZIPs remain in Downloads, provide a fully expanded command with
the tester's actual Windows user folder:

```powershell
.\bootstrap.cmd -Engine docker -Gpu off -PackageZip C:\Users\<tester>\Downloads\TowerScout-v0.1.0-rc1\<application-package-zip> -AssetZip C:\Users\<tester>\Downloads\TowerScout-v0.1.0-rc1\<model-data-package-zip>
```

Only provide a Podman command if support explicitly assigned the Podman path and
confirmed the Podman machine plus Compose provider are running.

## Required Smoke-Test Fixture

- Fixture name:
- Provider to use: Azure Maps / Google Maps
- Public/non-sensitive location description:
- Search text or navigation instruction:
- Shape type: circle / custom polygon
- Expected tile range:
- Whether zero detections is acceptable:
- Expected outcome:

Use a public/non-sensitive fixture. Do not ask testers to use a private
investigation AOI for the first smoke test.

## Tester Instructions To Send

Send these files or links to the tester:

- `docs/v1-rc1-quick-start.md`
- `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md`
- `.agent_work/user-testing/instructions/TESTER-ISSUE-REPORT-CHECKLIST.txt`

Include the filled release URL, filenames, bootstrap command, fixture, and
support contact from this packet in the tester message.

## Support Evidence To Request If Blocked

Ask only for support-safe evidence:

- Exact failed step.
- Exact command.
- Exact error text.
- `Get-Content .\IMAGE.txt` output.
- Bootstrap or launcher output showing engine, port, and readiness state.
- `.\scripts\status.cmd -Engine docker` output, or the selected engine.
- Reviewed/redacted screenshot only if it does not show API keys, private AOIs,
  raw provider responses, or sensitive local data.

Do not ask for provider keys, full `.env` files, raw logs, private AOI
screenshots, browser network traces, cached provider responses, exported
datasets, or named-volume contents unless the site has an approved handling
procedure.

## Final Pre-Send Check

- [ ] Exact release URL/tag is filled in.
- [ ] Accepted source ref is filled in and matches `SOURCE.txt` plus
      `release-manifest.v1.json`.
- [ ] Exact Application Package filename is filled in.
- [ ] Exact Model & Data Package filename is filled in.
- [ ] Checksum filenames are filled in.
- [ ] Smoke-test fixture is filled in.
- [ ] Support contact is filled in.
- [ ] Tester has Docker Desktop/WSL 2 approval or an explicitly assigned Podman
      path.
- [ ] Provider-key ownership/restriction expectations are confirmed.
- [ ] Packet owner has removed any placeholder values from tester-facing text.
