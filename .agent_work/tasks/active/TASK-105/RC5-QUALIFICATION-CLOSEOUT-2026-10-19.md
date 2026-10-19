# RC5 Qualification Closeout

**Prepared**: October 19, 2026
**Task**: TASK-105
**Outcome**: Two-host functional results credited; bounded acceptance approved October 19
in [ADR-026](../../../decisions/026-rc5-bounded-candidate-acceptance.md).
The owner approved reviewed commit `33bd3a3`. Draft-PR review, task closure,
and official adoption remain pending.

## Exact candidate and public-byte recheck

| Identity | Value |
| --- | --- |
| Fork candidate | Immutable, non-Latest `v0.1.3-rc5` |
| Source and tag target | `835cbb910573a931350c5b704d14496952d7ef87` |
| CPU image | `sha256:833dbe0d0097ffcc9e52dcf39d64f25cf503c3c9ffc806f55c42b60e452845d5` |
| CUDA image | `sha256:df0f30ac1bed4514d50c5b11eeac4ea64e38e6575bb209448fea4c53e5347890` |
| CPU ZIP SHA-256 | `dfcc653eef4d0c9666604d6455797c123b757d92d4507ad1d451032f5cdd7a8f` |
| CUDA ZIP SHA-256 | `c418e1948ed2719cd8c3678b612addccf468a139aafc97f99d3f4bd7676974d0` |
| Asset ZIP SHA-256 | `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb` |

The October 19 read-only GitHub API check found the same source on `main`, the
same direct commit tag, immutable prerelease status, and the same six asset
digests/sizes. All six original first-host browser downloads were rehashed
and matched. `gh release verify v0.1.3-rc5` verified the signed release
attestation. Latest still resolved to `v0.1.2`. These checks changed no remote
state and did not rescan image vulnerabilities.

Existing accepted-source CI runs `38608395091` and `38608394922` reported
success. CPU/CUDA publish runs `38609314677` and `38609372836` reported success.
Their October 14 strict security results were baseline 396, candidate 79,
five exact accepted residuals, zero blockers/escalations. These are dated
scan results; official build/publication requires fresh security evaluation.

## Evidence map

- [First-host checkpoints](../TASK-105-final-release-correction-and-qualification.md)
  bind exact browser files, extraction markers, 74 internal checksums, actual
  models, providers, UI observations, exported-file parsing, and lifecycle.
- [Independent-host intake](RC5-INDEPENDENT-HOST-EVIDENCE-INTAKE-2026-10-16.md)
  binds the report and archive, 108 verified manifest rows, 61 parsed JSON
  files, and the owner's October 16 restore clarification.
- Private first-host probe JSON/logs remain ignored under task-owned `dist`.
  Independent raw logs, screenshots, exports, and credentials remain under
  owner custody outside tracked evidence. No AOI or key values enter this file.

## Functional matrix

Each profile ran the CPU or CUDA image pinned above, with eight named volumes
and both Google/Azure providers. `FIRST-HOST-LOCAL` uses the RTX PRO 500
Blackwell Laptop GPU; `INDEP-HOST-01` uses the T1000 8GB.

| Profile | First host | Independent host |
| --- | --- | --- |
| Docker CPU | Package, both models on CPU, both providers, browser exports/cancel/ZIP, restore, relaunch/reboot passed | Real CPU models, both providers, Edge exports/cancel, relaunch/reboot passed; restore owner-confirmed |
| Docker CUDA | Both models on CUDA, fixture/kernel/fault recovery, both providers, browser workflows and lifecycle passed | Both models on CUDA `sm_75`, no fallback, both providers, late-cancel/export and lifecycle passed; restore owner-confirmed |
| Podman CPU | Rootless selected provider, both models on CPU, both providers, browser workflows, restore and lifecycle passed | Same functional result after short-path relocation and explicit Python 3.12; restore owner-confirmed |
| Podman CUDA | Missing-image pull, CDI, both models on CUDA, providers/UI, restore and lifecycle passed | First CUDA pull/provisioning passed; both models on CUDA, providers/UI/lifecycle passed in short path; restore owner-confirmed |

First-host CPU/CPU-Podman/CUDA/CUDA-Podman combined probes used the identical
12-tile fixture and passed expected normalized outputs with 54 detections.
One-warm-up/three-measured medians were respectively 49.606243, 44.923575,
2.633402, and 2.508349 seconds. Independent HTTP same-area runs consistently
produced Azure 48 and Google 40 detections, all with secondary scores and
stable confidence fingerprints across profiles/relaunch/reboot. The live
counts are not substituted into the frozen-fixture expected-output contract.

