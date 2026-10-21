# TowerScout RC6 GPU Validation Public Summary

**Release candidate:** `v0.1.0-rc6`  
**Validation prerelease tag:** `gpu-validation-2026-06-16`  
**Source ref:** `12daa5536f580f76d063559e86b9a474451bc54b`  
**Result:** PASS for the RC6 CUDA package GPU validation gate.

This summary is sanitized for external sharing. It omits the raw test AOI,
provider responses, personal paths, credential previews, and local host
directories. The raw email-safe evidence packet remains internal.

## Artifact Identity

| Artifact | SHA-256 or digest |
|---|---|
| CPU control ZIP | `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d` |
| CUDA control ZIP | `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603` |
| Shared Model & Data Package ZIP | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |
| CPU image | `sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd` |
| CUDA image | `sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0` |

## Runtime Gate Results

| Engine | Provider path | Result |
|---|---|---|
| Docker GPU | Google | Ready with `selected_device=cuda`, `pytorch_flavor=cuda121`, assets `ok`, pinned CUDA image digest. |
| Docker GPU | Azure | Ready with `selected_device=cuda`, `pytorch_flavor=cuda121`, assets `ok`, pinned CUDA image digest. |
| Podman GPU CDI | Google | Ready with `selected_device=cuda`, `pytorch_flavor=cuda121`, assets `ok`, pinned CUDA image digest. |
| Podman GPU CDI | Azure | Ready with `selected_device=cuda`, `pytorch_flavor=cuda121`, assets `ok`, pinned CUDA image digest. |
| CPU package guardrail | `-Gpu on` | Refused before container startup with package-aware guidance to use the CUDA package. |

The GPU host exposed an NVIDIA T1000 8GB to both Docker and Podman CDI.
Readiness reported `torch_version=2.2.1+cu121`,
`torch_cuda_available=true`, and CUDA 12.1 build metadata.

## Detection Result Summary

End-to-end detection completed on CUDA for both provider paths and both
container engines. Runtime metrics reported CUDA model execution for the
YOLOv5 primary detector and EfficientNet secondary classifier.

Representative selected detection counts:

| Engine | Provider path | Selected detections |
|---|---|---|
| Docker GPU | Google | 49 high-mode; repeated Docker log also captured 26 low-mode. |
| Podman GPU CDI | Google | 49 representative high-mode run. |
| Docker GPU | Azure | 50 high-mode; repeated Docker log also captured 22 low-mode. |
| Podman GPU CDI | Azure | 50 high-mode; repeated Podman log also captured 22 low-mode. |

The count differences are attributable to intermittent provider imagery
changes for the same fixed public fixture, not to cache behavior or CUDA
nondeterminism. Runtime logs consistently fetched 10 map tiles per detection
run, and model output was deterministic within each imagery mode.

## Publication Decision

The RC6 CUDA package has the required Docker GPU and Podman GPU CDI runtime
evidence for a support-validated NVIDIA GPU release path. The CPU package
remains the default package for non-GPU or unsure users.
