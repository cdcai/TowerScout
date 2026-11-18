# Dependency security disposition

The release gate retains the accepted 396-key baseline and eight exact time-limited HIGH util-linux residual identities. The authoritative machine-readable package identities, versions, CPU/CUDA scope and expiry are in `.github/security/task103-accepted-residuals.v1.json` in corresponding source. On November 18, 2026, the owner renewed those same eight records through January 30, 2027 at 23:59:59 UTC, replacing the December 5 deadline. Package identities and acceptance scope remain unchanged.

## Resolved pip findings and inventory boundary

The hash-verified bootstrap now selects the official pip 26.3 wheel, whose private urllib3 is 2.8.0. This addresses CVE-2026-97687 and CVE-2026-97689 in pip's old private urllib3 2.7.0; the two pip exceptions are removed. The application's separately installed urllib3 remains 2.8.0. Pip 26.3 also updates its private msgpack beyond the 1.2.3 fix for CVE-2026-114613.

The exact-image inventory requires pip 26.3, application and private urllib3 module versions 2.8.0, matching distribution metadata and embedded SBOM, the expected license notice, and no extra copies. Historical residual-comparison code can validate only the separately selected exact pip 26.2.2/urllib3 2.7.0 inventory; a fixed inventory cannot justify an old exception. The committed policy no longer accepts either pip finding. Old images therefore fail under the updated policy.

The application does not invoke pip at runtime, and automatic model dependency installation remains disabled. Pip is still used for controlled dependency downloads during builds/installations. Retain normal TLS verification and the mandatory wheel hash; do not edit pip's private files manually to suppress findings. The real downloaded wheel and bootstrap have been exercised locally, but rebuilt official CPU/CUDA artifacts still require their own exact-image checks and qualification.

Runtime `apt` and `libapt-pkg6.0` are additionally pinned to Debian's 2.6.2 security update for CVE-2026-109518. These updates do not authorize other exceptions or change the baseline.

The runtime pins Debian `openssl` and `libssl3` to `3.0.22-1~deb12u2`, fixing CVE-2026-84782; their two exceptions are removed. This updates system OpenSSL, not separately bundled wheel copies. The earlier fixed `libexpat1@2.5.0-1+deb12u5` remains outside the residual policy.

The runtime also pins torch's `filelock` dependency to 4.2.1, fixing CVE-2026-112940. The affected SQLite-backed reader/writer-lock path requires attacker-controlled local filesystem entries; no exception is accepted. Final-image inventories, fresh scans and affected runtime checks must establish the actual fixed packages in both flavors. See the [filelock advisory](https://github.com/tox-dev/filelock/security/advisories/GHSA-v4x8-3wr5-3wq8).

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

