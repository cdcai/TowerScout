# Task-103 `rc4` Cleanup Inventory - 2026-10-02

**Scope**: First-host Docker, Task-103 Podman, repository build/evidence trees,
and the browser-download diagnostic folder
**Decision**: Remove only verified-stopped container records and test-owned
temporary files now. Preserve named volumes, images, build cache, release
packages, and qualification evidence until the documentation-aligned candidate
is built, validated, and no longer needs the rollback/regression baseline.

## Actions Completed

- Stopped/removed the browser-download diagnostic container through its package
  wrapper. Its eight named volumes remain.
- Verified eight historical Docker TowerScout containers were `exited`, with
  eight named volume mounts each, then removed only those container records.
- Verified five Task-103 Podman TowerScout containers were `exited`, with eight
  named volume mounts each, then removed only those container records.
- Removed two exact pytest temp trees created during this session. One was
  empty; the other contained 6078 bytes of test-owned temporary data.
- Did not run Docker/Podman system prune, image prune, builder prune, volume
  prune, or machine removal.

The container record removals are not recoverable as records, but their images,
named-volume data, package inputs, and written qualification evidence remain.
The containers can be recreated from their exact retained packages/Compose
projects if needed.

## Post-Cleanup Engine Inventory

### Docker

| Class | Count | Reported size | Current disposition |
| --- | ---: | ---: | --- |
| Containers | 0 | 0 B | 8 verified-stopped records removed, plus the diagnostic container removed by its wrapper |
| Images | 27 | 151.6 GB | Retained; Docker reports 145.8 GB reclaimable because no container currently references them |
| Named volumes | 104 | 13.8 GB | Retained; now reported reclaimable because containers were removed |
| Build cache | 136 records | 50.47 GB total; 4.162 GB reclaimable | Retained to avoid slowing/risking the documentation-aligned rebuild |

The image and volume reclaimable labels mean “not referenced by a current
container,” not “unneeded.” They include exact `rc4`, rollback, historical
qualification, and provider/persistence state.

### Task-103 Podman Machine

| Class | Count | Reported size | Current disposition |
| --- | ---: | ---: | --- |
| Containers | 0 | 0 B | 5 verified-stopped records removed |
| Images | 8 | 46.67 GB | Retained |
| Named volumes | 56 | 6.741 GB | Retained |

Podman machine inventory also showed:

- `towerscout-task103`: running, configured disk size 100 GiB;
- `podman-machine-default`: stopped, configured disk size 100 GiB; and
- `towerscout-task087-rootless`: never started, configured disk size 100 GiB.

Those configured sizes are VM capacity settings, not proof of physical bytes
currently allocated. No machine was started, stopped, switched, or removed for
cleanup. The Task-103 machine remains the exact Podman regression environment.

## Repository And Download Trees

| Path/class | Measured bytes | Approximate size | Disposition |
| --- | ---: | ---: | --- |
| `dist/` | 13,407,722,175 | 12.49 GiB | Retain through documentation-aligned rebuild/validation |
| `.agent_work/tmp/` after test cleanup | about 6,998,744,346 before removing 6078 bytes | 6.52 GiB | Retain qualification evidence and package sources |
| Browser diagnostic folder under Downloads | 1,120,053,376 | 1.04 GiB | Retain exact browser-downloaded/extracted evidence until final handoff |

Largest `dist/` entries at inventory time:

- `v0.1.3-rc3-w09-final`: 5,309,603,533 bytes;
- `v0.1.3-rc1-w09`: 3,077,580,186 bytes;
- `v0.1.3-rc1-w09-final`: 3,069,462,736 bytes;
- `v0.1.3-rc1-w10-local`: 1,122,021,403 bytes; and
- `v0.1.3-rc4-w09-final`: 802,338,640 bytes.

Largest `.agent_work/tmp/` entries at inventory time:

- `Task 103 RC4 W09`: 5,308,266,040 bytes, including the four extracted
  profile packages and one shared 800,655,295-byte asset ZIP;
- `task103-rc3-package-source`: 920,291,598 bytes; and
- `task103-rc4-package-source`: 411,629,842 bytes.

These directories are large, but their names alone do not establish that they
are disposable. They bind W09/W10 package construction, exact bytes, and
regression/rollback evidence.

## Deferred Cleanup Order

After the documentation-aligned CPU/CUDA images and control ZIPs have new
identities and pass the required package/browser/independent-host gates:

1. Confirm which `rc4` package/evidence copy remains the canonical retained
   regression baseline.
2. Preserve hashes, manifests, evidence indexes, and any owner-required offline
   archive before deleting duplicate extracted/package-source trees.
3. Remove explicit superseded RC1/RC3 `dist/` directories only after release
   owner confirmation; never use a broad workspace delete.
4. Remove explicit superseded Docker/Podman images only after confirming the
   final images and rollback requirement. Keep digest identities in evidence.
5. Remove build cache last; it is safe to recreate but useful during the
   imminent rebuild.
6. Delete named volumes or Podman machines only through a separately approved
   destructive data-custody decision. Do not use broad prune as a substitute
   for that inventory.
