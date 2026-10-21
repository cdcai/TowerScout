# PR #113 dependency correction before cdcai adoption

**Date:** October 21, 2026. **Owner:** TASK-104, coordinated with TASK-089/105.
**State at preparation:** local compatibility checks passed; the combined PR
must pass fresh remote checks and review before merge. Official artifacts are
not qualified by this record.

## Trigger and bounded correction

[PR #113](https://github.com/J-Schulein/TowerScout/pull/113) originally changed
only aiohttp 3.14.3 to 3.14.4. Dependabot alerts 77/78/79 identify 3.14.4 as
the fixed version for two High and one Low advisory. Update the exact-pin
test, retaining its security contract, and clarify the obsolete agent pin
instruction while preserving historical Task-099 evidence.

The corrected aiohttp head `6dd2a7c` passed both Python CI jobs, but the fresh
[security job](https://github.com/J-Schulein/TowerScout/actions/runs/39637315670/job/119351252515)
failed on Pillow 12.3.0: one Critical and six High findings. The reported keys
are CVE-2026-112403 (Critical), CVE-2026-112397, CVE-2026-112400,
CVE-2026-112404, CVE-2026-112895, CVE-2026-112896 and CVE-2026-112897.
The scanner identifies Pillow 13.0.0 as the fixed version for all seven.
This is a separate existing dependency exposed by the fresh scan, not evidence
that the aiohttp update introduced these Pillow vulnerabilities.

The follow-up commit pins Pillow 13.0.0 and aligns the YOLO runtime minimum
and its two existing test contracts. No image-processing algorithm, model
weight, threshold, torch/torchvision pin, security exception or baseline changes.
The [Pillow release notes](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html)
describe security fixes and API removals. Python 3.10 is dropped; the project's
maintained CI/runtime Python 3.11 and 3.12 remain supported. Inspect the actual
resolved dependency inventories in the new images, including bundled libraries.

## Checks and limits

- Windows Python 3.12, isolated aiohttp 3.14.4 with resolved dependencies:
  21 provider, timeout, cancellation, redirect, retry and redaction checks pass.
  Verified dependency constraints, including yarl 1.25.1. An earlier overlay
  against the existing yarl 1.24.5 was superseded by this resolved-set run.
- Isolated Pillow 13.0.0 plus the resolved aiohttp set: 68 maintained upload,
  allocation/admission, provider, local-loader and classifier contracts pass.
  Local torch/torchvision are 2.6.0+cpu/0.21.0+cpu; these results are bounded
  compatibility evidence, not validation of the ADR-022 pair or real models.
- Remote CI installs torch 2.10.0/torchvision 0.25.0 on Python 3.11 and 3.12.
  Require fresh results at the combined PR head. Pytest model loading is mocked.
- Initial sandbox attempts could not load the isolated dependency or access
  the default temporary directory. The successful runs asserted imported
  versions and used isolated dependencies/test-owned temporary paths. No
  existing application environment was upgraded.
- The full-image CI job intentionally runs on main only. Its skipped PR
  status is expected. Advisory checks remain advisory; the blocking security
  gate remains unchanged and must pass.

## Adoption and release implications

Do not merge while a required check fails. Record the final head and completed
checks, then the accepted main identity and post-merge results. Integrate into
the adoption branch with an explicit conflict review; the adoption guidance
already replaced the historical agent-instruction block edited here.

The prior adoption review's unchanged-runtime-dependency statement describes
its earlier checkpoint only. The refreshed delta must include aiohttp, its
resolved transitive dependencies, Pillow and the minimum-version guard. Repeat
affected source checks and official-image security scans, actual image decode/
crop/RGB/resize, both model/device paths, Google/Azure downloads, cancellation/
retry and recovery under the official qualification plan.

Preserve immutable RC5 bytes and the five exact ADR-024 residuals and expiry.
Neither successful PR CI nor this patch qualifies new official packages or
authorizes publication/Latest. No cdcai changes are part of this correction.
