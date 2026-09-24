# TowerScout PyTorch CUDA 12.8 (Blackwell) Migration — Implementation Brief (Plan v3)

**Date:** 2026-09-24. **Owner:** release owner (all approvals below are recorded 2026-09-24).
**Audience:** the developer agent on the Blackwell laptop (`HOST-BLACKWELL`).
**Supersedes** Plan v1, Plan v2 (`TowerScout-PyTorch-cu128-Blackwell-Migration-Plan-v2-2026-09-23.md`) and the email-kit README **for implementation purposes**. Those documents are history; if you have them, do not follow their steps where this brief differs. This brief folds in every correction from the pilot (report §8) and every owner decision.
**Companion attachments** (same email): pilot patch series, expected-tree hash, RGB fixture tiles, fixture manifest, T1000 reference run, wheel evidence, pilot report. See §5.

---

## 1. Mission

Replace TowerScout's ML runtime `torch==2.6.0 / torchvision==0.21.0` (CUDA 12.6, flavor `cuda126`) with **`torch==2.10.0` / `torchvision==0.25.0` (CUDA 12.8, flavor `cuda128`)** so the app runs on Blackwell GPUs (sm_120), while preserving Turing (sm_75) and CPU behavior exactly. The CPU image moves to the same pair as one coordinated change.

