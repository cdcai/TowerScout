# `rc4` Browser-Download Diagnostic - 2026-10-02

**Label**: `rc4 preliminary browser-download diagnostic`
**Result**: `PASS` for the bounded first-host Docker CPU subset described here
**Acceptance boundary**: Diagnostic only. This is not final release acceptance,
an independent-host result, or evidence for documentation-aligned artifact
bytes that do not yet exist.

## Purpose

Run the already-qualified `rc4` package through the standard GitHub browser
download, Windows File Explorer extraction, supplied wrapper, setup, live
provider workflow, and volume-preserving relaunch path before Task-092 content
is frozen. The intent was to expose a larger package/runtime problem early,
not to qualify the pre-ADR-023 manuals as final documentation.

## Bound Identities

- Accepted source:
  `541622556fb7999ee4e88fb1e44f7797b9da34f5`.
- Draft release tag: `v0.1.3-rc4`.
- Draft release record:
  <https://github.com/J-Schulein/TowerScout/releases/tag/untagged-8a104f8f8289c55b3b59>.
- Draft state at the end of the run: `isDraft=true`, `isPrerelease=false`,
  target commit equal to the accepted source. The record is not a public
  release and was used only as an authenticated browser-accessible staging
  location.
- CPU control ZIP: `towerscout-v0.1.3-rc4-cpu.zip`, 185080 bytes, SHA-256
  `1cf763b6184bb96dfe976f41f56a4aa5b8eeeea51a8de59830a9bf7fb9784a55`.
- CUDA control ZIP: `towerscout-v0.1.3-rc4-cuda128.zip`, 185097 bytes, SHA-256
  `02ec76b93bea28417b7ea4b086f23148b57b34c33823ce2f113da7147165915f`.
- Shared asset ZIP:
  `towerscout-v0.1.3-rc4-assets-towerscout-v1-assets-2026-05-05.zip`,
  800655295 bytes, SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- CPU image digest:
  `sha256:a3eeb77152577f3656a286777bd4c4312cecc311cb5a5cc1b132b459f1ecd18f`.
- Safe committed fixture SHA-256:
  `fd6771ed3aa30a44c5bedb7575ed7f164896e496292fae29ac1da4bb9638d715`.
- Sanitized runner SHA-256:
  `0ee0a785cf90bbf96dad45451dd5d00c34368d809a6ff207ab9670b37359070d`.

All six uploaded assets were downloaded through the normal GitHub browser
flow. GitHub's server-side sizes/digests, downloaded ZIP hashes, downloaded
sidecar contents, and frozen local originals agreed. The three downloaded ZIPs
and their sidecars carried Windows downloaded-file markers.

## Standard Windows Path

- The signed-in user downloaded the six assets with the default browser.
- File Explorer extracted the CPU package to a user-writable path containing
  spaces: `<Downloads>\TowerScout rc4 Browser Diagnostic\RC4 Browser CPU
  20261002`.
- Download-marker propagation was present on representative extracted control
  files, including `setup-towerscout.cmd`, `start.bat`, `compose.yaml`,
  `IMAGE.txt`, `release-manifest.v1.json`, and `SHA256SUMS.txt`.
- The wrapper ran under the ordinary signed-in user; the process was not
  elevated to the local Administrators role.
- The supported process-scoped wrapper was used. No persistent execution
  policy, endpoint-protection setting, or security control was weakened.
- No SmartScreen, EDR, WDAC, AppLocker, or organization-policy outcome was
  captured. This run therefore makes no compatibility claim for endpoints that
  require trusted signing or organization-specific allowlisting.

## Setup And Runtime Result

The CPU setup wrapper was given the exact downloaded CPU and asset ZIP paths
and launched Docker on `127.0.0.1:5000` with GPU mode off. The target project
had no pre-existing container or volume.

Observed result:

- Setup exited `0` after verifying both outer hashes, staging/importing the
  assets, creating configuration, and verifying the imported files in full.
- Initial readiness correctly reported `setup_required`; after the owner
  entered an Azure key privately through Setup Wizard, readiness became
  `ready` with Azure configured, Google unconfigured, and Azure selected as
  default. No credential value was read or retained.
- Health was `ok`, assets/config were `ok`, the Docker engine and CPU policy
  were reported correctly, and the selected device plus PyTorch flavor were
  both CPU.
- The reported digest and independently inspected container image ID both
  matched the bound CPU digest.
- The container was healthy and exposed only `127.0.0.1:5000`.
- Exactly eight fresh named volumes were mounted for cache, config, data,
  Flask session, logs, model parameters, session temporary data, and uploads.
- In-app Help at `/docs/` returned HTTP 200. Its content is the pre-ADR-023
  `rc4` documentation and is not the final documentation surface.

