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

The local control ZIPs are also expressly non-publishable because they use
mutable local image tags rather than authoritative registry digests.

## New Findings And Disposition

| Finding(s) | Keys | Current disposition |
| --- | ---: | --- |
| `CVE-2026-97687`, `CVE-2026-97689` / `urllib3` | 2 | Fix available in `urllib3==2.8.0`. Pin added and focused provider/TLS tests pass. A rebuilt image and fresh scan are required. |
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
- The temporary build/scan CA bundle contained only a public trusted root, was
  used with certificate verification enabled, and was deleted after the scans.
- The temporary Trivy database cache and isolated dependency target were
  deleted after evidence generation.

## Required Next Decision

1. Land the bounded `urllib3==2.8.0` correction through normal review and CI.
2. Rebuild both local image flavors from the resulting accepted-main commit
   and repeat Trivy/SBOM generation.
3. Do not modify the accepted baseline merely to make the gate pass. Present
   the remaining no-fix, non-reachable findings and exact rebuilt scan evidence
   to the release owner for an explicit residual-risk decision, or wait for
   fixed Debian bookworm packages.
4. Only after the security gate has an approved disposition may the owner
   separately authorize immutable GHCR publication. Final packages must then
   bind exact published digests and exact browser-downloaded bytes.