**You are not designing this migration — it is already implemented and proven.** A full pilot ran on `HOST-T1000` on 2026-09-23: 39 qualification runs, 21 comparator verdicts, all archived under `<TASK103_T1000_EVIDENCE_ROOT>\` (index: `INDEX.md`; narrative: `PILOT-LOG.md`). The pilot branch (9 commits) arrives with this brief as a plain-text patch series. Your work is:

1. **Phase 0** — reconstruct the pilot branch and environment on this laptop (§6).
2. **Phase 1** — verify the migration on this laptop's Blackwell GPU ("Track L", §7). **Checkpoint: report to the owner.**
3. **Phase 2** — turn the pilot branch into the merged, released migration ("Track H", §8), with owner checkpoints where marked.

**Baseline:** `main` @ `715d153`. **The pilot branch tree hash is `debdf25d55cae2bded0649a32aa4e1f02fbd3f60`** — Phase 0 proves your reconstruction matches it byte-for-byte.

---

## 2. What the pilot proved (facts you can rely on)

| Result | Detail |
|---|---|
| **CPU outputs bit-identical** | torch 2.10.0 CPU vs accepted `main` (2.6.0): all 54 frozen-fixture detections and all 13 EfficientNet scores, delta 0. |
| **GPU outputs within noise** | T1000 CUDA vs CPU reference: box 1.2e-07, conf 2.4e-06, secondary 4.8e-07 — same level as today's cu126 image. |
| **Speed unchanged** | Interleaved same-window runs, N=3/side: CPU 0.96–1.03×, GPU 0.98–1.03×. |
| **Security clean** | Trivy 0.69.3 image scans: 0 new CRITICAL/HIGH in C vs A, both flavors (392 pre-existing bookworm/packaging findings on both sides). |
| **Sizes** | CUDA image 11.06 → **14.39 GB** (+3.33 GB); CPU 3.92 → 3.97 GB. |
| **Memory** | CUDA-mode host RSS +15% (owner-accepted, D-P1) but GPU reserved −375 MB → **total footprint −117 MB**, min free VRAM 5.51 GB. CPU-mode memory fell 10–14%. |
| **Packaging works** | Real package built, imported the v0.1.2 asset bundle, launched `-Gpu on`, readiness `selected_device=cuda pytorch_flavor=cuda128`. CPU package refuses `-Gpu on` (N1). |
| **Tests** | 548 unit tests pass on torch 2.10.0 CPU; 55/55 Windows PowerShell tests pass. Only failures: 8 pre-existing host-helper tests that need admin (identical on `main`). |
| **Arch coverage** | Wheel fatbins cover sm_70–sm_120: T1000 (sm_75) and Blackwell (sm_120) both native. Maxwell/Pascal are not covered — accepted (D3). |

**Wheel facts** (full filenames + SHA-256 in `P4-wheel-evidence.txt`): torch 2.10.0+cu128 pins cuDNN 9.10.2.21, cuBLAS 12.8.4.1, NCCL 2.27.5, nvshmem 3.4.5, triton 3.6.0, and a **new dependency `cuda-bindings==12.9.4`**. Build hosts (via the PR #76 `PIP_CERT` BuildKit secret): `download.pytorch.org`, `download-r2.pytorch.org`, `pypi.nvidia.com`, `files.pythonhosted.org`, `pypi.org`. Never use `--trusted-host`; never upgrade setuptools in the torch pip step.

**Two pre-existing defects found and fixed on the pilot branch** (they matter beyond the migration):

- **F-A2 (NMS):** the vendored YOLOv5 NMS time limit (0.5 + 0.05×batch s) counted the *asynchronous* GPU forward pass, silently dropping the rest of a batch's detections on any slow/busy GPU. On the T1000, accepted `main` has only ~5% headroom today. Fixed in commit `9a6473a` (CUDA synchronize before NMS; semantics unchanged; regression test). Owner-approved (D-P2).
- **F-A1 (fixtures):** the historical 12 test tiles are palette-mode PNGs — EfficientNet crashed on all of them and fail-open hid it, so past "fixture parity" evidence never exercised EfficientNet. The pilot derived a **lossless RGB set** (same tiles, `convert("RGB")`) which is now the combined-flow fixture (gates v2, owner-approved D-P3). The palette originals survive only as a YOLO-only continuity check.

---

## 3. Owner decisions — all resolved (2026-09-24)

No open decisions remain. Do not re-open these; if reality contradicts one, stop and report (§4).

| # | Decision | Resolution |
|---|---|---|
| D-P1 | CUDA-mode host RAM +15% broke gate G8 | **Accepted.** Rationale: +108 MB from the CPU-first loader fix, +150 MB from CUDA 12.8 libraries; total host+GPU footprint fell 117 MB; free VRAM rose. **G8 is amended before any Phase 2 measurement** to judge GPU profiles on total (host + device) footprint, interleaved N≥3 (§8 step H-1, Appendix A). |
| D-P2 | Vendored NMS synchronize fix (`9a6473a`) | **Approved.** Ships with the migration. |
| D-P3 | RGB-derived tiles as the combined fixture, incl. TASK-091 W05 / PR #83 | **Approved.** |
| D-P4 | EfficientNet forces RGB (`det_img.convert("RGB")`) | **Approved.** New work item in Phase 2 (§8, item W-B2). |
| D-P5 | Track L transfer method | **Email kit** (this package). The laptop rebuilds the image from patch-identical source; the 8.2 GB same-image-ID transfer set is not used. The tiles travel in this package by one-time owner exception — see the licensing note in §5. |
| D-P6 | T1000 disk cleanup | Owner-side action on the workstation; **not your concern**. |
| D-P7 | New Podman machine | **Deferred** until the Podman cells (H6). |
| D-P8 | Proceed to the real migration | **Yes, conditional on Phase 1 (Track L) passing on this laptop** and the owner acknowledging the verdict (Checkpoint 1). |
| D3 | Pascal-era GPUs in the fleet? | **No** (to the owner's knowledge). `cuda128` replaces `cuda126`; Maxwell/Pascal become CPU-only. Docs state this (H4). |
| D10 | W06 (EfficientNet fail-open fix, PR #78) | **Release dependency, not a merge dependency.** The migration branch may merge before PR #78, but nothing ships to users until PR #78 is merged. |
| D11 | cu128 bridge review | **Handover item.** torch 2.10/cu128 is a time-limited bridge (PyTorch never backports security fixes; cu128 wheels end at torch 2.11). Technical review date **2027-01-31** or the first torch ≥2.14.1 evaluation, whichever is first. The project ends **2026-10-31**, so ADR-022 records that this obligation transfers to whoever maintains TowerScout afterward, with the exit triggers (§8, H0). |
| D1/D2/D9/D12 (plan v2) | – | Resolved by events: pilot ran first (D1); 2.10.0/0.25.0 passed, no downgrade ladder needed (D2); fixtures authorized (D9); the TASK-091 contract was reused via cherry-pick of PR #83 @ `889ffba` as commit `c796792` (D12). |

---

## 4. Boundaries, invariants, stop rules

**Authorization boundaries:**

- **No push to `origin`, no PR, and no image/release publication during Phases 0–1.** Pushing the feature branch and opening the TASK-103 PR is authorized **only after Checkpoint 1** (Track L pass + owner acknowledgment).
- **Publication is owner-only, always:** dispatching `container-publish.yml`, pushing to GHCR, and releasing packages happen at Checkpoint 2 (§8, H9) with the owner's explicit go.
- Do not run destructive Docker cleanup (`system prune`, `compose down -v`, volume deletion) against anything you did not create in this work.
- Compose project names `docker-cpu`, `docker-cuda`, `podman-cpu`, `podman-cuda` are reserved by existing installations — never reuse them.

**Invariants (any change to these is a stop, not a judgment call):** model weights and trusted hashes; thresholds (conf 0.25, IoU 0.45, `max_det`); the EfficientNet window 0.25–0.65; NMS semantics (the sync fix changes *timing measurement*, not selection); tiling/geometry/exports; IEEE FP32 precision policy; the eight named volumes; loopback binding; TLS verification; key redaction; the 100-tile cap and 50 MiB body limit; `numpy==1.26.4`, `ultralytics==8.3.249`, `efficientnet_pytorch==0.7.1`, Python 3.11 base image; exact `==` pins everywhere; the PR #76 CA-secret build path.

**Evidence rules:** declare gates before measuring (commit the gates file first; never widen a gate after seeing results). Missing evidence is a fail, never a pass. A CPU fallback never passes a GPU cell. Historical artifacts are immutable — never relabel them. Keep every run, including failed ones, in an evidence index.

**Stop rules — stop, record, and report to the owner; never work around:**
- A Phase 1 gate fails (do not tune anything to make it pass).
- Combined outputs differ from the reference beyond G7 tolerances.
- A new CRITICAL/HIGH image finding has no written disposition.
- A build would need TLS verification disabled.
- Any invariant above would have to change.
- Anything would require modifying existing (non-task103) containers or volumes.

---

## 5. Package contents and verification

| File | What it is |
|---|---|
| `TASK103-IMPLEMENTATION-BRIEF-v3-2026-09-24.md` | This document. |
| `task103-pilot-patches.txt` | The 9 pilot commits as a `git format-patch` series (plain text). |
| `EXPECTED-TREE.txt` | The source-tree hash the patches must reproduce. |
| `fixtures-rgb.zip` | The 12 RGB-derived test tiles + a copy of the fixture manifest. |
| `fixture-manifest.json` | Expected per-detection outputs for the 12 tiles (54 detections, 13 EfficientNet candidates), PR #83 contract format. |
| `task103-reference-run.zip` | The stage-A (accepted `main`, torch 2.6.0) CPU reference run from the T1000 — JSON and logs only. The comparator judges your runs against it. |
| `P4-wheel-evidence.txt` | Exact wheel filenames, SHA-256 hashes and dependency pins for the 2.10.0/0.25.0 pair. |
| `TowerScout-PyTorch-cu128-Pilot-Report-2026-09-23.md` | The pilot report — background and full results. Read it once for context. |

**Licensing note on the tiles:** they are captured Google satellite imagery, released to you by the owner for this qualification only. **Never commit them to the repository, never redistribute them, never regenerate them** (a different Pillow/zlib build produces different PNG bytes and the gates check exact SHA-256 hashes).

**Note:** the raw reference run contains a host-local name and user-profile
paths inside some JSON files; the committed documentation represents them as
`HOST-T1000` and host-relative placeholders. The raw values remain only in the
externally retained evidence because changing them would invalidate custody
hashes.

---

## 6. Phase 0 — Environment setup and branch reconstruction

Use **Windows PowerShell 5.1** (`powershell.exe`) for all repository scripts — not pwsh 7 (§11, G-4). Python for the comparator is the approved 3.12 (`py -3.12`).

**Prerequisites to verify and record first:**
- Docker Desktop running; `docker info` succeeds; `docker run --rm --gpus all python:3.11-slim-bookworm nvidia-smi -L` lists the RTX PRO 500.
- `nvidia-smi` — record driver (596.71 at last inventory) and GPU name.
- **Disk: at least 60 GB free.** The CUDA image is 14.4 GB, its build transient is larger, and the optional cu126 control image adds 11 GB + cache. (The pilot's full three-stage set consumed ~120 GB on the workstation; you build at most two stages.)
- Your private CA bundle for the managed (TLS-inspecting) network, stored **outside** the repo. Builds pass it via `-BuildCaBundlePath`; the PR #76 flow feeds it to pip as a BuildKit secret.
- The v0.1.2 asset ZIP (already on this laptop): `towerscout-v0.1.2-assets-towerscout-v1-assets-2026-05-05.zip`, SHA-256 `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.

