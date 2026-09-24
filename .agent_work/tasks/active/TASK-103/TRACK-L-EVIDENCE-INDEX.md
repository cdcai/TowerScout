# TASK-103 Track L Evidence Index

**Date**: 2026-09-24
**Host ID**: `l510046`
**Custody**: Raw run directories remain outside Git at
`C:\ts-task103\evidence\`; this index contains only sanitized facts and paths.
**Operative Track L gates**: v2 SHA-256
`f1096e7e00a1b8edf8e4acdb20bd07f1053cc7bec04faf596eaf8e01e661557f`

| Evidence | Outcome | Raw relative location |
| --- | --- | --- |
| Blackwell CUDA candidate | PASS; G1-G8/G11-G12 pass, G9/G10 not applicable | `verdicts\blackwell-built\` |
| Initial CPU profile | FAIL; harness incorrectly conflated CPU profile with CPU image flavor; retained | `verdicts\blackwell-cpu\` |
| Corrected CPU profile of cuda128 image | PASS; CPU outputs within tolerance | `verdicts\blackwell-cpu-fixed\` |
| Negative control N2 | PASS; torch 2.6.0/cu126 lacks `sm_120` and decisive kernel probe fails | `runs\..._n2-built\` |
| Negative control N3 | PASS; torch 2.10.0/cu128 includes `sm_120` and decisive kernel probe succeeds | candidate identity above |

## CUDA Identity Highlights

- GPU: NVIDIA RTX PRO 500 Blackwell Generation Laptop GPU
- Capability: `sm_120`
- Arch list: `sm_70, sm_75, sm_80, sm_86, sm_90, sm_100, sm_120`
- torch: `2.10.0+cu128`
- torchvision: `0.25.0+cu128`
- CUDA build: `12.8`
- CUDA kernel probe: `true`
- Observed model devices: YOLO `cuda:0`; EfficientNet `cuda:0`
- Minimum free VRAM during the memory phase: `3,101,749,248` bytes (2.89 GiB)
- Combined output vector: `0,0,12,8,0,4,6,9,4,6,5,0`; 13 secondary candidates
- Maximum deltas: box `1.19e-07`, confidence `1.64e-06`, secondary `5.96e-07`

The raw folder is retained in full, including failed runs. No raw logs,
provider material, credentials, models, or licensed fixture imagery are
committed here.
