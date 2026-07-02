# RC6 GPU Validation Artifact Provenance

This file makes the email-safe evidence packet standalone. It records the exact
release source, artifact identity, checksums, image digests, and runtime
evidence files used to accept the RC6 CUDA validation gate.

## Source And Release References

| Item | Value |
|---|---|
| Release candidate | `v0.1.0-rc6` |
| GPU-validation prerelease tag | `gpu-validation-2026-06-16` |
| Source ref | `12daa5536f580f76d063559e86b9a474451bc54b` |
| Prerelease asset source | `https://github.com/J-Schulein/TowerScout/releases/tag/gpu-validation-2026-06-16` |

The official `v0.1.0-rc6` release tag remained reserved while this GPU
validation prerelease was used to move the rebuilt RC6 artifacts to the GPU
host.

## Artifact Checksums And Digests

| Artifact | Identity | SHA-256 or digest |
|---|---|---|
| Shared Model & Data Package ZIP | `towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip` | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |
| CPU image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cpu` | `sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd` |
| CUDA image | `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cuda121` | `sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0` |
| CPU control ZIP | `towerscout-v0.1.0-rc6-cpu.zip` | `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d` |
| CUDA control ZIP | `towerscout-v0.1.0-rc6-cuda121.zip` | `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603` |

These values match the final package gate checklist and the uploaded
GPU-validation prerelease assets.

## Manifest And Runtime Consistency

- The CUDA package runtime path used the digest-pinned CUDA image.
- GPU readiness captures reported `runtime.container_engine=docker` or
  `runtime.container_engine=podman`, `device_policy=cuda`,
  `selected_device=cuda`, `pytorch_flavor=cuda121`, and the pinned CUDA image
  digest.
- GPU readiness captures reported `torch_version=2.2.1+cu121`,
  `torch_cuda_build=12.1`, `torch_cuda_available=true`, and
  `cuda_device_name="NVIDIA T1000 8GB"`.
- GPU runtime evidence reported `components.assets.status=ok`.
- CPU guardrail evidence reported exit code `1` and the expected package-aware
  refusal when the CPU package was launched with `-Gpu on`.

## Runtime Evidence Index

| Evidence file | Purpose |
|---|---|
| `1a-docker-google-READY-status.txt` | Docker GPU readiness after Google setup. |
| `1b-docker-azure-READY-status.txt` | Docker GPU readiness after Azure setup. |
| `2-podman-google-READY-status.txt` | Podman GPU CDI readiness after Google setup. |
| `2b-podman-azure-READY-status.txt` | Podman GPU CDI readiness after Azure setup. |
| `1a-docker-google-DETECTION.json` | Representative Docker GPU Google detection result. |
| `1b-docker-azure-DETECTION.json` | Representative Docker GPU Azure detection result. |
| `2-podman-google-DETECTION.json` | Representative Podman GPU CDI Google detection result. |
| `2b-podman-azure-DETECTION.json` | Representative Podman GPU CDI Azure detection result. |
| `perf-logs/1a-docker-google/performance.jsonl` | Repeated Docker GPU Google runtime metrics. |
| `perf-logs/1b-docker-azure/performance.jsonl` | Repeated Docker GPU Azure runtime metrics. |
| `perf-logs/2-podman-google/performance.jsonl` | Representative Podman GPU Google runtime metrics. |
| `perf-logs/2b-podman-azure/performance.jsonl` | Repeated Podman GPU Azure runtime metrics. |
| `3-cpu-guardrail.txt` | CPU package `-Gpu on` guardrail evidence. |
| `CACHE-investigation.md` | Cache and imagery-mode analysis. |

## Evidence Boundary

The raw evidence files are internal/email-safe only. They contain the fixed
test AOI and validation-machine context and are intentionally ignored by git in
this public repository. `PUBLIC-SUMMARY.md` is the sanitized public-safe
artifact for external attachment.