**Reconstruction** (paths without spaces — spaced paths have bitten this project before, §11 G-6):

```powershell
$T = "<TASK103_WORK_ROOT>"; $Repo = "<TOWERSCOUT_REPO_ROOT>"
New-Item -ItemType Directory -Force "$T\kit" | Out-Null
# Put all package attachments in $T\kit\ ; expand the tiles:
Expand-Archive "$T\kit\fixtures-rgb.zip" "$T\fixture-manifest-A-cpu"

# 1. Accepted main (715d153) in a clean detached worktree.
git -C $Repo fetch origin
git -C $Repo worktree add --detach "$T\repo" 715d153

# 2. Fresh checkouts show 5 TowerScoutSite files as modified (line endings only, known issue). Hide locally:
git -C "$T\repo" ls-files -m | ForEach-Object { git -C "$T\repo" update-index --skip-worktree $_ }

# 3. Apply the pilot and PROVE the source is identical:
git -C "$T\repo" am --keep-cr "$T\kit\task103-pilot-patches.txt"
git -C "$T\repo" rev-parse "HEAD^{tree}"        # MUST equal the hash in EXPECTED-TREE.txt:
                                                #   debdf25d55cae2bded0649a32aa4e1f02fbd3f60
git -C "$T\repo" status --porcelain --untracked-files=no    # MUST print nothing

# 4. Models from the asset ZIP:
Expand-Archive "<path>\towerscout-v0.1.2-assets-towerscout-v1-assets-2026-05-05.zip" "$T\assets"
Copy-Item "$T\assets\model_params" "$T\repo\webapp\" -Recurse -Force

# 5. Verify the tiles against the declared gates (exact SHA-256):
py -3.12 -c "import json,hashlib,pathlib,sys; g=json.load(open(r'$T\repo\scripts\task103_gates.v2.json',encoding='utf-8-sig')); bad=[t['name'] for t in g['fixture']['tiles'] if hashlib.sha256(pathlib.Path(r'$T\fixture-manifest-A-cpu',t['name']).read_bytes()).hexdigest()!=t['sha256']]; sys.exit(f'HASH MISMATCH: {bad}' if bad else print('all 12 tiles verified'))"
```

If the tree hash does not match, or `git am` conflicts, **stop and report** — do not hand-fix patches.

---

## 7. Phase 1 — Track L: Blackwell verification

This is the migration's first-ever run on sm_120 hardware. It rebuilds the qualified image from patch-identical source and judges it with the pre-declared gates (`scripts/task103_gates.v2.json`, in the reconstructed repo) against the T1000 reference run.

**Rebuild caveat (accepted):** your image will have a different image ID than the T1000's — same source (proved by the tree hash), same pinned torch wheels, but unpinned transitive packages and the base-image state may differ slightly. `identity.json` in your evidence records exactly what was built, so any difference is visible.

```powershell
# 1. Build the CUDA 12.8 image and run all six qualification phases (~15–20 min + build time):
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$T\repo\scripts\task098-qualify-ml.ps1" `
  -Profile cuda -CudaWheelTag cu128 -TorchVersion 2.10.0 -TorchvisionVersion 0.25.0 `
  -BuildCaBundlePath "<private CA bundle path>" `
  -EvidenceRoot "$T\evidence" -Stage C `
  -FixtureManifest "$T\fixture-manifest-A-cpu\fixture-manifest.json" -RunLabel blackwell-built

# 2. Verdict against the T1000 stage-A CPU reference:
Expand-Archive "$T\kit\task103-reference-run.zip" "$T\reference"
$ref = (Get-ChildItem "$T\reference" -Directory | Select-Object -First 1).FullName
$run = (Get-ChildItem "$T\evidence\runs" -Directory | Sort-Object Name | Select-Object -Last 1).FullName
py -3.12 "$T\repo\scripts\task103_compare.py" --gates "$T\repo\scripts\task103_gates.v2.json" `
  --reference-outputs $ref --candidate $run --out "$T\evidence\verdicts\blackwell-built"
