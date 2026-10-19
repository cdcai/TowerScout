# RC5 Candidate And cdcai Handoff Packet

**Prepared**: October 19, 2026
**Status**: Bounded candidate accepted October 19; fork draft-PR review and official adoption pending
**Operational closeout target**: October 30, 2026

## What is ready for review

The fork's immutable, non-Latest `v0.1.3-rc5` has four-profile functional
evidence on two separate Windows NVIDIA hosts. The owner confirms independent
dataset download/restore and repeated same-area model comparisons. Exact
identities and tested scope are in the [candidate notes](task105-candidate-notes.md).
The [operations addendum](rc5-operations-addendum.md) supplies the short Podman
layout, explicit Python selection, lifecycle/recovery, and known issues.

The accepted decision is [ADR-026](../../.agent_work/decisions/026-rc5-bounded-candidate-acceptance.md).
The [closeout matrix](../../.agent_work/tasks/active/TASK-105/RC5-QUALIFICATION-CLOSEOUT-2026-10-19.md)
distinguishes measured tests, owner confirmations, accepted evidence reuse,
and deferred findings. The owner approved bounded candidate qualification in
reviewed commit `33bd3a3`; official adoption remains separate. These supplemental files are absent from
the immutable RC5 ZIPs and in-app Help; any approved RC5 handoff must include them.

## Artifact inventory

Use the six files at the fork's
[RC5 release](https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.3-rc5):

- `towerscout-v0.1.3-rc5-cpu.zip` and its `.sha256` sidecar;
- `towerscout-v0.1.3-rc5-cuda128.zip` and its `.sha256` sidecar;
- `towerscout-v0.1.3-rc5-assets-towerscout-v1-assets-2026-05-05.zip` and its
  `.sha256` sidecar.

The candidate source is `835cbb910573a931350c5b704d14496952d7ef87`.
The candidate notes bind each ZIP and both image digests. On October 19 the
tag, six asset digests/sizes, retained browser files, and signed release
attestation matched. Latest remained `v0.1.2`. Security scans were successful
on October 14; that dated result is not a substitute for a fresh official scan.

Do not rebuild or upload replacement bytes under RC5. Keep the unchanged
`v0.1.2` pilot available through official adoption.

The packaged `SBOM.txt` is a reference/placeholder, not a complete embedded
software inventory. Preserve its accurate description and the release-specific
scan/SBOM artifacts retained with the image workflow evidence. The official
owner must decide and document their durable publication/custody location.

## Maintenance responsibilities

| Responsibility | Current custody / handoff action |
| --- | --- |
| Candidate decisions and acceptance | `J-Schulein` approved ADR-026 in reviewed commit `33bd3a3` on October 19 |
| Official repository, tag/title, namespace, publication | Project lead and cdcai owner select and explicitly approve |
| User support and backup contact | Confirm named people and access privately; prior pilot contacts are not assumed to accept new obligations |
| Provider subscriptions, key restrictions and billing | Site/account owner confirms approved accounts; transfer through approved private channels |
| TLS trust and managed-endpoint approval | Site IT maintains approved trust and endpoint policy |
| Model/data assets and notices | Maintainer preserves verified asset hash, notices, and access |
| Evidence custody | Owner preserves private raw evidence; repository holds sanitized indexes and decisions |
| Security follow-up | `J-Schulein` currently; cdcai assumes it only when a maintainer accepts handoff |

The exact five ADR-024 HIGH residual entries expire at
**2026-10-31T23:59:59Z**. The receiving maintainer must re-evaluate fixes and
reachability, rebuild where appropriate, or obtain a new written disposition
before relying on an expired acceptance for a new publication. An available
fix, changed identity/severity, or additional blocking finding triggers review
earlier. Keep the committed 396-key baseline and fail-closed comparator.

ADR-022's torch 2.10.0/torchvision 0.25.0 CUDA 12.8 bridge also has a review
trigger at **January 31, 2027**, or the first evaluation of torch >=2.14.1,
whichever comes first. Security/support changes can trigger earlier review.
Record the person accepting these obligations before operational closeout.

