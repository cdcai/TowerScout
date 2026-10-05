# Task-092 Round 2 Documentation Review Disposition

- **Date**: 2026-10-05
- **Review source**: `TowerScout-Round-2-Documentation-and-PR94-Review.md`
- **Review SHA-256**: `d62e3bceaed6a33bf278fff521369a7d4be1248705567f99d2ffd59037b73e6f`
- **Reviewed repository source**: `a87008c3036e80785610ee7e8675c51ea5b07704`
- **1440 px evidence SHA-256**: `331365c84a5705f5c3aec83f4e74ff4073fb3419a486b29cf3d5a359ca665af8`
- **720 px evidence SHA-256**: `8823a5ab3e4ac96387dbbcd5c077c0087cd06b7db80715318aab7719a0171e37`

## Authority Boundary

The report and screenshots are review evidence, not repository instructions or
release approval. Project instructions, accepted decisions, source behavior,
and current first-party vendor documentation remain authoritative. No provider
credential was inspected, inferred, or recorded while resolving the findings.

## Disposition

| Finding | Disposition | Implemented result |
| --- | --- | --- |
| R2-01 | Accepted; pre-rebuild blocker | Setup cards use a content-aware single-column layout where needed. A Puppeteer/Edge regression now checks the complete four commands at 1440 px and 720 px, including the `-Gpu` endings and absence of horizontal scrolling. |
| R2-02 | Accepted; pre-rebuild blocker | Maintained Quick Start now links the Podman GPU guide, places the package-local CDI helper after extraction, documents the limited `.ps1` exception, and requires `selected_device=cuda` in addition to general readiness. Markdown and HTML parity is regression-tested. |
| R2-03 | Accepted; pre-rebuild blocker | Every engine guide opens PowerShell in the four-download folder before relative hash commands. Package-local Podman provider/CDI helpers occur only after verified extraction and after opening the extracted package folder. |
| R2-04 | Accepted; pre-rebuild blocker | Package verification covers CPU and CUDA variants in both PowerShell and `certutil` alternatives. Fixed examples are labeled Docker CPU and instruct readers to retain their selected engine/GPU. Port guidance lists only setup, start, status, browser, and applicable TLS commands; stop/log commands are excluded. |
| R2-05 | Accepted; pre-rebuild blocker | Start/reopen, status, and stop are separate tasks and command blocks in the Wiki, Quick Start, and User Guide. Podman machine startup is conditional on its recorded machine being stopped. |
| R2-06 | Accepted; pre-rebuild blocker | Wiki and Local IT material link directly to the Package Guide procedure. That procedure is divided into `Diagnostic Only`, `Review And Obtain Approval`, and `Apply The Approved Change`, while preserving the selected configuration. |
| R2-07 | Accepted; pre-rebuild blocker | Source inspection identifies Maps JavaScript API, Places API (New), Maps Static API, and Geocoding API. First-party Google guidance confirms that one key cannot simultaneously carry Websites and IP-address application restrictions. Because TowerScout accepts one Google key for browser and server requests, the compatible current setting is API-restricted to those four services with `Application restrictions: None`. This is explicitly documented as a TowerScout limitation, not Google's preferred design. Sites requiring an application restriction must stop or use Azure Maps. |
| R2-08 | Accepted; pre-rebuild blocker | Remaining project-support permission language and first-cohort/tester examples were removed from current end-user surfaces. Podman depends on local permission and documented prerequisites, not project assignment. |
| R2-09 | Accepted; publication improvement | Wiki navigation now routes setup choice to credentials, then installation, while retaining a labeled shortcut for readers with a suitable credential. Engine-guide web destinations are descriptive links. |
| R2-10 | Accepted; publication improvement | Conditions precede Podman-machine creation, unsigned-package action, and export actions. The Podman Wiki received the same ordering correction. |
| R2-11 | Accepted; publication improvement | WSL 2, GHCR, rootless, Compose provider, CDI, and named volumes receive plain-language definitions. First search instructions specify metres, provider-specific polygon completion, and an illustrative 1–6 tile target. |
| R2-12 | Accepted; publication improvement | Tests now cover working-folder order, exact Google/Podman GPU parity, both package variants, configuration preservation, TLS phase separation, task-separated commands, warning order, and missing assignment/pilot phrases. A real-browser layout regression checks both requested widths. |

## Google Restriction Basis

TowerScout's browser loads the Maps JavaScript API with the Places library and
uses `PlaceAutocompleteElement`; its local application service also calls the
Maps Static and Geocoding web services. Google recommends separate keys when
client and server calls need different application-restriction types, but the
current TowerScout settings model has one Google credential field. Therefore:

- API restriction to the four used APIs is supported and required by the
  instructions.
- A Websites-only key cannot cover the local server requests.
- An IP-address-only key cannot cover the browser requests.
- `Application restrictions: None` is the functional one-key boundary for
  this release, accompanied by a dedicated project, quotas, alerts,
  monitoring, and rotation.
- Supporting separately restricted Google browser/server keys is future
  product work, not a documentation-only change.

First-party references:

- <https://developers.google.com/maps/api-security-best-practices>
- <https://developers.google.com/maps/documentation/javascript/place-autocomplete-new>
- <https://developers.google.com/maps/faq>

## Verification State

All 105 focused documentation, ADR-023, package, asset-import, and Flask-route
tests pass using a clean host temporary directory. The documentation
command/path checker, agent-work validator, stale-language scan, and diff
hygiene check pass. The new browser regression passes at both 1440 px and 720
px in installed Microsoft Edge. Link/render and bundle-identity checks run as
part of the source-bound Round 3 bundle build. Human Round 3 review remains
open, so documentation content is not frozen and no release image or control
package is rebuilt by this disposition.