## Bounded Live Azure Workflow

| Check | Safe observation | Result |
| --- | --- | --- |
| Provider initialization | Settled, fully initialized Azure provider | `PASS` |
| Estimate | HTTP 200; one tile | `PASS` |
| Controlled recoverable error | Empty estimate returned HTTP 400 | `PASS` |
| Immediate next request | Real request returned HTTP 200 in the same browser session | `PASS` |
| Detection and review | 14 detections; 14 selected/listed; detection and tile navigation available | `PASS` |
| Dataset export | HTTP 200; nonempty ZIP with a valid ZIP signature and 14 selected inputs | `PASS` |
| Browser errors/evidence hygiene | Zero page errors; no sensitive artifacts retained | `PASS` |

Cancellation was not repeated in this bounded diagnostic because doing so with
the stock harness would retain unnecessarily sensitive browser artifacts. The
same exact `rc4` identities already have sanitized four-profile cancellation
and immediate-next-request evidence in the W10 index; that earlier evidence is
not represented as a new browser-download result here.

## Stop/Relaunch Persistence

The extracted package's own `scripts\stop.cmd -Engine docker` removed its
container and network without deleting volumes. All eight named volumes
remained. The package's `start.bat -Engine docker -Gpu off -Port 5000
-NoBrowser -TimeoutSeconds 180` then returned `ready`.

Independent post-relaunch inspection confirmed:

- health/readiness `ok`/`ready` and assets/config `ok`;
- Azure still configured and selected by default, with Google unconfigured;
- the exact CPU image digest and healthy container state;
- CPU device policy/selection and CPU PyTorch flavor;
- loopback-only port binding;
- the same eight named volume mounts; and
- HTTP 200 from in-app Help.

## Findings And Task-092 Disposition

| Finding | Disposition |
| --- | --- |
| No larger blocker appeared in the tested browser-download, hash, File Explorer extraction, ordinary-user wrapper, Docker CPU setup, Azure detection/export, or stop/relaunch path. | Continue Task-092 implementation; do not change the runtime design solely because of this diagnostic. |
| The control ZIP and large asset ZIP can be downloaded to one directory while the control ZIP is extracted into a nested spaced directory. Explicit quoted `-PackageZip` and `-AssetZip` paths worked. | Make the default co-location path and the explicit-path alternative unmistakable in packaged, Wiki, and demo instructions. |
| All download bytes and sidecars agreed, and Windows download markers were preserved. | Put authoritative release-page SHA-256 comparison before extraction; show a copyable Windows command and the expected comparison outcome. |
| The unsigned process-scoped wrapper worked for this permitted host. No managed signing-policy result was observed. | State the ADR-023 boundary near the first launch step. Never advise disabling protection or changing persistent execution policy; direct blocked users to Local IT. |
| Setup correctly paused for private provider configuration, then reached `ready`. | Explain `setup_required` versus `ready`, private browser entry of provider keys, and the safe readiness checks without exposing `.env` or key previews. |
| Package stop/start preserved provider settings, assets, and all eight volumes. | Document normal stop/relaunch and distinguish it from destructive volume removal or reset. |
| In-app Help was reachable but contains the older `rc4` manuals. | Update paired Markdown/HTML and in-app Help before rebuilding; assign new CPU/CUDA image and control-ZIP identities and repeat affected gates. |
| The draft release required an authenticated repository session. | Final acceptance still needs the public release record, authoritative hashes, and link/download verification without a privileged session. |
| In-app browser automation was unavailable, but the user's normal browser download succeeded. | Treat this as test-tool availability, not a TowerScout product finding. Keep the manual browser action explicit in the final test sheet. |

## Explicitly Open

- Documentation-aligned CPU/CUDA images and control ZIPs have not been built.
- Final exact-byte browser download and public unauthenticated link/hash checks
  have not run.
- CUDA, Podman, Google, cancellation, and reboot were not repeated in this
  bounded browser-download diagnostic; their local `rc4` regression evidence
  remains in the W09/W10 records.
- Independent-host Docker/Podman CPU/NVIDIA reproduction remains blocked on an
  independent suitable Windows computer.
- The draft release remains non-public; no `latest` tag was promoted.

## Evidence Hygiene And Preservation

The workflow summary contains only provider labels, HTTP status codes, counts,
booleans, artifact identities, and coarse runtime state. It excludes provider
keys, `.env` contents, AOI coordinates, provider URLs, request/response bodies,
console text, screenshots, and raw browser traces. The runner removed its
temporary export directory and reported `sensitiveArtifactsRetained=false`.
The diagnostic container and all eight volumes are retained until Task-092
reconciliation and the final candidate handoff no longer require them.
