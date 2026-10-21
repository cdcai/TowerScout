# ADR-025: Two-Host Final-Candidate Qualification

**Status**: Accepted
**Date**: October 14, 2026
**Owner**: `J-Schulein` until project handoff; `cdcai` thereafter
**Scope**: Task-105 final-candidate Windows host allocation and the independent-host portions of the September 21 v2 acceptance plan

## Decision

The final-candidate host allocation is `FIRST-HOST-LOCAL`, this Windows 11
NVIDIA machine, and `INDEP-HOST-01`, the separate Windows 11 NVIDIA machine
used for the RC9 independent-host run. On each machine, qualify the same
corrected, exact browser-downloaded candidate
through Docker CPU, Docker CUDA 12.8, Podman CPU, and Podman CUDA 12.8. The
second machine is an independent validator, not a continuation of the first
machine's local test state. Record anonymous host IDs, hardware and runtime
versions, exact downloaded file hashes, image digests, pass/fail results, and
sanitized evidence for every profile.

This replaces the v2 allocation calling for an additional CPU-only Windows
machine and a Podman installation without Docker Desktop. Those two
environments are outside this final-candidate qualification claim. CPU mode
must still be explicitly proven on both NVIDIA-equipped machines. For Podman,
record the selected machine and approved Compose provider, and exercise the
documented Docker/Podman coexistence and safe recovery path with Docker
Desktop closed when Podman runs.

The first machine runs the complete shipped-package workflow for all four
profiles. The independent validator repeats the four profiles using the exact
same published candidate identities and the shipped instructions. A scripted
driver may collect repeatable measurements, but real application requests,
both configured providers, model/device proof, review/export, cancellation,
recovery, persistence, and reboot remain required. Changed browser behaviors,
especially separate CSV/KML downloads and late-cancel display, require direct
browser observation. Record any deviation from the ordinary user path as a
gap until it is resolved or expressly bounded in the final claim.

RC9 results on these machines are historical evidence only. They do not
qualify changed Task-105 bytes. A source, image, control ZIP, asset, or public
download change requires a new identity and the affected reruns.

## Boundaries retained

- Four Docker/Podman CPU/CUDA profiles, real YOLO and EfficientNet execution
  on the required device, and no GPU-profile CPU fallback.
- Authoritative published SHA-256 checks on the exact browser-downloaded
  unsigned Windows packages, ordinary-account extraction with the downloaded
  file marker, and digest-pinned same-source CPU/CUDA images.
- Google and Azure workflows, approved Podman provider, managed TLS, asset
  import, cancellation and next-request success, controlled recovery,
  review/export, stop/relaunch, reboot, volume persistence, and sanitized
  independent evidence.
- ADR-023's unsigned-package support boundary and ADR-024's strict,
  time-bounded security gate. GHCR dispatch, GitHub release publication,
  cdcai mutation, and stable/Latest promotion retain separate authorization.

## Rationale and consequence

Only these two machines are available for the current delivery window. Both
have NVIDIA GPUs, allowing genuine CPU and CUDA checks on two different
devices, and the second machine has already served as an independent RC9
validator. The release owner chooses this narrower host diversity so the
corrected package can be retested without treating inaccessible machines as
silent passes.

The resulting support statement may name only the tested Windows, engine,
driver, GPU, Python, WSL, and Podman combinations shown by final-candidate
evidence. It must not claim validation on a CPU-only computer or on Podman
without Docker Desktop installed. A failure on either available machine or a
missing required profile remains a release blocker. This decision changes
host allocation only; it does not authorize publication or waive a failed
runtime, provider, security, integrity, or workflow check.
