# Task-103 W09 Candidate Evidence Index

**Recorded**: 2026-09-28  
**Verdict**: Artifact assembly PASS; first-host four-profile package startup
PASS; overall release remains AT_RISK pending the open acceptance cells below.  
**Publication state**: Control ZIPs and the asset ZIP are assembled locally but
not published. No `latest` tag was promoted.

## Frozen Candidate Inventory

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

The earlier control ZIPs in the rehearsal output directory are superseded and
are not release candidates.

## Security Artifacts

Both exact-digest H9 dispatches used `push_latest=false` and passed the
accepted-baseline HIGH/CRITICAL delta gate with zero new findings.

| Flavor | Publish run | Scan SHA-256 | SBOM SHA-256 | Components |
| --- | --- | --- | --- | ---: |
| CPU | [run 36070708249](https://github.com/J-Schulein/TowerScout/actions/runs/36070708249) | `1dd40cc6125e32a1fe917864afd68075c622ec326212d12273c00933f5340256` | `6bf8dfd334900f8c3400d148ac45b21f919146af627cfb5c87971e07f338d004` | 444 |
| CUDA 12.8 | [run 36070710384](https://github.com/J-Schulein/TowerScout/actions/runs/36070710384) | `3750bb254dc66e0cecbc7a08169a8c72ecfa2d87d4e8a6a3d99e9fb737fc2911` | `5d7ec0e87913678be819f59670e0c9c50b51ed43d4e6dcd929e8d1bd00e23dfd` | 462 |

The written dependency disposition remains in
`DEPENDENCY-SECURITY-DISPOSITION.md`.

## Package Integrity

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

## First-Host Qualification

Host IDs are neutral evidence identifiers. Raw outputs remain under the
authorized external evidence root for `HOST-BLACKWELL`; no user-specific path
or machine hostname is required for custody.

| Host | Engine | Package | Device | Result |
| --- | --- | --- | --- | --- |
| `HOST-BLACKWELL` | Docker Desktop | CPU | CPU | PASS: exact ZIP/asset checks, import with hash verification, assets `ok`, selected device `cpu`, exact digest |
| `HOST-BLACKWELL` | Docker Desktop | CUDA 12.8 | NVIDIA | PASS: exact ZIP/asset checks, import with hash verification, assets `ok`, selected device `cuda`, exact digest |
| `HOST-BLACKWELL` | rootless Podman 6.0.2 | CPU | CPU | PASS: spaced-path package, relative approved provider, assets `ok`, selected device `cpu`, exact digest, stop/relaunch |
| `HOST-BLACKWELL` | rootless Podman 6.0.2 | CUDA 12.8 | NVIDIA | PASS: spaced-path package, relative approved provider, assets `ok`, selected device `cuda`, exact digest, stop/relaunch |

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

- Live Google and Azure provider workflows were not run because credentials
  were not supplied to this qualification session.
- Managed-endpoint/policy and any required signing decision remain owner or
  environment dependent.
- A real host reboot persistence check has not been recorded for these bytes.
- Independent-host W10 reproduction is not complete.
- Control-package publication and any `latest` promotion require explicit
  owner authorization.

