# Third-Party Notices

This notice file is for the TowerScout YOLO-enabled `agpl-yolo` release track.
It replaces any prior attribution that described YOLO or Ultralytics YOLOv5 as
MIT-licensed for the current runtime.

## Release Posture

Project-controlled application code has an additional AGPL-3.0-only grant,
including inherited CC-marked code and extracted modules, with project-controlled
supporting code and accompanying documentation covered by the October 25 scope
clarification. Its scope is
in [the application grant](licenses/TowerScout-APPLICATION-GRANT.md). Prior CC
permissions and existing Apache-2.0 grants remain available where applicable.
The full YOLO-enabled runtime package/image is not Apache-2.0-only because it
includes AGPL-3.0 Ultralytics YOLOv5 components.
Complete texts are provided in `licenses/Apache-2.0.txt` and
`licenses/AGPL-3.0.txt`; dependency-specific copyright and license notices
remain in the vendored source and installed package distributions.

## Individually Marked TowerScout Files

The following application files retain CC-BY-NC-SA-4.0 as an alternative to
the additional AGPL-3.0-only grant: `webapp/ts_azure_maps.py`, `ts_en.py`, `ts_events.py`,
`ts_geocache.py`, `ts_geocoding.py`, `ts_gmaps.py`, `ts_imgutil.py`, `ts_maps.py`,
`ts_yolov5.py`, and `ts_zipcode.py` (all under `webapp/`), the two
`webapp/css/ts_styles*.css` files, `webapp/templates/incompatible.html` and
`unauthorized.html`, and `webapp/js/src/towerscout.js` and
`webapp/js/towerscout.original.js`. The generated `webapp/js/towerscout.js`
retains its source notice. Credit: Karen Wong, Gunnar Mein, Thaddeus Segura,
Jia Lu, and the TowerScout team, as recorded in those files.

The complete alternative license texts are `licenses/CC-BY-NC-SA-4.0.txt` and
`licenses/AGPL-3.0.txt`. Recipients may rely on the AGPL grant for the covered
application code without the CC noncommercial/share-alike conditions applying
to that AGPL-licensed use. Earlier CC permissions and attribution are preserved.
The grant also covers the listed main application, active HTML template and
extracted frontend modules; coverage is not limited to these 16 headers.
This application-code decision is separate from model-weight terms and does
not relicense third-party material or clear other release obligations.

## Machine Learning Runtime

| Component | License | Source / URL | TowerScout Use |
| --- | --- | --- | --- |
| Ultralytics YOLOv5 | AGPL-3.0 | https://github.com/ultralytics/yolov5 | Vendored runtime snapshot under `webapp/vendor/yolov5_local/`. |
| ultralytics Python package | AGPL-3.0 | https://github.com/ultralytics/ultralytics | Runtime dependency pinned in `webapp/requirements.txt`. |
| PyTorch | BSD-style | https://pytorch.org/ | Tensor runtime used by the detector and classifier. |
| torchvision | BSD-style | https://pytorch.org/vision/stable/index.html | Torch vision support library. |
| efficientnet_pytorch | Apache-2.0 | https://github.com/lukemelas/EfficientNet-PyTorch | EfficientNet-B5 classifier implementation dependency. |

`efficientnet_pytorch` 0.7.1 is by Luke Melas-Kyriazi and contributors. Its
installed distribution does not supply a standalone license file. The upstream
project supplies the Apache-2.0 text, included here as `licenses/Apache-2.0.txt`.
This attribution concerns the implementation, not the separately licensed
TowerScout classifier weights.

TowerScout vendored YOLOv5 snapshot:

- Path: `webapp/vendor/yolov5_local/`
- Upstream project: `ultralytics/yolov5`
- Validated upstream commit recorded by TowerScout: `1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c`
- License text: `webapp/vendor/yolov5_local/LICENSE`
- Local integration points: `webapp/ts_yolov5_local.py`, `webapp/ts_yolov5.py`, Docker/Compose `YOLO_CONFIG_DIR` runtime configuration, and release asset import paths.

## Core Python Dependencies

The adapted loader `webapp/ts_yolov5_local.py` derives from YOLOv5
`hubconf.py` at the pinned commit above, under AGPL-3.0. The vendored README
describes the local modifications and their dated notice reconciliation.