Get-Content "$T\evidence\verdicts\blackwell-built\verdict.md"
```

**Expected:** G1–G7, G11 and G12 **pass**; G8 passes its **absolute** check (≥1 GiB device memory stays free during the workload — there is no same-host torch 2.6.0 GPU baseline, so relative G8/G9 are `not_applicable`; your numbers become the Blackwell baseline). Record `get_device_capability()` from the identity output — it should confirm **sm_120** for this exact SKU (previously unverified). Run with normal display/browser use; power and thermal state are recorded, not gated.

**3. Negative control N2 (required):** the *old* runtime must fail closed on Blackwell.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$T\repo\scripts\task098-qualify-ml.ps1" `
  -Profile cuda -CudaWheelTag cu126 -TorchVersion 2.6.0 -TorchvisionVersion 0.21.0 `
  -BuildCaBundlePath "<private CA bundle path>" -EvidenceRoot "$T\evidence" -Stage CTRL `
  -FixtureManifest "$T\fixture-manifest-A-cpu\fixture-manifest.json" -RunLabel n2-built
```

**Expected:** phases fail, each **still writes its JSON** (the always-emit contract), `identity.json` shows `cuda.arch_supported=false`, errors mention `sm_120` / "no kernel image", nonzero exit.

**4. Negative control N3 (recommended):** on the CTRL image, `TOWERSCOUT_DEVICE=auto` must fall back to CPU and still produce the reference counts (proves the loader fix means Blackwell users get a *working slow* app, not a broken one, on the old package). `scripts/task103_auto_fallback_check.py` on the pilot branch drives this; also run an explicit `-Profile cpu` pass of the C image.

**5. Also explicitly run the CPU profile of the cu128 image** (`-Profile cpu`, Stage C) and verdict it — CPU behavior on this laptop should be bit-identical to the reference just as it was on the T1000.

### ⛔ Checkpoint 1 — report to the owner

Send the owner: the `verdict.md` files, `identity.json` highlights (device capability, arch list, driver), min-free-VRAM from the memory phase, and the N2/N3 outcomes. Keep the whole evidence folder, pass or fail. **Proceed to Phase 2 only after the owner acknowledges a passing verdict.** If any gate fails: stop rules (§4) apply.

---

## 8. Phase 2 — Track H: the real migration

### H-pre — Sync and rebase

1. `git fetch origin`; check the state of PRs **#77–#84** (snapshot as of 2026-09-23, all open — re-check, states will have changed):

   | PR | Content | Interaction with this work |
   |---|---|---|
   | #77 | Rewrites `scripts/lib/TowerScoutCompose.ps1` | **Known conflict** with the pilot's P5 commit, which touches 3 spots in that file: the cu128 index URL constant (was line 4), the "Use the CUDA 12.8 package" message (was line 290), and the `"cuda128"` flavor constant (was line 614). Resolve by re-applying those three *changes by content* to the rewritten file. |
   | #78 | W06: EfficientNet fail-open fix | **Release dependency (D10).** Do not duplicate its change; the migration merges independently of it, but H9 requires it merged. |
   | #83 (draft) | TASK-091 W05 combined contract (branch @ `889ffba`) | Already on the pilot branch as cherry-pick `c796792`. If #83 has merged: drop `c796792` during rebase and reconcile any drift (H1). If it evolved, reconcile to **one** contract. |
   | #84 | Governance checkpoint | May touch `.agent_work` files you will also touch in H0 — rebase order matters; take theirs, then re-apply H0 content. |

2. Create the working branch from your reconstructed pilot branch: `git switch -c feature/task-103-cuda128-ml-runtime`, then **rebase onto current `origin/main`**. Keep the commit structure (it documents what changed and why).
3. After rebase, re-run the full test suite (Appendix C). Expect: ~548 unit tests pass, 55/55 Windows-only pass; the 8 host-helper failures appear only in non-admin sessions and are pre-existing.
4. Re-verify the stale-CUDA-reference scan passes (it is a test on the branch; N4).

### H-1 — Amend the gates FIRST (owner decision D-P1, lesson L8)

**Before any Phase 2 measurement**, commit `scripts/task103_gates.v3.json` (exact content: Appendix A) **and** extend `scripts/task103_compare.py` to implement it, with unit tests (extend the comparator's existing test suite):

- **G8 for GPU profiles:** judged on **total footprint** — peak host RSS (`VmHWM`) **plus** `max_memory_reserved` — ≤ 1.10 × the same-host reference total; the ≥1 GiB absolute min-free-VRAM check stays. CPU profiles keep the host-only relative gate.
- **Method (G8 and G9):** relative gates are valid **only** for interleaved, same-window runs, ≥3 per side. Single cross-window runs drift up to ~9% (CPU timing) / ~16% (CUDA host RSS) with no code change.

The commit timestamp is the predeclaration record — same discipline as the pilot.

### H0 — Governance (`.agent_work` edits are authorized in this phase)

- **ADR-022** `.agent_work/decisions/022-cuda128-blackwell-ml-runtime.md` (ADR-020 format). Must record: the adopted pair and flavor rename; Maxwell/Pascal → CPU-only (D3); the D-P1 G8 amendment and rationale; the NMS fix (D-P2) and RGB fixture (D-P3) inclusions; W06 as a release dependency (D10); and the **bridge exit plan**: review 2027-01-31 or first torch ≥2.14.1 evaluation; exit triggers = (1) HIGH/CRITICAL advisory on the shipped pair not evidenced unreachable, (2) review date passes, (3) a dependency requires newer torch, (4) fleet drops pre-Turing needs making cu130 viable, (5) cu128 loses security support. **The project closes 2026-10-31: state that this obligation transfers with maintenance ownership at handover.**
- **TASK-103** `.agent_work/tasks/active/TASK-103-cuda128-blackwell-ml-runtime.md` (TASK-098 skeleton) + `TASK-103/` folder holding this brief, the gates files, and the evidence indexes (yours and a pointer to the T1000 set).
- Board: `current-tasks.md` (a `### **TASK-103:` heading — the validator requires that exact form), `task-backlog.md`; dated TASK-091 and TASK-095 log entries; "Amended by ADR-022" pointers in the canonical v2 prioritization/hardening docs; `AGENTS.md` pointer.
- Run `validate_agent_work.py` (record the exit code) and `check_agent_work_quick.py`.
- **Push the branch and open the TASK-103 PR** (authorized by Checkpoint 1). PR description links the ADR and the Track L verdict.

