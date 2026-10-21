# Official build and verification plan - review draft

**Date:** October 21, 2026. **Task:** TASK-089 / TASK-105.
This plan does not dispatch builds or authorize publishing. Use the exact
reviewed cdcai merge source and ADR-022 through ADR-026 at execution.

## Identities and order

1. Review the final adoption PR and agree a history-preserving merge. Check
   remote heads, tag/release availability, support destination and permissions.
2. Record the exact accepted cdcai merge SHA. Proposed official tag/title remain
   `v0.1.3` / `TowerScout v0.1.3 - First Official cdcai Release`.
   If validation requires corrections after publication, use a new approved
   candidate identity; never overwrite immutable tag/assets or assume the
   same name can be reused. Decide candidate-versus-final tagging before dispatch.
3. From the same frozen source, build CPU and cuda128 images under
   `ghcr.io/cdcai/towerscout` with `push_latest=false`. Run the strict local
   security gate before registry login/push. Preserve scan/tool/DB/source IDs.
4. After authorized versioned publication, verify config/source/flavor identity
   against the local image and rescan each exact registry digest. Verify package
   repository linkage and anonymous public pull. A mutable tag is not a digest.
5. Assemble CPU/cuda128 control ZIPs from clean tracked source with actual pinned
   image digests and verified shared-asset identity. Preserve model/data notices;
   do not substitute unreviewed local weights. Verify manifests, internal hashes,
   external SHA-256 sidecars, source references and software inventory evidence.
6. Publish authorized validation downloads without prematurely recommending them
   or promoting Latest. Download the exact hosted bytes through a browser;
   compare authoritative hashes before extraction and retain download markers.
7. Execute the matrix below, record failures and corrected-candidate identities,
   and review acceptance. Promote/recommend only after explicit approval.

## Delta and evidence reuse

| Change or unchanged area | Required new evidence | Prior evidence use |
| --- | --- | --- |
| Registry/release namespace and package identity | Correct cdcai source labels, exact digest pulls, public access, manifests and browser download checks | Fork hashes and publication proof are historical only |
| Four CPU defaults | Explicit image/digest precedence, environment-file resolution and clean unset fallback | Existing 63 selected static/mocked checks support source review, not deployment readiness |
| Manuals/wiki/support destinations | Packaged Markdown/HTML and in-image Help parity; live official links; Podman short path and explicit Python 3.12 instructions | Fork rendering can inform layout; cdcai destinations require their own checks |
| Rebuilt images/system dependencies | Fresh CPU/CUDA scans; exact-image model/device/provider checks | Unchanged Dockerfile/runtime code does not prove identical installed dependencies |
| Unchanged application/model source at ca24d6f | Verify final source delta again; compare actual assets/dependencies and affected behavior | ADR-026 describes exact fork candidate acceptance; cite retained results only where the owner accepts a specific reuse rationale |
| Organization/governance/Codecov uploader removal | Link/task consistency and CI checks; allowlist and coverage-artifact review | No application behavior change inferred; no fresh runtime pass claimed |

## Proposed operational qualification

Default to all four profiles on this Windows NVIDIA host and the independent
NVIDIA host: Docker CPU, Docker CUDA, Podman CPU, Podman CUDA. Confirm tester
availability early. Any reduction or method reuse needs an explicit documented
delta decision; ADR-026's fork-specific exceptions do not automatically carry over.

For each applicable profile record exact ZIP/hash, source/image digest, engine,
host/device, setup and asset import, both model execution, intended CPU/CUDA
selection, Google/Azure workflows, detection/review, CSV/KML export, dataset
download/restore, cancellation/retry and recoverable failure. Verify stop/start,
configuration/assets/volumes retention, reboot persistence and engine switching
with preserved installations. Use owned test project names and ports; do not
delete existing volumes or weaken machine security to make a result pass.

Record real model/device outcomes, not merely health endpoints or mocked tests.
Preserve the unsigned-wrapper support boundary, Podman root <=80 characters,
explicit 64-bit Python 3.12 provider prerequisite, and tested-hardware limits.
Docker users do not need host Python for the normal packaged route.

## Wiki and final delivery

Retain the fork wiki clone and verified manifest. Recheck cdcai immediately
before initialization; preserve any newly introduced pages. Publish reviewed
official source pages separately from the code PR, with current release/support
links and correct publication labels. Check all pages, sidebar, anchors and
external destinations anonymously. Do not copy fork-preview banners or pinned
fork-manual links into the official wiki.

The user proved a 65 MB upload/display in cdcai's new-page preview, then discarded
the page. Record the final Docker/CPU video only after the demonstrated official
workflow is verified. Check the actual published MP4/player, seeking, readability
and anonymous access; provide a direct watch/download fallback if needed.

Record Chris's access to the release, wiki, owner guidance, backlog, maintenance
calendar and private evidence. Acceptance and receipt are separate from general
ownership. Keep October 31 security expiry visible; do not automatically renew.