## Official adoption sequence

1. Bounded candidate acceptance and fork draft-PR publication are authorized.
   Review the supplemental instructions, sanitized evidence, and source-document
   changes. Publish/merge only within
   the authorized fork review scope. Task-087/PR #67 remains deferred.
2. The project lead and cdcai owner choose the official tag, display title,
   image namespace, release visibility, target source, and support custodian.
   Record separate approval before any cdcai repository mutation or dispatch.
3. Review the complete delta from candidate source `835cbb9` to the selected
   official source. This review branch changes evidence and guidance only;
   it is not automatically the official source. Incorporate the accepted
   short-path/Python guidance into the official package and served Help.
   The ZIP builder has an explicit document allowlist: merge the guidance into
   its included manuals or deliberately include the supplement. Resolve
   source-only tracking links to durable reviewed-source references before
   packaging; `.agent_work` is not shipped inside the control ZIP.
4. Build official CPU/CUDA images and packages consistently with the selected
   identity. Run the existing strict local scan before registry login/push,
   verify the exact published digest/config identity, and rescan both digests.
   Preserve manifests, source/SBOM and license/model/data/provider notices.
5. Publish official assets only with separate owner authorization. Download
   the actual public bytes in a browser, verify authoritative hashes,
   extraction markers and internal checksums, and run affected package/Help/
   provider/device/lifecycle checks on those bytes. Document which candidate
   tests carry forward and why the official delta does not affect them.
6. Confirm support access, recovery/rollback, private evidence custody, and
   maintenance deadlines. Obtain any stable/Latest authorization separately,
   then close each task only when its own obligations are fulfilled.

## Evidence reuse review for official bytes

| Official change | Proof required before carrying candidate evidence |
| --- | --- |
| Tag/title/namespace/source notices | Verify every identity reference and published digest; do not call candidate ZIPs official |
| Accepted operating text and in-app Help | Check packaged Markdown/HTML, served Help parity, paths and commands on official bytes |
| Rebuilt base or dependency versions | Fresh security and actual-model/device checks; assess output/performance deltas |
| Installer, compose, TLS, provider or frontend code | Focused regression plus affected real package/browser/profile reruns |
| Model/data hash or inference settings | New model correctness/device/output comparison and affected workflow tests |

A small documented delta can reuse unaffected evidence. Identity-only reuse
still requires exact official-byte integrity and security checks. The owner
accepted decision does not waive failed or changed-image checks.

## Recovery and rollback handoff

Use the original package folder, connection, project, port, and named volumes.
Export a dataset before migration; keep the old installation and its volumes.
Stop the selected test-owned app through its shipped script. If returning to
the pilot, use its own retained package/configuration and approved engine.
RC5 and v0.1.2 have distinct ML/runtime identities; do not point either package
at the other's volumes or assume an untested volume-schema downgrade works.
For result transfer use the tested dataset restore path, with the receiving
application's compatibility confirmed. A dataset is not a backup of provider
keys, models, or the engine's eight volumes.

Coordinate any full volume backup or migration with the maintainer. Factory
reset, volume pruning, and blanket deletion are excluded from recovery.

## Task closure checklist

| Task | Remaining closeout responsibility |
| --- | --- |
| 091 | Record accepted matrix/method exceptions and official artifact qualification |
| 092 | Incorporate supplemental guidance into official docs/Help; reconcile external Setup Guide/demo deliverables and owner acceptance |
| 093 | Preserve restore/recovery evidence and hand off volume/rollback procedures |
| 095 | Confirm receiving custodian, navigation, governance and deferred backlog |
| 097 | Accept short-path/Python/rootless Podman scope and official affected reruns |
| 103 | Reconcile exact official identities and transferred ML bridge obligations |
| 104 | Fresh official security gates and accepted residual maintenance owner |
| 105 | Approved bounded candidate, reviewed packet, official adoption/qualification and handoff |

Task-089 cdcai migration stays gated by explicit adoption approval. No task is
closed merely because this packet has been prepared.
