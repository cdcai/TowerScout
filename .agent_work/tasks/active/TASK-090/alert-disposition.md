# Task-090 Trivy Alert Disposition

**Retrieved**: 2026-07-23T17:25:55-04:00
**Repository**: `J-Schulein/TowerScout`
**Query**: open alerts; `ref=refs/heads/main`; `tool_name=Trivy`
**Alert commit**: `350d56deec7c85545386e3120c1896d48ba20b39`
**Trivy version in alerts**: `0.69.3`
**Result**: 62 open alerts

## Reconciliation

The authenticated GitHub API returned exactly the 62 alerts recorded by the
July 23 readiness assessment. GitHub alert numbers are non-contiguous:
`1`, `6-29`, `31-35`, and `41-72`.

All 62 locations are direct Python pins in `webapp/requirements.txt`. This
filesystem-scan baseline contains no container-image or operating-system
package findings.

| Severity | Alerts |
| --- | ---: |
| Critical | 4 |
| High | 16 |
| Medium | 25 |
| Low | 17 |
| **Total** | **62** |

| Package | Alerts | Release-blocking | Required hardening | Not reachable |
| --- | ---: | ---: | ---: | ---: |
| `aiohttp` | 33 | 1 | 0 | 32 |
| `Pillow` | 13 | 2 | 1 | 10 |
| `torch` | 9 | 1 | 0 | 8 |
| `fiona` | 2 | 0 | 0 | 2 |
| `waitress` | 2 | 1 | 0 | 1 |
| `geopandas` | 1 | 0 | 0 | 1 |
| `python-dotenv` | 1 | 0 | 0 | 1 |
| `Flask` | 1 | 0 | 0 | 1 |
| **Total** | **62** | **5** | **1** | **56** |

No alert is classified as accepted risk or scanner/version false positive at
this stage. Findings marked not reachable retain their alert record and
function-level evidence; they are not treated as nonexistent.

## Evidence Codes

- `AIO-CLIENT`: `webapp/ts_maps.py` creates an `aiohttp.ClientSession` and
  performs outbound `GET` requests to generated Google/Azure provider URLs.
  The HTTP response parser is live.
- `AIO-UNUSED`: TowerScout does not create an aiohttp server and does not use
  aiohttp static serving, request-body parsing, websockets, multipart writers,
  persisted cookie jars, digest auth, per-request cookies, proxy auth, or
  per-request SNI overrides.
- `PIL-CUSTOM`: `/detectcustom` accepts up to 50 MiB and validates only the
  filename extension before `Image.open()`. Pillow selects decoders from file
  content, so an allowed filename can contain another registered format.
- `PIL-UNUSED`: the vulnerable encoder/API/plugin is not called or registered
  by TowerScout's runtime. Local Pillow 12.2.0 confirms EPS, JPEG2000, McIdas,
  and TGA decoders are registered; PDF, GD, BDF, and PCF are not registered
  through `Image.open()`. TowerScout does not call ImageCms, RankFilter, or
  ImageShow.
- `TORCH-LOAD`: `webapp/ts_en.py` directly calls
  `torch.load(..., weights_only=True)`. The vendored YOLO loader calls
  Ultralytics `torch_load`, which supplies `weights_only=False`.
- `TORCH-UNUSED`: the named PyTorch operator is absent from application and
  vendored inference call paths. `torch.jit.load` is present, but
  `torch.jit.script` is not.
- `WAITRESS-LIVE`: Waitress serves the Flask app on container `0.0.0.0:5000`;
  `compose.yaml` currently publishes the port on all host interfaces.
- `WAITRESS-MITIGATED`: `channel_request_lookahead` is not configured and the
  installed/default value is `0`, which disables the vulnerable lookahead
  condition.
- `GEO-PACKAGED`: TowerScout calls only `geopandas.read_file()` on the
  checksummed packaged `.shp`. It does not call `to_postgis()` or ask
  Fiona/GDAL to open user-controlled ZIP/PROJ grid input. Fiona 1.9.6 contains
  GDAL 3.6.4, so the vulnerable transitive code exists but is outside the
  supported input path.
- `DOTENV-READ`: TowerScout uses `load_dotenv()` and `dotenv_values()`. Its own
  temp-file writer replaces the env path; it never calls `set_key()` or
  `unset_key()`.
