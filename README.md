# TowerScout

TowerScout helps public health teams find and review possible cooling towers in
satellite and aerial imagery. It can support Legionnaires' disease outbreak
investigations and the development of cooling-tower registries. All detections
require human review.

## Start Here

- **[Watch the Demo](https://github.com/cdcai/TowerScout/wiki/Demo-Video-And-Written-Walkthrough#watch-the-demo)** — see TowerScout in use in about six minutes.
- **[Read the User Guide](https://github.com/cdcai/TowerScout/wiki)** — choose your setup, install TowerScout, and learn the everyday workflow.
- **[Download TowerScout for Windows](https://github.com/cdcai/TowerScout/releases/tag/v0.1.3-rc.1)** — get the supported release and its installation packages.

### Download And Install

Follow [Install And First Run](https://github.com/cdcai/TowerScout/wiki/Install-And-First-Run)
for package selection, SHA-256 checksum verification, and setup. Choose
[Docker or Podman, CPU or NVIDIA GPU processing, and Google Maps or Azure Maps](https://github.com/cdcai/TowerScout/wiki/Choose-Your-Setup).
See [supported configurations](https://github.com/cdcai/TowerScout/wiki/Releases-And-Supported-Versions#tested-configurations)
for requirements and test coverage.

The supplied Windows scripts are **unsigned**. Use them only where your
organization permits them. If policy blocks installation or startup, stop and
consult [Local IT](https://github.com/cdcai/TowerScout/wiki/Local-IT-Administrator-Guide).

The application package includes offline manuals, and the running app provides
version-matched Help. For assistance, see
[Troubleshooting And Safe Support](https://github.com/cdcai/TowerScout/wiki/Troubleshooting-And-Safe-Support).

## Features

### Automated Detection

- **Machine Learning Pipeline**: YOLOv5 object detection followed by EfficientNet classification.
- **Imagery Providers**: Google Maps and Azure Maps satellite imagery.
- **Tile Processing**: Process a selected search area tile by tile.
- **Confidence Scores**: Review model confidence scores and adjust the review threshold.

### Manual Tower Addition

- **Interactive Drawing**: Add missed tower candidates with the polygon drawing tool after a detection run.
- **Visual Distinction**: Manual additions display with purple borders and "✋ Manual" badges.
- **Automatic Geocoding**: Retrieve addresses and cache them for later use.
- **Dataset Integration**: Include manual additions in CSV, KML, and YOLO exports under each format's export rules.
- **Dataset Restoration**: Save and restore datasets to continue a review later.
- **Provider Lock**: Keep imagery and detections together by locking provider selection after a run.

### Export And Analysis

- **CSV Export**: Save detection rows with addresses, confidence scores, coordinates, and selection, boundary, and threshold flags.
- **KML Export**: Save selected results that meet the confidence and boundary rules for viewing in geographic software such as Google Earth.
- **YOLO Format**: Export selected annotations that meet the confidence threshold across full imagery tiles for model-development work.
- **Dataset Export**: Save imagery, labels, metadata, and manual additions for later restoration.

CSV retains detection rows with their review flags; unchecking a detection does
not remove its CSV row. See the [export instructions](docs/user-guide.md#export-results)
for each format's selection and boundary rules.

### Search And Navigation

- **Address Search**: Find locations by street address, city, or neighborhood.
- **ZIP Code Search**: Define a search area using postal-code boundaries.
- **Custom Polygons**: Draw a search area on the map.
- **Circular Search**: Define a search radius around a location.
- **Tile Estimation**: Preview the number of imagery tiles before running detection.

### Review And Validation

- **Interactive Review**: Select a detection in the list to highlight it on the map, or select it on the map to find it in the list.
- **Selection Review**: Mark detections as selected or unselected before exporting results.
- **Tile-by-Tile Review**: Examine imagery systematically to check detection accuracy.

## About TowerScout

Cooling towers are potential sources of *Legionella* bacteria, which cause
Legionnaires' disease. The [Centers for Disease Control and Prevention](https://www.cdc.gov)
provides [guidance for identifying cooling towers during outbreak investigations](https://www.cdc.gov/legionella/health-depts/environmental-inv-resources/id-cooling-towers.html).
TowerScout has been used in more than 12 outbreak investigations across eight
states since 2021.

In 2021, TowerScout was the
[Hal Varian Award winner](https://www.ischool.berkeley.edu/programs/mids/capstone/varianaward)
for the [Master of Information and Data Science program](https://www.ischool.berkeley.edu/programs/mids)
at the [UC Berkeley School of Information](https://www.ischool.berkeley.edu).
This repository carries forward the original `TowerScout/TowerScout` project.

Public health applications include:

- The Utah Department of Health and Human Services used TowerScout for [detecting cooling towers in aerial imagery](https://gis.utah.gov/blog/2023-07-04-cooling-tower-update/).
- The Los Angeles County Enterprise GIS team and Department of Public Health used TowerScout to build an initial dataset of likely cooling-tower locations across the county. The work received the [2023 NACo Achievement Award for Information Technology, Best in Category](https://www.naco.org/resources/award-programs/towerscout-adaptation-%E2%80%93-automated-image-analysis-identify-cooling-towers).

Related project: [TowerScout Enterprise](https://github.com/cdcai/TowerScout-Enterprise).

### TowerScout Team

Karen K Wong, Jia Lu, Gunnar Mein, and Thaddeus Segura.

Fred Nugen, Alberto Todeschini, Elizabeth J Hannapel, Jasen M Kunz, Troy Ritter,
Jessica C Smith, and Chris Edens helped guide the project.

## Attribution

Please cite the following publication and this GitHub repository when utilizing TowerScout:

- Wong, KK, Segura T, Mein G, Lu J, Hannapel EJ, Kunz JM, Ritter T, Smith JC, Todeschini A, Nugen F, Edens C. Automated cooling tower detection through deep learning for Legionnaires’ disease outbreak investigations: a model development and validation study. *Lancet Digit Health.* 2024;6(7):e500-e506. [doi.org/10.1016/S2589-7500(24)00094-3](https://doi.org/10.1016/S2589-7500(24)00094-3)

## Additional files

* YOLOv5 detector weights - distributed through the release asset bundle and treated as YOLO-derived/AGPL-governed unless separate written model terms say otherwise; see `MODEL_LICENSES.md` and `webapp/asset_manifest.v1.json`.
* EfficientNet weights - distributed under the original TowerScout CC-BY-NC-SA-4.0 license, including attribution, noncommercial and share-alike conditions; see `MODEL_LICENSES.md` and `webapp/asset_manifest.v1.json` for the exact asset identity.
* ZCTA shapefile data - distributed according to `DATA_LICENSES.md` and the release asset manifest.

TowerScout is a research tool. Its licenses govern permitted uses; imagery and data provider terms also apply.

## License

The YOLO-enabled release is a composite-license package. Project-controlled application code, including inherited CC-marked code and extracted modules, is additionally available under AGPL-3.0-only; see the [application grant and exact scope](licenses/TowerScout-APPLICATION-GRANT.md). Prior CC permissions, existing Apache grants and third-party terms remain effective where applicable. The current YOLO-enabled package/image has AGPL-3.0 obligations, while the EfficientNet classifier weights retain their separate CC-BY-NC-SA-4.0 terms. Complete license texts are in `licenses/`.

See `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, and `PROVIDER_TERMS.md`. The generated release control ZIP is authoritative for release-specific source, checksum, image digest, SBOM-reference, and manifest metadata. The running local app exposes the formatted source/license notice at `/license` and plain-text combined notices at `/license.txt`.
