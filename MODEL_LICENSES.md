# Model Licenses And Provenance

This file documents model-asset terms for the TowerScout YOLO-enabled
`agpl-yolo` release track.

## YOLO Detector Weights

| Field | Value |
| --- | --- |
| Asset ID | `yolo-newest` |
| Path | `model_params/yolov5/newest.pt` |
| Manifest | `webapp/asset_manifest.v1.json` |
| Model family | YOLOv5 detector |
| Runtime source | Ultralytics YOLOv5 vendored under `webapp/vendor/yolov5_local/` |
| Release treatment | YOLO-derived/AGPL-governed unless separate written model terms say otherwise |

The YOLO detector weights must not be described as MIT-licensed in the
YOLO-enabled release. If the team obtains separate written terms for the
weights, record the grant, scope, version, and publication conditions here and
in the release manifest.

## EfficientNet Classifier Weights

| Field | Value |
| --- | --- |
| Asset ID | `efficientnet-b5-project-weights` |
| Path | `model_params/EN/b5_unweighted_best.pt` |
| Manifest | `webapp/asset_manifest.v1.json` |
| Runtime source | `efficientnet_pytorch` package |
| Release treatment | Project model asset; distribution authority must be confirmed for each release |

The EfficientNet implementation dependency is separately licensed from the
classifier weights. Confirm the right to package and publish the weights before
broad release.

## Release Requirements

Every release that publishes model weights must include:

- The asset manifest version and hashes.
- A statement of the governing model terms.
- The release track (`agpl-yolo` for the current YOLO-enabled package).
- A source/ref record for the matching TowerScout code and vendored YOLO source.
- Revocation notes for a defective or incorrectly licensed model asset.