### H-work — Remaining implementation items

The pilot branch already contains all P1/P2/P5 work. What remains:

| Item | Content |
|---|---|
| **W-B2** (D-P4, approved) | `EN_Classifier.classify`: convert each crop/tile with `.convert("RGB")` before tensor transforms. Add a regression test feeding a palette-mode PNG (build the test image in code — do not commit imagery). Coordinate with PR #78's W06 area. |
| **H1 contract unification** | One combined-flow acceptance contract: reconcile the pilot tooling (`task091_combined_contract.py`, cherry-picked `c796792`) with PR #83 as merged. Repair-or-retire the historical HTTP harness (`v012-validation\harness\`): true offline mode (no live geocoding), full hashes, enforced comparisons, nonzero exit — or formally retire it in favor of the combined runner. |
| **H2 messages** | Failure-class recovery messages in `webapp/ts_runtime.py` (snippet: Appendix B.1). Five classes: newer-GPU-than-build, older-GPU-than-build, CPU-only build, driver/container, precision-policy. Hints only when a fallback actually selected CPU. Optional: vendored `torch.amp.autocast("cuda", …)` modernization. |
| **H3 build hardening** | `Set-TowerScoutGpuEnvironment` `-Build` handling (snippet: Appendix B.2): export pinned versions from requirements.txt when unset; override stale cu-URLs with a warning; fail closed on unflavored custom mirrors. Windows tests N5–N7 (stale shell URL, custom mirror without flavor, old package `.env` copied forward → fail closed). Mind the constraint from `test_task_087_host_helper.py`: no new dot-source-time file reads. |
| **H4 docs** | Full documentation pass (file list: §10). Publish **only qualified combinations** (GPU/driver/Windows/WSL/engine/toolkit as actually tested); "current NVIDIA or OEM production driver that lists your exact GPU"; supported = Volta-or-newer expectation with only tested GPUs qualified, Maxwell/Pascal unsupported by the CUDA package (D3); measured sizes (14.4 GB CUDA image) + peak build/pull disk footprint; keep "12.8 Application Package" on one line (`test_flask_routes.py` asserts it); arch-mismatch troubleshooting; CDI-spec refresh guidance after driver updates; never install a Linux display driver in WSL; keep md/html doc pairs in sync. |
| **H5 CI/security** | `ci.yml`: install torch/torchvision from the CPU index first + pip cache. Add Trivy image scan + SBOM of the exact published digests to `container-publish.yml` (or a release step) with written finding dispositions. Record the Dependabot residual closures (2.10.0 clears 7 of the 8 TASK-098 residuals). |
| **H6 Podman** | Podman CPU + NVIDIA CDI cells per TASK-097. Requires a new Podman machine (D-P7 unlocks here). NVIDIA Container Toolkit in the machine ≥1.19.1 (1.20.x recommended); record `nvidia-ctk --version`. A blocked cell is recorded `blocked`, never `pass`. |
| **H7 rollback rehearsal** | Three mechanisms: (1) source revert of the TASK-103 commits; (2) artifact rollback to the previous package/image — extract into a folder with the **same leaf name** or set `COMPOSE_PROJECT_NAME`, so the eight volumes are reused; verify data survives both directions; (3) `-Gpu off` CPU escape hatch (not a rollback — it keeps the migrated runtime). On Blackwell the old cu126 package is only a CPU recovery option. Retain the artifacts rollback needs. |
| **H8 compliance** | Route the NVIDIA runtime libraries shipped in the CUDA image through `towerscout-release-compliance-review` **before publication**. Inventory the components; make no legal determination. |

**Final qualification before release:** re-run the gate suite on the **rebased** release images (CPU + CUDA cells on this laptop; the owner can add T1000 cells), using gates v3, interleaved N≥3 where a same-host baseline exists. Never overlap scans/builds with measurement runs.

### ⛔ Checkpoint 2 — H9 publication and closeout (owner executes/authorizes)

Owner dispatches `container-publish.yml` for `cpu` and `cuda128` (`push_latest=false`), records digests; verify pulled images (G1/G2); package from the digests; run the TASK-091 W09/W10 flow; confirm **PR #78 (W06) is merged — release dependency D10**; close out `HANDOFF.md`, `requirements.md` (SEC-001, RUNTIME-001), `design.md`, completed tasks; record the bridge exit plan with the 2026-10-31 handover note.

---

## 9. Corrections to plan v2 already folded into this brief

If you consult plan v2 (history), know that this brief corrects it as follows — the pilot proved each point:

