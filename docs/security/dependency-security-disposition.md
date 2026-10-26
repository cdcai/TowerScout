# Dependency security disposition

The release gate retains the accepted 396-key baseline and twelve exact time-limited HIGH residual identities: four renewed records and eight separately approved util-linux records.
The authoritative machine-readable identities, versions, CPU/CUDA scope and expiry are in
`.github/security/task103-accepted-residuals.v1.json` in corresponding source.
On October 22, 2026, the project owner authorized conditional renewal of the existing findings supported by fresh evidence, with a maximum expiry of January 31, 2027 at 23:59:59 UTC. The resolved Expat entry has been removed. That renewal remains limited to the four older records. The project owner subsequently approved the separate eight-record November 5 exception below.

| Finding | Exact retained identity | Scope |
| --- | --- | --- |
| CVE-2026-97687 | `urllib3@2.7.0` | pip-private Python package, CPU/CUDA |
| CVE-2026-97689 | `urllib3@2.7.0` | pip-private Python package, CPU/CUDA |
| CVE-2026-84782 | `libssl3@3.0.22-1~deb12u1` | Debian package, CPU/CUDA |
| CVE-2026-84782 | `openssl@3.0.22-1~deb12u1` | Debian package, CPU/CUDA |

The project owner owns weekly review under TASK-107, immediate review on a fix, severity/identity/exposure change or failed gate, and a final review during the week of January 25. Retain each entry only while its evidence remains valid. There is no automatic extension beyond January 31.

## Reachability rationale

Two urllib3 findings apply to pip 26.2.2's private urllib3 2.7.0, not the application's separately installed 2.8.0.
The application does not invoke pip at runtime, and automatic model dependency installation is disabled.
Exact-image filesystem inventory must prove the accepted copy and reject additional copies.
Pip still handles controlled HTTPS dependency downloads during installation/builds. The proxy-TLS and chunked-response risks are therefore not claimed unreachable in pip; this is bounded owner acceptance. Official pip 26.2.2 remains the latest published release at review time and still vendors 2.7.0. Do not replace its private files manually or disable TLS verification to suppress a finding.

The OpenSSL/libssl3 records affect DTLS retransmission; supported provider requests use HTTPS over TCP.
The fresh paired Bookworm builds contain fixed `libexpat1@2.5.0-1+deb12u5`; CVE-2026-77214 is absent and its exception is removed. Bookworm still has no vendor fix for the retained OpenSSL identities. Preserve exact installed versions and re-evaluate reachability after changes.

## Separately approved util-linux exception

Fresh paired CPU/CUDA scans identify CVE-2026-53615 on eight Debian util-linux binary-package records. It affects crafted DOS extended-partition metadata processing in libblkid. No supported application caller or raw-block-device mapping was found in the bounded review; this does not prove the library unexploitable. On October 22, the project owner separately approved only the following exact HIGH `os-pkgs` / `debian` records for CPU/CUDA through **2026-11-05T23:59:59Z**. This is temporary risk acceptance, not remediation.

| Package | Exact installed version |
| --- | --- |
| bsdutils | `1:2.38.1-5+deb12u3` |
| libblkid1 | `2.38.1-5+deb12u3` |
| libmount1 | `2.38.1-5+deb12u3` |
| libsmartcols1 | `2.38.1-5+deb12u3` |
| libuuid1 | `2.38.1-5+deb12u3` |
| mount | `2.38.1-5+deb12u3` |
| util-linux | `2.38.1-5+deb12u3` |
| util-linux-extra | `2.38.1-5+deb12u3` |

The project owner owns TASK-107 weekly review and immediate review on a vendor fix, severity/identity change, new disk-probing caller, raw-device exposure, privileged/capability change or failed gate. Remove these entries when fixed and repeat affected qualification. The November 5 expiry is independent of the January 31 renewal; no automatic extension applies. Publication still requires separate authorization and final-artifact qualification.

An isolated Debian 13 CPU assessment removed that CVE and the OpenSSL residuals, but introduced eight unaccepted records for four other util-linux CVEs on `login` and `liblastlog2-2`. Debian protects `login`, and essential util-linux requires liblastlog2-2. The assessment is not adopted; do not force-remove required packages, mix Debian suites, or broaden the baseline. The approved short exception applies only to the retained Debian 12 identities; none of the Debian 13 findings is accepted.

Primary review sources: [Debian util-linux finding](https://security-tracker.debian.org/tracker/CVE-2026-53615), [Debian OpenSSL status](https://security-tracker.debian.org/tracker/CVE-2026-84782), [urllib3 proxy advisory](https://github.com/urllib3/urllib3/security/advisories/GHSA-8988-9cw3-xx77), [urllib3 response advisory](https://github.com/urllib3/urllib3/security/advisories/GHSA-vxq7-64xx-v4gw), and [pip's exact vendored versions](https://github.com/pypa/pip/blob/26.2.2/src/pip/_vendor/vendor.txt).

## Enforcement and maintenance

Fresh scans must fail on new HIGH/CRITICAL keys, severity increases, changed identities, incomplete scans,
extra copies, unused exceptions and expired policy. Local scans precede publication, with identity checks and rescans of exact published digests.
Do not renew by editing dates alone. Resolve an upstream fix with an appropriate rebuild and affected qualification.
If no valid disposition remains after expiry, hold future publication; installed copies continue to operate.

The selected torch 2.10.0/torchvision 0.25.0 CUDA 12.8 bridge preserves tested older and Blackwell GPU support.
The existing LOW torch advisory remains visible; trusted hash-verified model loading is required.
Maintenance review is due January 31, 2027 or earlier for a relevant advisory, supported-path change or dependency incompatibility.
See [maintenance boundaries](../maintenance.md) for ownership and qualification requirements.

## Receiving-maintainer follow-up register

This source-contained register makes the obligations also tracked privately as
TASK-107 accessible to the receiving maintainer. The project owner is the risk
acceptance owner; the receiving maintainer performs monitoring, records evidence
and proposes remediation; an independent reviewer checks acceptance/publication
gates. Assignment of named receiving custodians and a durable evidence copy is
still required at handoff, without publishing private approval correspondence.

| Obligation | Due/trigger | Required evidence and disposition |
| --- | --- | --- |
| Eight exact util-linux identities | Weekly and immediately on the changes listed above; hard expiry 2026-11-05T23:59:59Z | Fresh exact-digest scans, installed identities and exposure review; remove fixed entries and requalify. No automatic extension. |
| Four renewed older identities | Weekly/immediate-change review; week of January 25 review; hard expiry 2027-01-31T23:59:59Z | Same exact-identity/scan review; retain only still applicable approved entries. |
| New/changed/unused/expired findings | Every build and publication verification | Fail closed against the unchanged 396-key baseline and exact residual policy at `.github/security/task103-accepted-residuals.v1.json` in the corresponding source identified by `SOURCE.txt`. The control ZIP does not include `.github/`. |
| Corresponding source and evidence custody | Before artifact publication/handoff | Final-version recursive source, build/relink inputs, notices and SBOMs; checksum-verified receiving-held evidence copy. Retain commit-addressed fork records and their evidence ref. |
| Receiving publication controls | Before authoritative publication; promotion before stable/Latest | Independently protected main-only release environment, approved source/ref, administrator/package-write review and exact qualified-digest promotion. |

Record each review date, source/image identities, evidence location, outcome and
next review in the receiving maintainer's approved record. Source adoption alone
does not execute any settings change, publish a new tracker or accept a finding.
The About description/homepage correction remains a separate unexecuted action.