- `FLASK-TOPOLOGY`: the finding requires a caching proxy plus a specific
  session-access pattern. The supported Compose path has no caching proxy,
  although upgrading remains prudent because TowerScout uses filesystem
  sessions and several `key in session` checks.

## Per-Alert Disposition

The “fixed” column records Trivy's minimum direction, not an approved
Task-098 pin.

### aiohttp 3.9.3

| Alert | Severity | Vulnerability | Fixed | Evidence | Classification |
| ---: | --- | --- | --- | --- | --- |
| [59](https://github.com/J-Schulein/TowerScout/security/code-scanning/59) | Low | CVE-2026-54280 | 3.14.1 | AIO-UNUSED: client performs no payload writes | NOT_REACHABLE |
| [58](https://github.com/J-Schulein/TowerScout/security/code-scanning/58) | Low | CVE-2026-54279 | 3.14.1 | AIO-UNUSED: no CookieJar save/load | NOT_REACHABLE |
| [57](https://github.com/J-Schulein/TowerScout/security/code-scanning/57) | Low | CVE-2026-54275 | 3.14.1 | AIO-UNUSED: no per-request `server_hostname` | NOT_REACHABLE |
| [56](https://github.com/J-Schulein/TowerScout/security/code-scanning/56) | Low | CVE-2026-50269 | 3.14.0 | AIO-UNUSED: no MultipartWriter/payload headers | NOT_REACHABLE |
| [55](https://github.com/J-Schulein/TowerScout/security/code-scanning/55) | Medium | CVE-2026-54278 | 3.14.1 | AIO-UNUSED: server request-body cleanup | NOT_REACHABLE |
| [54](https://github.com/J-Schulein/TowerScout/security/code-scanning/54) | Medium | CVE-2026-54277 | 3.14.1 | AIO-UNUSED: server request-line parser | NOT_REACHABLE |
| [53](https://github.com/J-Schulein/TowerScout/security/code-scanning/53) | Medium | CVE-2026-54276 | 3.14.1 | AIO-UNUSED: no DigestAuthMiddleware | NOT_REACHABLE |
| [52](https://github.com/J-Schulein/TowerScout/security/code-scanning/52) | Medium | CVE-2026-54274 | 3.14.1 | AIO-UNUSED: no websocket server/client | NOT_REACHABLE |
| [51](https://github.com/J-Schulein/TowerScout/security/code-scanning/51) | Medium | CVE-2026-54273 | 3.14.1 | AIO-UNUSED: no aiohttp server/pipelined request queue | NOT_REACHABLE |
| [44](https://github.com/J-Schulein/TowerScout/security/code-scanning/44) | Medium | CVE-2026-47265 | 3.14.0 | AIO-UNUSED: no per-request cookies | NOT_REACHABLE |
| [43](https://github.com/J-Schulein/TowerScout/security/code-scanning/43) | Medium | CVE-2026-34993 | 3.14.0 | AIO-UNUSED: no CookieJar load | NOT_REACHABLE |
| [27](https://github.com/J-Schulein/TowerScout/security/code-scanning/27) | Critical | CVE-2026-34520 | 3.13.4 | AIO-CLIENT: response-header C parser is live for provider downloads | RELEASE_BLOCKING |
| [26](https://github.com/J-Schulein/TowerScout/security/code-scanning/26) | Low | CVE-2026-34519 | 3.13.4 | AIO-UNUSED: no aiohttp Response construction | NOT_REACHABLE |
| [25](https://github.com/J-Schulein/TowerScout/security/code-scanning/25) | Medium | CVE-2026-34518 | 3.13.4 | AIO-UNUSED: no Cookie/Proxy-Authorization headers | NOT_REACHABLE |
| [24](https://github.com/J-Schulein/TowerScout/security/code-scanning/24) | Low | CVE-2026-34517 | 3.13.4 | AIO-UNUSED: no server multipart form parsing | NOT_REACHABLE |
| [23](https://github.com/J-Schulein/TowerScout/security/code-scanning/23) | Low | CVE-2026-34514 | 3.13.4 | AIO-UNUSED: no attacker-controlled content type | NOT_REACHABLE |
| [22](https://github.com/J-Schulein/TowerScout/security/code-scanning/22) | Low | CVE-2026-34513 | 3.13.4 | AIO-CLIENT but provider host set is fixed and bounded | NOT_REACHABLE |
| [21](https://github.com/J-Schulein/TowerScout/security/code-scanning/21) | Low | CVE-2025-69230 | 3.13.3 | AIO-UNUSED: no server cookie parsing | NOT_REACHABLE |
| [20](https://github.com/J-Schulein/TowerScout/security/code-scanning/20) | Low | CVE-2025-69226 | 3.13.3 | AIO-UNUSED: no `web.static()` | NOT_REACHABLE |
| [19](https://github.com/J-Schulein/TowerScout/security/code-scanning/19) | Low | CVE-2025-69225 | 3.13.3 | AIO-UNUSED: no server Range parser | NOT_REACHABLE |
| [18](https://github.com/J-Schulein/TowerScout/security/code-scanning/18) | Low | CVE-2025-69224 | 3.13.3 | AIO-UNUSED: no pure-Python server parser | NOT_REACHABLE |
| [17](https://github.com/J-Schulein/TowerScout/security/code-scanning/17) | Low | CVE-2025-53643 | 3.12.14 | AIO-UNUSED: no server request/trailer parser | NOT_REACHABLE |
| [16](https://github.com/J-Schulein/TowerScout/security/code-scanning/16) | Medium | CVE-2026-34525 | 3.13.4 | AIO-UNUSED: no aiohttp server Host-header validation | NOT_REACHABLE |
| [15](https://github.com/J-Schulein/TowerScout/security/code-scanning/15) | High | CVE-2026-34516 | 3.13.4 | AIO-UNUSED: provider path does not parse multipart responses | NOT_REACHABLE |
| [14](https://github.com/J-Schulein/TowerScout/security/code-scanning/14) | Medium | CVE-2026-34515 | 3.13.4 | AIO-UNUSED: no Windows static resource handler | NOT_REACHABLE |
| [13](https://github.com/J-Schulein/TowerScout/security/code-scanning/13) | Medium | CVE-2026-22815 | 3.13.4 | AIO-UNUSED: server header/trailer handling | NOT_REACHABLE |
| [12](https://github.com/J-Schulein/TowerScout/security/code-scanning/12) | Medium | CVE-2025-69229 | 3.13.3 | AIO-UNUSED: no server `request.read()` | NOT_REACHABLE |
| [11](https://github.com/J-Schulein/TowerScout/security/code-scanning/11) | Medium | CVE-2025-69228 | 3.13.3 | AIO-UNUSED: no server `Request.post()` | NOT_REACHABLE |
| [10](https://github.com/J-Schulein/TowerScout/security/code-scanning/10) | Medium | CVE-2025-69227 | 3.13.3 | AIO-UNUSED: no server POST parser | NOT_REACHABLE |
| [9](https://github.com/J-Schulein/TowerScout/security/code-scanning/9) | Medium | CVE-2024-52304 | 3.10.11 | AIO-UNUSED: no pure-Python server parser | NOT_REACHABLE |
| [8](https://github.com/J-Schulein/TowerScout/security/code-scanning/8) | Medium | CVE-2024-27306 | 3.9.4 | AIO-UNUSED: no aiohttp static index | NOT_REACHABLE |
| [7](https://github.com/J-Schulein/TowerScout/security/code-scanning/7) | High | CVE-2025-69223 | 3.13.3 | AIO-UNUSED: no aiohttp server request decompression | NOT_REACHABLE |
| [6](https://github.com/J-Schulein/TowerScout/security/code-scanning/6) | High | CVE-2024-30251 | 3.9.4 | AIO-UNUSED: no aiohttp server multipart POST | NOT_REACHABLE |

### Pillow 12.2.0

| Alert | Severity | Vulnerability | Fixed | Evidence | Classification |
| ---: | --- | --- | --- | --- | --- |
| [72](https://github.com/J-Schulein/TowerScout/security/code-scanning/72) | Medium | CVE-2026-59203 | 12.3.0 | PIL-CUSTOM: EPS content parser registered; extension-only gate | REQUIRED_HARDENING |
| [71](https://github.com/J-Schulein/TowerScout/security/code-scanning/71) | Medium | CVE-2026-59198 | 12.3.0 | PIL-UNUSED: TGA RLE encoder is never selected | NOT_REACHABLE |
| [70](https://github.com/J-Schulein/TowerScout/security/code-scanning/70) | Medium | CVE-2026-55798 | 12.3.0 | PIL-UNUSED: no ImageShow/WindowsViewer call | NOT_REACHABLE |
| [69](https://github.com/J-Schulein/TowerScout/security/code-scanning/69) | High | CVE-2026-59205 | 12.3.0 | PIL-UNUSED: no ImageCms transform | NOT_REACHABLE |
| [68](https://github.com/J-Schulein/TowerScout/security/code-scanning/68) | High | CVE-2026-59204 | 12.3.0 | PIL-CUSTOM: JPEG2000 decoder is registered and available | RELEASE_BLOCKING |
| [67](https://github.com/J-Schulein/TowerScout/security/code-scanning/67) | High | CVE-2026-59200 | 12.3.0 | PIL-UNUSED: PDF decoder is not registered/called | NOT_REACHABLE |
| [66](https://github.com/J-Schulein/TowerScout/security/code-scanning/66) | High | CVE-2026-59199 | 12.3.0 | PIL-UNUSED: crop coordinates are bounded to loaded image dimensions; paste/alpha composite absent | NOT_REACHABLE |
| [65](https://github.com/J-Schulein/TowerScout/security/code-scanning/65) | High | CVE-2026-59197 | 12.3.0 | PIL-UNUSED: RankFilter absent | NOT_REACHABLE |
| [64](https://github.com/J-Schulein/TowerScout/security/code-scanning/64) | High | CVE-2026-55380 | 12.3.0 | PIL-UNUSED: GD plugin is not registered/called | NOT_REACHABLE |
| [63](https://github.com/J-Schulein/TowerScout/security/code-scanning/63) | High | CVE-2026-55379 | 12.3.0 | PIL-UNUSED: BDF font parser absent | NOT_REACHABLE |
| [62](https://github.com/J-Schulein/TowerScout/security/code-scanning/62) | High | CVE-2026-54060 | 12.3.0 | PIL-UNUSED: FontFile compiler absent | NOT_REACHABLE |
| [61](https://github.com/J-Schulein/TowerScout/security/code-scanning/61) | High | CVE-2026-54059 | 12.3.0 | PIL-UNUSED: PCF font parser absent | NOT_REACHABLE |
| [60](https://github.com/J-Schulein/TowerScout/security/code-scanning/60) | High | CVE-2026-54058 | 12.3.0 | PIL-CUSTOM: McIdas decoder is registered; later pixel access is live | RELEASE_BLOCKING |

### torch 2.2.1

| Alert | Severity | Vulnerability | Fixed | Evidence | Classification |
| ---: | --- | --- | --- | --- | --- |
| [50](https://github.com/J-Schulein/TowerScout/security/code-scanning/50) | Medium | CVE-2025-3001 | 2.10.0 | TORCH-UNUSED: `torch.lstm_cell` absent | NOT_REACHABLE |
| [49](https://github.com/J-Schulein/TowerScout/security/code-scanning/49) | Medium | CVE-2025-3000 | 2.13.0 | TORCH-UNUSED: `torch.jit.script` absent | NOT_REACHABLE |
| [48](https://github.com/J-Schulein/TowerScout/security/code-scanning/48) | Low | CVE-2025-2149 | No fix cited | TORCH-UNUSED: quantized sigmoid operator absent | NOT_REACHABLE |
| [47](https://github.com/J-Schulein/TowerScout/security/code-scanning/47) | Medium | CVE-2025-2148 | No fix cited | TORCH-UNUSED: profiler callback operator absent | NOT_REACHABLE |
| [46](https://github.com/J-Schulein/TowerScout/security/code-scanning/46) | Medium | CVE-2025-2999 | 2.9.1 | TORCH-UNUSED: `unpack_sequence` absent | NOT_REACHABLE |
| [45](https://github.com/J-Schulein/TowerScout/security/code-scanning/45) | Medium | CVE-2025-2998 | No fix cited | TORCH-UNUSED: `pad_packed_sequence` absent | NOT_REACHABLE |
| [33](https://github.com/J-Schulein/TowerScout/security/code-scanning/33) | Low | CVE-2025-2953 | 2.7.1-rc1 | TORCH-UNUSED: `mkldnn_max_pool2d` absent | NOT_REACHABLE |
| [32](https://github.com/J-Schulein/TowerScout/security/code-scanning/32) | Low | CVE-2025-3730 | 2.8.0 | TORCH-UNUSED: `ctc_loss` absent | NOT_REACHABLE |
| [31](https://github.com/J-Schulein/TowerScout/security/code-scanning/31) | Critical | CVE-2025-32434 | 2.6.0 | TORCH-LOAD: direct `weights_only=True` checkpoint load | RELEASE_BLOCKING |

### Remaining direct packages

| Alert | Package | Severity | Vulnerability | Fixed | Evidence | Classification |
| ---: | --- | --- | --- | --- | --- | --- |
| [42](https://github.com/J-Schulein/TowerScout/security/code-scanning/42) | python-dotenv 1.0.0 | Medium | CVE-2026-28684 | 1.2.2 | DOTENV-READ | NOT_REACHABLE |
| [41](https://github.com/J-Schulein/TowerScout/security/code-scanning/41) | geopandas 0.14.3 | High | CVE-2025-69662 | 1.1.2 | GEO-PACKAGED: no `to_postgis()` or PostgreSQL path | NOT_REACHABLE |
| [35](https://github.com/J-Schulein/TowerScout/security/code-scanning/35) | waitress 3.0.0 | High | CVE-2024-49769 | 3.0.1 | WAITRESS-LIVE: production WSGI boundary and all-interface publish | RELEASE_BLOCKING |
| [34](https://github.com/J-Schulein/TowerScout/security/code-scanning/34) | waitress 3.0.0 | Critical | CVE-2024-49768 | 3.0.1 | WAITRESS-MITIGATED: lookahead defaults to disabled | NOT_REACHABLE |
| [29](https://github.com/J-Schulein/TowerScout/security/code-scanning/29) | fiona 1.9.6 | High | GHSA-g4m4-9q4c-mfw6 | 1.10b2 | GEO-PACKAGED: no JPEG-compressed untrusted PROJ grid | NOT_REACHABLE |
| [28](https://github.com/J-Schulein/TowerScout/security/code-scanning/28) | fiona 1.9.6 | Critical | GHSA-q5fm-55c2-v6j9 | 1.10b1 | GEO-PACKAGED: no GDAL open of user-controlled ZIP | NOT_REACHABLE |
| [1](https://github.com/J-Schulein/TowerScout/security/code-scanning/1) | Flask 3.0.2 | Low | CVE-2026-27205 | 3.1.3 | FLASK-TOPOLOGY | NOT_REACHABLE |

## Cross-Cutting Runtime Finding

`compose.yaml` uses:

```yaml
ports:
  - "${TOWERSCOUT_PORT:-5000}:5000"
```

This publishes on all host interfaces by default. It contradicts the
single-user local-runtime assumption used by several provisional
classifications. Task-098 must bind the normal package to loopback explicitly
and add a contract test. Until then, the Waitress and custom-image release
blockers must be assessed against possible same-network reachability rather
than localhost-only reachability.

## Sources

- GitHub code-scanning REST records and individual alert pages linked above.
- `webapp/ts_maps.py`, `webapp/towerscout.py`, `webapp/ts_validation.py`,
  `webapp/ts_en.py`, `webapp/ts_zipcode.py`, `webapp/ts_config.py`,
  `webapp/vendor/yolov5_local/models/experimental.py`, `compose.yaml`, and
  `Dockerfile`.
- Pillow 12.3.0 official release notes:
  <https://pillow.readthedocs.io/en/stable/releasenotes/12.3.0.html>
- Official PyPI release metadata for aiohttp, Fiona, GeoPandas, Flask, and
  python-dotenv.
- Official PyTorch previous-version matrix:
  <https://pytorch.org/get-started/previous-versions/>
- Waitress 3.0.1 official changelog:
  <https://docs.pylonsproject.org/projects/waitress/en/stable/#change-history>
