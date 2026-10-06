# RC5 Pre-Publication Security Disposition - 2026-10-06

## Outcome

The local, non-publishable `v0.1.3-rc5` CPU and CUDA 12.8 images built from
accepted `main` commit `a24d369668d27240ed0baa184d071395455b9c95` are
functionally healthy, but the fail-closed Task-103 Trivy delta gate is
**BLOCKED**. Neither image may be published or used to assemble a final
release package.

Trivy `0.69.3` reported the same result for both flavors:

- 928 total vulnerability records: 5 CRITICAL, 147 HIGH, 284 MEDIUM, 475 LOW,
  and 17 UNKNOWN;
- 152 normalized HIGH/CRITICAL `(VulnerabilityID, PkgName)` keys;
- 14 new HIGH keys, representing seven CVEs, compared with the committed
  396-key accepted baseline;
- 258 accepted-baseline keys no longer present; and
- no flavor-specific difference between CPU and CUDA 12.8.

The five CRITICAL records are pre-existing accepted-baseline findings. All 14
new blocking keys are HIGH.

## Local Evidence

The ignored local evidence is under
`.agent_work/tmp/Task 103 RC5 Local Validation/security/`:

| File | SHA-256 |
| --- | --- |
| `cpu-trivy.json` | `0db4938d158359d3a94981becb5a46f146caecf339466183a39f72fcb7597645` |
| `cuda128-trivy.json` | `0993b13984d7540d6ead9dbe00db080a5fbd53185165d799e25232ebf35c1697` |
| `cpu-sbom.cdx.json` | `9b78770c58139fd0302f35d93818e5bcdbe050c3935170a94d1f70dd51ec0030` |
| `cuda128-sbom.cdx.json` | `492401812a5b171f55503d98cb9ba8f38ebfaa8425806fc92a94986828a1aab6` |
| `securityfix-cpu-trivy.json` | `f7d144062508fe95187f57cdedc25711717e96842245ac3200344f013c16cb3d` |
| `securityfix-cpu-sbom.cdx.json` | `ff2b58a6b8de38238573e83745decfa5a1ca265149a06f25e0c95a26a2ff0c8b` |

The local control ZIPs are also expressly non-publishable because they use
mutable local image tags rather than authoritative registry digests.

## New Findings And Disposition

| Finding(s) | Keys | Current disposition |
| --- | ---: | --- |
| `CVE-2026-97687`, `CVE-2026-97689` / `urllib3` | 2 | TowerScout's importable runtime dependency is fixed at `urllib3==2.8.0`. Trivy still reports these keys against pip 26.2.1's isolated vendored `urllib3==2.7.0`, not TowerScout's imported package. Pip is used by qualification tooling but not by the running application. The fail-closed key gate still blocks until this residual is explicitly accepted or upstream pip vendors 2.8.0. |
| `CVE-2026-19445` / four Python 3.11 binary packages | 4 | No Debian bookworm fix is listed. The affected behavior is a TLS server changing `SSLContext` from `sni_callback`; TowerScout does not configure a TLS server or `sni_callback`. Residual acceptance remains owner-gated. |
| `CVE-2026-19553` / four Python 3.11 binary packages | 4 | No Debian bookworm fix is listed. The affected behavior requires `wrap_bio()` without a valid `server_hostname`; TowerScout has no direct `wrap_bio()` use and its supported provider clients use hostname-bearing HTTPS URLs. Residual acceptance remains owner-gated. |
| `CVE-2026-84450`, `CVE-2026-84451` / `libheif1` | 2 | No Debian bookworm fix is listed. `libheif1` is a transitive geospatial runtime package, but TowerScout's validated custom-image boundary accepts only JPEG, PNG, and TIFF; no HEIF/AVIF path is supported. Residual acceptance remains owner-gated. |
| `CVE-2026-84782` / `libssl3`, `openssl` | 2 | No Debian bookworm fix is listed. The finding affects DTLS retransmission; TowerScout does not implement a DTLS workflow. Residual acceptance remains owner-gated. |

Primary references checked on 2026-10-06:

- Debian security tracker: [CVE-2026-19445](https://security-tracker.debian.org/tracker/CVE-2026-19445),
  [CVE-2026-19553](https://security-tracker.debian.org/tracker/CVE-2026-19553),
  [CVE-2026-84450](https://security-tracker.debian.org/tracker/CVE-2026-84450),
  [CVE-2026-84451](https://security-tracker.debian.org/tracker/CVE-2026-84451),
  and [CVE-2026-84782](https://security-tracker.debian.org/tracker/CVE-2026-84782);
- the corresponding upstream advisories linked by Debian; and
- the [PyPI `urllib3` 2.8.0 release metadata](https://pypi.org/project/urllib3/2.8.0/).

Changing the Python 3.11 base is not a bounded remediation. Python 3.11 is an
explicit Task-103 invariant, the application qualification evidence is bound
to it, and Debian trixie's Python 3.13 packages are also listed as vulnerable
to both Python findings. A base/runtime migration would require a new decision
and full requalification.

## Verification Completed

- `urllib3==2.8.0` installed in an isolated target beside `Requests==2.33.1`;
  both imported with the expected versions.
- Eight Task-098 provider-download tests passed after the exact pin was added.
- Fifty-six provider HTTP, geocoding, configuration, and TLS-focused tests
  passed with the isolated `urllib3==2.8.0` target active.
- A local CPU image was rebuilt from exact commit
  `721fe38cae668e0e14a1de2ed7083fc92efdf506`; its OCI source label matches,
  and Python imports `urllib3 2.8.0`, `Requests 2.33.1`, torch `2.10.0+cpu`,
  and torchvision `0.25.0+cpu`.
- The rebuilt-image scan still reports 14 new HIGH keys. Direct inspection
  proves the two `urllib3` keys originate from
  `pip._vendor.urllib3==2.7.0`; the normal `urllib3` distribution and import
  path are version 2.8.0. No baseline entry was added.
- A patched CUDA rebuild was not started after the common CPU dependency layer
  proved the key gate remains blocked; publishing either flavor remains
  prohibited, and both flavors will be rebuilt after the residual decision.
- The temporary build/scan CA bundle contained only a public trusted root, was
  used with certificate verification enabled, and was deleted after the scans.
- The temporary Trivy database cache and isolated dependency target were
  deleted after evidence generation.
- Draft PR #96 contains the bounded dependency correction and this disposition.
  All required CI checks passed at head commit
  `2e4f0c472dce0c033eca510d27eabb064fbd67b7`, and the requested Codex review
  reported no major issues. The expected publish/build job remained skipped
  because the PR is a draft. This review checkpoint does not accept the
  residual keys, amend the accepted baseline, or authorize publication.

## Required Next Decision

1. PR #96 has passed normal CI and automated review. The release owner may
   merge the bounded `urllib3==2.8.0` correction independently of the residual
   decision; it protects TowerScout's imported HTTP client even though pip's
   vendored inventory continues to trigger the key-based scanner.
2. Do not modify the accepted baseline merely to make the gate pass. Present
   all 14 scanner keys, including the pip-vendor explanation and the 12 no-fix
   operating-system keys, to the release owner for an explicit residual-risk
   decision, or wait for fixed pip/Debian packages.
3. If the owner accepts the residuals, amend the baseline only through a
   reviewed, auditable commit that preserves this disposition; then rebuild
   both local image flavors and repeat Trivy/SBOM generation.
4. Only after the security gate has an approved disposition may the owner
   separately authorize immutable GHCR publication. Final packages must then
   bind exact published digests and exact browser-downloaded bytes.
