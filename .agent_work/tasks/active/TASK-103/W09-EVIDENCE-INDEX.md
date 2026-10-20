# Task-103 W09 Candidate Evidence Index

## Current interpretation - October 20, 2026

This index retains the previously local RC9-era record below in full.
Its results concern the exact historical artifacts named there, not new
official cdcai bytes. No runtime tests or security scans were repeated during
this reconciliation.

The current accepted fork candidate is `v0.1.3-rc5`, governed by
[ADR-026](../../../decisions/026-rc5-bounded-candidate-acceptance.md) and the
[RC5 closeout](../TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md).
[ADR-025](../../../decisions/025-two-host-final-candidate-qualification.md)
replaced the earlier CPU-only/Podman-without-Docker allocation with two
Windows NVIDIA hosts; the excluded environments remain unqualified.

Below, phrases such as "current candidate", "still open", "remaining", and
"required" describe the historical checkpoint date. They are not today's
release requirements or publication status. RC9 independent-host findings
led to TASK-105 corrections and subsequent RC5 acceptance; do not reopen
resolved items solely because their earlier status is retained here.

## Historical evidence snapshot - retained from local working copy

**Recorded**: 2026-09-28; updated 2026-10-13
**Verdict**: Same-source RC9 CPU/CUDA registry and package qualification PASS;
exact-digest W05 PASS; all four exact browser-downloaded RC9 first-host
profiles PASS, and RC9 Docker/Podman reboot persistence PASS. The local `rc4`
four-profile and reboot matrix remains valid regression evidence, but overall
release readiness remains AT_RISK pending independent-host repetition.
ADR-023 resolves policy/signing through an unsigned, narrower support boundary.
**Publication state**: The RC9 control ZIPs, shared asset ZIP, and all three
sidecars are published in non-draft GitHub prerelease `v0.1.0-rc9`. GitHub's
recorded sizes/digests match the approved local files, and the tag resolves to
the frozen source. Stable `v0.1.2` remains Latest, and no GHCR image `latest`
tag was promoted.

**Superseded RC8/RC4/RC3 context**: RC8 reproduced the Podman CPU
pre-registration cancellation race and is retained only as defect evidence.
PR #92 (`cbb574f`) and PR #93 (`fba9dcb`)
merged after the retained `rc3` artifacts were assembled. That produced the
now-superseded `rc4` candidate from accepted `main` at
`541622556fb7999ee4e88fb1e44f7797b9da34f5`. The `rc4` and `rc3` identities
remain historical regression/qualification evidence only; they are not
publication inputs. The RC9 inventory below is the sole current candidate.

## Same-Source RC9 Candidate Inventory

The current source is
`b3431cf86d8a000462df487685104558ac7becd3`. Owner-authorized CPU run
`37942033212` and CUDA 12.8 run `37942073914` qualified:

- CPU image:
  `ghcr.io/j-schulein/towerscout@sha256:9d24cc71724953fba7e062b6ee71dac38f2ec413716a9b60bfaf8ad0be20c950`.
- CUDA 12.8 image:
  `ghcr.io/j-schulein/towerscout@sha256:c2d99f178465a8cdc83430092554d98aeb181797ff330fba2661bc95a45d8287`.
- CPU control ZIP: `towerscout-v0.1.0-rc9-cpu.zip`, 199812 bytes, SHA-256
  `66e674ef28d98835a981bd731bc7a86e7c6bdd07cb9ea964d47e4e9c63cfacfc`.
- CUDA control ZIP: `towerscout-v0.1.0-rc9-cuda128.zip`, 199840 bytes,
  SHA-256
  `5157a3a396502e524b16dd5eda6cf46aa80521ba4409546af8625f1ca43cad10`.
- Shared asset ZIP: 800655295 bytes, SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.

Both image workflows passed their local pre-login scan and exact-published-
digest confirmation with baseline 396, candidate 79, accepted baseline 74,
accepted residual 5, blocking 0, severity escalations 0, and resolved 322. Both
package manifests, outer sidecars, all 73 internal checksums, and the focused
  `7/7` package suite passed. All four exact browser-downloaded RC9 profiles
  also pass the affected cancel-then-immediate-retry and broader provider,
  review/export, persistence, ZIP-data, and Help cells recorded in the W10
  index. Both CUDA profiles bind both real models to CUDA 12.8 on the `sm_120`
  NVIDIA device with no CPU fallback.

