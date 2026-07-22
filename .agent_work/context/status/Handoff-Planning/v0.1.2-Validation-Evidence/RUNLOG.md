# v0.1.2 Full Matrix Validation — Run Log

**Date started**: 2026-07-08 (late evening, continues 07-09)
**Machine**: validation workstation (NVIDIA T1000 8GB; Docker 29.6.1; Podman 5.8.3 client / 5.8.5 machine)
**System under test**: TowerScout v0.1.2 release assets from GitHub release "Validation v0.1.2-1" (prerelease transfer channel)
**Scope**: 4-cell matrix (docker-cpu, docker-cuda, podman-cpu, podman-cuda) × both providers (google, azure), fixture parity vs rc7.1 baseline (inputs/expected-outputs reuse only — nothing rc7.1 executes), live smokes, wizard S1–S7 (docker-cpu cell), detection→export per cell/provider, v0.1.2 identity gates per cell.

## Anchors (verified before start)

- Tag `v0.1.2` → `718a564` = PR #48 squash at `main` tip; all 4 workflow runs green at that SHA.
- Release "Validation v0.1.2-1": prerelease, 6 assets; all 3 downloaded ZIPs sidecar-verified OK.
- Image digests (package IMAGE.txt == GHCR, verified independently):
  - CPU: `sha256:86c54bd723ff970f70f0883397a1f2f804db796507a461a5718aeab57258afe8`
  - CUDA: `sha256:bab2eda26fa6cf0483780cfcdb0a10008fb67fe058ba99a28ebdd6212fda2214`
