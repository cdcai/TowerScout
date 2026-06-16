# TowerScout RC5 → GA — Two Open Packaging Decisions

**Date:** 2026-06-15
**Context:** Surfaced during validation of the published pre-release `v0.1.0-rc5-candidate.3` (PR #33).
That validation **passed** the full runtime matrix (Docker CPU/GPU, Podman CPU, Podman GPU CDI) with
byte-identical fixed-fixture parity (45 detections / 25 tiles) for both Google and Azure maps. The two
items below are **not rc5 blockers** — the runtime works in every cell today. They are
ship-to-end-user packaging/distribution decisions worth settling before GA.

Image under test: `ghcr.io/j-schulein/towerscout:v0.1.0-rc5-candidate.3-cuda121@sha256:841bc196c753654d359ff399e5ac5a547d4b2ab01150c7cc20eb2b7be73852ad`
Source ref: `ef6904fc`.

---

## Decision 1 — The release image is `cuda121`-only

### What's actually shipped
The release pins **one** image for everyone (the cuda121 build), which bakes in CUDA 12.1 userspace +
`torch 2.2.1+cu121`. It is **10.8 GB uncompressed on disk** (a few GB compressed to pull). There is no CPU
image for this candidate, so CPU-only testers/users pull the full CUDA image and run cu121-torch on the CPU.
It works (validation showed `selected_device=cpu`, parity 45/25), but:

- they download CUDA libraries they never use;
- `readiness` still reports `pytorch_flavor=cuda121` on CPU cells, which is confusing;
- CPU-only deployments carry a larger CVE/attack surface than they need.

### The machinery for a CPU image already exists — it just wasn't run/published for this candidate
- `Dockerfile` is parameterized: `ARG TOWERSCOUT_PYTORCH_FLAVOR` + `ARG PYTORCH_INDEX_URL` (defaults to `whl/cpu`).
- `.github/workflows/container-publish.yml` exposes a `pytorch_flavor` input (`cpu | cuda121`) and tags
  `…-cpu` / `latest-cpu` accordingly. It builds **one flavor per dispatch**.
- `compose.yaml` even defaults to `image: ${TOWERSCOUT_IMAGE:-…:latest-cpu}` — but the release `.env`
  overrides that with the pinned cuda121 digest.

### Why it matters
Download/disk cost (10.8 GB vs typically a few GB for a CPU-only image), bandwidth pain for air-gapped /
government sites, mild UX confusion (flavor vs selected device), and unnecessary CVE surface for CPU sites.

### Options

| Option | What it is | Trade-off |
|---|---|---|
| **A. Publish both flavors; CPU users get the CPU image** *(recommended)* | Run the publish workflow for `cpu` too; deliver the CPU image to non-GPU users | Best UX; ~one extra build per release + a delivery sub-decision (below). This is the intended design — `compose.yaml`'s `latest-cpu` default shows it. |
| **B. Keep cuda121-only, document it** | Status quo + a release note ("CPU runs on the CUDA image; expect a large pull") | Zero build work; CPU users keep pulling 10.8 GB; flavor/readiness mismatch remains. |
| **C. One combined / auto-selecting image** | Single image that installs the right torch at runtime | More complex build, slower cold start, no real size win — not worth it. |

**If Option A, sub-decision on how the package selects the image:**

- **A1 — two packages** (a `-cpu` control zip pinning the CPU digest; a `-cuda121` one pinning the CUDA digest).
  Cleanest for users; two artifacts to publish + checksum. *(Recommended for a clean GA.)*
- **A2 — one package, both digests pinned**, launcher picks by `-Gpu`/device. One artifact; needs a small
  launcher change (today `TOWERSCOUT_IMAGE` is a single pinned value — the launcher sets
  `TOWERSCOUT_PYTORCH_FLAVOR` but never swaps the image).
- **A3 — one cuda121 package + documented override** (CPU users set `TOWERSCOUT_IMAGE` to the CPU digest).
  Least work, but relies on users editing `.env`.

**Recommendation:** **A1** for a clean GA (two pinned packages), or **A2** if a single artifact is preferred
and the small launcher change is acceptable.

---

## Decision 2 — `PODMAN_COMPOSE_PROVIDER` defaults blank (no provider shipped)

### What's actually happening
`podman compose` is a thin shim that delegates to an **external** Compose provider binary. PR #33's guardrail
(`Initialize-TowerScoutPodmanComposeProvider` / `Assert-TowerScoutPodmanComposeProviderAllowed` in
`scripts/lib/TowerScoutCompose.ps1`) **fail-closed rejects Docker Desktop's bundled `docker-compose.exe`** —
that is the licensing-clean point, since Docker Desktop's subscription terms (SSA) bar free government use.
So the Podman path requires an **approved, non-Docker-Desktop** Compose binary, and the package ships:

- `.env.example` with `PODMAN_COMPOSE_PROVIDER=` **blank** plus a comment that "support should set this," and
- **no bundled provider** — there is no `scripts/vendor/` directory in this branch (the rc4 auto-vendoring
  idea, finding F2, did not make it into PR #33).

### Net effect
Validation passed because a known-good standalone Compose (v5.1.4) was already installed on the host and
pointed to via `PODMAN_COMPOSE_PROVIDER`. But a real Podman-only user who has **only** Docker Desktop's
compose (rejected by the guardrail) or **no** Compose provider at all cannot start the Podman path out of the
box — and that user (e.g. CDC / health-department, the reason the Podman path exists) is exactly who hits this.

### Options

| Option | What it is | Trade-off |
|---|---|---|
| **A. Bundle/bless the Apache-2.0 standalone Compose binary** | Ship the binary in `scripts/vendor/`, auto-resolve it (SHA256-verified) when the var is blank | Best UX, works offline / air-gapped. Costs: +~60 MB per-OS binary in the package, redistribution/license attestation (Apache-2.0 permits it), and you maintain/pin its version. |
| **B. Scripted fetch + verify** *(recommended)* | A helper (e.g. `scripts/get-compose-provider.ps1`) that downloads the official Compose release, checksum-verifies it, drops it in a known path, and sets the var | No redistribution, small package; needs network at setup (not air-gapped). |
| **C. Document-only** | Instructions: install standalone Compose, set the var | Lowest effort; worst UX; leaves the blank-default footgun. Roughly status quo. |
| **D. Auto-detect on PATH** | If the var is blank, search PATH for a non-Docker-Desktop `docker compose` / `docker-compose`, use it; only error if none | Cheap win where a user already has one; pairs well with A or B as the fallback. |

**Recommendation:** **B + D** — auto-detect an approved provider if one is already present; otherwise offer the
fetch-and-verify helper. Reserve **A** (bundling) for a future fully-air-gapped installer where offline is a
hard requirement.

---

## Summary

| Item | Status | Recommendation |
|---|---|---|
| cuda121-only image | Not a blocker; GA polish | Publish a CPU flavor too; ship as two pinned packages (A1), or one package selecting by device (A2) |
| `PODMAN_COMPOSE_PROVIDER` blank | Not a blocker; blocks Podman-only end users out of the box | Auto-detect on PATH + a fetch-and-verify helper (B + D); bundle (A) only for air-gapped installer |

**Possible next steps (on request):**
- Draft the `container-publish.yml` change to emit both flavors + a two-package build, and the launcher tweak for A2.
- Write `scripts/get-compose-provider.ps1` (fetch + SHA256 verify) and the PATH auto-detect fallback for the provider.
