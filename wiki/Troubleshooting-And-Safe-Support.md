# Troubleshooting And Safe Support

> **Audience:** TowerScout users and Local IT. **Applies to:** The next final
> Windows release. **Last reviewed:** 2026-10-06. **Publication state:** Local
> draft.

Start with what you can see. Run commands from the extracted Application
Package folder and use the same engine and port recorded for your setup.

## Safe First Checks

```powershell
.\scripts\status.cmd -Engine docker -Port 5000
.\scripts\logs.cmd -Engine docker -Tail 200
```

For Podman, replace `docker` with `podman`. `status.cmd` may initialize missing
local configuration; it is not a read-only forensic command. Review log output
on the computer and share only a small redacted excerpt when asked.

| What you see | What it usually means | Safe next step |
| --- | --- | --- |
| Command is not recognized | PowerShell is in the wrong folder, or the engine is not installed/running. | Open the extracted folder in File Explorer, type `powershell` in the address bar, and retry. Start the chosen engine. |
| Browser cannot open `localhost` | TowerScout is stopped, starting, or using another port. | Run status with the recorded engine/port. Use the recorded browser address. |
| `setup_required` | TowerScout is running but no provider credential has been saved. | Complete Setup Wizard with one provider. |
| `degraded` | A recoverable capability such as model/data assets is missing. | Read the status detail; rerun verified asset import or setup. |
| `fatal` | TowerScout cannot safely provide normal service. | Stop. Record the sanitized status category and package/image identity. |
| ZIP hash differs | The download is incomplete, wrong, or untrusted. | Delete only that downloaded copy, download it again from the same final release, and repeat all three comparisons before extraction. |
| Provider says invalid key or unauthorized API | The key, billing, enabled service, or API restriction is wrong. | Use the provider credential page. Never post the key. |
| Certificate or TLS verification error | A managed network may be inspecting HTTPS and the container does not trust the organization's CA. | Stop ordinary troubleshooting and give the Local IT TLS section to an administrator. Do not disable certificate verification. |
| Port is already in use | Another program is using the chosen port. | Choose a different port, record it, and use it consistently on setup/start/status and in the browser URL. |
| GPU mode does not show `selected_device=cuda` | The GPU, driver, engine integration, package, or CDI path is not ready. | Stop GPU use. Correct the stated prerequisite or use the CPU package. |
| Podman target mismatch | The active machine/connection is not the one TowerScout recorded. | Start/select the intended rootless machine; do not let a helper mutate a different target. |

## Local IT Certificate Work

Use this workflow only when provider validation cannot reach Google or Azure
and the message or local logs include `CERTIFICATE_VERIFY_FAILED`. An invalid
key, missing API, billing problem, or quota error needs a different fix.

Certificate selection and trust import are Local IT or advanced-user tasks:

1. Record the provider (`google` or `azure`), engine (`docker` or `podman`),
   GPU mode (`off`, `auto`, or `on`), and port used to start TowerScout.
2. From the extracted Application Package folder, run one diagnostic command
   without `-Apply`. For example, the Docker CPU path on port 5000 is:

   ```powershell
   .\scripts\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off -Port 5000
   ```

   This example is not a command for every setup. Substitute the recorded
   provider, engine, GPU mode, and port. The diagnostic is a dry run: it does
   not import a certificate or change TowerScout.
3. Review the proposed certificate and target privately with Local IT. The
   output can contain certificate subjects and thumbprints that identify the
   organization, so do not paste it into a public issue, chat, or screenshot.
4. If Local IT approves the proposed change, run the complete command printed
   by the diagnostic. That command preserves the selected settings and ends
   with `-Apply`. Do not run `-Apply` by itself, add it to an unreviewed
   command, or paste the diagnostic and apply commands as one block.
5. Follow the restart and verification steps in the complete package
   procedure. Open `docs\package-guide.md` inside the extracted TowerScout
   Application Package and find **Provider-Key Validation Or TLS Failure**.
   That file matches the installed release. An
   [online preview](https://github.com/J-Schulein/TowerScout/blob/main/docs/package-guide.md#provider-key-validation-or-tls-failure)
   is also available, but `main` may describe a newer release.

Do not disable TLS verification. If Local IT cannot confirm an approved
certificate trust path, stop rather than weakening a computer or network
security control.

## Getting Help After Project Handoff

First use your organization's Local IT contact for Windows policy, software
installation, proxy, firewall, TLS certificate, and managed-device issues.

For a reproducible TowerScout defect that contains no sensitive data, use the
[TowerScout GitHub issue tracker](https://github.com/J-Schulein/TowerScout/issues).
The repository may transfer at handoff; use the issue link shown by the current
repository. This is a public project record, not a staffed private help desk.
Do not name an individual as permanent support.

If you have no Local IT and the safe checks do not resolve the problem, stop at
the applicable safety boundary and use the public documentation or issue
tracker. Do not weaken a computer security control to continue.

## Safe Issue Template

Include only:

- TowerScout release and Application Package filename;
- CPU or NVIDIA GPU, Docker or Podman, and port;
- Windows build, engine version, and sanitized readiness state;
- the step that failed and the exact non-secret error category; and
- a short redacted excerpt if it contains no credential, local username/path,
  private location, provider response, certificate detail, or investigation
  data.

Never post provider keys, `.env`, raw logs, raw screenshots, browser traces,
private areas of interest, cached provider responses, certificates, uploaded
files, exports, or named-volume contents.
