# Task-105 Candidate Notes — Qualification In Progress

These notes describe the intended Windows 11 CPU and CUDA 12.8 candidate.
The final `v0.1.3-rc.N` identity, downloads, SHA-256 values, image digests,
and support matrix will be filled in only after accepted-source builds and
exact browser-download testing. RC9 remains a validation prerelease and is
not a final release.

## Tested GPU evidence

- NVIDIA RTX PRO 500 Blackwell Generation Laptop GPU (`sm_120`): the RC9
  first host passed Docker and rootless Podman CUDA 12.8 workflows with both
  YOLO and EfficientNet on CUDA and no CPU fallback.
- NVIDIA T1000 (`sm_75`): one independent Windows host passed the RC9 Docker
  and rootless Podman CUDA 12.8 profiles with both models on CUDA, subject to
  the Task-105 fresh-install and UI findings.

These are GPU models observed in the retained RC9 evidence, not a blanket
claim for every driver, Windows build, WSL version, or engine version. The
corrected final candidate must repeat Docker CPU/CUDA and Podman CPU/CUDA on
both available Windows NVIDIA hosts using the exact public bytes. CPU-only
hardware and Podman without Docker Desktop installed are outside the tested
claim. The CUDA package expects Volta or newer; an architecture present in a
wheel alone does not
qualify an untested GPU. Maxwell and Pascal use the CPU package.

## Tested support boundary

The tested Podman path uses a rootless WSL 2 machine, 64-bit Python 3.12,
TowerScout's package-local Compose provider, and NVIDIA CDI for GPU work.
A reviewer observed Python 3.13.6 and rootful Podman during onboarding, but
those alternatives are not claimed as tested support. The standard Windows
control package is unsigned and uses its supplied process-scoped wrappers;
signature-enforcing endpoints are outside the claim.

The control ZIP uses Windows path separators in ZIP entry names. It is a
Windows package and is not claimed as a portable Unix archive. This remains
an explicit packaging limitation for this candidate.

The accepted ADR-024 security residuals expire October 31, 2026. A corrected
build or publication after that date needs a new written disposition. No
`latest` promotion or stable/general release follows from these notes.
