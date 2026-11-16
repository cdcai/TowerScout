# Runtime dependency exposure assessment ? November 16, 2026

## Outcome and boundary

A small local assessment that omits unused Unix NIS functionality removes 56 HIGH Kerberos CVE/package keys: 69 unaccepted keys become 13, with no new keys or severity increases. The publication gate still fails. No baseline, exception, expiry, TLS policy, model hash, inference setting or user-data contract is changed.

The source change is an application-specific runtime reduction, not a patched Kerberos release. Python's optional `nis` extension is intentionally unavailable in the dedicated image. The ordinary Windows installation prerequisites and managed-endpoint support boundary are unchanged.

## Why NIS can be assessed separately

The original installed OS dependency graph is `nis` extension ? libnsl2 ? libtirpc3 ? the Kerberos libraries. Inspection of 508 native ELF files under `/usr/local`, including Python, Torch and CUDA libraries, found the NIS extension as the only consumer of this system chain; no TowerScout NIS import or supported account-directory feature was found. The image contains no krb5kdc, kadmind or kadmin executable. Absence of those servers is bounded applicability evidence, not proof that every library vulnerability is unreachable.

The guarded build helper first verifies the Linux/root/Python 3.11 profile, exactly one regular ELF NIS extension, and the complete installed/non-essential package set. It simulates APT removal and rejects any additional removal, installation, missing package or essential package before changing files. It then omits that extension and uses normal, non-forced APT purge of exactly:

- libnsl2, libtirpc3, libtirpc-common
- libgssapi-krb5-2, libkrb5-3, libk5crypto3, libkrb5support0, libkeyutils1

APT dependency checking and dpkg audit must pass afterward. There is no automatic dependency sweep or forced removal. Unexpected package status or APT removal actions fail the image build for review. Future base/wheel updates must repeat the native-link audit and affected runtime checks; an APT plan cannot establish wheel binary compatibility by itself.

The remaining ELF inspection reports no new missing links versus the unmodified image. Both all-native audits have 47 standalone `ldd` warning records, including pre-existing optional Tk, wheel-private loader paths and unmapped GPU dependencies; those warnings are not claimed resolved. Actual imports and workflows supplement this static comparison. Removed bytes can remain in inherited image layers; this reduces the running filesystem's functionality and package exposure, not necessarily compressed image size.

## Scan results

| Stage | HIGH/CRITICAL scanner keys | Accepted baseline | Accepted residuals | Unaccepted keys |
| --- | ---: | ---: | ---: | ---: |
| pip/apt assessment before omission | 126 | 49 | 8 | 69 |
| Guarded NIS omission assessment | 70 | 49 | 8 | 13 |

Both use Trivy 0.69.3 and the same November 16 vulnerability database. The unchanged 396-key historical baseline and eight util-linux residual entries are retained exactly. The final comparator returns failure, as required. These counts are scanner CVE/package keys, not distinct exploitable application defects or a complete native-library inventory.

## Components retained and follow-up

| Component | Remaining unaccepted keys | Observed use and next action |
| --- | ---: | --- |
| PAM | 4 | Required by Debian's essential login package. No supported TowerScout PAM login path was found. Retain it; do not force-remove essential packages. Review the specific pam_namespace configuration and vendor fix. |
| System Expat | 4 | Fiona's GDAL extensions actually link to it, so OS reverse dependencies alone were insufficient. Preserve it and pursue a supported fix or rebuild of the native stack. |
| System SQLite | 3 | Loaded by Python's `_sqlite3`; both FTS5 and session support are compiled in. Review the precise crafted-database/changeset preconditions and supported input paths. Do not remove the library and leave a broken Python extension. |
| zlib | 2 | Used by Python and imaging dependencies. Preserve compression support; review the gzip-write error path and resolve the advisory identity conflict below. |

Additional observed copies are Python's embedded Expat 2.8.5, Fiona's bundled SQLite 3.33.0, and pyproj's bundled SQLite 3.46.1. Both wheel SQLite copies include FTS5 but not session support; the system SQLite is 3.40.1 and includes both. The reviewed app writes XML annotations as text and uses Fiona to read packaged ZIP-code data; no direct NIS/PAM authentication, arbitrary SQL execution or SQLite database-upload route was found. These are bounded source/workflow observations, not assertions that indirect library code can never be reached. A supported native dependency update must inventory and assess bundled copies as well as Debian packages. The OS scan count alone cannot establish their remediation.

