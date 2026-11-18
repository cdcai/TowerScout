# Experimental beta publication decision — November 18, 2026

The project owner explicitly directed publication of **v0.1.4-beta.1**, with
both CPU and CUDA 12.8 images, despite the twelve known blocking HIGH package
findings in the November 18 CPU scan. This decision accepts those exact records
for this experimental prerelease through **January 30, 2027 at 23:59:59 UTC**.
It supersedes the earlier requirement to complete P1/E1/S1/Z1 before publication
of this beta only. Those investigations and full deployment qualification remain
pending; this decision does not claim remediation, non-applicability or a
qualified production release.

The request also authorizes the focused policy change and beta publication.
Required source CI and normal branch protections remain in effect.

| Findings | Packages | Installed version |
| --- | --- | --- |
| CVE-2025-6020 | libpam-modules, libpam-modules-bin, libpam-runtime, libpam0g | 1.5.2-6+deb12u2 |
| CVE-2026-113351, CVE-2026-115506, CVE-2026-117610, CVE-2026-118370 | libexpat1 | 2.5.0-1+deb12u5 |
| CVE-2026-119373, CVE-2026-119374, CVE-2026-119379 | libsqlite3-0 | 3.40.1-2+deb12u2 |
| CVE-2026-85091 | zlib1g | 1:1.2.13.dfsg-1 |

The exact records are in
[`task107-beta1-residuals.v1.json`](../../.github/security/task107-beta1-residuals.v1.json).
The comparator applies them only to an image whose source/flavor identities
are verified and whose version label is exactly `v0.1.4-beta.1`. Other versions
continue using the unchanged normal policy and its eight util-linux records.
Fresh scans must match each accepted package/version/class/type and HIGH
severity. New, escalated, changed, missing or expired records still fail closed.
Each flavor must independently pass its scan; CPU findings do not establish
CUDA image contents. Policy hashes and exact-image scan reports accompany
publication evidence. The 396-key baseline is unchanged.

Publish separate immutable CPU and CUDA image tags and digest-pinned Windows
control ZIPs with checksums, source identity, notices and verified asset-bundle
references. Create a GitHub **prerelease**, with `make_latest=false` and
`push_latest=false`. Preserve the current release, existing images and latest
aliases. Retain model hashes, inference settings, TLS verification, loopback
binding, standard capabilities and all existing named volumes. Test installs
must use a separate directory, Compose project and unused port.

Release notes must disclose known unresolved vulnerabilities and incomplete
Windows/model/device qualification. A hosted CUDA image build is not a real
GPU inference test; no GPU qualification may be claimed from that build.
The unsigned Windows package support boundary is unchanged.

The project owner retains TASK-107 weekly and immediate-change review. Remove
exceptions when fixes or changed exposure invalidate them. Future betas and
stable promotion require their own decision; no automatic renewal applies.

Supporting review: [runtime exposure assessment](2026-11-16-runtime-exposure.md).
Fresh CPU scan: [GitHub run 44379485761](https://github.com/cdcai/TowerScout/actions/runs/44379485761),
source `4d8169eed2b541f6c5beea38d3b6ddff72cd60f4`: 69 keys, 49 accepted baseline,
eight util-linux residuals, twelve blocking HIGH keys, no severity escalations.
That failed run performed no registry login or push. New publication runs must
retain their own source and exact-image identities.