On November 2, 2026, the project owner explicitly renewed these same eight identities through **2026-12-05T23:59:59Z**, replacing the original November 5 deadline while awaiting vendor fixes. The same-day [Debian advisory review](https://security-tracker.debian.org/tracker/CVE-2026-53615) still found the accepted Bookworm version vulnerable with no listed Bookworm fix. Static source review found no supported disk-probing caller, privileged mode, SYS_ADMIN capability or raw-block-device mapping in the standard profiles; GPU mappings remain present. This is continued temporary risk acceptance with evidence limits: fresh exact-digest scans, filesystem inventories and live exposure revalidation were not performed for this renewal and remain required before publication. The existing package identities, severity, CPU/CUDA scope, controls and 396-key baseline remain unchanged. No remediation or fresh runtime qualification is claimed.

On November 18, 2026, the project owner explicitly renewed the same eight exact records through **2027-01-30T23:59:59Z**, superseding the December 5 deadline above. The refreshed [Debian advisory](https://security-tracker.debian.org/tracker/CVE-2026-53615) still lists the reviewed Bookworm version as vulnerable with no listed Bookworm fix. Static source and standard Compose-profile review again found no supported disk-partition probing caller, raw-block-device mapping, privileged mode or SYS_ADMIN grant; GPU mappings remain present. This renewal changes the expiry and records the owner's decision; it does not claim a fresh scan, a live exposure test, a fix or release qualification. Fresh exact-image scans, inventories and live exposure revalidation remain publication prerequisites.

The project owner owns TASK-107 weekly review and immediate review on a vendor fix, severity/identity change, new disk-probing caller, raw-device exposure, privileged/capability change or failed gate. Remove these entries when fixed and repeat affected qualification. The January 30 exception expiry and January 31 Torch bridge review are separate requirements; no automatic extension applies. Publication still requires separate authorization and final-artifact qualification.

An isolated Debian 13 CPU assessment removed that CVE and the OpenSSL residuals, but introduced eight unaccepted records for four other util-linux CVEs on `login` and `liblastlog2-2`. Debian protects `login`, and essential util-linux requires liblastlog2-2. The assessment is not adopted; do not force-remove required packages, mix Debian suites, or broaden the baseline. The approved short exception applies only to the retained Debian 12 identities; none of the Debian 13 findings is accepted.

Primary review sources: [Debian util-linux finding](https://security-tracker.debian.org/tracker/CVE-2026-53615), [Debian OpenSSL status](https://security-tracker.debian.org/tracker/CVE-2026-84782), [urllib3 proxy advisory](https://github.com/urllib3/urllib3/security/advisories/GHSA-8988-9cw3-xx77), [urllib3 response advisory](https://github.com/urllib3/urllib3/security/advisories/GHSA-vxq7-64xx-v4gw), and [pip's fixed vendored versions](https://github.com/pypa/pip/blob/26.3/src/pip/_vendor/vendor.txt).

## November 16 local assessment

The available pip and apt updates resolve six HIGH scanner keys in a small local CUDA assessment, but 69 unaccepted keys remain and the publication gate fails. See the [assessment and remaining blocker register](2026-11-16-local-assessment.md) for counts, package groups, validation limits and follow-up. No new risk acceptance or release qualification is claimed.

## Runtime exposure follow-up

The [guarded NIS omission assessment](2026-11-16-runtime-exposure.md) removes 56 HIGH scanner keys in a small local assessment, leaving 13 unaccepted keys. No exception is added and no baseline key is broadened. The dedicated image intentionally omits the optional Unix NIS module and its reviewed non-essential package chain; it retains Expat, SQLite, PAM and compression support. Bundled native copies, an advisory-data mismatch and final-artifact qualification remain open.

The [current-runtime applicability review](2026-11-16-runtime-exposure.md#current-runtime-applicability-review) retains Python 3.11 and Debian 12 as directed by the project owner. It separates 13 package keys into ten advisories, records inactive PAM namespace configuration, validates the backported Expat allocation tracker, and strengthens the SQLite secure-delete mapping question with patched Debian source evidence. The November 18 refresh below supersedes the November 16 zlib mapping status. No match is suppressed, no acceptance is added, and publication remains blocked.

## Proposed decisions, pending owner review

The [November 18 release-disposition proposal](2026-11-16-runtime-exposure.md#proposed-release-dispositions-november-18-2026) recommends considering four exact PAM acceptance candidates, retaining seven conditional candidates as blocking pending focused final-artifact evidence, and separately adjudicating the system SQLite secure-delete match. Debian has corrected the erroneous zlib CVE-2026-76844 mapping; verify its disappearance with updated scanner data rather than adding an exception. The owner has set **January 30, 2027 at 23:59:59 UTC** as the expiry for any newly approved decisions, replacing the proposal's December 18 date and aligning it with the renewed util-linux deadline. This date instruction leaves individual new findings' evidence and acceptance decisions pending. No new exception is activated; publication holds and qualification requirements remain in force.

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
and proposes remediation. Publication uses explicit owner authorization and automated
source/security gates; an environment reviewer is not required. Assignment of named receiving custodians and a durable evidence copy is
still required at handoff, without publishing private approval correspondence.

| Obligation | Due/trigger | Required evidence and disposition |
| --- | --- | --- |
| Eight exact util-linux identities | Weekly and immediately on the changes listed above; hard expiry 2027-01-30T23:59:59Z | Owner renewed November 18 after the scoped advisory/static review. Fresh exact-digest scans, installed identities and exposure revalidation remain required; remove fixed entries and requalify. No automatic extension. |
| New/changed/unused/expired findings | Every build and publication verification | Fail closed against the unchanged 396-key baseline and exact residual policy at `.github/security/task103-accepted-residuals.v1.json` in the corresponding source identified by `SOURCE.txt`. The control ZIP does not include `.github/`. |
| Corresponding source and evidence custody | Before artifact publication/handoff | Final-version recursive source, build/relink inputs, notices and SBOMs; checksum-verified receiving-held evidence copy. Retain commit-addressed fork records and their evidence ref. |
| Receiving publication controls | Before authoritative publication; promotion before stable/Latest | Main-only release environment without mandatory reviewer approval, approved source/ref, scoped package-write permissions and exact qualified-digest promotion. |

Record each review date, source/image identities, evidence location, outcome and
next review in the receiving maintainer's approved record. Source adoption alone
does not execute any settings change, publish a new tracker or accept a finding.
The About description/homepage correction remains a separate unexecuted action.
