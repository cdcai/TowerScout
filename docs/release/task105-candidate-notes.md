# Task-105 Candidate Notes — Closeout Review

The corrected Windows 11 CPU and CUDA 12.8 validation candidate is the
immutable, non-Latest `v0.1.3-rc5` prerelease from accepted `main`
`835cbb910573a931350c5b704d14496952d7ef87`. Its exact browser-downloaded
control and asset ZIPs passed first-host integrity checks. Docker CPU/CUDA and
Podman CPU/CUDA passed real model and provider workflows, lifecycle checks,
and reboot persistence on that host. The separate NVIDIA host also completed
all four functional profiles, with short-path/Python deviations recorded and
dataset restore confirmed by the owner. Bounded acceptance of those deviations
and the comparative model-test method was approved on October 19 under
[ADR-026](../../.agent_work/decisions/026-rc5-bounded-candidate-acceptance.md)
following review of commit `33bd3a3`. RC9 is historical evidence. Official cdcai
adoption, build, publication, and any Latest promotion remain separate gates.

The [operations addendum](rc5-operations-addendum.md) and
[handoff packet](task105-cdcai-handoff.md) are prepared supplements. They are
not inside the immutable RC5 downloads or served Help. An approved handoff of
RC5 must include the accepted supplement; an official package must incorporate
equivalent guidance and receive its own verified identity.

| Published input | SHA-256 |
| --- | --- |
| CPU control ZIP | `dfcc653eef4d0c9666604d6455797c123b757d92d4507ad1d451032f5cdd7a8f` |
| CUDA 12.8 control ZIP | `c418e1948ed2719cd8c3678b612addccf468a139aafc97f99d3f4bd7676974d0` |
| Shared asset ZIP | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |

The CPU image digest is
`sha256:833dbe0d0097ffcc9e52dcf39d64f25cf503c3c9ffc806f55c42b60e452845d5`;
the CUDA image digest is
`sha256:df0f30ac1bed4514d50c5b11eeac4ea64e38e6575bb209448fea4c53e5347890`.
The three `.sha256` sidecars and internal package checksums also passed.

## Tested GPU evidence

- NVIDIA RTX PRO 500 Blackwell Generation Laptop GPU (`sm_120`): the RC5
  first host passed Docker and rootless Podman CUDA 12.8 workflows with both
  YOLO and EfficientNet on CUDA and no CPU fallback.
- NVIDIA T1000 8GB (`sm_75`): the independent RC5 host ran Docker and rootless
  Podman CUDA 12.8 with both models on CUDA and no fallback. It used Windows
  11 Pro 23H2 build 22631.6199, driver 616.92, WSL 3.0.3, Docker Desktop 4.95.0
  (Engine 29.8.2), and Podman CLI 6.1.4/server 6.0.2. Podman used explicit
  Python 3.12.10 and the short-folder workaround.

These are GPU models observed in the RC5 two-host evidence,
not a blanket claim for every driver, Windows build, WSL version, or engine
version. CPU-only hardware and Podman without Docker Desktop installed are
outside the tested claim. The CUDA package expects Volta or newer; an architecture present in a
wheel alone does not qualify an untested GPU. Maxwell and Pascal use the CPU
package.

## Tested support boundary

The tested Podman path uses a rootless WSL 2 machine, 64-bit Python 3.12,
TowerScout's package-local Compose provider, and NVIDIA CDI for GPU work.
The accepted RC5 restriction uses a short local package-root path (80
characters or fewer) and explicit interpreter selection; see the addendum.
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

## Qualification evidence and limits

The [closeout matrix](../../.agent_work/tasks/active/TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md)
binds exact identities and evidence. On October 19 the six original browser
downloads again matched GitHub's asset digests/sizes, the accepted commit tag,
and signed release attestation. The release remained immutable and non-Latest.

The first host ran the frozen combined-model fixture, expected-output checks,
warm measurements, CUDA-unavailable negative and classifier fault/recovery.
The independent host ran both models/providers against a repeated public area,
with stable HTTP detection counts/fingerprints across profiles and lifecycle
checkpoints. Those live comparisons are not an independent frozen-fixture
benchmark. ADR-026 accepts that precise evidence substitution for this
candidate; no extra benchmark result is claimed. Security scan results are
dated October 14, and official publication requires fresh security checks.
