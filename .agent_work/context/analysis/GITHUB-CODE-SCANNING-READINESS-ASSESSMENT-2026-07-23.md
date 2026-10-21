# GitHub Code-Scanning Readiness Assessment

**Date**: July 23, 2026
**Repository**: `J-Schulein/TowerScout`
**Source**:
[GitHub code-scanning alerts](https://github.com/J-Schulein/TowerScout/security/code-scanning)
**Tool**: Trivy filesystem scan uploaded by `.github/workflows/ci.yml`
**Scope**: All alerts that GitHub reported as open on `refs/heads/main`
**Alert Commit**: `bce9dab585e839f9adead32b9aee38410d046ae7`

**Task-090 Follow-Up**: The authenticated 62-record reconciliation,
function-level dispositions, and proposed Task-098 scope are now recorded in:

- [`alert-disposition.md`](../../tasks/completed/TASK-090/alert-disposition.md)
- [`remediation-scope.md`](../../tasks/completed/TASK-090/remediation-scope.md)

## Decision Summary

The 62 open records are real dependency alerts, not 62 independent TowerScout
code defects. They reduce to eight direct Python packages in
`webapp/requirements.txt`.

Do not stop before Task-090 to patch alerts ad hoc. Make the alert inventory,
reachability review, and release classification the first Task-090 workstream.
Then use Task-098 for approved dependency remediation and compatibility
validation.

Task-087 and later runtime feature work may proceed only after:

- every alert has a recorded classification
- no release-blocking critical or high finding remains unresolved
- patchable mandatory findings pass regression and package validation
- any residual critical/high risk has written project-lead/cdcai-owner
  acceptance with compensating controls and a follow-up disposition

The release gate is not “GitHub must display zero alerts.” Some alerts describe
server APIs TowerScout does not use, local-only functions TowerScout does not
call, scanner version-range ambiguity, or findings without a usable fixed
version. The gate is zero **unresolved release-blocking** findings plus an
evidence-backed disposition for every remaining record.

## Inventory

GitHub reported:

| Severity | Open records |
| --- | ---: |
| Critical | 4 |
| High | 16 |
| Medium | 25 |
| Low | 17 |
| **Total** | **62** |

Package grouping:

| Package | Installed | Alerts | Severity mix | Scanner fixed-version direction |
| --- | --- | ---: | --- | --- |
| `aiohttp` | `3.9.3` | 33 | 1 critical, 3 high, 16 medium, 13 low | Up to `3.14.1`, depending on CVE |
| `Pillow` | `12.2.0` | 13 | 10 high, 3 medium | `12.3.0` |
| `torch` | `2.2.1` | 9 | 1 critical, 5 medium, 3 low | Mixed; critical `torch.load` finding fixed in `2.6.0` |
| `fiona` | `1.9.6` | 2 | 1 critical, 1 high | Scanner cites `1.10b1`/`1.10b2` |
| `waitress` | `3.0.0` | 2 | 1 critical, 1 high | `3.0.1` |
| `geopandas` | `0.14.3` | 1 | 1 high | `1.1.2` |
| `python-dotenv` | `1.0.0` | 1 | 1 medium | `1.2.2` |
| `Flask` | `3.0.2` | 1 | 1 low | `3.1.3` |

No alerts were dismissed or otherwise changed during this review.

## Provisional Applicability

### Patch-oriented group

These packages have direct TowerScout use and scanner-identified fixed
versions that should be tested as the first remediation slice:

- `Pillow`: TowerScout opens user-selected images and provider tiles. Many
  listed formats or APIs are not exposed by TowerScout, but `12.3.0` is a
  narrow patch target and removes 13 records.
- `waitress`: this is TowerScout's production WSGI server. The critical
  pipelining race depends on request lookahead that TowerScout does not enable,
  but the high CPU-exhaustion finding is on a live server boundary and `3.0.1`
  is a narrow patch target.
- `aiohttp`: TowerScout uses it as an outbound Google/Azure tile client, not as
  its inbound server. Most server-request findings are therefore not reachable,
  but the critical response-header parsing finding is client-relevant. Upgrade
  and provider/download regression testing are required.

### Significant compatibility decision

[`CVE-2025-32434`](https://github.com/J-Schulein/TowerScout/security/code-scanning/31)
is a critical `torch.load(..., weights_only=True)` remote-code-execution
finding fixed in PyTorch `2.6.0`.

TowerScout does load model checkpoints. Current controls materially reduce
exposure:

- release assets and individual model files are checksum-controlled during
  setup/import
- normal users receive the known release asset bundle
- model upload is disabled by default
- the EfficientNet path requests `weights_only=True`

Those controls do not remove the vulnerable library behavior, and the vendored
YOLO checkpoint path requires full-object loading. A PyTorch upgrade also
affects `torchvision`, the CPU/CUDA wheel pair, the current CUDA 12.1 publish
flavor, YOLO compatibility, model loading, and all four final runtime profiles.

Task-098 should attempt a coordinated supported upgrade. If that cannot be
qualified safely within the release schedule, residual acceptance must be an
explicit owner decision backed by checksum enforcement, default-disabled model
upload, documented trusted-model rules, and a future upgrade item. It must not
be silently treated as cleared.

### Likely non-reachable or lower-priority group

- The `geopandas` high finding concerns `to_postgis()` SQL construction;
  TowerScout only uses `geopandas.read_file()` for the packaged ZIP-code
  shapefile.
- The `fiona` findings concern bundled GDAL/MiniZip handling of untrusted ZIP
  content; TowerScout reads a packaged `.shp` dataset through GeoPandas.
  Confirm the installed wheel/GDAL provenance and whether a stable compatible
  upgrade exists before disposition.
- The `python-dotenv` finding concerns `set_key()`/`unset_key()` following a
  local symlink. TowerScout imports `load_dotenv()`/`dotenv_values()` and uses
  its own controlled configuration writer.
- The Flask finding depends on a caching-proxy/session pattern outside the
  documented single-user local package.
- Several PyTorch medium/low alerts concern APIs TowerScout does not call and
  some lack a fixed version. Record function-level evidence rather than
  upgrading blindly to satisfy a raw count.

These provisional conclusions must be verified and recorded per alert in
Task-090 before any alert is dismissed or accepted.

## Required Task-090 Output

Task-090 must produce:

1. a 62-record disposition table keyed by GitHub alert number
2. package and call-path reachability evidence
3. a distinction between application dependency alerts and container-image/OS
   findings
4. a proposed Task-098 patch/upgrade matrix with compatible versions
5. regression requirements for providers, uploads, model loading, CPU/GPU,
   Docker, and Podman
6. an owner decision packet for any residual critical/high risk
7. a recommendation for CI policy after the baseline is understood

CI currently uploads Trivy SARIF with `continue-on-error: true`. Do not make
the existing 62-alert baseline merge-blocking before the baseline is
classified. After Task-098, ratchet CI so new critical/high dependency
findings fail the security job or require an explicit time-bounded exception.

## Schedule Effect

This work belongs before Task-087 resumes because dependency changes can alter
the same runtime images and four-profile qualification baseline. It does not
justify resolving every alert before Task-090; Task-090 is the mechanism for
deciding what truly requires remediation.

Reforecast Phase 1 after the Task-090 classification. Preserve the September 18
code-complete, September 25 package/documentation-complete, and October 9 freeze
controls. Task-058/059 capacity remains subordinate to Tasks 090/098 and all
required release work.