### SQLite feature applicability follow-up

A benign in-memory FTS5 test accepted the normal `automerge` configuration on all three SQLite copies. The system 3.40.1 and Fiona 3.33.0 copies rejected the FTS5 `secure-delete` configuration; pyproj 3.46.1 accepted it. Upstream [SQLite 3.42.0 release notes](https://sqlite.org/releaselog/3_42_0.html) identify that release as introducing the FTS5 secure-delete command, while the [CVE-2026-119374 record](https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2026/119xxx/CVE-2026-119374.json) uses a broad pre-3.54.0 affected range and describes that feature. This is evidence that version-only matching needs refinement, not a final not-affected ruling: distro backports, exact code and each bundled copy still need review. No malformed databases, deletion operations or vulnerability triggers were used in the feature probe. The scanner entry and gate are retained unchanged pending a valid disposition.

### Conflicting zlib advisory metadata

The official [CVE-2026-76844 record](https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2026/76xxx/CVE-2026-76844.json) identifies webpack-dev-middleware. The [Debian entry](https://security-tracker.debian.org/tracker/CVE-2026-76844) nevertheless maps it to zlib and lists the same fix as CVE-2026-85091. The [upstream zlib fix](https://github.com/madler/zlib/commit/df84af25dc1942490e1d1c899a07619152a46148) identifies CVE-2026-85091. This cross-source inconsistency needs vendor/advisory-data clarification; it is not a confirmed new waiver or grounds to suppress either scanner entry here. No report was sent to third parties and no acceptance was added.

## Validation

- Guarded helper executed against real installed package metadata in the small assessment build; APT removed exactly eight non-essential packages and its audit/check passed. Dependency consistency passed.
- Four fixed saved imagery tiles were processed through both production model loaders before and after omission, on forced CPU and CUDA. Each run exercised 10 secondary-classifier candidates across three batches. Detection/classification outputs matched exactly within each device profile; trusted model checks remained enabled.
- Live Azure estimate/detection produced 25 detections across four tiles. CSV contained 25 rows and KML 16 placemarks. Dataset restore, invalid-archive recovery and export after controlled restart passed. Both ZIPs passed CRC checks and preserved all four tile-image byte hashes.
- Maintained Azure cancellation/retry coverage passed, with 25 review entries and 16 visible markers; no browser page errors were recorded.
- A real ZIP-code boundary read through GeoPandas/Fiona returned one feature with HTTP 200. This supplements the native-import and linkage checks.
- The attempted Google workflow failed map-tile TLS validation. An isolated verified-HTTPS comparison reproduced the Google-domain certificate failure in both the unmodified and guarded images, while Azure succeeded in both. This is an unresolved current network/trust limitation, not a successful Google qualification. TLS verification was never disabled and no CA trust change was made.
- Full maintained unit suite: 931 passed, 74 skipped. Blocking Python lint reports zero findings; whitespace/adoption checks are recorded separately.
- New removal-guard tests cover unexpected/essential/missing package metadata, extra APT actions, malformed extension files, host refusal and refusal before any file/system mutation. The genuine package-removal build and real-model/browser checks are separate evidence from these source tests.

All private imagery, fixtures, raw scans, model outputs, credentials and logs remain outside commits. A small dependency layer over the previously tested application image was used to avoid a full CUDA rebuild. It is not a clean build from this branch, a separate CPU-flavor image, an official downloaded package, a second-host test or Podman qualification. Source changes must still be built and qualified in official artifacts before any release decision.

## Exact evidence identities

- Accepted main at start: `bce3e1bc49b0ba012961ccb3fb65d5afd1832c6b`.
- The reused application image identifies source `79422383e9e09dad301cf66ea659d30335fa7661`; its application tree matches the accepted merged main. The assessment retains that inherited label and is not advertised as a clean build of this branch.
- Guarded assessment inspected image: `sha256:19cacfbd2eecf5b79bb2f27fb133154804875e5fcdc8143c94c6bd5f04477ad2`.
- Guarded assessment scan SHA-256: `7fd41629d87eeb533acbf98375d3bd2e333116120c2239afb62920b4cfdc70dc`.
- Build helper SHA-256: `34c562e9bc87c51897f1a86ff4584da966ad6460946b0eec3b251bd5ae8753f0`.
- Raw and sanitized local evidence are retained by the maintainer; artifact identities do not authorize publication.
