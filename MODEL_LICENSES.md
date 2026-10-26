# Model Licenses And Provenance

This file documents model-asset terms for the TowerScout YOLO-enabled
`agpl-yolo` release track.

## YOLO Detector Weights

| Field | Value |
| --- | --- |
| Asset ID | `yolo-newest` |
| Path | `model_params/yolov5/newest.pt` |
| Manifest | `webapp/asset_manifest.v1.json` |
| SHA-256 | `27315e156d8370d51d9c2a3c047c4bf5cc0c8ae1521036bdf800b7a8a81554e6` |
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
| SHA-256 | `645113badfcd17a1f9b451aabb54bf80e115a4faaceb65e0ce3fc8dbfb108a5d` |
| Runtime source | `efficientnet_pytorch` package |
| Distribution authority | Project owner approved distribution of the current manifest-identified asset on October 22, 2026 |
| Recipient license | CC-BY-NC-SA-4.0, retaining the original TowerScout repository license as confirmed by the project lead on October 22, 2026 |
| Full license | `licenses/CC-BY-NC-SA-4.0.txt` |

The classifier weights retain the original TowerScout repository's
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Credit the TowerScout team and the original project at
https://github.com/cdcai/TowerScout. The original repository identifies the
[EfficientNet weight download](https://drive.google.com/file/d/1Cs3nXQddNf-Y0HYO8a5Yvm6mNB-Rx8HP/view).
The exact release asset is identified by the SHA-256 above; this notice change
does not modify its bytes.

The license permits sharing and adaptation subject to attribution, a license
link, indication of changes, noncommercial use and share-alike conditions for
distributed adaptations. Preserve supplied notices and do not impose additional
restrictions on the licensed rights. Exceptions and limitations remain unaffected;
the full license governs. These weights must not be described as unrestricted
or Apache-2.0-licensed. The separately licensed `efficientnet_pytorch`
implementation does not change the classifier weight license. This confirmation
does not change the YOLO detector treatment above.

## Release Requirements

Every release that publishes model weights must include:

- The asset manifest version and hashes.
- A statement of the governing model terms.
- The release track (`agpl-yolo` for the current YOLO-enabled package).
- A source/ref record for the matching TowerScout code and vendored YOLO source.
- Revocation notes for a defective or incorrectly licensed model asset.
