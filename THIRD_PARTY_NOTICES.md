# Third-Party Notices

This notice file is for the TowerScout YOLO-enabled `agpl-yolo` release track.
It replaces any prior attribution that described YOLO or Ultralytics YOLOv5 as
MIT-licensed for the current runtime.

## Release Posture

TowerScout-authored code may be Apache-2.0 where ownership and relicensing
authority are confirmed. The full YOLO-enabled runtime package/image is not
Apache-2.0-only because it includes AGPL-3.0 Ultralytics YOLOv5 components.

## Machine Learning Runtime

| Component | License | Source / URL | TowerScout Use |
| --- | --- | --- | --- |
| Ultralytics YOLOv5 | AGPL-3.0 | https://github.com/ultralytics/yolov5 | Vendored runtime snapshot under `webapp/vendor/yolov5_local/`. |
| ultralytics Python package | AGPL-3.0 | https://github.com/ultralytics/ultralytics | Runtime dependency pinned in `webapp/requirements.txt`. |
| PyTorch | BSD-style | https://pytorch.org/ | Tensor runtime used by the detector and classifier. |
| torchvision | BSD-style | https://pytorch.org/vision/stable/index.html | Torch vision support library. |
| efficientnet_pytorch | Apache-2.0 | https://github.com/lukemelas/EfficientNet-PyTorch | EfficientNet-B5 classifier implementation dependency. |

TowerScout vendored YOLOv5 snapshot:

- Path: `webapp/vendor/yolov5_local/`
- Upstream project: `ultralytics/yolov5`
- Validated upstream commit recorded by TowerScout: `1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c`
- License text: `webapp/vendor/yolov5_local/LICENSE`
- Local integration points: `webapp/ts_yolov5_local.py`, `webapp/ts_yolov5.py`, Docker/Compose `YOLO_CONFIG_DIR` runtime configuration, and release asset import paths.

## Core Python Dependencies

The release uses Python packages from `webapp/requirements.txt`. Examples
include Flask, Flask-Session, Waitress, Requests, NumPy, pandas, GeoPandas,
Fiona, Shapely, Pillow, OpenCV, tqdm, aiohttp, aiofiles, psutil, torch,
torchvision, and ultralytics. Release maintainers should generate or attach an
SBOM for the exact package/image release.

## JavaScript Dependencies

The frontend build currently uses npm development dependencies listed in
`package.json` and runtime JavaScript assets under `webapp/js/`. The release
package should use the generated frontend bundle from the exact source ref.

## Cloud And Map Provider Services

Google Maps and Azure Maps are external proprietary services. TowerScout does
not include provider keys. Users must supply their own keys or approved
site-owned keys and comply with provider terms. See `PROVIDER_TERMS.md`.

## Model And Data Assets

Model weights and ZIP-code data are not governed solely by the application
source license. See `MODEL_LICENSES.md`, `DATA_LICENSES.md`, and
`webapp/asset_manifest.v1.json`.