## Superseded Same-Source RC8 Local Package Inventory

The final documentation-aligned image source is
`7827c2af8ecb7d8b21d246b69e135807fa497fd2`. Owner-authorized CPU run
`37674158762` and CUDA run `37674161407` published and qualified the first
unused same-source tag pair with `push_latest=false`:

- CPU image:
  `ghcr.io/j-schulein/towerscout@sha256:2e040c3b09d1aa493b205ec2100c112a839ab7a9bfc90a639f73918e06135412`.
- CUDA 12.8 image:
  `ghcr.io/j-schulein/towerscout@sha256:712beb4e143495ba72705cc56b89a939c5bebfdc47dc2f6d0694c81e9e60ca57`.
- CPU control ZIP: `towerscout-v0.1.0-rc8-cpu.zip`, 199842 bytes,
  SHA-256
  `8fd46711b57a25dd71cd879a06fe519674596ee9a71fa66b2347204fe8bc74f0`.
- CUDA control ZIP: `towerscout-v0.1.0-rc8-cuda128.zip`, 199850 bytes,
  SHA-256
  `463d3f2348e369ed647bb8ed66c15588fc4051197e49ac90441552b8318bdada`.
- Shared asset ZIP: 800655295 bytes, SHA-256
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.

The control ZIPs were assembled from a clean detached checkout of the exact
image source. Both manifest checks, outer sidecars, all 73 internal checksums
across 74 entries, and the focused `7/7` package/manifest regression suite
passed. The retained browser-downloaded asset ZIP was rehashed directly before
a same-content RC8-named publication input was staged. All six release assets
are now published at
[v0.1.0-rc8](https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc8).
Final browser-download and independent-host evidence still must use the exact
downloaded release bytes and authoritative checksums.

## Final Local `rc4` Candidate Inventory And Qualification

- Source and OCI source label:
  `541622556fb7999ee4e88fb1e44f7797b9da34f5`.
- CPU image:
  `ghcr.io/j-schulein/towerscout:v0.1.3-rc4-cpu@sha256:a3eeb77152577f3656a286777bd4c4312cecc311cb5a5cc1b132b459f1ecd18f`.
- CUDA image:
  `ghcr.io/j-schulein/towerscout:v0.1.3-rc4-cuda128@sha256:61dab3b83e1be8e2cf955d9d7d2d9b997a207a4dcb76b20344a268a5690f654a`.
- CPU control ZIP SHA-256:
  `1cf763b6184bb96dfe976f41f56a4aa5b8eeeea51a8de59830a9bf7fb9784a55`.
- CUDA control ZIP SHA-256:
  `02ec76b93bea28417b7ea4b086f23148b57b34c33823ce2f113da7147165915f`.
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.

