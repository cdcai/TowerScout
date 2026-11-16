# November 16, 2026 local dependency assessment

## Result

Publication remains blocked. The existing local search-test image failed the unchanged 396-key baseline and its then-current exceptions with 72 unaccepted HIGH CVE/package keys. Small local assessment layers updating only pip and apt reduced that count to 69. No exception was added or renewed, and no baseline identity was broadened.

| Stage | HIGH/CRITICAL CVE/package keys | Accepted baseline keys | Accepted residual keys | Blocking keys |
| --- | ---: | ---: | ---: | ---: |
| Existing image | 132 | 50 | 10 | 72 |
| pip 26.3 and apt/libapt 2.6.2 assessment | 126 | 49 | 8 | 69 |

These are scanner CVE/package keys, not counts of distinct underlying vulnerabilities. Both reports used Trivy 0.69.3 with the same freshly downloaded database. The change introduced no new keys or severity escalations. The gate returned failure for the final assessment, as required.

## Changes assessed

- Replace the official hash-verified pip 26.2.2 wheel with pip 26.3. Its private urllib3 is 2.8.0 and msgpack is 1.2.4; the application's urllib3 remains 2.8.0.
- Update the base image's existing apt and libapt-pkg6.0 packages from 2.6.1 to Debian's signed 2.6.2 security packages. Preserve all other explicit runtime pins and inference settings.
- Remove only the two pip-private urllib3 exceptions. Preserve the eight exact util-linux exceptions and their December 5, 2026 deadline.
- Require the fixed pip/module/SBOM/notice inventory in current images; retain explicitly selected historical inventory validation only for historical residual-gate regression coverage.

The six resolved keys were CVE-2026-97687 and CVE-2026-97689 on urllib3; CVE-2026-114613 and GHSA-6v7p-g79w-8964 on msgpack; and CVE-2026-109518 on apt and libapt-pkg6.0.

## Remaining blockers

| Debian source group | Unaccepted CVE/package keys | Distinct CVE IDs within group |
| --- | ---: | ---: |
| krb5: four installed library packages | 56 | 14 |
| pam: four installed packages | 4 | 1 |
| expat: libexpat1 | 4 | 4 |
| sqlite3: libsqlite3-0 | 3 | 3 |
| zlib: zlib1g | 2 | 2 |

A fresh package-index query in an isolated Debian 12 container found no newer candidate for representative installed packages in these five groups. The scan lists no fixed Debian version for these remaining keys. That is evidence of the available repository state, not a claim that the code is unreachable or safe. Do not suppress these findings, copy packages from another Debian suite, or extend acceptance dates to pass the gate.

Next, reassess supported vendor updates or an isolated base-image migration against the full current scan. Backporting and any new bounded risk decision require separate technical review; only the owner can approve new acceptance. Preserve the release hold until a valid disposition and affected artifact qualification are complete.

## Artifact identities

The security branch starts from accepted main `5ea89807bcc71c397522679a66dcddc0c9bae977`. The reused application layers identify search-test source `79422383e9e09dad301cf66ea659d30335fa7661`; they do not identify the security branch as their clean build source.

| Local artifact | Inspected image identity |
| --- | --- |
| Existing image | `sha256:7e60a53e8fc01619ec71cf8b1c4b7be6921c9faf9a86751ab43f2ef665a88805` |
| pip-only assessment | `sha256:3f16543c0244f4a29959b45dd7d445e69fac1be4f4acffeeef04d1bd4f49bc3a` |
| Combined assessment | `sha256:6ed09078c6a916ea1c1e22ec5910f77f353d955682a51933f4609ce4886b3e0d` |

Database updated at `2026-11-16T13:03:44.830426244Z` and downloaded at `2026-11-16T15:08:04.0289753Z` (UTC). Subsequent paired scans disabled database updates. Raw report SHA-256 identities:

- `before-trivy.json`: `5c047566e42723055d487fdd1bea8b2a90aae0ee1e784b30ffa970f2c6ee30b2`
- `after-trivy.json`: `bb62a034b6d07dcdfc31b5ac30836b609b94f04f0e46c40fc55dcf55b457eba9`
- `final-trivy.json`: `2fd0a4b4850d2b208f4275bb0653d52a9f617793d399b2fc222613dc016f361e`

## Evidence and limits

A real downloaded, hash-verified pip wheel was inspected and the updated bootstrap executed in an isolated environment. Exact-image inventories confirmed the old and new private urllib3 versions. The combined assessment passed pip dependency consistency and both production model loaders/inference probes on forced CPU and CUDA, including device and output checks. All 106 focused bootstrap, inventory, gate, container-workflow and runtime-contract tests passed.

The assessment inherited the tested application's layers and added small dependency layers. It is not a clean rebuild from the security branch, a downloaded release, a separate CPU-flavor image, or a new Podman/second-host qualification. Its inherited application source revision remains the search-test revision; assessment images must not be published as releases. Official rebuilt CPU/CUDA images require fresh exact-identity scans, inventories, notices/SBOMs and affected runtime checks before release authorization. The earlier application workflow results remain evidence for the original search-test image only.

Raw scans, logs, local paths, model files and private evidence are retained outside commits. This report authorizes no publication, promotion, merge or additional risk acceptance.