- Fixture tiles: 12 copied to `v012-validation\fixtures\`; every SHA256 prefix matches the rc7.1 QA doc (e3c97267 … 6ebf7c0a).
- Harness: byte-identical copy of `ts-detect-harness.ps1` in `v012-validation\harness\`; reviewed — no hardcoded versions/digests/paths; reads fixtures only (no `-CaptureFixtures` ever).
- Baseline for parity: rc7.1 `out-docker-cpu`, `out-docker-cpu-pass2`, `out-docker-gpu` (53 detections; per-tile 0,0,13,8,0,4,6,11,2,4,5,0).

## First-startup cleanup (completed pre-GO)

- Docker: removed running rc7.1 CUDA container (held port 5000), 16 towerscout volumes (2 old project prefixes, incl. config w/ stale keys), both rc7.1 images (~14.6 GB), project network; `docker logout ghcr.io` (stale login found+removed → anonymous pulls).
- Podman: removed rc7.1 container, 8 volumes, all images (incl. nvidia/cuda base), 4 stale project networks; no login present. **User then reset the podman machine entirely** (fresh `podman-machine-default`, created minutes before GO, empty).
- Host: zero TOWERSCOUT_*/CA-bundle/COMPOSE_PROJECT_NAME/PODMAN_COMPOSE_PROVIDER env vars at User/Machine scope; port 5000 free; global pip podman-compose exists but off-PATH (inert for auto-detect → cells use the packaged provider-install path); Docker Desktop docker-compose.exe on PATH (expected; preflight rejects it for podman by design).
- Left intentionally: historical archives (inert, evidence/fallback), managed-network CA/proxy (known exception).

## Package integrity — docker-cpu cell (PASS)

- All 70 files verify against SHA256SUMS.txt.
- Packaged launcher contains both hardening fixes: `Sync-TowerScoutPackageEnvToProcess` (PR #47), `$isMatch` + `imageInspectExitCode` capture-then-select (PR #48).
- `scripts/lib/TowerScoutCertificateStore.ps1` + `docs/support/host-helper.md` present.
- Manifest: `release_version=v0.1.2-cpu`, pinned image@digest correct, honest deferred SBOM posture.
- `.env.example` pins image@digest + digest + flavor=cpu.

## Key handling

Provider keys staged by user in `secrets\provider-keys.env`. Values are read by shell → POSTed to localhost app APIs only; never printed/echoed into logs or this evidence; referenced only as "Google key"/"Azure key". File will be deleted at run end (noted here when done).

## Cell log

### Cell 1: docker-cpu — IN PROGRESS
- Setup launched via packaged `setup-towerscout.cmd -AssetZip <downloads>\towerscout-v0.1.2-assets-towerscout-v1-assets-2026-05-05.zip` (user-documented single-command path; WinPS, non-interactive). Log: `evidence\docker-cpu-setup.log`.
- (first attempt failed on harness-side cwd quirk — cmd background lacked working dir; relaunched with `cd /d`; not a product issue)

### Cell 1: docker-cpu — progress
- **Setup (packaged single-command path): PASS.** Preflight all green; assets ZIP checksum verified + staged; anonymous digest-pinned pull; import with hash verification: `post_import_health=ok state=setup_required asset_status=ok`; `.env` created from template. Log: `docker-cpu-setup.log`.
- **Readiness identity gate: PASS.** `state=setup_required→ready`, `app v0.1.2`, digest `86c54bd7…` (== pin), engine docker, device cpu, flavor cpu, torch `2.2.1+cpu`, assets ok.
- **Anti-spoof status gate: PASS.** `status.cmd` printed `Running image: …v0.1.2-cpu@sha256:86c54bd7…` + `Running image digest: sha256:86c54bd7…`, exit 0; independent `docker inspect` RepoDigests identical. (First live proof of the PR #48-fixed Docker inspect path.)
- **Wizard S2 (bogus key): PASS.** Clean `403 / invalid_provider_key` message (F4 fix behavior), stayed on step 2, repair panel never visible, state stayed setup_required.
- **Wizard S1 (real keys): PASS.** Validate advanced to provider step; google default pre-checked; save → `state=ready`, `app v0.1.2`; wizard closed after the by-design reload. Zero page errors; zero application JS console errors.
  - *Exception noted:* one `favicon.ico` 404 resource-load console entry — app ships no favicon; cosmetic, pre-existing trait (not a v0.1.2 regression); backlog note.
  - *Harness-side reruns:* first wizard run aborted on the by-design step-5 reload (script fixed to await navigation); config volume was surgically reset (config+session volumes only) to re-run the wizard from clean setup_required. Not product findings.
- **S4 (geocode warning schema): PASS.** `warning_message`/`warning_category`/`warning_provider` keys present in `results[0]`, null-valued on healthy TLS; `provider_used=google_maps`.
- **S3 (F7 derivation): PASS with nuance.** Live checks confirm contract behavior for reachable states: stored default with usable key → no spurious derivation (`derived=False`), keys persist (`persisted=azure,google`). The exact `derived=True` branch requires a legacy env-seeded state (default set with no stored key) not reachable via the packaged UI/API flow; that branch is unit-covered in CI at the tag (`test_save_keys_derives_default_provider_when_omitted_and_one_provider_validates`).
- **Shared per-IP rate limiter observed live** (429 on a rapid third save-keys call) — known documented behavior since rc7.1 QA; validation protocol's spacing rules apply. Restore of default=google pending limiter drain.
- **S7 (cert-store dot-source, WinPS 5.1): PASS** — 3 TowerScout certificate functions load cleanly from the packaged lib.
- **Harness pass 1: PASS.** Live: google 67 @ 14.4s, azure 69 @ 18.1s (recorded, not gated; within documented bimodality band). **Fixtures: 12/12 exact parity with rc7.1 baseline — 0,0,13,8,0,4,6,11,2,4,5,0 = 53 total.** Evidence: `out-docker-cpu\`.
- **Harness pass 2: PASS.** Live: google 67 @ 12s, azure 69 @ 16.5s. Fixtures 12/12 = 53.
- **Fixture parity gate (three-way): PASS.** rc7.1 baseline vs v0.1.2 pass1 vs pass2 — identical per-tile on all 12 tiles; totals 53/53/53; summaries carry digest 86c54bd7… device cpu/cpu engine docker.
- **Export workflow (azure): PASS.** Full UI path in real Chrome: search → rectangle AOI drawn via the Azure Maps draw toolbar → Find towers → 46 detections (server raw 54/9 tiles, threshold-filtered to 46) → one-click export produced BOTH files: `detections.csv` (46 rows, exact contract header) and `detections.kml` (valid, Placemarks). App confirmations observed: "✅ CSV exported successfully" / "✅ KML exported successfully". UI provider verified = azure; server logs show `provider=azure` on the detection request. Evidence: `exports/docker-cpu-azure/` + `export-verdict-docker-cpu-azure.json`.
- **S6 (settings re-save + default flip): PASS.** Settings panel opened, both keys re-entered, default changed azure→google via the panel select, saved; post-save reload is by design; fresh-page verification shows UI provider = google. (Second scripted attempt hit the documented `config-save` 5/300s bucket — expected limiter behavior, not a defect.)
- **Product observations from the UI workflow (for the report):**
  1. `showNotification` uses blocking `alert()` — fine for humans, automation must dismiss dialogs; also means the CSV success alert defers the KML export until acknowledged (by design, but worth a UX backlog note).
  2. `/favicon.ico` 404 (cosmetic, pre-existing).
  3. "Find towers" without a drawn boundary runs a 1-tile detection at the map center — undocumented but user-reasonable default behavior.
  4. The shared per-IP rate limiter (60/min general + 5/300s config-save) intermittently 429s rapid automated UI sequences — matches the documented rc7.1-era finding; user-paced interaction is unaffected.
- Harness-side script iterations (dialog handling, protocol timeout, multipart provider capture, point-mode) are test-tooling fixes, not product findings; final scripts archived in `harness/`.

### FINDING (product, pre-existing): google-mode "Find towers" without a drawn boundary always fails
- **Mechanism (verified in source + live):** `webapp/js/src/ui/search.js` `getObjects()` computes `let bounds = currentMap.getBoundaryBoundsUrl()` BEFORE the auto-viewport fallback block; inside `if (boundaries === "[]")` the recomputed bounds is a **shadowed `const`**, so the outer degenerate sentinel (`"1,180,-1,-180"` — GoogleMap's empty-boundaries value) is what gets POSTed. Azure mode escapes only because `AzureMap.getBoundaryBoundsUrl()` returns valid viewport-derived values with zero boundaries.
- **Server behavior: SAFE.** Input validation rejects it cleanly ("Validation error: Invalid bounds: lat1 must be less than lat2", HTTP 400) — no resource impact. Client shows a confusing generic "Network error during Cooling Tower Detection".
- **User impact:** a google-default user who searches and clicks "Find towers" without drawing an area gets an unexplained error (azure-default users doing the same get a working 1-tile detection). Workaround: draw any boundary first.
- **Regression status:** not a v0.1.2 regression — code path predates the release line (TASK-041/045-era; file unchanged rc7.1→v0.1.2). Goes to the findings/backlog list, not the release gate.
- **Export workflow (google): PASS.** Point-mode flow (programmatic centering + explicit multi-tile boundary as the documented workaround for the google no-draw defect): 2 detections on google imagery, CSV 2 rows + valid KML, both app confirmations, ui_provider=google, server logs `provider=google`.
- **Stopped-status contract: PASS.** `stop.cmd` then `status.cmd`: exit 2, "No running TowerScout container found for this package." + accurate readiness-unreachable warning, and NO false "pinned identity" mismatch — the PR #48/R5-specified behavior verified live.

**CELL 1 (docker-cpu): COMPLETE — ALL GATES PASS** (setup, identity, S1–S7, 2× fixture parity 12/12=53, live smokes ×2, both-provider exports, stopped-status).

### Cell 2: docker-cuda — starting
- **Setup (docker, -Gpu on): PASS.** Anonymous pull of the pinned CUDA digest; asset import hash-verified; state setup_required.
- **Readiness identity gate: PASS.** app v0.1.2, digest `bab2eda2…` (== CUDA pin), engine docker, **selected_device=cuda**, flavor cuda121, torch `2.2.1+cu121`, **cuda_device_name=NVIDIA T1000 8GB**.
- **Anti-spoof status gate: PASS.** Both digest lines == pin == independent `docker inspect` RepoDigests; exit 0.
- Keys seeded via API (fresh cell limiter); state=ready. Harness pass running.
- **Harness (GPU): PASS.** Live google 67 @ 7.1s, azure 34 @ 4.9s (34 = documented low mode of azure bimodality; recorded, not gated). **Fixtures 12/12 = 53; three-way parity rc7.1-GPU == v0.1.2-CPU == v0.1.2-GPU on every tile.** GPU inference measurably faster than CPU (7.1s vs 14.4s live google).
- **Export (google): PASS.** 2 detections, CSV 2 rows, valid KML, ui_provider=google, server `provider=google`.
- Azure export first attempt inconclusive (harness-side quoting bug dropped the default-flip; detection ran on google again — caught by the verdict's provider gate). Flip re-applied properly; azure export rerunning.
- **Export (azure, rerun after proper flip): PASS.** 3 detections on azure imagery, CSV 3 rows, valid KML, ui_provider=azure. (First attempt's provider gate correctly caught a harness-side quoting bug that dropped the default flip — the verdict check did its job.)

**CELL 2 (docker-cuda): COMPLETE — ALL GATES PASS.**

### Cell 3: podman-cpu — starting
- Package extraction verified (70/70 SHA256SUMS).
- **Compose-provider preflight contract: PASS.** First `setup -Engine podman` correctly REJECTED Docker Desktop's bundled docker-compose.exe with the exact documented remediation message (install-podman-compose-provider.cmd -Apply).
- **Managed provider install: PASS** (`-Apply -Force`): provider package SHA-256 verified, package-local venv, `.env` PODMAN_COMPOSE_PROVIDER updated. Two harness-side notes: (1) first attempt hit the known pwsh→WinPS PSModulePath/Get-FileHash gotcha (rc7.1 QA finding #2 — harness env leak, not a product defect; all wrapper calls now use clean PSModulePath); (2) `-Force` needed only because the gotcha's failed attempt left a partial install dir.
- **Setup attempt 2 (with provider): PASS.** Anonymous pull into the podman machine, hash-verified asset import, setup_required reached.
- **Readiness identity gate: PASS.** app v0.1.2, digest `86c54bd7…`, **engine=podman**, device cpu, torch 2.2.1+cpu.
- **Anti-spoof status gate: PASS on podman.** Digest lines == pin; independent `podman inspect` RepoDigests contains the pinned digest (second entry = podman's index/platform digest pair, expected).
- **Harness: PASS.** Live google 67 @ 13.4s, azure 69 @ 14.1s (identical counts to docker-cpu). **Fixtures 12/12 = 53 — tile-identical to docker-cpu: cross-engine parity proven.**
- **Exports: PASS both providers.** google 2 det/2 rows; azure 3 det/3 rows; CSV+KML valid; ui_provider verified each.

**CELL 3 (podman-cpu): COMPLETE — ALL GATES PASS.**

### Cell 4: podman-cuda — starting
- **GPU/CDI enablement from factory-fresh podman machine: FULL PASS.** `enable-podman-gpu.ps1 -VerifyOnly` correctly reported unprovisioned CDI with exact remediation; full run: all 6 rungs OK (machine-inspect, machine-gpu, toolkit-install, cdi-generate, cdi-verify `nvidia.com/gpu`, transient GPU container smoke). Runtime evidence JSON written by the script itself.
- **Provider install (per-package): PASS** (SHA-256 verified, .env updated).
- **Setup (podman, -Gpu on): PASS.** Fresh pull into podman storage; hash-verified import.
- **Readiness identity gate: PASS.** app v0.1.2, digest `bab2eda2…`, **engine=podman, selected_device=cuda**, torch 2.2.1+cu121, **cuda_device_name=NVIDIA T1000 8GB via freshly provisioned CDI**.
- **Anti-spoof status gate: PASS** (digest line == pin, exit 0).
- **Harness: PASS.** Live google 67 @ 7.1s, azure 34 @ 5.6s (GPU low-mode azure again — consistent). Fixtures 12/12 = 53.
- **SIX-WAY PER-TILE PARITY: ALL MATCH** — rc7.1-CPU-baseline == docker-cpu == docker-cpu-p2 == docker-cuda == podman-cpu == podman-cuda, all 53, identical on every one of the 12 tiles. Determinism across both engines and both devices proven.
- **Exports: PASS both providers** (google 2 det, azure 3 det; CSV+KML valid; ui_provider verified).
- **Stopped-status contract: PASS on podman** (exit 2, accurate messages, no false mismatch — contract now proven on BOTH engines).

**CELL 4 (podman-cuda): COMPLETE — ALL GATES PASS.**

---

## FINAL VERDICT: PASS — all four cells, both providers, all gates

- 4/4 cells green on every gate: package integrity, setup, readiness identity, anti-spoof status, fixture parity, live smokes, both-provider detection→export workflows, stopped-status contract.
- **Six-way per-tile fixture parity ALL MATCH** (rc7.1 baseline + 5 v0.1.2 runs; 53 detections, 12/12 tiles each).
- Fresh-machine paths validated end-to-end: anonymous digest pulls, compose-provider preflight reject + managed install, GPU/CDI enablement from factory-reset podman machine, wizard-first key entry.
- Product findings (all non-blocking, documented above): google-mode no-draw detection defect (pre-existing, server-side validation contains it), favicon 404 (cosmetic), alert()-based notifications (UX note), shared rate limiter behavior (documented since rc7.1).

## Key handling closeout
`secrets\provider-keys.env` **deleted** at run end (verified). Key values were never printed to any log, evidence file, or document; they were read by local shells and POSTed only to 127.0.0.1 app APIs during per-cell setup.
