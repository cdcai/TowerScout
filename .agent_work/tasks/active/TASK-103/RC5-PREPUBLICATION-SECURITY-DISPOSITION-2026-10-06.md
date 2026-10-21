# RC5 Pre-Publication Security Disposition - 2026-10-06

## Corrected Outcome - October 7, 2026

The retained local `v0.1.3-rc5` CPU and CUDA 12.8 evidence from accepted
`main` commit `a24d369668d27240ed0baa184d071395455b9c95` remains valid as the
record of the blocked first scan. Those images and their mutable-tag control
ZIPs are not publishable.

Trivy `0.69.3` reported the same 14 new HIGH keys in both flavors compared with
the unchanged 396-key baseline. The corrected disposition is:

- ten removable keys belong to Debian Python 3.11 and `libheif1` packages
  pulled into the image by the unused `gdal-bin` dependency;
- two keys identify `urllib3==2.7.0` inside pip 26.2.1's private inventory;
  TowerScout itself imports the separately installed `urllib3==2.8.0`; and
- two keys identify Debian Bookworm `libssl3` and `openssl`
  `3.0.22-1~deb12u1` for `CVE-2026-84782`.

CPython 3.11.17, used by the pinned Python base, includes the fixes for the two
reported Python CVEs. Removing `gdal-bin` removes the second Debian Python
installation and the unused libheif chain instead of accepting those ten
findings. The four remaining records are governed by ADR-024's exact,
time-bounded residual policy through October 31, 2026.

## Local Evidence

The ignored raw evidence remains under
`.agent_work/tmp/Task 103 RC5 Local Validation/security/`:

| File | SHA-256 |
| --- | --- |
| `cpu-trivy.json` | `0db4938d158359d3a94981becb5a46f146caecf339466183a39f72fcb7597645` |
| `cuda128-trivy.json` | `0993b13984d7540d6ead9dbe00db080a5fbd53185165d799e25232ebf35c1697` |
| `cpu-sbom.cdx.json` | `9b78770c58139fd0302f35d93818e5bcdbe050c3935170a94d1f70dd51ec0030` |
| `cuda128-sbom.cdx.json` | `492401812a5b171f55503d98cb9ba8f38ebfaa8425806fc92a94986828a1aab6` |
| `securityfix-cpu-trivy.json` | `f7d144062508fe95187f57cdedc25711717e96842245ac3200344f013c16cb3d` |
| `securityfix-cpu-sbom.cdx.json` | `ff2b58a6b8de38238573e83745decfa5a1ca265149a06f25e0c95a26a2ff0c8b` |

The reviewer-supplied second opinion is retained locally as non-authoritative,
untracked material. ADR-024 and TASK-104 are the authoritative decision and
execution records.

## Corrected Finding Disposition

| Finding(s) | Keys | Disposition |
| --- | ---: | --- |
| `CVE-2026-19445`, `CVE-2026-19553` / Debian Python packages | 8 | Remove `gdal-bin` and prove the Debian Python packages are absent. Active CPython 3.11.17 contains both fixes. No exception is allowed. |
| `CVE-2026-84450`, `CVE-2026-84451` / `libheif1` | 2 | Remove `gdal-bin` and prove `libheif1` is absent. No exception is allowed. |
| `CVE-2026-97687`, `CVE-2026-97689` / `urllib3@2.7.0` | 2 | Exact temporary exception for pip's private inventory only. The workflow must independently prove TowerScout imports `urllib3==2.8.0`. |
| `CVE-2026-84782` / `libssl3`, `openssl` `3.0.22-1~deb12u1` | 2 | Exact temporary exception for the current Bookworm packages. TowerScout has no supported DTLS workflow. |

The Trivy report does not provide `PkgPath` or PURL values for the urllib3
records, so the attribution is not based on a scanner-reported file path. It
is supported by the exact reported package ID/version plus direct in-image
inspection of pip's private and application-imported versions.

## Decision And Required Proof

PR #96 merged as `b0725e750c1541e7cb60df881d3906f761657089`; it is no longer a
draft or an open decision. ADR-024, accepted October 7, and TASK-104 now govern
the remaining work:

1. Keep the 396-key historical baseline unchanged.
2. Pin the candidate base-image indexes and pip 26.2.1; remove `gdal-bin`.
3. Accept only the four exact records in
   `.github/security/task103-accepted-residuals.v1.json`, with strict identity,
   version, class/type, flavor, severity, use, and expiry checks.
4. Build, inspect, and scan locally before any GHCR login or push.
5. Rebuild and qualify CPU and CUDA 12.8, including Fiona/ZCTA and real model
   execution, before review.
6. Keep GHCR dispatch, package publication, and `latest` promotion separately
   owner-authorized.

Any new HIGH/CRITICAL key, baseline severity escalation, changed residual,
incomplete scan, identity mismatch, or expired/unused exception blocks the
candidate. This correction does not reduce the final browser-download,
four-profile, provider, persistence/recovery, or independent-host gates.