1. **Gates:** the operative file is `task103_gates.v2.json` (v1 is history). **G7 is not the 53-count vector**: the RGB fixture reference is the captured stage-A CPU outputs — per-tile counts `0,0,12,8,0,4,6,9,4,6,5,0` (54 total), 13 EfficientNet candidates in 6 batches, scores 0.57–0.95. The historical vector `0,0,13,8,0,4,6,11,2,4,5,0` (53) applies only to palette originals run YOLO-only (`-NoSecondary` / comparator `--check-historical-vector`).
2. **Harness interface** (as built, not as v2 specced): `-Image`, `-Profile`, `-Stage`, `-CudaWheelTag`, `-TorchVersion/-TorchvisionVersion`, `-FixtureDirectory`/`-FixtureManifest`, `-EvidenceRoot` (absolute, outside the repo), `-RunLabel`, `-NoSecondary`, `-Phases` (string[]), `-BuildCaBundlePath`. There is no `-MemoryWorkload` switch — memory is a phase. **`-Phases` cannot be passed multi-valued through `powershell -File`**; run all phases or use `-Command`.
3. **Comparator interface:** `--gates --reference-outputs --candidate [--baseline] [--cpu-counterpart] [--scan-reference --scan-candidate --scan-dispositions] [--check-historical-vector] --out`.
4. `package-release.ps1 -OutputDir` must be **repo-relative** (absolute paths fail).
5. `test_ts_en_classifier.py` is **not** LEAVE (v2 A.6 was wrong): it stubs `_cuda_kernel_probe` — already fixed on the branch.
6. Never pipe `docker save` through PowerShell 5.1 (binary corruption); use `-o` or Git Bash. `gzip -1` compresses the CUDA image 14.4 → 4.8 GB.
7. Repo-wide text sweeps: use `git ls-files`-based scans; plain `rg` misses `.github/` and `.agents/` without `--hidden`.
8. TASK-091's contract branch is `889ffba` (not `be50246`), already cherry-picked as `c796792`.
9. Line numbers in v2's inventories were verified against `715d153` and have shifted; **always re-locate symbols by content**, never by line number.

---

## 10. Impacted areas of the codebase (nothing-overlooked inventory)

**Already changed by the pilot branch** (55 files, 7,844 insertions — this is the ground-truth diff `715d153..debdf25`):

| Area | Files |
|---|---|
| ML runtime | `webapp/ts_device.py` (FP32 enforcement + read-back, decisive kernel probe, arch diagnostics, new DeviceSelection fields), `webapp/ts_yolov5_local.py` (CPU-first load/fuse), `webapp/towerscout.py` (startup log fields), `webapp/vendor/yolov5_local/models/common.py` + `README.md` (NMS synchronize fix) |
| Versions/build | `webapp/requirements.txt`, `Dockerfile`, `compose.build.yaml`, `.env.example` (pins → 2.10.0/0.25.0, flavor `cuda128`) |
| CI/publish | `.github/workflows/container-publish.yml` (cuda128 matrix, cu128 URL, generic tag guard, pins) |
| Launcher/packaging | `scripts/lib/TowerScoutCompose.ps1` (3 spots — the #77 conflict), `scripts/package-release.ps1` (generic fail-closed flavor handling) |
| Qualification tooling | `scripts/task098-qualify-ml.ps1`, `scripts/task098_ml_qualification.py`, new `scripts/task103_{pilot_probe,compare,make_manifest,auto_fallback_check}.py`, `scripts/task103_gates.v{1,2}.json`, `scripts/task091_combined_contract.py` |
| Tests | updated: `test_task_098_slice_dg.py` (incl. stale-scan rewrite), `test_container_publish_workflow.py`, `release_manifest_contract.py`, `test_release_manifest_schema.py`, `test_release_package_script.py`, `test_task_075_launcher_gpu.py`, `test_task_074_bootstrap.py`, `test_podman_gpu_enablement.py`, `test_task_075_device_policy.py`, `test_yolov5_local_loader.py`, `test_ts_en_classifier.py`, `test_flask_routes.py`; new: `ml_runtime_contract.py`, `test_task_103_ml_runtime_contract.py` (N1–N3), `test_task103_{compare,device_precision,pilot_tooling}.py`, `test_task_091_combined_contract.py` |
| Docs (pilot-minimal pass) | `docs/quick-start.{md,html}`, `docs/user-guide.{md,html}`, `docs/project-overview.{md,html}`, `docs/package-guide.md`, `docs/docker-gpu-user-guide.md`, `docs/podman-gpu-user-guide.md`, `docs/support/oci-{quick-start,runtime-contract}.md`, `docs/release/release-asset-bundle-contract.md`, `README.md`, `HANDOFF.md` |
| Pointers | `.github/copilot-instructions.md`, `.agents/skills/towerscout-release-candidate-gate/SKILL.md` |

**Still to touch in Phase 2** (not on the pilot branch): `webapp/ts_en.py` (W-B2 RGB conversion), `webapp/ts_runtime.py` (H2 messages), `scripts/lib/TowerScoutCompose.ps1` `-Build` path (H3), `.github/workflows/ci.yml` (H5), `container-publish.yml` scan step (H5), `.agent_work/**` governance set (H0), the full H4 docs pass, and — via PR #78, not you — `webapp/ts_yolov5.py` fail-open (W06).

**Deliberately unchanged (LEAVE):** `compose.yaml`, `compose.gpu.yaml`, `compose.gpu.podman.yaml` (do **not** add `NVIDIA_REQUIRE_CUDA`), `release-manifest.v1.json`, `webapp/.env.example`, `SBOM.txt`, `SOURCE.txt`, `.dockerignore`, `launch.ps1`, `TowerScoutBootstrap.ps1` and the bootstrap/setup/import/status/host-helper scripts (flavor is opaque to them), `hosting/`.

---

## 11. Known gotchas (each one cost the pilot real time)

| # | Gotcha | Do this |
|---|---|---|
| G-1 | Fresh clones show 5 `TowerScoutSite/assets` files modified (CRLF committed, `.gitattributes` says lf) — the harness's clean-tree check then refuses to run. | `git update-index --skip-worktree` those files (Phase 0 step 2). Permanent fix (optional Phase 2 hygiene): one `git add --renormalize` commit. |
| G-2 | The harness refuses a dirty tree — correct, but you can't measure while editing. | Measure from a separate clean worktree pinned to a commit. |
| G-3 | Windows PowerShell 5.1 writes JSON with a BOM; Python's default cp1252 decoder chokes. | Read every JSON as `utf-8-sig` (the pilot tooling already does). |
| G-4 | Windows PowerShell 5.1 test suites launched **from pwsh 7** break (`Get-FileHash`, `Set-Acl` PSModulePath issue). | Launch Windows suites from Git Bash or Windows PowerShell. 8 host-helper tests also need admin; their local failures are pre-existing. |
| G-5 | In PowerShell, `,` binds tighter than `+` inside `@(...)` — this silently split a harness argument and failed every phase with exit 2. | Build strings on their own line. Behavioral tests that assert real `docker run` args caught it. |
| G-6 | Spaced paths: a recursive delete guard misread `<SPACED_WORK_ROOT>\...`; a spaced provider path broke podman compose in rc6. | Keep the selected `<TASK103_WORK_ROOT>` space-free. |
| G-7 | Running Trivy (or builds) concurrently with measurement runs caused `ENOMEM` on bind-mount reads and NMS timeouts. | Never overlap scans/builds with qualification runs. |
| G-8 | Cross-window single runs drift ~9% (CPU timing) to ~16% (CUDA host RSS) with no code change. | Relative gates only from interleaved same-window runs, ≥3/side (now codified in gates v3). |
| G-9 | Binary `docker save` piped through PowerShell 5.1 gets corrupted. | `docker save -o file.tar`, or Git Bash for pipes. |
| G-10 | The build log shows torch pulling numpy 2.4.6 before requirements pin 1.26.4 back. | Existing, expected behavior — not a defect. |
| G-11 | GPU batch-8 forward times creep upward across consecutive runs (thermal). | Expect it in timing data; the NMS fix removes the correctness risk. |
| G-12 | A global/other Python with a different torch (workstation had 2.9+cu130) poisons results. | Only ever use the per-pair venv or in-image Python. |

---

## 12. Explicitly out of scope (do not do these as part of TASK-103)

Logged improvement candidates the owner has **not** put in this migration's scope: image slimming (removing Debian GDAL, headless OpenCV, setuptools pinning — candidate follow-up task), ZIP-code data format change, `free_gpu_memory` log-line fix, absolute `-OutputDir` support, forward-slash ZIP entries, host-helper skip-when-not-elevated, T1000 disk cleanup (owner's machine). They live in `TowerScout-Pilot-Improvement-Opportunities-2026-09-23.md` on the owner's side; mention them in the TASK-103 closeout as follow-ups if useful, but do not implement them here.

