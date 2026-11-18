# Runtime dependency exposure assessment: November 16, 2026

## Outcome and boundary

A small local assessment that omits unused Unix NIS functionality removes 56 HIGH Kerberos CVE/package keys: 69 unaccepted keys become 13, with no new keys or severity increases. The publication gate still fails. No baseline, exception, expiry, TLS policy, model hash, inference setting or user-data contract is changed.

The source change is an application-specific runtime reduction, not a patched Kerberos release. Python's optional `nis` extension is intentionally unavailable in the dedicated image. The ordinary Windows installation prerequisites and managed-endpoint support boundary are unchanged.

## Why NIS can be assessed separately

The original installed OS dependency graph is `nis` extension -> libnsl2 -> libtirpc3 -> the Kerberos libraries. Inspection of 508 native ELF files under `/usr/local`, including Python, Torch and CUDA libraries, found the NIS extension as the only consumer of this system chain; no TowerScout NIS import or supported account-directory feature was found. The image contains no krb5kdc, kadmind or kadmin executable. Absence of those servers is bounded applicability evidence, not proof that every library vulnerability is unreachable.

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
- The initial Google workflow failed map-tile TLS validation in both the unmodified and guarded images, while Azure succeeded in both. A follow-up used the documented certificate importer in an isolated test control project, with a CA already trusted by Windows. The importer validated the CA, built a combined bundle and verified Google HTTPS before activating it. TLS verification stayed enabled; the user's normal control package and configuration were not modified.
- With that bundle, live Google detection produced 26 detections across four tiles. CSV contained 26 rows and KML 16 placemarks. Dataset restore, invalid-archive recovery, readiness and export after restart passed. Both ZIPs passed CRC checks and preserved the same four image byte hashes; restored export paths were normalized. An initial restart test attempted export before the server was ready and timed out; a repeat with an explicit health wait passed. This is local network-trust validation, not official package qualification.
- Google cancellation/retry also passed: cancellation cleared the active run, retry produced 26 review entries and 16 visible markers, and no browser page errors were recorded.
- Full maintained unit suite: 931 passed, 74 skipped. Blocking Python lint reports zero findings; whitespace/adoption checks are recorded separately.
- New removal-guard tests cover unexpected/essential/missing package metadata, extra APT actions, malformed extension files, host refusal and refusal before any file/system mutation. The genuine package-removal build and real-model/browser checks are separate evidence from these source tests.

All private imagery, fixtures, raw scans, model outputs, credentials and logs remain outside commits. A small dependency layer over the previously tested application image was used to avoid a full CUDA rebuild. It is not a clean build from this branch, a separate CPU-flavor image, an official downloaded package, a second-host test or Podman qualification. Source changes must still be built and qualified in official artifacts before any release decision.

## Supported dependency update path

