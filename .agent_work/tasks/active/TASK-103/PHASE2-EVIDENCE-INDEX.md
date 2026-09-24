# TASK-103 Phase 2 Evidence Index

**Date**: 2026-09-24
**Host ID**: `l510046`
**Source**: `e55abaecc601` rebased on accepted `main` `10cd13a`
**Operative gates**: v3 SHA-256
`1dd6f7f105c62e3d741999f02c198ae69858d012d5769605a0817cc9dcd8240`

Raw runtime evidence is retained outside Git under
`C:\ts-task103\phase2\e55abae\`. This file records sanitized identities,
outcomes, and custody paths only. It contains no credentials, model weights,
or fixture imagery.

## Final Docker qualification

| Cell | Image identity | Verdict | Raw evidence |
| --- | --- | --- | --- |
| CPU | `sha256:7d6e49820fd787b85983bed19f3344710c374314a069f331d19677fdbd7c4aff`; 867,919,134 bytes | PASS; G1, G3-G8, G11-G12 pass; GPU-only and scan-relative gates not applicable | `full-cpu\runs\20260924T202828Z_l510046_docker_C_cpu_torch2-10-0_e55abaecc601_final-cpu\`; `verdicts\final-cpu\` |
| CUDA 12.8 | `sha256:a68b2c00b5653bc2814fd6008b63e3d2702cab83eb80f101f10bd49958bac45f`; 4,830,698,137 bytes | PASS; G1-G8 and G11-G12 pass; G9/G10 not applicable | `full-cuda\runs\20260924T205545Z_l510046_docker_C_cuda128_torch2-10-0_e55abaecc601_final-cuda\`; `verdicts\final-cuda\` |

Both images carry `org.opencontainers.image.revision=e55abae` and
`org.opencontainers.image.version=task103-e55abae`. The CPU flavor is `cpu`;
the GPU flavor is `cuda128`. The CUDA cell selected `cuda:0` for YOLO and
EfficientNet, executed a kernel on `sm_120`, kept 2.89 GiB of VRAM free, and
matched the reference vector `0,0,12,8,0,4,6,9,4,6,5,0`. Maximum differences
were box `1.19e-07`, confidence `1.64e-06`, and secondary `5.96e-07`.

The accepted output reference is the T1000 stage-A CPU run. This Blackwell
host has no valid torch 2.6.0 same-host GPU performance baseline, so gates v3
correctly report relative G8/G9 as not applicable. No cross-window result is
presented as a relative comparison.

## Podman CPU and NVIDIA CDI cells

The dedicated rootless `towerscout-task103` Podman 6.0.2 machine has 8 GiB
configured memory, NVIDIA Container Toolkit 1.20.1, and CDI device
`nvidia.com/gpu=all`. Podman 6.0.2 did not start its rootless API socket from
the user systemd session despite lingering being enabled. The cell therefore
used a scoped machine-local `podman --cgroup-manager=cgroupfs system service`
process; the normal-user connection remained rootless.

The exact Docker images were transferred without a rebuild in
`task103-final-images.tar` (5,650,857,472 bytes; SHA-256
`0a9f225a22780fc1124b7253427ed0156fa7ae5d2a9aae19ac3bd29c11d47099`).
Podman rewrote storage manifests during import, so the imported storage IDs
differ; OCI labels and payload behavior bind them to the source images.

| Cell | Outcome | Key evidence |
| --- | --- | --- |
| Podman CPU | PASS | torch `2.10.0+cpu`; torchvision `0.25.0+cpu`; both models on CPU; frozen combined contract passes; 54 detections; 13 EfficientNet candidates in 6 batches |
| Podman NVIDIA CDI | PASS | torch `2.10.0+cu128`; torchvision `0.25.0+cu128`; CUDA 12.8; Blackwell `sm_120`; kernel probe true; both models on CUDA; same combined output contract |

Raw JSON and hashes:

- `podman\cpu\identity.json` —
  `381717a1507eeec49f7e3faad260be8ac95480d2a191312582737ea2a398daca`
- `podman\cpu\combined.json` —
  `cefee3b040e1056478df3572d76d6fe8a960772c078e879ef1f78e3e939c8824`
- `podman\cuda\identity.json` —
  `5fac768c77be2ebc55785baa8d273c43f28ebf17f342be3af24132805ab7f1d0`
- `podman\cuda\combined.json` —
  `c8d14bac0cfcfd9b836d1531ce17db509adf9ca31c4ecc5ebc0dfbac0bee53e3`

These H6 cells establish local OCI/model/device compatibility. Exact published
digest pulls, release ZIP setup, provider workflows, reboot persistence, and
independent-host W09/W10 acceptance remain after Checkpoint 2; this evidence
does not claim those later gates.

## Rollback and recovery rehearsal

- **Source**: an isolated detached worktree applied a no-commit revert of all
  11 commits in `10cd13a..e55abae`. Its tracked tree matched `10cd13a` exactly
  (`git diff --exit-code` returned 0).
- **Artifact**: Compose project `task103rollback` created eight task-owned
  named volumes. The final cuda128 image, retained cu126 image, and final image
  again each started healthy under the same project name in CPU mode. The old
  image reported torch `2.6.0+cu126`; the restored image reported
  `2.10.0+cu128`. Model assets and markers persisted across both switches.
  The application deliberately deletes top-level upload files at startup, so
  the uploads-volume marker was placed in a subdirectory for the return leg.
  All eight markers then verified. The stopped container, volumes, and both
  images are retained; no volume deletion or prune was performed.
- **CPU escape hatch**: the final cuda128 image was forced to CPU and loaded
  both real models successfully. Raw `podman\cpu-escape\startup.json` has
  SHA-256
  `96488222c6fbd484292f528402c70d3fa8d9483ecd30a5cefe856ef17bf11db3`.

## Automated validation

- Focused implementation suite: 81 passed.
- Full unit suite: 584 passed, 74 skipped, 19 failed. All 19 failures are the
  pre-existing Task-087 host-helper module blocked by Windows Defender's
  `ScriptContainedMaliciousContent`; no new failure class appeared.
- Windows-only brief suite: 58 passed.
- Selected flake8 fatal checks: zero findings; Python byte compilation passed.
- Strict and quick `.agent_work` validators passed.
- Documentation command scan and the authoritative N4 stale-CUDA-reference
  checks passed.
- Gates v1/v2/v3 copies match their package hashes.

## Publication boundary

No workflow dispatch, registry push, package/release publication, `latest`
update, or task closeout occurred. Exact-digest Trivy/SBOM evidence and final
release-package acceptance remain H9 work after Checkpoint 2 authorization.