---

## Appendix A — `scripts/task103_gates.v3.json` (commit in H-1, before any Phase 2 measurement)

Copy `task103_gates.v2.json` and apply exactly these changes (everything else, including every tolerance and the fixture definition, stays identical):

```json
{
  "description": "TASK-103 gates, amendment 3. Owner decision D-P1 (2026-09-24) and pilot lesson L8: GPU-profile memory is judged on total host+device footprint; relative gates require interleaved same-window runs.",
  "memory": {
    "relative_max": 1.10,
    "min_device_free_bytes": 1073741824,
    "gpu_profile_judgment": "total_footprint",
    "total_footprint_definition": "peak host VmHWM bytes + torch.cuda.max_memory_reserved bytes, each from the same run; compared as one sum against 1.10 x the reference sum",
    "cpu_profile_judgment": "host_only"
  },
  "method": {
    "relative_gates_require": "interleaved same-window runs",
    "min_runs_per_side": 3,
    "no_concurrent_scans_or_builds": true
  },
  "amends": {
    "file": "scripts/task103_gates.v2.json",
    "reason": "D-P1: the +15% CUDA-mode host RSS is +108 MB loader fix + +150 MB CUDA 12.8 libraries while device reserved fell 375 MB (total -117 MB). Host-only relative judgment misrepresents GPU-profile footprint. L8: cross-window single-run drift up to 16% invalidates non-interleaved relative comparisons.",
    "tolerances_changed": false
  }
}
```

Extend `task103_compare.py` to implement `gpu_profile_judgment`/`method` (fail closed if the fields are present but unimplemented), with unit tests for: total-footprint pass/fail arithmetic, CPU profiles unaffected, and missing-run-count detection.

## Appendix B — Snippets for the two Phase-2 code items not on the pilot branch

### B.1 `webapp/ts_runtime.py` — failure-class recovery messages (H2)