The CPU [publish run 36616086115](https://github.com/J-Schulein/TowerScout/actions/runs/36616086115)
and CUDA [publish run 36616639330](https://github.com/J-Schulein/TowerScout/actions/runs/36616639330)
used `push_latest=false`. Each exact-digest G10 comparison passed with 396
accepted-baseline findings, 151 candidate findings, zero new findings, and 245
resolved findings. The exact-digest SBOMs contained 340 CPU and 358 CUDA
components.

Both control ZIP sidecars, all 71 internal checksum entries across 72 packaged
files, manifest identities, required notices/helpers, compliance inventory,
and forbidden/secret/path checks passed. No package was published.

| Host | Engine | Package | Port | Result |
| --- | --- | --- | ---: | --- |
| `FIRST-HOST-LOCAL` | Docker Desktop | CPU | 5231 | PASS: exact digest, assets `ok`, CPU selected, eight volumes retained across stop/relaunch |
| `FIRST-HOST-LOCAL` | Docker Desktop | CUDA 12.8 | 5232 | PASS: exact digest, assets `ok`, CUDA selected, real `sm_120` kernel, eight volumes retained across stop/relaunch |
| `FIRST-HOST-LOCAL` | rootless Podman 6.0.2 | CPU | 5233 | PASS: approved package-local provider, exact digest, assets `ok`, CPU selected, eight volumes retained across stop/relaunch |
| `FIRST-HOST-LOCAL` | rootless Podman 6.0.2 | CUDA 12.8 | 5234 | PASS: approved provider plus NVIDIA CDI, exact digest, assets `ok`, CUDA selected, real `sm_120` kernel, eight volumes retained across stop/relaunch |

The exact `rc4` CPU and CUDA digests also passed all six W05 phases. The CPU
run identifier is
`20260929T194841Z_FIRST-HOST-LOCAL_docker_C_cpu_torch2-10-0_541622556fb7_rc4-exact-cpu`;
its `run.json` SHA-256 is
`17e14ac418ec57ad65efe74ddb30631ef25ee415498794e66b78f5069ac0724f`
and verdict SHA-256 is
`e62b6723da24fb7ddb4a59ebe4162de9e8f44436e39a537657bbd0c7bff38187`.
The CUDA run identifier is
`20260929T201729Z_FIRST-HOST-LOCAL_docker_C_cuda128_torch2-10-0_541622556fb7_rc4-exact-cuda`;
its `run.json` SHA-256 is
`d49bc89226e4e1ebc108f48a6c9b5ad4ab2bae680b8c3040a7a34c0f44049a71`
and verdict SHA-256 is
`f09aa31d7787d1f4c8ea463f769c0a191ff3154eb51bc056f6ac965a5fb379e2`.
Both models used CPU in the CPU run and `cuda:0` in the CUDA run; each run
recorded positive EfficientNet work. Every applicable absolute comparator gate
passed.

## Replacement `rc3` Frozen Candidate Inventory

- Source: `7a5eedd8c6d3d6f300f320de69646f61da64c7ae` (PR #90 merge).
- CPU image:
  `ghcr.io/j-schulein/towerscout:v0.1.3-rc3-cpu@sha256:a84201cec5704e35e0e7e5e05ca96aebeebb976ddeb89c88ac3145776bc1ba88`
- CUDA image:
  `ghcr.io/j-schulein/towerscout:v0.1.3-rc3-cuda128@sha256:6c54725b63cc8b66c996bc6d32d3e6714aada5fb51d07d840b7895dc70041fe5`
- CPU control ZIP SHA-256:
  `0845a71a4b71ada66d9ba0be0ea71c500c1b0127317beff73af3e38ffbc2576b`
- CUDA control ZIP SHA-256:
  `d558db674c964c3a7cf47e661725157e59e7442a96e442ed02e9ff849ee5dcab`
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`

Both exact-digest dispatches used `push_latest=false`. The accepted-baseline
G10 result was 396 baseline findings, 151 candidate findings, zero new, and
245 resolved for each flavor.

| Flavor | Publish run | Scan SHA-256 | SBOM SHA-256 | Delta SHA-256 | Disposition SHA-256 | Components |
| --- | --- | --- | --- | --- | --- | ---: |
| CPU | [run 36483117066](https://github.com/J-Schulein/TowerScout/actions/runs/36483117066) | `b4a8e5d39ba603ad6e509459cc8d2534cbcc773a1f1cadef3b4e81753ea4d432` | `ca45a7c93f292374278e51a58656f78cbbc5358f637bcb2e9ed4162bdcaae7a7` | `81ed7f788c2ba161b2a078cd56bd57b65db8458982355f0f3057ccdad787f2b0` | `80e2df0d56612fffc2f09affd58118175de2fd06cd2da7d653e51be1bd4db00a` | 340 |
| CUDA 12.8 | [run 36483119457](https://github.com/J-Schulein/TowerScout/actions/runs/36483119457) | `bd813c5f8825090bb51765b55db503c57a52fc405061e5389244c91bfc684f87` | `ea96b43a30604d8af6ab50cf275a131481237ab47874cb007474e85e5bd4bd78` | `f132d95d2675c98dc65a6c72ab63c55a91c09f99f37afc77d5ded33e7ede9585` | `46e0d3ef0fa388f87de4b6449c3d4ed8bca8d0a5c030cddf5a066ffd5b737234` | 358 |

Package double-checks passed for both control ZIPs: the outer sidecars match;
each ZIP has 72 files and all 71 internal `SHA256SUMS.txt` entries verify;
the manifests bind the exact source, flavor, image digest, asset filename, and
asset digest; required notices and recovery/TLS helpers are present; and no
credential file, model/data payload, log, session, cache, dependency tree, or
user-specific path was found.

## Replacement `rc3` First-Host Qualification

| Host | Engine | Package | Device | Result |
| --- | --- | --- | --- | --- |
| `FIRST-HOST-LOCAL` | Docker Desktop | CPU | CPU | PASS: exact ZIP/asset verification, assets `ok`, device `cpu`, exact digest, eight volumes retained across stop/relaunch on port 5221 |
| `FIRST-HOST-LOCAL` | Docker Desktop | CUDA 12.8 | NVIDIA | PASS: exact ZIP/asset verification, assets `ok`, device `cuda`, exact digest, eight volumes retained across stop/relaunch on port 5222 |
| `FIRST-HOST-LOCAL` | rootless Podman 6.0.2 | CPU | CPU | PASS: spaced-path relative approved provider, assets `ok`, device `cpu`, exact digest, eight volumes retained across stop/relaunch on port 5223 |
| `FIRST-HOST-LOCAL` | rootless Podman 6.0.2 | CUDA 12.8 | NVIDIA | PASS: spaced-path relative approved provider, assets `ok`, device `cuda`, exact digest, eight volumes retained across stop/relaunch on port 5224 |

Both CUDA profiles report torch `2.10.0+cu128`, CUDA build `12.8`, cuDNN
`91002`, capability `sm_120`, and an architecture list containing `sm_120`.
Real CUDA tensor kernels completed on the NVIDIA device under both engines.
The Podman package-local provider required supported Python 3.12; the default
host Python 3.14 could not install pinned PyYAML 6.0.2 because no matching
binary wheel exists. The documented Python prerequisite remains material.

All four sessions remain isolated under release-specific project names. Their
volumes are preserved; the Docker CPU session remains available for the fresh
`rc3` provider/TLS smoke.

## Replacement `rc3` Exact-Digest W05 Qualification

The automated review on PR #91 correctly found that the initial index bound
the six-phase W05 evidence only to the superseded `rc1` digests. The four `rc3`
package containers and the Task-103 rollback container were therefore stopped
without deleting volumes, and the exact `rc3` CPU and CUDA images were run
through the complete W05 harness sequentially. All five containers were then
restored healthy with their volumes intact.

Both runs used the frozen RGB fixture manifest SHA-256
`c72b65cca35b10ed96a45b1c609f184ce3a2df93a9a100855bc9745abb2c9447`
and gates v3 SHA-256
`1dd6f7f105c62e3d741999f02c198ae69858d012d5769605a0817cc9dcd8240c`.
The raw directory names retain their original host label outside the repo;
the host-neutral identifiers below preserve the timestamp and remaining join
key needed for evidence custody.

| Profile | Host-neutral raw-run identifier | Six phases | Device proof | `run.json` SHA-256 | Verdict SHA-256 |
| --- | --- | --- | --- | --- | --- |
| CPU | `20260929T114520Z_FIRST-HOST-LOCAL_docker_C_cpu_torch2-10-0_7a5eedd8c6d3_rc3-exact-cpu` | PASS: identity, startup, synthetic, combined, three-run 100-tile memory, injection | YOLO and EfficientNet observed on CPU; positive secondary candidates | `755644b58c6c94be2b85492c14aaeaf40c3004c62668e51f5b6bd436f47879c2` | `46d3952c47df9c51f85b54aa6cd856c182280a16003f1e0430224803f7473915` |
| CUDA 12.8 | `20260929T121453Z_FIRST-HOST-LOCAL_docker_C_cuda128_torch2-10-0_7a5eedd8c6d3_rc3-exact-cuda` | PASS: identity, startup, synthetic, combined, three-run 100-tile memory, injection | YOLO and EfficientNet observed on `cuda:0`; positive secondary candidates | `7c270c1d64e3649cadabf9c356f5d390167089d6f6669e4ac9de7a30449c21c8` | `92dc67679aff874f89eecc2ef76fcf7dafb63c09a51ed67822d4007966a4151e` |

The CPU comparator passed G1, G3, G4, G6, G7, G8, G11, and G12; G2 and G5
were correctly not applicable to CPU. The CUDA comparator, using the exact
`rc3` CPU run as its counterpart, passed G1-G8, G11, and G12. G9 was not
applicable because this exact-candidate confirmation was not an interleaved
same-host relative comparison. G10 was not applicable inside W05; the exact-
digest H9 scan delta above separately passed with zero new HIGH/CRITICAL
findings. Both comparator verdicts were overall `pass`.

## Superseded `rc1` Candidate Inventory

- Control-package source: `99de5595b0d98b67c24909c1f2712f72d8714ab3`
  (PR #87 merge; package-only Podman spaced-path correction).
- OCI image source label: `378b37fbe2422d23a1dc25655f4dbad1d47d5b5f`
  (PR #86 merge). PR #87 changed only host-side package scripts that are not
  copied into the OCI images, so the owner-confirmed image digests remain valid.
- CPU image:
  `ghcr.io/j-schulein/towerscout:v0.1.3-rc1-cpu@sha256:4d673a8ca0b3c221899062769f28adc8825e96af7413573ab31ba62d198b6a0a`
- CUDA image:
  `ghcr.io/j-schulein/towerscout:v0.1.3-rc1-cuda128@sha256:8b2c518443977e11f43509b8f96fbc4490a0eb1993d44abe052d912e6664d96a`
- CPU control ZIP SHA-256:
  `02f191eade141ad06251f2611892fe12064eb84601ebd39010aedf8115d98c79`
- CUDA control ZIP SHA-256:
  `238bbd3343f6e72daea2e6c954438aed6447e8aafff129595053a8f62c2196fe`
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`
- Gates v3 SHA-256:
  `1dd6f7f105c62e3d741999f02c198ae69858d012d5769605a0817cc9dcd8240c`
- RGB fixture ZIP SHA-256:
  `83c3278dc3ce0c89e4b7db4babe1e3912880e23b55f9deb963d03995e49b0ae9`
- RGB fixture manifest SHA-256:
  `c72b65cca35b10ed96a45b1c609f184ce3a2df93a9a100855bc9745abb2c9447`

The `rc1` images and control ZIPs below remain immutable historical evidence
but are superseded and are not release candidates.

## Superseded `rc1` Security Artifacts

Both exact-digest H9 dispatches used `push_latest=false` and passed the
accepted-baseline HIGH/CRITICAL delta gate with zero new findings.

| Flavor | Publish run | Scan SHA-256 | SBOM SHA-256 | Components |
| --- | --- | --- | --- | ---: |
| CPU | [run 36070708249](https://github.com/J-Schulein/TowerScout/actions/runs/36070708249) | `1dd40cc6125e32a1fe917864afd68075c622ec326212d12273c00933f5340256` | `6bf8dfd334900f8c3400d148ac45b21f919146af627cfb5c87971e07f338d004` | 444 |
| CUDA 12.8 | [run 36070710384](https://github.com/J-Schulein/TowerScout/actions/runs/36070710384) | `3750bb254dc66e0cecbc7a08169a8c72ecfa2d87d4e8a6a3d99e9fb737fc2911` | `5d7ec0e87913678be819f59670e0c9c50b51ed43d4e6dcd929e8d1bd00e23dfd` | 462 |

The written dependency disposition remains in
`DEPENDENCY-SECURITY-DISPOSITION.md`.

## Superseded `rc1` Package Integrity

- Both control ZIP sidecars match their archives.
- Each ZIP contains 72 files; every `SHA256SUMS.txt` entry verifies.
- Both manifests bind the expected package source, flavor, exact image digest,
  asset filename, and asset SHA-256.
- Required notices, source offer, SBOM reference, `.env.example`, launchers,
  and support documentation are present.
- No `.env`, bundled model/data payload, log, cache, bytecode, or dependency
  tree is present in either control ZIP.
- Secret-oriented inspection found only template/documentation names and
  runtime token-handling source; no packaged credential value was found.
- The shared asset ZIP sidecar matches its 800,655,295-byte archive.

## Superseded `rc1` First-Host Qualification

Host IDs are neutral evidence identifiers. Raw outputs remain under the
authorized external evidence root for `FIRST-HOST-LOCAL`; no user-specific path
or machine hostname is required for custody.

| Host | Engine | Package | Device | Result |
| --- | --- | --- | --- | --- |
| `FIRST-HOST-LOCAL` | Docker Desktop | CPU | CPU | PASS: exact ZIP/asset checks, import with hash verification, assets `ok`, selected device `cpu`, exact digest |
| `FIRST-HOST-LOCAL` | Docker Desktop | CUDA 12.8 | NVIDIA | PASS: exact ZIP/asset checks, import with hash verification, assets `ok`, selected device `cuda`, exact digest |
| `FIRST-HOST-LOCAL` | rootless Podman 6.0.2 | CPU | CPU | PASS: spaced-path package, relative approved provider, assets `ok`, selected device `cpu`, exact digest, stop/relaunch |
| `FIRST-HOST-LOCAL` | rootless Podman 6.0.2 | CUDA 12.8 | NVIDIA | PASS: spaced-path package, relative approved provider, assets `ok`, selected device `cuda`, exact digest, stop/relaunch |

The CUDA package reported torch `2.10.0+cu128`, CUDA build `12.8`, device
capability `sm_120`, architecture support, IEEE FP32 settings, and a successful
CUDA kernel probe. All eight named volumes for each Docker and Podman package
were retained after stop; no qualification container remains running.

The exact confirmed image digests also passed the six-phase W05 harness for
identity, startup, synthetic inference, combined real-model inference, the
three-run 100-tile memory method, and injection checks. Gates v3 passed all
applicable CPU and CUDA absolute gates. Relative G8/G9 and vulnerability G10
remain governed by their separately recorded applicability rules and H9
security artifacts.

## Correction And Double Check

W09 reproduced a Windows Podman 6 failure when an approved external `.cmd`
provider was stored as a long absolute path beneath a spaced extraction root.
PR [#87](https://github.com/J-Schulein/TowerScout/pull/87) keeps a validated
package-local provider relative and supplies the package root as the subprocess
working directory. The final local regression ring passed 155 tests; PR #87
CI passed Python 3.11/3.12, frontend, Docker frontend, security/Trivy, and
Windows/production-controller jobs. The final ZIPs were rebuilt only after the
PR merged.

## Open Acceptance Cells

These items prevent a release-ready or full W09/W10 acceptance claim:

- The `rc4` four-profile first-host provider/recovery/review-export and
  controlled-error matrix passes and is recorded in the W10 evidence index.
- Exact-`rc4` reboot persistence passes for all four profiles; Docker restored
  automatically and Podman used the documented manual retained-container
  start without recreation or volume deletion.
- ADR-023 resolves policy/signing by limiting the standard claim to users/sites
  that permit the supplied unsigned wrapper path. Signature-enforcing managed
  endpoints are out of scope, not passed.
- The ADR-023 manual changes are present in the published control-ZIP and OCI-
  image bytes because `Dockerfile` copies `docs/` for the in-app routes. Final
  acceptance must validate those exact browser-downloaded package bytes.
- Browser-download W10 first-host acceptance now passes for all four RC9
  profiles, and Docker/Podman reboot persistence passes. One independent
  NVIDIA host repeated all four profiles, but the run selected TASK-105
  corrections and left the CPU-only, second-NVIDIA, and Podman-without-Docker
  allocation incomplete.
- Control-package publication was separately authorized and completed as the
  non-Latest `v0.1.0-rc9` validation prerelease. Any `latest` promotion remains
  separately owner-gated.
- RC9 remains immutable validation evidence. The corrected `v0.1.3-rc.N`
  source/images/packages must receive new identities and repeat affected W09/
  W10 gates under TASK-105.
