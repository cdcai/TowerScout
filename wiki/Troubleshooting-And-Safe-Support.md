# Troubleshooting And Safe Support

> **Audience:** TowerScout users and Local IT. **Applies to:** The next final
> Windows release. **Last reviewed:** 2026-10-02. **Publication state:** Local
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

Certificate selection and trust import are administrator/advanced tasks. The
package's repair helper first performs a dry run. Run the diagnostic by itself,
review the proposed certificate and target, and only then run a separate
`-Apply` command if Local IT approves it. Never paste both commands as one
unreviewed block. See the packaged Local IT guide for the exact release-
specific command.

Do not disable TLS verification. Ask Local IT to resolve the certificate trust
path or stop.

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