`ultralytics-thop` is AGPL-3.0; `certifi` is MPL-2.0. Retain their installed
license payloads and exact-version source with distribution. The reviewed
installed distributions identify python-dotenv 1.2.2 as BSD-3-Clause, packaging
25.0 as Apache-2.0 OR BSD-2-Clause, seaborn 0.13.2 as BSD-3-Clause, and urllib3
2.8.0 as MIT. Preserve their full installed notices and reconcile these versions
against each final image; this source summary does not pin unpinned dependencies.
These examples supplement the exact image inventory, not replace it.

## Synthetic-data research source

`SyntheticData/dataset_generator.py` and `SyntheticData/defaults.py` adapt Debidatta Dwibedi's
[`syndata-generation`](https://github.com/debidatta/syndata-generation)
implementation. Its 2017 copyright and complete MIT notice are retained in
`licenses/SyntheticData-MIT.txt`. A paper citation alone is not that notice.
This upstream permission does not establish the rights to unrelated research
material, imagery or local contributions.

## Final distribution obligations

Source staging and installed license inventories are preparation. Before image
distribution, reconcile exact Debian/Python/native versions, modifications,
patch/build inputs, applicable relinking obligations and durable corresponding
source/SBOM access. Do not claim complete delivery from download counts alone.
The preserved native inventory includes Qt/FFmpeg (OpenCV wheel), GEOS, GNU
runtime libraries and OpenSSL, as well as the base image's `/usr/local` CPython.
Their exact component builds, embedded patches, license alternatives, installed
copyright/license payloads and applicable source/relink requirements require
final-image reconciliation; a parent wheel's license is not a blanket license
for everything bundled inside it. Retain Debian package copyright files and
wheel license directories. See [the maintainer register](docs/security/dependency-security-disposition.md#receiving-maintainer-follow-up-register).

## Runtime dependency inventory

The release uses Python packages from `webapp/requirements.txt`. Examples
include Flask, Flask-Session, Waitress, Requests, NumPy, pandas, GeoPandas,
Fiona, Shapely, Pillow, OpenCV, tqdm, aiohttp, aiofiles, psutil, torch,
torchvision, ultralytics, certifi, and cryptography. Cryptography supplies the
X.509 parser used to reject distrusted CA keys; its installed distribution's
license files and dependencies must be retained in the image. The publication
workflow generates an exact-image-digest CycloneDX SBOM; retain it with the
release artifacts and identify it in the release evidence. See `SBOM.txt`.

## JavaScript Dependencies

The frontend build currently uses npm development dependencies listed in
`package.json` and runtime JavaScript assets under `webapp/js/`. The release
package should use the generated frontend bundle from the exact source ref.

Bundled jQuery 3.5.1 (`webapp/js/jquery-3.5.1.min.js`) is MIT-licensed.
Copyright JS Foundation and other contributors, https://js.foundation/.
The full permission and warranty notice from the upstream 3.5.1 release is
included as `licenses/jQuery-MIT.txt`.

## CUDA And System Dependencies

The CUDA image also installs NVIDIA CUDA libraries through the PyTorch cu128
wheel dependencies. Many carry NVIDIA proprietary redistribution terms; others
(including NCCL and NVTX) carry their own BSD or Apache terms. They are not
relicensed under TowerScout's application grant. Preserve the exact installed
wheel `*.dist-info/License.txt` or `licenses/` payloads and inspect the matching
redistribution conditions for the final image. The CPU image has no such CUDA
wheel set. Do not describe the complete CUDA image as entirely AGPL or Apache.

Debian copyright files under `/usr/share/doc/<package>/copyright`, Python
distribution license files, and bundled-library notices remain part of the
image. Record exact package and source-package versions and provide required
corresponding source alongside the release. An image SBOM or upstream project
homepage does not, by itself, satisfy these source-delivery requirements.

## Cloud And Map Provider Services

Google Maps and Azure Maps are external proprietary services. TowerScout does
not include provider keys. Users must supply their own keys or approved
site-owned keys and comply with provider terms. See `PROVIDER_TERMS.md`.

## Model And Data Assets

Model weights and ZIP-code data are not governed solely by the application
source license. See `MODEL_LICENSES.md`, `DATA_LICENSES.md`, and
`webapp/asset_manifest.v1.json`.

The TowerScout EfficientNet classifier weights retain CC-BY-NC-SA-4.0 with
attribution, noncommercial and share-alike conditions. The complete text is
`licenses/CC-BY-NC-SA-4.0.txt`. This model license is distinct from the
Apache-2.0 license of the EfficientNet implementation dependency.
