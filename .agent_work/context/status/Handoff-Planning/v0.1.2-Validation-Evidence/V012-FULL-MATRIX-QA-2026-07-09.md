# TowerScout v0.1.2 — Full Matrix Validation QA Summary

**Date**: 2026-07-08 → 2026-07-09 · **Host**: validation workstation (Windows 11, Docker 29.6.1, Podman 5.8.x fresh machine, NVIDIA T1000 8GB)
**System under test**: the six release assets of GitHub release **"Validation v0.1.2-1"** (tag `v0.1.2` → `718a564`), sidecar-verified before use.
**Verdict: PASS — all four cells, both providers, every gate.** Full narrative: `RUNLOG.md` (same folder).

## Matrix results

| Gate | docker-cpu | docker-cuda | podman-cpu | podman-cuda |
|---|---|---|---|---|
| Package SHA256SUMS (70 files) | PASS | PASS | PASS | PASS |
| Setup (packaged flow, anonymous digest pull, hash-verified import) | PASS | PASS | PASS¹ | PASS¹² |
| Readiness identity (app **v0.1.2**, pinned digest, engine/device/flavor/torch) | PASS | PASS (cuda, cu121, T1000) | PASS | PASS (cuda via CDI, T1000) |
| Anti-spoof status gate (digest lines == pin == engine inspect) | PASS | PASS | PASS | PASS |
| Fixture parity (12 tiles vs rc7.1 baseline) | **53 = 12/12 ×2 passes** | **53 = 12/12** | **53 = 12/12** | **53 = 12/12** |
| Live smoke google / azure (recorded, not gated) | 67/69 (×2) | 67/34 | 67/69 | 67/34 |
| UI detect→export google (CSV+KML) | PASS (2 rows) | PASS (2) | PASS (2) | PASS (2) |
| UI detect→export azure (CSV+KML) | PASS (46 rows, drawn AOI) | PASS (3) | PASS (3) | PASS (3) |
| Stopped-status contract (exit 2, no false mismatch) | PASS | — | — | PASS |

¹ compose-provider preflight correctly rejected Docker Desktop's docker-compose.exe; managed `install-podman-compose-provider.cmd -Apply` installed the SHA-256-pinned provider per package.
² GPU/CDI enablement from the factory-reset podman machine: all 6 rungs of `enable-podman-gpu.ps1` PASS (verify-only refusal → toolkit install → CDI generate/verify → GPU container smoke).

**Six-way per-tile parity: ALL MATCH** — rc7.1-CPU baseline == v0.1.2 docker-cpu (both passes) == docker-cuda == podman-cpu == podman-cuda. Per-tile `0,0,13,8,0,4,6,11,2,4,5,0` = 53 in every run. Azure live counts reproduced the documented bimodality (69 high / 34 low); google live was 67 in all five runs.

## Cell-1-only depth (per protocol)

Wizard S1 (UI keys→validate→save→ready, repair panel never visible, no app JS errors) PASS · S2 (bogus key → clean `403/invalid_provider_key`, blocked) PASS · S3 (F7 derivation contract; live-reachable states correct, `derived=true` branch is unit-covered) PASS-with-nuance · S4 (geocode warning schema keys present, null on healthy TLS) PASS · S5 (no repair panel/commands on non-TLS failures) PASS · S6 (settings re-save + default flip via panel) PASS · S7 (cert-store dot-source in WinPS) PASS.

## Product findings (none block v0.1.2)

1. **google-mode "Find towers" with no drawn boundary always fails** — shadowed `bounds` variable in `webapp/js/src/ui/search.js getObjects()` sends the degenerate sentinel `1,180,-1,-180`; server-side validation **correctly rejects** it (400 "lat1 must be less than lat2"); user sees a generic "Network error". Azure mode escapes via its provider's different empty-boundary fallback. Pre-existing (file unchanged since 2026-06-12; identical in rc7.1). → backlog fix: use the recomputed bounds after the auto-viewport block (1-line); improve the client error message.
2. **`/favicon.ico` 404** — cosmetic, pre-existing.
3. **`alert()`-based notifications** — export success/status messages block the UI thread until acknowledged (fine for humans; automation must dismiss; UX polish candidate).
4. **Shared per-IP rate limiter** (general bucket + `config-save` 5/300 s) — intermittently 429s rapid automated sequences; user-paced flows unaffected; documented since rc7.1.

## Environment fidelity statement

First-startup conditions verified before GO: zero TowerScout containers/images/volumes/networks on either engine (rc7.1 remnants removed, including a running container holding port 5000 and config volumes with old keys); registry logouts (anonymous pulls); factory-reset podman machine (user-executed); no TowerScout/CA env vars at any scope; fixtures re-hashed against the QA record; harness byte-identical to the rc7.1 archive. Known managed-network differences accepted per scope. Harness-side automation issues encountered during the run (PSModulePath leak, dialog handling, Google SearchBox automation) are documented in RUNLOG and were fixed in the driver scripts — none are product defects; two were rediscoveries of documented rc-era gotchas.

## Evidence map (this folder)

`RUNLOG.md` (full narrative) · `docker-*/podman-*-setup.log`, `*-status-*.log` (identity gates) · `out-*/` (harness readiness/geocode/live/fixture JSON + summaries) · `exports/<cell>-<provider>/` (CSV/KML + screenshots) · `export-verdict-*.json`, `wizard-smoke-verdict.json`, `settings-smoke-verdict-*.json`, `s3-s4-verdict.json` (scripted verdicts) · `podman-gpu-*.log`, `podman-*-provider-install.log` (enablement flows) · `wizard-*.png`, `google-mode-ui.png` (UI states). Driver scripts archived in `../harness/`.
