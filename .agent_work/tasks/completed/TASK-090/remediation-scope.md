# Task-090 Proposed Task-098 Scope And Release Gate

**Status**: APPROVED BY PROJECT LEAD 2026-07-23 - fork-side implementation may
begin under Task-098's non-regression contract; cdcai-owner approval remains
required only for residual critical/high acceptance or official adoption
**Input**: 62-record Task-090 disposition

## Decision Summary

Task-090 identifies five release-blocking alerts and one required-hardening
alert:

- aiohttp alert 27: live outbound response parser
- Pillow alerts 68 and 60: content-sniffed custom-image parsers
- torch alert 31: direct `weights_only=True` checkpoint load
- Waitress alert 35: live WSGI boundary
- Pillow alert 72: reachable EPS-parser denial of service

Task-098 should be approved as a coordinated remediation and qualification
task. Task-087 must remain paused until the mandatory Task-098 slices pass.

## Proposed Remediation Matrix

Targets are directions for a compatibility spike, not changes authorized by
Task-090.

| Slice | Current | Minimum/target direction | Scope | Estimate | Gate |
| --- | --- | --- | --- | ---: | --- |
| A: loopback and input boundary | all-interface Compose publish; extension-only image validation | bind `127.0.0.1`; enforce JPEG/PNG/TIFF signatures before Pillow; keep 50 MiB cap and rate limit | Compose, launch/status tests, custom-image validation | 0.5-1 day | Mandatory |
| B: narrow runtime patches | Pillow 12.2.0; Waitress 3.0.0 | Pillow 12.3.0; Waitress >=3.0.1 | pins plus image and WSGI regression | 0.5-1 day | Mandatory |
| C: provider client | aiohttp 3.9.3 | aiohttp 3.14.2 (minimum fixes converge at 3.14.1) | Google/Azure tile and metadata downloads, redirects, TLS error classification, cancellation | 0.5-1 day | Mandatory |
| D: ML runtime | torch 2.2.1; torchvision 0.17.1; CPU/cu121 | at least torch 2.6.0 + torchvision 0.21.0; compare with a currently supported pair | YOLO/EfficientNet checkpoints, Ultralytics wrapper, CPU/GPU, wheel flavor and package scripts | 2-4 days plus GPU hosts | Mandatory or owner residual-risk decision |
| E: geospatial | Fiona 1.9.6/GDAL 3.6.4; GeoPandas 0.14.3 | stable Fiona >=1.10.1 and GeoPandas >=1.1.2, selected together | ZIP-code shapefile load, geometry lookup, Python 3.11/3.12, Linux wheel/system GDAL | 1-2 days | Required hardening if compatibility passes |
| F: config/web framework | python-dotenv 1.0.0; Flask 3.0.2 | python-dotenv 1.2.2; Flask 3.1.3 | setup/settings persistence, filesystem sessions, route/cache behavior | 0.5-1 day | Required hardening if compatibility passes |
| G: model trust controls | runtime hash verification defaults off; upload default off | verify release model hashes by default; preserve upload-off default; bind admin override to loopback/trusted files | asset readiness, imports, model catalog/load | 0.5-1 day | Mandatory with ML decision |

The PyTorch minimum fixed pair no longer has the current CUDA 12.1 wheel
flavor. Official PyTorch matrices pair 2.6.0 with torchvision 0.21.0 and
CPU/CUDA 11.8/12.4/12.6 wheels. Task-098 must therefore treat the GPU wheel
flavor, `Dockerfile`, container-publish choices, package manifests, launch
scripts, and four-profile qualification as one decision.

Ultralytics 8.3.249 declares `torch>=1.8.0` (excluding 2.4.0 on Windows) and
`torchvision>=0.9.0`, but declared compatibility is not model-load proof.
EfficientNet-PyTorch declares an unbounded torch dependency. Both actual
checkpoint paths must be exercised.

## Required Regression Matrix

| Surface | Required evidence |
| --- | --- |
| Static dependency resolution | Clean Python 3.11 and 3.12 installs; exact resolved versions; no incompatible wheel/source fallback |
| Google provider | TLS-verified tile and metadata downloads; header parsing; retry/timeout/error redaction |
| Azure provider | TLS-verified tile and attribution/metadata downloads; header parsing; retry/timeout/error redaction |
| Custom image | Valid JPEG/PNG/TIFF; renamed EPS/JPEG2000/McIdas rejection before Pillow; oversized and malformed files; output drawing |
| Waitress | Startup/readiness; loopback host binding contract; request-size cap; malformed/disconnected-client regression where practical |
| EfficientNet | Known checksum model loads with `weights_only=True`; inference on representative detection crops; CPU and CUDA |
| YOLO | Vendored full-object checkpoint loads only from trusted/checksummed model path; inference parity; CPU and CUDA |
| Model upload | Disabled by default; trusted-admin override only; sanitized filename, type/size checks, and no non-loopback exposure |
| Geospatial | Packaged ZIP-code shapefile loads and returns representative geometry on Python 3.11/3.12 |
| Configuration/session | Setup/settings reads and writes config; secret persistence; filesystem-session routes; cache headers |
| Package/runtime | Rebuilt image plus Docker CPU, Docker GPU, Podman CPU, and Podman GPU before final-candidate qualification |

Runtime validation should be staged. Unit/static work does not require a
runtime. Before the rebuilt-image or four-profile stages, the active agent must
ask the user to start the exact Docker/Podman profiles needed.

## Residual Critical/High Owner Decision Packet

This packet is needed only if the PyTorch or another mandatory upgrade cannot
be qualified safely.

### Decision required

Choose one:

1. Delay later runtime work and complete the compatible upgrade.
2. Accept a time-bounded residual risk through the final candidate.
3. Remove/disable the affected capability from the supported release.

### Minimum evidence for option 2

- exact unresolved alert IDs and vulnerable versions
- failed upgrade candidates and reproducible compatibility evidence
- proof that normal release model upload remains disabled
- loopback-only package binding
- release and individual model checksum enforcement enabled by default
- explicit trusted-model-only documentation
- expiration date no later than the October 9 freeze unless renewed
- named owner and follow-up task
- written project-lead and cdcai-owner approval

Task-090 does not grant this acceptance.

## CI Ratchet Recommendation

Keep the current SARIF upload advisory during Task-098 so the known baseline
does not become an accidental merge blocker.

After mandatory remediation:

1. Keep an all-severity SARIF generation/upload step with `if: always()`.
2. Add a second Trivy filesystem gate restricted to `CRITICAL,HIGH` with
   `exit-code: 1`.
3. Do not use `ignore-unfixed` as a blanket safety claim; an unfixed direct
   critical/high must still receive a reachability decision.
4. If an owner-approved residual finding remains, use a narrow
   `.trivyignore.yaml` entry scoped to its vulnerability/package path with a
   written statement and `expired_at`.
5. Pin the action and Trivy version, record the baseline database/version, and
   add a scheduled scan so newly published advisories do not wait for source
   changes.
6. Fail on any new critical/high finding not covered by an unexpired approved
   exception.

Trivy supports `exit-code`, severity filtering, separate SARIF upload after a
non-zero scan, and expiring structured ignore entries. Task-098 should validate
the exact pinned action behavior before making the gate blocking.

## Recommended Approval

Approve Task-098 with mandatory slices A-D and G. Approve slices E-F as
coordinated hardening subject to clean compatibility tests. Do not resume
Task-087 until the release-blocking findings are fixed or receive the explicit
residual-risk decision described above.