```python
def _cuda_failure_class(ml: Dict[str, Any]) -> str:
    if not ml.get("torch_cuda_build"):
        return "cpu_only_build"
    if ml.get("cuda_precision_ok") is False:
        return "precision_policy"
    if ml.get("cuda_arch_supported") is False:
        cap = ml.get("cuda_device_capability") or ""
        archs = [a for a in ml.get("torch_cuda_arch_list") or [] if a.startswith("sm_")]
        newest = max((int(a[3:].rstrip("af")) for a in archs if a[3:].rstrip("af").isdigit()), default=0)
        device = int(cap[3:]) if cap[3:].isdigit() else 0
        return "gpu_newer_than_build" if device > newest else "gpu_older_than_build"
    return "driver_or_container"

# Messages (emit only when selected_device != "cuda"):
#   gpu_newer_than_build -> "This GPU (sm_XY) is newer than this package's PyTorch build; use the CUDA 12.8 package."
#   gpu_older_than_build -> "This GPU generation (sm_XY) is not supported by the CUDA 12.8 package; use the CPU package or -Gpu off."
#   cpu_only_build       -> existing "CPU-only PyTorch" text (keep asserted substrings)
#   precision_policy     -> "CUDA precision policy could not be enforced; TowerScout will not run CUDA inference."
#   driver_or_container  -> existing "Confirm NVIDIA container access" text
# Auto-mode hint appended only when selected_device == "cpu" AND fallback_reason is set.
```

### B.2 `scripts/lib/TowerScoutCompose.ps1` — `-Build` index/flavor/version handling (H3)

```powershell
function Set-TowerScoutBuildTorchVersions {
    # Process env beats .env during Compose interpolation; export the pinned pair from
    # requirements.txt unless the caller explicitly set it. Read only when called, never at
    # dot-source time (test_task_087_host_helper.py sandbox-copies this library).
    $requirementsPath = Join-Path (Get-TowerScoutRepoRoot) "webapp\requirements.txt"
    if (-not (Test-Path -LiteralPath $requirementsPath -PathType Leaf)) { return }
    foreach ($line in Get-Content -LiteralPath $requirementsPath) {
        if ($line -match '^torch==([^\s#;]+)' -and [string]::IsNullOrWhiteSpace($env:TOWERSCOUT_TORCH_VERSION)) {
            $env:TOWERSCOUT_TORCH_VERSION = $Matches[1]
        }
        elseif ($line -match '^torchvision==([^\s#;]+)' -and [string]::IsNullOrWhiteSpace($env:TOWERSCOUT_TORCHVISION_VERSION)) {
            $env:TOWERSCOUT_TORCHVISION_VERSION = $Matches[1]
        }
    }
}

# In Set-TowerScoutGpuEnvironment: call Set-TowerScoutBuildTorchVersions whenever $Build, then:
    if ($Build) {
        $indexUrl = ([string] $env:PYTORCH_INDEX_URL).Trim().TrimEnd("/")
        if ([string]::IsNullOrWhiteSpace($indexUrl) -or $indexUrl -eq $script:TowerScoutCpuPytorchIndexUrl) {
            $indexUrl = $script:TowerScoutCudaPytorchIndexUrl
        }
        elseif ($indexUrl -match '^https://download\.pytorch\.org/whl/cu\d+$' -and $indexUrl -ne $script:TowerScoutCudaPytorchIndexUrl) {
            Write-Warning "Ignoring stale PYTORCH_INDEX_URL=$indexUrl; GPU source builds use $($script:TowerScoutCudaPytorchIndexUrl)."
            $indexUrl = $script:TowerScoutCudaPytorchIndexUrl
        }
        $env:PYTORCH_INDEX_URL = $indexUrl
        if ($indexUrl -eq $script:TowerScoutCudaPytorchIndexUrl) {
            $env:TOWERSCOUT_PYTORCH_FLAVOR = "cuda128"
        }
        elseif ([string]::IsNullOrWhiteSpace($env:TOWERSCOUT_PYTORCH_FLAVOR)) {
            throw "PYTORCH_INDEX_URL=$indexUrl is a custom index; set TOWERSCOUT_PYTORCH_FLAVOR explicitly for this source build."
        }
    }
# Then verify the declared flavor against the built image's actual torch local tag and
# torch.version.cuda before the image is used (G1), so a misdeclared mirror flavor fails.
```

## Appendix C — Test and sweep commands

```powershell
# Venv (per torch pair, outside the repo; laptop Python 3.12 works for the comparator,
# but the app venv should use a Python 3.11 if available, matching the image):
#   pip install "torch==2.10.0" "torchvision==0.25.0" --index-url https://download.pytorch.org/whl/cpu
#   pip install -r webapp\requirements.txt -r requirements-dev.txt

# Pure-Python suite (any shell):
python -m pytest tests/unit/ -q
# Windows-only suites — run from Git Bash or Windows PowerShell, NEVER from pwsh 7:
python -m pytest tests/unit/test_release_package_script.py tests/unit/test_task_075_launcher_gpu.py `
  tests/unit/test_task_074_bootstrap.py tests/unit/test_podman_gpu_enablement.py `
  tests/unit/test_task_081_runtime_hardening.py `
  "tests/unit/test_task_098_slice_dg.py::test_cross_device_harness_rejects_build_ca_inside_context" -q
# Host-helper suite (needs PYTHONPATH=webapp; 8 failures are expected without admin):
python -m pytest --confcutdir=tests/unit tests/unit/test_task_087_host_helper.py -q -p no:cacheprovider
# Lint:
python -m flake8 webapp/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Stale-reference sweep (note --hidden; the N4 test on the branch is the authoritative check):
rg -n -i --hidden "cuda126|cu126|cuda 12\.6|12\.6 (application|package)|torch==2\.6\.0|torchvision==0\.21\.0" `
  --glob '!.git/**' --glob '!.agent_work/**' --glob '!docs/superpowers/**'

# YOLO-only continuity check against the historical 53-count vector (palette originals only):
#   harness -NoSecondary, comparator --check-historical-vector
```

---

*Questions or anything ambiguous: stop and ask the owner. A wrong assumption in this migration costs more than a day's pause.*
