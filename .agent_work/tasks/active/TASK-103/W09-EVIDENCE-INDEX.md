# Task-103 W09 Candidate Evidence Index

**Recorded**: 2026-09-28  
**Verdict**: Replacement `rc3` artifact assembly PASS; first-host four-profile
package startup and volume-preserving relaunch PASS; overall release remains
AT_RISK pending the open acceptance cells below.
**Publication state**: Control ZIPs and the asset ZIP are assembled locally but
not published. No `latest` tag was promoted.

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

- Fresh-`rc3` managed-TLS repetition passes on the Docker CPU package. Live
  Google/Azure detection awaits interactive credential entry; credentials are
  not copied from the superseded session.
- Managed-endpoint/policy and any required signing decision remain owner or
  environment dependent.
- A real host reboot persistence check has not been recorded for these bytes.
- Independent-host W10 reproduction is not complete.
- Control-package publication and any `latest` promotion require explicit
  owner authorization.
