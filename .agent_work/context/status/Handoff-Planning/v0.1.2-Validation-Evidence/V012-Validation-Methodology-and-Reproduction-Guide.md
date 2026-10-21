# TowerScout v0.1.2 Validation — Methodology & Reproduction Guide

**Purpose**: background for the Developer (and any future maintainer) on the full validation process used to certify the v0.1.2 release package: what each component is, what it tests, why it exists, and how to reproduce the whole matrix or any single piece.
**Companions**: results live in `v012-validation\evidence\` (`V012-FULL-MATRIX-QA-2026-07-09.md` = verdict tables; `RUNLOG.md` = full narrative). This document explains the *process*; those record the *outcomes*.
**Lineage**: this suite is the D4 protocol from the Implementation Strategy (§D4), extended from its bounded 2-cell form to the full rc5-style 4-cell matrix, plus the v0.1.2-specific gates added by reviews R2–R6.

---

## 1 · Test philosophy

Three principles shaped every step:

1. **Test the shipped bytes, not the source tree.** Every cell starts from the release assets a user would download (control ZIP + assets ZIP, sidecar-verified), pulls the image anonymously by pinned digest, and follows the packaged documentation's own commands. Nothing is run from a repo checkout.
2. **Prove identity before trusting behavior.** Before any functional result counts, the cell must prove *what is actually running*: app version, image digest from three independent sources (readiness JSON, `status.cmd` output, engine `inspect`). This exists because the readiness value alone is spoofable via environment drift — the exact defect class the v0.1.1→v0.1.2 fixes addressed.
3. **Deterministic regression detection via frozen fixtures.** Live provider imagery changes day to day (documented count bimodality), so live detections are *recorded, never gated*. The gate is a frozen 12-tile fixture set with known-good per-tile counts — the only signal that can distinguish "model/runtime drift" from "provider weather."

## 2 · The test matrix

| Axis | Values | Why |
|---|---|---|
| Package variant | CPU (`towerscout-v0.1.2-cpu.zip`), CUDA (`…-cuda121.zip`) | Each pins a different image digest and torch flavor |
| Container engine | Docker Desktop, Podman (WSL machine) | Independent runtimes, volume stores, compose providers |
| Map provider | Google, Azure | Independent key validation, imagery, geocoding paths |

Four cells (engine × variant), run **sequentially on port 5000** (the app is port-fixed per protocol). Each cell is a fresh extraction of the downloaded ZIP into a **space-free path** (`v012-validation\cells\<engine>-<variant>\`) — the rc6 spaced-path lesson. Both providers are exercised *within* each cell. Cell-1 (docker-cpu) additionally carries the deep wizard/manual smoke set (S1–S7) and a second fixture pass; the protocol treats one deep cell + parity-checked siblings as sufficient depth.

## 3 · First-startup environment fidelity (the pre-GO cleanup)

Goal: the matrix must behave like a first install on a new machine, with the known managed-network differences as the only accepted delta. Checklist executed and evidenced before GO:

- **Both engines zeroed of TowerScout state**: containers (one rc7.1 container was still *running* and holding port 5000), all `towerscout_*` volumes under every old compose-project prefix (old config volumes contain previously saved keys!), all towerscout images, leftover project networks.
- **Registry logouts** on both engines → pulls exercise the true anonymous public-GHCR path (also re-validates package visibility).
- **Podman machine factory reset** (`podman machine rm` + `init`) → the GPU cell must re-provision CDI from nothing, proving the packaged enablement ladder rather than inheriting old machine state. (`podman machine rm` is a whole-VM deletion — expect to confirm it deliberately.)
- **Host env sweep**: no `TOWERSCOUT_*`, `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE`, `COMPOSE_PROJECT_NAME`, `PODMAN_COMPOSE_PROVIDER` at User/Machine scope. (The v0.1.2 launcher now neutralizes these for package roots — but a fresh machine wouldn't have them, so fidelity says remove; their *neutralization* is separately proven by the PR #47 Windows tests.)
- **PATH awareness, not sterilization**: Docker Desktop's `docker-compose.exe` stays on PATH — the podman preflight is *designed* to reject it, and that rejection is part of the test. An off-PATH global pip `podman-compose` is inert to the auto-detect and may stay.
- **Port 5000 free**; **fixtures re-hashed** against the recorded SHA256 prefixes; **browser flows use fresh temp profiles** every run (no cache carryover).

What deliberately stays: historical archives on disk (inert — nothing references them), and the managed network's CA/proxy posture (the accepted exception).

## 4 · The components, one by one

### 4.1 Artifact verification (per cell, before anything runs)
*What*: `.sha256` sidecar check of all three downloaded ZIPs; after extraction, every file hashed against the packaged `SHA256SUMS.txt` (70 files); `release-manifest.v1.json` fields (release_version, image, digest, flavor); grep-fingerprints proving the release's hardening fixes are in the packaged launcher (`Sync-TowerScoutPackageEnvToProcess`, `$isMatch`, `imageInspectExitCode`).
*Tests*: transfer integrity, package completeness, and that the bytes contain the code the release notes claim.

### 4.2 Packaged setup flow (per cell)
*What*: the documented single command — `.\setup-towerscout.cmd [-Engine podman] [-Gpu on] -AssetZip <downloaded assets zip>` — exactly as the packaged quick-start prescribes. Podman cells intentionally run it once *before* the compose provider exists to capture the preflight rejection contract, then `install-podman-compose-provider.cmd -Apply`, then setup again. GPU-podman prepends the documented CDI ladder: `enable-podman-gpu.ps1 -VerifyOnly` (expect a clean refusal on a fresh machine) then full provisioning (toolkit → CDI spec → verify → GPU container smoke).
*Tests*: preflight correctness, anonymous digest-pinned pull, assets-ZIP checksum + staging + hash-verified import, `.env` creation from the pinned template, engine-specific guidance messages, first-launch to `setup_required`.

### 4.3 Identity gates (per cell, before functional gates count)
*What*: three cross-checked identity sources —
1. `/api/readiness`: `state`, `version.app == v0.1.2`, `version.image_digest == the flavor's pin`, `runtime.container_engine/selected_device/pytorch_flavor`, `ml_runtime.torch_version` (+`cuda_device_name` on GPU cells);
2. `scripts\status.cmd`: must print `Running image:` / `Running image digest:` matching the pin, exit 0 (this is the PR #48 engine-inspect path — the anti-spoof gate);
3. Independent `docker|podman inspect` of the running container's image `RepoDigests`.
*Tests*: that results are attributable to the exact released image — closing the readiness-spoof hole R3 identified. GPU cells additionally gate on `selected_device=cuda` + the expected physical GPU name.

### 4.4 Wizard & API contract smokes (deep cell only: docker-cpu)
S1 wizard happy path (real browser, fresh profile: keys typed in UI → validate → provider step → save → `ready` → completion reload; repair panel must never appear; zero app JS console errors) · S2 plausible-bogus Google key (clean `invalid_provider_key` message, progression blocked, no repair panel — the F4 fix) · S3 save-keys derivation contract (F7; live-reachable states + the unit-covered derived branch noted) · S4 geocode warning schema (F5: `warning_*` keys present, null on healthy TLS) · S5 repair-panel-stays-dark on non-TLS failures · S6 settings panel re-save + default-provider flip · S7 packaged `TowerScoutCertificateStore.ps1` dot-sources in Windows PowerShell.
*Tests*: the release's user-facing contracts, especially everything PR #46 fixed and everything that must stay dark.

### 4.5 Fixture parity — the release gate
*What*: `ts-detect-harness.ps1` (byte-identical copy from the rc7.1 QA archive; fully parameterized, version-agnostic — reviewed before reuse) posts the 12 frozen tiles to `/getobjectscustom` and records per-tile detection counts. Run twice on the deep cell (run-to-run determinism), once per other cell.
*Pass condition*: per-tile equality with the rc7.1 baseline on **every** tile — `0,0,13,8,0,4,6,11,2,4,5,0` = 53. Any deviation is a hard FAIL (model/runtime drift), because the detection path (vendored YOLO, weights from the same `00599cc4…` asset bundle, torch version) is unchanged by design.
*The matrix multiplies its value*: equality across cells simultaneously proves CPU↔GPU parity, Docker↔Podman parity, and v0.1.2↔baseline parity — six-way in total.
*Fixture custody*: tiles are captured provider imagery — keep them out of the public repo; verify the 12 SHA256 prefixes after every copy; never run the harness with `-CaptureFixtures` (it overwrites the set).

### 4.6 Live provider smokes (recorded, not gated)
*What*: the harness geocodes the anchor address (google), builds a 200 m circle AOI, and runs `/getobjects` live per provider.
*Tests*: real key validity, provider HTTP/TLS paths, live imagery download, end-to-end detection latency. Counts are recorded for the evidence table but never compared as a gate — provider imagery has documented same-day bimodality (azure 69 vs 34 observed in both rc7.1 and this run). Rate-limit discipline: ≥60 s clearance around harness passes; no UI interaction during a pass; the app's shared per-IP limiter (plus the stricter `config-save` 5-per-300 s bucket) will 429 rapid automation otherwise.

### 4.7 Detection→export workflow (per cell × per provider)
*What*: a real Chrome (fresh profile) drives the running app: map centered on a detection-dense point, AOI established, "Find towers", wait for results, then the export button — capturing the actual `detections.csv` + `detections.kml` downloads.
*Pass condition*: ≥1 detection; CSV first line equals the exact contract header (`id,selected,inside_boundary,…,source`) with row count = detections; KML contains `<Placemark>`; the app's own success confirmations observed; the *active provider proven* (UI radio state + server-side `provider=` log line), zero app JS errors.
*Provider switching between runs*: the app's configured default (settings panel or the same `/api/config/save-keys` endpoint the panel calls) — the UI detects with the default.
*Two flow variants*: the fully-manual variant (drawn rectangle via the map toolbar) proven once on the deep cell; the streamlined point-mode variant (programmatic centering + explicit boundary) for the remaining runs — a documented deviation that exists because of a *real product finding* (§6.1): google mode cannot auto-create its viewport boundary.

### 4.8 Stopped-state contract (once per engine)
*What*: `stop.cmd` then `status.cmd`.
*Pass condition*: exit code 2 with "No running TowerScout container found for this package." and the readiness-unreachable warning — and **no** "pinned identity mismatch" text. This pins the PR #48 `container_not_found` special-case on both engines.

## 5 · Reproduction runbook

Prereqs: Windows 11 x64, Docker Desktop (WSL2), Podman ≥5.x, Chrome, Node ≥18 (UI automation only), pwsh 7 (harness only), an NVIDIA GPU for the CUDA cells, one Google Maps key + one Azure Maps key (localhost-permitted).

1. **Stage**: create a space-free root (e.g. `C:\ts-validation\`) with `downloads\`, `cells\`, `fixtures\`, `harness\`, `evidence\`, `secrets\`. Download the six release assets into `downloads\`; verify every sidecar. Copy `ts-detect-harness.ps1` + the 12 fixture tiles from the rc7.1 QA archive (`Validation Evidence\rc7.1-docker-qa-2026-07-07\`); verify the tile SHA256 prefixes against that QA doc. Put keys in `secrets\provider-keys.env` (`GOOGLE_MAPS_API_KEY=…`, `AZURE_MAPS_SUBSCRIPTION_KEY=…`); delete the file when done.
2. **Clean** per §3 (inventory first; delete only TowerScout-named resources; reset the podman machine deliberately).
3. **Per cell** (order: docker-cpu → docker-cuda → podman-cpu → podman-cuda):
   a. Extract the right ZIP into `cells\<cell>\`; run §4.1 checks.
   b. Podman cells: expect the provider preflight rejection; run `scripts\install-podman-compose-provider.cmd -Apply`; podman-cuda: run `scripts\enable-podman-gpu.ps1 -VerifyOnly` then without the flag.
   c. `.\setup-towerscout.cmd [-Engine podman] [-Gpu on] -AssetZip <downloads>\towerscout-v0.1.2-assets-….zip`
   d. §4.3 identity gates. Then keys: wizard UI on the deep cell (S1); `POST /api/config/save-keys` elsewhere.
   e. Harness: `pwsh -NoProfile -File harness\ts-detect-harness.ps1 -Cell <name> -OutDir evidence\out-<cell> -FixtureDir fixtures` (twice on the deep cell, ≥60 s apart). Compare `summary.json.fixtures` per-tile to the baseline.
   f. Exports per provider (§4.7), flipping the default between runs.
   g. `stop.cmd`; on the engine's first cell also capture the stopped-`status.cmd` contract; port 5000 must be free before the next cell.
4. **Close out**: verdict tables + narrative into `evidence\`; delete `secrets\provider-keys.env` and note the deletion.

**Automation drivers** (optional — everything above is also human-executable): `v012-validation\harness\` archives `wizard-smoke.js`, `export-smoke.js`, `settings-smoke.js` (puppeteer-core against system Chrome). If you reuse them, three Windows/app realities they already handle: the app's notifications are blocking `alert()`s (auto-dismiss dialogs); wizard completion and settings save trigger `window.location.reload()` (await navigation); invoke `.cmd` wrappers with a **clean Windows PowerShell `PSModulePath`** and absolute paths (pwsh-parent module-path leakage breaks `Get-FileHash` inside WinPS scripts — the documented rc7.1 QA gotcha — and `NoDefaultCurrentDirectoryInExePath` machines won't resolve bare wrapper names from the CWD).

**Time budget observed**: ~6–8 h wall for the full matrix (dominated by image pulls ≈14 GB × 2 engine stores and the 800 MB import × 4), single-digit minutes per harness pass, 2–4 min per export run.

## 6 · Findings the process surfaced (validation working as intended)

1. **google-mode no-draw detection defect** (product, pre-existing — `ui/search.js` shadowed `bounds`; server-side validation contains it; 1-line fix candidate + clearer client error).
2. **Server-side bounds validation held** under the malformed request — defense-in-depth confirmation.
3. **The provider gate in the export verdicts caught a mis-provisioned run** (a harness quoting bug dropped a default-flip; the check flagged imagery provider ≠ expected) — keep that check; it earns its place.
4. Cosmetics/UX for backlog: favicon 404; `alert()` notifications; the documented limiter's interaction with automation.

*Prepared 2026-07-09 alongside the v0.1.2 full-matrix validation. Results: `v012-validation\evidence\`. The suite extends Implementation-Strategy §D4; gates added by reviews R2–R6 (identity/anti-spoof, stopped-status, packaged-fix fingerprints) are folded in above.*