The November 16 official package metadata lists Fiona 1.10.1, already pinned here, as its latest release. The installed pyproj 3.7.2 is the latest release compatible with Python 3.11; pyproj 3.8.0 requires Python 3.12. Inspection of the hash-verified official Linux CPython 3.11 pyproj 3.7.2 wheel confirmed bundled SQLite 3.46.1. Reinstalling those current wheels would not replace their old SQLite copies. Sources: [Fiona metadata](https://pypi.org/pypi/fiona/json), [pyproj metadata](https://pypi.org/pypi/pyproj/json), and [pyproj 3.7.2 metadata](https://pypi.org/pypi/pyproj/3.7.2/json).

The next dependency implementation should be a separate native-stack change:

1. Resolve the advisory identity and feature-applicability questions above without suppressing the existing gate entries prematurely.
2. Prefer fixed vendor packages and upstream wheels. If those remain unavailable, assess reproducible, hash-pinned builds of the affected native libraries and their Python consumers as one stack, including Fiona/GDAL, PROJ/pyproj and Python's own extensions. Replacing only Debian's SQLite or one shared-library filename leaves bundled copies unaddressed and does not establish ABI compatibility.
3. Retain Python 3.11 and Debian 12 for this phase, as directed by the project owner. Runtime/base upgrades are deferred. Prefer compatible vendor fixes; project-maintained backports would require a separate reviewed build and maintenance plan. Do not mix Debian suites or force-remove essential login/PAM packages.
4. Reinventory every native copy, rescan the resulting image, repeat native linkage and dependency-sensitive decoding/ZIP-code checks, compare both production models on CPU/CUDA and repeat Google/Azure workflows before official artifact qualification.

No unsupported binary swaps, dependency-policy exceptions, new base migration or additional full CUDA build were made for this follow-up. The 13 unaccepted assessment keys and release hold remain.

## Current-runtime applicability review

This follow-up reviews accepted main `a9a60901bc94d0061f4a2ea9b87f4b556551a6c5` and the same assessment image while retaining Python 3.11 and Debian 12. The 13 unaccepted CVE/package keys represent **10 distinct advisories**: PAM contributes four package keys for one advisory; the other nine advisories contribute one key each. The refreshed November 16 Debian tracker still lists all ten as open for Bookworm and lists the same package versions installed in the assessment. No fixed Bookworm vendor package was identified for these records. An open scanner record is distinct from confirmed exploitation through TowerScout.

| Advisory | Required behavior or input | Current evidence and disposition |
| --- | --- | --- |
| [CVE-2025-6020](https://github.com/linux-pam/linux-pam/security/advisories/GHSA-f9p8-gjr4-j9gx) (four PAM keys) | A PAM session uses `pam_namespace` with attacker-controlled paths. | The module exists, but the assessed `/etc/pam.d` files contain no active reference to it and `namespace.conf` has no active rules. TowerScout has no PAM authentication caller. The vulnerable module remains installed; record the inactive configuration as bounded mitigation evidence, not a package fix or permission to remove essential dependencies. |
| [CVE-2026-113351](https://security-tracker.debian.org/tracker/CVE-2026-113351) | XML parsing followed by parser reset leaves allocation accounting inconsistent. | Do not reject this match just because the library reports 2.5.0. Debian's backported allocation tracker is present in the source and binary, and the reviewed reset path lacks the offset adjustment described upstream. Python's separate embedded Expat 2.8.5 is also in the advisory's upstream range. No supported app-level parser-reset path was identified; retain the finding. |
| [CVE-2026-115506](https://security-tracker.debian.org/tracker/CVE-2026-115506) | An XML document uses DTD/entity expansion to consume excessive CPU before protection intervenes. | GDAL really imports `XML_Parse`. TowerScout's GIS reader uses a fixed packaged shapefile path, but GDAL metadata/sidecar processing means absence of a direct Python XML import is insufficient to dismiss the library. No arbitrary XML parsing endpoint was identified. Retain pending a compatible fix or a reviewed exposure decision covering both Expat copies. |
| [CVE-2026-117610](https://security-tracker.debian.org/tracker/CVE-2026-117610) | An external-entity subparser receives an empty non-final first chunk and later input. | No supported TowerScout caller configuring that subparser/chunk sequence was identified. This is a narrower precondition than ordinary image decoding; it does not establish that the installed library is fixed. Retain the finding. |
| [CVE-2026-118370](https://security-tracker.debian.org/tracker/CVE-2026-118370) | A multi-gigabyte XML start tag contains more than 2^30 attributes. | Default request and archive-member budgets are far below the described input size, and custom images require JPEG/PNG/TIFF signatures. These are partial controls: they do not universally bound third-party decompression, provider responses, optional metadata or files replaced outside the application. Retain the finding. |
| [CVE-2026-119373](https://security-tracker.debian.org/tracker/CVE-2026-119373) | A populated FTS5 `detail=none` table with negative rowids is queried using prefix `MATCH`. | All three assessed SQLite copies include FTS5; the patched Debian source contains the named merge function. No app route creates such tables or accepts arbitrary SQL/databases. That reduces supported-path exposure but is not a fixed-library claim. Retain the system key and track both bundled copies separately. |
| [CVE-2026-119374](https://security-tracker.debian.org/tracker/CVE-2026-119374) | Deleting from a corrupted FTS5 index invokes `fts5DoSecureDelete`. | Strong candidate for correcting the **system-package** match: the reviewed Debian source, including its patch series, contains neither the named function nor the secure-delete option, and the actual system library rejects that option. Fiona's older SQLite also rejected it, but pyproj's 3.46.1 accepted it. A correction for one copy would not resolve every copy or the other SQLite findings. Keep the gate entry pending authoritative clarification or an explicitly approved exact disposition. |
| [CVE-2026-119379](https://security-tracker.debian.org/tracker/CVE-2026-119379) | A crafted SQLite session changeset reaches `sqlite3changeset_apply`. | Session support exists in system SQLite and is absent in both assessed wheel copies. No app changeset ingestion/application route was identified. Retain the system key; do not describe the entire process as lacking session support. |
| [CVE-2026-76844](https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2026/76xxx/CVE-2026-76844.json) | The official CVE describes webpack-dev-middleware path traversal. | The Debian zlib mapping conflicts with that product identity and points to the separate zlib fix below. This is an advisory-data discrepancy, not an established second zlib defect. Keep the exact scanner record until corrected or specifically adjudicated; do not silently remap or suppress it. |
| [CVE-2026-85091](https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2026/85xxx/CVE-2026-85091.json) | A zlib `gz*` write fails and a later write reuses stale state; this installed pre-1.3.1.2 version additionally requires `gzclearerr`. | The native import review found OpenCV importing `gzputs`, so a blanket claim that no native gzip writer exists would be wrong. Its upstream caller is compressed `FileStorage` output; no TowerScout call to that OpenCV API or named `gzclearerr` import was found in the reviewed shared objects. Python/ZIP compression alone is not proof of this specific C API sequence. Retain the finding and the limitation that dynamic symbol lookup/static copies are not excluded by an import audit. |

### Evidence and limits of this review

- Read the official CVE records and refreshed Debian tracker. Source archives for the installed Expat, SQLite and zlib versions were downloaded from official Debian HTTPS mirrors and checked against their `.dsc` SHA-256/size records. This verifies the downloaded source-file checksums; it is not a claim of an independently verified Debian signing-key chain or a reproduced binary build.
- Processed all 70 Expat and 14 SQLite Debian patch-series entries in declared order, applying hunks for the relevant source file to isolated copies without rejected hunks. Hunks for other files were excluded; this is not a complete package rebuild. Expat's patched source retains the allocation tracker and resets accounting through `parserInit`; the assessed binary exposes the allocation-tracker API. SQLite's patched FTS5 index source contains zero references to the secure-delete function/option, and none of its Debian patches introduces them. No malformed XML, databases, changesets or vulnerability triggers were executed.
- Inspected PAM configuration and relevant undefined dynamic symbols in 506 non-symlink ELF shared objects under `/usr/local`, in a disposable, network-disabled, read-only container with no user volumes mounted. This is a defined shared-object subset, not a claim to have audited every executable, OS library, runtime `dlsym` call or statically linked copy. GDAL imports `XML_Parse`; GDAL/PROJ and Python import SQLite execution functions; OpenCV imports `gzputs`.
- Reviewed `ts_zipcode.py`, image validation, dataset restore and XML export. The ZIP-code reader uses the fixed packaged Census shapefile; its manifest also lists optional XML metadata, so metadata parsing must remain in scope. Dataset restore consumes JSON metadata and validated images and skips `.xml` members; XML export writes annotation text. File-signature and expansion limits reduce some input paths but are not a universal native-decoder security guarantee. Filesystem sessions are not SQLite session changesets.
- Re-ran the unchanged comparator against the retained November 16 scan: it still returns **BLOCK / exit 1**, with 13 blocking keys and zero severity increases. This is policy re-evaluation of existing evidence, not a fresh image scan or a clean build of accepted main. Baseline and residual-acceptance files are unchanged.

### Next decisions without a runtime upgrade

Prepare separate vendor clarification drafts for the zlib product-identity conflict and SQLite secure-delete lower bound; do not report the Debian Expat version as a false match. No third-party report has been sent. Keep those candidates distinct from the other findings with code/features present but no identified supported application trigger.

For actual fixes, prefer Bookworm vendor updates and compatible upstream wheels as they become available. Upstream security changes can potentially be backported while retaining Python 3.11/Bookworm, but that would create project-maintained native packages and require reproducible source/hash pinning, licensing records, an inventory of bundled copies, ABI/workflow tests and ongoing advisory ownership. No such custom packages are introduced here.

If a release is needed before compatible fixes exist, the project owner would need to consider each exact unresolved record with its evidence, limits, expiry and review triggers under the existing policy. This review does not request or grant blanket acceptance, add exceptions, clear publication, or authorize a release. Relevant changes to PAM configuration, GIS inputs/drivers/metadata, SQL/changeset paths, OpenCV persistence, gzip error recovery, native packages or deployment profile require renewed review.

## Proposed release dispositions: November 18, 2026

**Individual new dispositions remain a draft for project-owner review.** The owner subsequently set January 30, 2027 as the common expiry and renewed the existing eight util-linux exceptions to that date. No additional finding is accepted or publication authorized by that date instruction. Keep Python 3.11 and Debian 12. The proposal uses the current-runtime review above to define a route to a release decision with explicit conditions, instead of requiring every upstream scanner entry to disappear.

### Refreshed status

The November 18 [Debian tracker](https://security-tracker.debian.org/tracker/data/json) still lists the reviewed Bookworm PAM, Expat, SQLite and genuine zlib CVE-2026-85091 records as open, with the same relevant installed versions. No compatible Bookworm vendor fix was identified for those records. However, [CVE-2026-76844](https://security-tracker.debian.org/tracker/CVE-2026-76844) now says `NOT-FOR-US: webpack-dev-middleware` and no longer assigns the finding to zlib. Refreshing the scanner database and rescanning should test whether that correction has propagated. Do not carry it as a new risk exception simply to accommodate stale metadata.

None of the ten reviewed CVE identifiers appears in the retrieved [CISA KEV catalog](https://raw.githubusercontent.com/cisagov/kev-data/main/known_exploited_vulnerabilities.json), catalog version `2026.11.17`. KEV absence does not establish absence of exploitation or acceptable application risk. The recommendation also considers the actual input/configuration paths, code present, impact and remaining uncertainty. [FIRST's CVSS guidance](https://www.first.org/cvss/v4.0/user-guide#cvss-base-score-cvss-b-measures-severity-not-risk) explains why a base severity score alone does not establish deployment risk.

The retained scan still has 13 unaccepted package keys. The categories below cover exactly those 13 keys; they are proposed actions, not new scan results:

- Four PAM keys: recommend considering a short, scoped risk acceptance after final-image configuration verification.
- Seven keys: conditional acceptance candidates; retain blocking status until the specific evidence conditions below are satisfied and the owner approves each exact record.
- One SQLite key: candidate for an exact component-applicability disposition; further source/runtime confirmation and explicit adjudication are required.
- One zlib key: vendor metadata has been corrected; verify disappearance through an updated scan without adding an exception.

### Record-by-record proposal

All identities below are the retained scan's HIGH `os-pkgs` / `debian` keys. They apply only to the listed package/version combination. A different version, severity, package class/type, flavor, additional copy or changed input path requires review rather than an automatic match.

| CVE | Exact package and installed version | Proposed action | Reason and evidence required before activation |
| --- | --- | --- | --- |
| CVE-2025-6020 | `libpam-modules@1.5.2-6+deb12u2` | Scoped acceptance candidate | Namespace module is installed but inactive in the assessed image; no supported app PAM login path. Recheck all active PAM configuration/include paths and namespace rules in the final image (P1). |
| CVE-2025-6020 | `libpam-modules-bin@1.5.2-6+deb12u2` | Scoped acceptance candidate | Same PAM source advisory and inactive namespace configuration. Verify this exact binary-package identity and P1; do not infer that helper binaries are patched. |
| CVE-2025-6020 | `libpam-runtime@1.5.2-6+deb12u2` | Scoped acceptance candidate | Same source advisory; configured activation is the relevant boundary. Verify identity and P1; retain essential login/PAM dependencies. |
| CVE-2025-6020 | `libpam0g@1.5.2-6+deb12u2` | Scoped acceptance candidate | Same source advisory; no supported TowerScout PAM authentication caller was identified. Verify identity and P1. |
| CVE-2026-113351 | `libexpat1@2.5.0-1+deb12u5` | Conditional acceptance; block until E1 | Availability impact requires the affected parser/reset behavior. Backported code is present, so do not use the 2.5.0 label as a not-affected argument. Assess system and embedded Expat callers and reset behavior (E1). |
| CVE-2026-115506 | `libexpat1@2.5.0-1+deb12u5` | Conditional acceptance; block until E1 | Entity-expansion CPU exhaustion matters if attacker-controlled XML reaches a parser. Verify GIS metadata/sidecars and image/restore input paths, including embedded Expat; file-size limits alone are insufficient (E1). |
| CVE-2026-117610 | `libexpat1@2.5.0-1+deb12u5` | Conditional acceptance; block until E1 | Crash requires external-entity subparser creation and the described chunk sequence. Establish the supported caller boundary, including indirect/native callers, before accepting remaining uncertainty (E1). |
| CVE-2026-118370 | `libexpat1@2.5.0-1+deb12u5` | Conditional acceptance; block until E1 | Memory corruption deserves more scrutiny than a generic availability issue. Verify whether supported inputs can supply or expand into the oversized XML attribute input, beyond merely citing request-size limits. If that path is plausible and uncontrolled, keep blocking and pursue a fix/control (E1). |
| CVE-2026-119373 | `libsqlite3-0@3.40.1-2+deb12u2` | Conditional acceptance; block until S1 | FTS5 code is present. Confirm fixed application query/database inputs, database provenance and all three native copies; no arbitrary FTS table/population/query route may be assumed solely from a source grep (S1). |
| CVE-2026-119374 | `libsqlite3-0@3.40.1-2+deb12u2` | Exact applicability adjudication candidate; keep blocking | Patched Debian source and the runtime feature probe support absence of this secure-delete feature in the system copy. Reconfirm source/build identity and runtime behavior for the final image, with a normal FTS5 control. The pyproj copy supports the feature and needs its own S1 decision. Seek vendor clarification; no global CVE suppression or claim that all copies are unaffected. |
| CVE-2026-119379 | `libsqlite3-0@3.40.1-2+deb12u2` | Conditional acceptance; block until S1 | System SQLite has the session extension, but no application changeset input/apply route was identified. Confirm the final call/input inventory and compiled options; wheel-copy absence of session support does not clear the system copy (S1). |
| CVE-2026-76844 | `zlib1g@1:1.2.13.dfsg-1` | Updated-scan correction; no exception proposed | Debian now identifies webpack-dev-middleware rather than zlib. Refresh the vulnerability database and rescan the exact candidate. If the record persists, investigate the scanner data source; retain the discrepancy for explicit adjudication rather than silently ignoring it. |
| CVE-2026-85091 | `zlib1g@1:1.2.13.dfsg-1` | Conditional acceptance; block until Z1 | OpenCV imports `gzputs`; the affected pre-1.3.1.2 error/recovery sequence additionally requires `gzclearerr`. Review relevant native callers, compressed FileStorage output and error recovery in the final image, with explicit limits on dynamic/static call analysis (Z1). |

### Evidence conditions for any decision

P1, E1, S1 and Z1 are completion criteria, not claims that qualification is complete:

- **P1 - PAM configuration:** inventory package identities, active PAM services/includes, module activation, namespace rules and the supported authentication/deployment profile in each final image. Confirm no supported path activates `pam_namespace`. A new service/include or activation invalidates the proposed acceptance.
- **E1 - XML input and parser behavior:** inventory system/embedded Expat versions/features and their consumers; trace supported custom-image, restored-image and GIS metadata paths, including optional XML sidecars and indirect native decoding. Verify provenance/hash controls for packaged assets and representative benign metadata fixtures. Record whether attacker-controlled entity expansion, external subparsers, parser reset or oversized XML attributes can reach the named behavior. Passing benign workflows alone does not establish absence of a vulnerability. Any credible uncontrolled memory-corruption path remains blocking.
- **S1 - SQLite copies and inputs:** inventory system, Fiona and pyproj SQLite versions/features and the databases/queries they consume, including PROJ database provenance and relevant environment/configuration. Confirm the supported interface does not accept arbitrary SQL, SQLite databases, FTS configuration or session changesets. Repeat the benign feature/control probes on the exact final copies and assess pyproj's secure-delete capability separately. An OS-package disposition must not conceal an affected bundled copy, even if the scanner omits it.
- **Z1 - native gzip error path:** identify relevant gzip-write and error-recovery callers in the final native dependency closure and supported app paths. Recheck OpenCV's compressed FileStorage use and any `gzclearerr` sequence. Record gaps for static linkage and runtime symbol lookup. If a supported path can exercise the vulnerable sequence with uncontrolled state, keep it blocking until fixed or separately mitigated.
- **Artifact qualification:** obtain a clean candidate build from the approved source; record the exact local image ID and per-flavor inventory, perform a fresh complete scan with database timestamp, and bind decisions to the final artifact identity. Every flavor needs its own evidence; forcing CPU mode inside a CUDA image does not qualify a CPU image. Preserve the existing real-model, provider, export/restore, cancellation/restart and downloaded-package qualification requirements. This proposal waives none of them.

### Proposed scope, expiry and review ownership

The project owner remains the decision owner and TASK-107 review owner. On November 18, 2026, the owner set **January 30, 2027 at 23:59:59 UTC** as the common expiry, replacing the proposed December 18 date. Individual new exact risk acceptances and any temporary scanner/applicability disposition still require their evidence conditions and explicit approval; any approved decision would use that fixed January 30 deadline, with no automatic extension. A later approval does not move the deadline. Review at least weekly and immediately when relevant facts change. Reconfirm advisory/exploitation information at implementation and publication time.

Scope is the documented local, single-user Windows profile with loopback binding, verified TLS, approved model/asset provenance, existing upload/restore controls and the qualified engine/device configuration. A server/shared/network-exposed deployment, changed capabilities/mounts or broadened inputs is outside this proposed decision. The Linux libraries remain affected where their vulnerable code is present; risk acceptance must not be labelled remediation or guaranteed unreachability.

Remove or reconsider a decision immediately on a compatible fix, known-exploitation information, changed severity/identity/version, a new relevant caller/input, altered metadata/PAM/SQL/gzip handling, a control failure or a changed deployment profile. Fix and requalify when a suitable update becomes available. Expiry holds future publication; it does not disable installed copies.

The owner also explicitly renewed the eight existing util-linux exceptions through **January 30, 2027 at 23:59:59 UTC**, replacing their December 5 deadline. Their exact identities, versions, severity and flavor scope are unchanged. Weekly/immediate review and final-artifact qualification remain required; the date renewal is separate from deciding whether to accept additional findings.

### What would continue to block release

Keep the unchanged 396-key baseline and exact-match policy. Continue blocking on unreviewed/new HIGH or CRITICAL findings, changed identities/severities, incomplete or stale evidence, extra/unassessed native copies, unused or expired exceptions, failed input/control assumptions, and failed runtime/package qualification. A finding remains blocking where a credible supported attack path has unacceptable impact and the required evidence or mitigation is missing. Lack of a vendor fix and absence from KEV are insufficient reasons for automatic acceptance.

Under this proposal the seven conditional candidates remain blocking until their conditions and exact owner decisions are complete; they are not automatically accepted with the PAM records. The SQLite applicability candidate requires its own decision, and the corrected zlib record requires a fresh scan. Any new finding in that scan gets a new review. Even if all listed security dispositions are eventually valid, separate publication authorization and all standing qualification requirements still apply.

### Implementation sequence for owner review

1. Review the 13 rows and proposed decision criteria, using the owner's January 30 expiry instruction. The common date does not resolve the individual evidence/acceptance decisions or authorize publishing an image.
2. Build one candidate from approved main when disk headroom is adequate, or use a separately authorized remote candidate-build path. Keep the current installation, images and named volumes available for rollback. Keep publication and registry upload separate from a build-only action.
3. Refresh scanner data, scan/inventory that candidate and complete P1/E1/S1/Z1 for the relevant rows. Resolve the corrected zlib mapping and review all remaining/new findings and bundled copies. Stop on failed conditions instead of writing an exception to make the scan pass.
4. Present the exact per-record decisions and artifact evidence for explicit owner acceptance. Only then implement matching expiring policy entries or a reviewed component-specific adjudication mechanism with positive and negative gate tests. Preserve fail-closed behavior for changed, unknown, unused and expired entries; keep corrected/absent records out of the exception set.
5. Complete the remaining artifact/package qualification and obtain separate publication authorization. A passing source PR, approved proposal or security comparator alone does not qualify a release.

No image was built or rescanned for this November 18 work. Docker remained stopped; no volume/image deletion, public push, third-party report or release action was performed. The subsequent owner-authorized renewal changes only the active util-linux expiry and associated decision records; the comparator, baseline and other acceptance scope remain unchanged. The November 16 scan remains historical evidence with its original 13-key result; a refreshed scan may differ.

## Exact evidence identities

- Accepted main at start: `bce3e1bc49b0ba012961ccb3fb65d5afd1832c6b`.
- The reused application image identifies source `79422383e9e09dad301cf66ea659d30335fa7661`; its application tree matches the accepted merged main. The assessment retains that inherited label and is not advertised as a clean build of this branch.
- Guarded assessment inspected image: `sha256:19cacfbd2eecf5b79bb2f27fb133154804875e5fcdc8143c94c6bd5f04477ad2`.
- Guarded assessment scan SHA-256: `7fd41629d87eeb533acbf98375d3bd2e333116120c2239afb62920b4cfdc70dc`.
- Build helper SHA-256: `34c562e9bc87c51897f1a86ff4584da966ad6460946b0eec3b251bd5ae8753f0`.
- Raw and sanitized local evidence are retained by the maintainer; artifact identities do not authorize publication.