Independent-host frozen-fixture/warm measurements and formal fault/negative
probe reports are not in its packet. ADR-026 accepts first-host
exact-image proof plus independent live-model/device comparisons for this
candidate. It also explicitly lists reused first-host ZIP/TLS/recovery proof.
The approved exceptions do not claim that the omitted formal tests were run.

## RC9 correction dispositions

| ID | Result and remaining boundary |
| --- | --- |
| F1 | Fixed: missing Podman GPU image pulled before CDI smoke; independent provisioning took 237 s and passed |
| F2 | Coexistence instructions exercised through repeated engine switches; first-host machine recovery passed; independent post-login collision not reproduced |
| F3 | Fixed: provider hashing/installation ran from Windows PowerShell 5.1 and inherited PowerShell 7 parents on the independent host |
| F4 | Fixed retry/promotion: injected failure, interrupted install, ordinary retry and idempotence passed in short path; N9 path regression and N10 orphan staging remain |
| F5 | Fixed: shipped setup/status reported the selected package-local Compose provider while global provider differed |
| F6 | Verified unchanged production behavior: late server completion was discarded by both CUDA browser sessions; retry succeeded |
| F7 | Fixed: separate CSV/KML/dataset controls, correct MIME types, one download per action, valid output structures |
| F8 | Corrected imagery/geocoding wording; inactive limit display and unexercised limit-log case explicitly retained as known issues |
| F9 | GPU/tested rootless/Python boundary present; addendum supplies missing explicit Python selection; no rootful/other-Python qualification |
| F10 | Stable frontend source fingerprint verified across profiles; Windows ZIP separators documented; no whole-ZIP bit-reproducibility claim |

## Accepted new-finding dispositions

| ID | Disposition |
| --- | --- |
| N1 | Defer inactive geocoding-limit message; document coordinate-only results |
| N2 | Defer misleading clear-all/provider-lock behavior; export current work before reload, then restore as needed |
| N3/N4 | Defer misleading Network error/duplicate text after cancellation or over-cap input; terminal outcome and next request passed |
| N5/N6 | Defer map/search-box and download-label cosmetics; map and separate exports worked |
| N7 | Record late-cancel geocoding can continue and consume requests despite discarded results |
| N8 | Record GPU free-memory log label is not actual free device memory |
| N9 | Restrict RC5 to short local Podman package paths per addendum; failed longer-path installation remains a failure, not a pass |
| N10 | Defer orphan staging-folder housekeeping; retry works; no blanket folder sweep |
| N11 | Record Podman Desktop transient machine-state warning; documented CLI start used after reboot |
| N12 | Record WSL/connection-closing client limitation; large browser ZIP passed CRC; ultimate host-change cause not established |
| N13 | Defer internal diagnostic path written inside the package by GPU provisioning; no user-data impact established |
| N14 | Document existing `-Python` selection; tested Python 3.12 only |

## Closeout and adoption gates

| Item | State / owner action |
| --- | --- |
| Two-host functional evidence and restore clarification | Credited with provenance above |
| Test-method and known-limitations acceptance | Owner approved ADR-026 in reviewed commit `33bd3a3` on October 19 |
| Supplemental operations/release/handoff docs | Draft-PR publication authorized; review and merge pending |
| Exact candidate source/tag/public bytes | Reverified October 19; unchanged |
| New code/image/package correction | None selected for this closeout |
| Official identity, target source and cdcai adoption | Project lead + cdcai owner approval pending |
| Official images/packages | Not built/published by this closeout; new identities and fresh scans required |
| Support/security custodian and backup | Confirm named contacts privately before handoff |
| October 31 residual expiry | Maintenance owner must resolve or renew through a new written decision |
| Task closure | Tasks 091/092/093/095/097/103/104/105 remain active until their actual adoption/handoff obligations are met |

## Review payload

Review this record with ADR-026, the updated candidate notes, the
[operations addendum](../../../../docs/release/rc5-operations-addendum.md), and
[cdcai handoff](../../../../docs/release/task105-cdcai-handoff.md). These source
documents are not retroactively present in RC5's immutable downloads.
The owner approved acceptance and publication of this review branch separately.
Approval to build or publish an official release remains pending.

## Preparation verification

On October 19 the strict agent-work validator and documentation command checker
passed. Local links in the changed/new Markdown files all resolved.
All four PowerShell examples in the operations addendum parsed without syntax
errors; the read-only interpreter-selection example selected 64-bit Python
3.12.10, and static parsing confirmed the shipped helper's `-Apply`/`-Python`
parameters. Credential-pattern checks printed counts only and found zero
Google/GitHub-token, private-key, key-bearing URL, or unredacted user-path
matches in the edited documents. No runtime/container/installer mutation was
performed to validate this documentation update. `git diff --check` passed.
