# TASK-103 NVIDIA Runtime Component Inventory

**Purpose**: Pre-publication component inventory for compliance review
**Date**: 2026-09-24
**Boundary**: Inventory only; this document makes no legal determination or
publication approval.

## Inspected Candidate

- Local Track L image: `towerscout:task098-4795970714e6-cuda128-torch2-10-0`
- Image ID: `sha256:4f6025a2a2206b03d5e9169eb251345a4179e50c8f563cc2906ff5040e0c38a7`
- Source revision label: `4795970714e631d9b3b480b96d5c9ec4de56eb76`
- Flavor label: `cuda128`
- Observed local image size: 14.4 GB
- Runtime source: torch/torchvision installed from the PyTorch `cu128` index

This is the Track L image, not a published release digest. The publication
workflow must regenerate the exact-digest SBOM and scan for each final CPU and
CUDA image.

## NVIDIA Python Runtime Distributions In The CUDA Image

The list below was read from `importlib.metadata` inside a disposable container
of the inspected image.

| Distribution | Version |
| --- | --- |
| `nvidia-cublas-cu12` | `12.8.4.1` |
| `nvidia-cuda-cupti-cu12` | `12.8.90` |
| `nvidia-cuda-nvrtc-cu12` | `12.8.93` |
| `nvidia-cuda-runtime-cu12` | `12.8.90` |
| `nvidia-cudnn-cu12` | `9.10.2.21` |
| `nvidia-cufft-cu12` | `11.3.3.83` |
| `nvidia-cufile-cu12` | `1.13.1.3` |
| `nvidia-curand-cu12` | `10.3.9.90` |
| `nvidia-cusolver-cu12` | `11.7.3.90` |
| `nvidia-cusparse-cu12` | `12.5.8.93` |
| `nvidia-cusparselt-cu12` | `0.7.1` |
| `nvidia-nccl-cu12` | `2.27.5` |
| `nvidia-nvjitlink-cu12` | `12.8.93` |
| `nvidia-nvshmem-cu12` | `3.4.5` |
| `nvidia-nvtx-cu12` | `12.8.90` |

The Windows NVIDIA display driver and Podman-machine NVIDIA Container Toolkit
are host/runtime prerequisites and are not shipped in the TowerScout image.

## Required Reviewer Follow-Up Before Publication

- Confirm the final exact-digest CycloneDX SBOM contains the components above
  (or explains a reviewed version difference) and includes their license data.
- Review NVIDIA/PyTorch redistribution terms and required notices for the exact
  final component set. Do not infer approval from package installation alone.
- Retain the exact-digest Trivy JSON and generated finding-disposition table;
  resolve every blocking HIGH/CRITICAL finding or obtain the separately
  authorized, time-bounded decision required by project policy.
- Confirm existing YOLO/AGPL, model-weight, Census data, and provider notices
  remain included. EfficientNet weight distribution authority remains an owner
  review item.
- Bind the final source ref, image digest, package hashes, SBOM, notices, and
  revocation note in the release evidence.

The release-compliance review found no new claim that makes the full runtime
Apache-only and no provider-key or imagery-rights expansion. Final legal and
release-policy approval remains with the project owner/legal reviewer.
