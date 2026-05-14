# TowerScout

TowerScout is a tool for identifying cooling towers from satellite and aerial imagery.  Cooling towers are potential sources of _Legionella_ bacteria, which causes Legionnaires' disease.  TowerScout has been utilized in over 12 investigations of outbreaks of Legionnaires' disease across 8 states since 2021.  It can be used after outbreaks to identify potential sources of _Legionella_, and it can be used before outbreaks to build and update a registry of cooling towers to aid future investigations.  

## About TowerScout 

The [Centers for Disease Control and Prevention](https://cdc.gov) have [procedures](https://www.cdc.gov/legionella/health-depts/environmental-inv-resources/id-cooling-towers.html) for identifying cooling towers during investigation of an outbreak of Legionnaires' disease, which can be significantly sped up by using TowerScout.  TowerScout has been used in more than 12 investigations of outbreaks of Legionnaires' disease across 8 states since 2021.  In 2021, TowerScout was the [Hal Varian Award Winner](https://www.ischool.berkeley.edu/programs/mids/capstone/varianaward) for the [Master of Information and Data Science Program (MIDS)](https://www.ischool.berkeley.edu/programs/mids) in the [School of Information](https://ischool.berkeley.edu) at [UC Berkeley](https://berkeley.edu).  

TowerScout has been used by local health departments:
- The the Utah Department of Health and Human Services (DHHS) used TowerScout for [detecting cooling towers](https://gis.utah.gov/blog/2023-07-04-cooling-tower-update/) in aerial imagery.
- The Los Angeles County Enterprise GIS (eGIS) team and Department of Public Health used TowerScout to build an initial dataset of likely cooling tower locations across the County.  The work was the [2023 NACo Achievement Award Winner, Information Technology (Best in Category)](https://www.naco.org/resources/award-programs/towerscout-adaptation-%E2%80%93-automated-image-analysis-identify-cooling-towers). 

**Additional files**
* YOLOv5 detector weights - distributed through the release asset bundle and treated as YOLO-derived/AGPL-governed unless separate written model terms say otherwise.
* EfficientNet weights - distributed through the release asset bundle when project distribution authority is confirmed.
* ZCTA shapefile data - distributed according to `DATA_LICENSES.md` and the release asset manifest.

This is a proof of concept and is not intended for commercial use. Users should adhere to terms of service when using tools and resources from any imagery and data providers. 

## TowerScout Team

[Karen K Wong](https://www.linkedin.com/in/karenkwong/),
[Jia Lu](https://www.linkedin.com/in/jia-lu-gracie-a8b5a71a/),
[Gunnar Mein](https://www.linkedin.com/in/gunnarmein/),
[Thaddeus Segura](https://www.linkedin.com/in/thaddeussegura/).  
[Fred Nugen](https://www.linkedin.com/in/drnooj/),
[Alberto Todeschini](https://www.linkedin.com/in/atodeschini/), 
[Elizabeth J Hannapel](https://www.linkedin.com/in/elizabeth-hannapel/), 
Jasen M Kunz,
[Troy Ritter](https://www.linkedin.com/in/troy-ritter-b1bb3a24/), 
Jessica C Smith, and
[Chris Edens](https://www.linkedin.com/in/wcedens/) helped guide the project.

## Features

### Automated Detection
- **Machine Learning Pipeline**: YOLOv5 object detection + EfficientNet classification
- **Multi-Provider Support**: Google Maps and Azure Maps satellite imagery
- **Batch Processing**: Efficiently process large geographic areas tile-by-tile
- **Confidence Scoring**: Adjustable thresholds for detection sensitivity

### Manual Tower Addition
- **Interactive Drawing**: Add cooling towers manually via polygon drawing tool
- **Visual Distinction**: Manual towers display with purple borders and "✋ Manual" badges
- **Automatic Geocoding**: Addresses automatically retrieved and cached for performance
- **Dataset Integration**: Manual towers included in all export formats (CSV, KML, YOLO)
- **Dataset Restoration**: Import/export datasets to preserve manual towers across sessions
- **Provider Lock**: Prevents imagery mismatch by locking provider selection after detections

### Export & Analysis
- **CSV Export**: Detection lists with addresses, confidence scores, and coordinates for epidemiological tracking
- **KML Export**: Google Earth compatible files for geographic visualization
- **YOLO Format**: Training dataset exports with normalized coordinates for ML model improvement
- **Flexible Filtering**: Export subsets based on confidence thresholds or manual selection

### Search & Navigation
- **Address Search**: Find locations by street address, city, or neighborhood
- **Zipcode Search**: Define search areas by postal code boundaries
- **Custom Polygons**: Draw complex search areas with interactive polygon tool
- **Circular Search**: Radius-based search around specific coordinates
- **Tile Estimation**: Preview processing time before running detection (~100 tiles ≈ 30 seconds)

### Data Validation
- **Interactive Review**: Click towers in list to highlight on map (bidirectional)
- **False Positive Removal**: Uncheck detections to exclude from exports
- **Tile-by-Tile Review**: Systematic review mode for accuracy verification
- **Cross-Provider Validation**: Compare detections across different imagery sources

## Attribution
Please cite the following publication and this GitHub repository when utilizing TowerScout:
- Wong, KK, Segura T, Mein G, Lu J, Hannapel EJ, Kunz JM, Ritter T, Smith JC, Todeschini A, Nugen F, Edens C. Automated cooling tower detection through deep learning for Legionnaires’ disease outbreak investigations: a model development and validation study. *Lancet Digit Health.* 2024;6(7):e500-e506. [doi.org/10.1016/S2589-7500(24)00094-3](https://doi.org/10.1016/S2589-7500(24)00094-3)
- [TO COME: [CITATION.cff file](https://citation-file-format.github.io/)]


## Additional files
* YOLOv5 detector weights - see `MODEL_LICENSES.md` and `webapp/asset_manifest.v1.json`.
* EfficientNet weights - see `MODEL_LICENSES.md` and `webapp/asset_manifest.v1.json`.
* ZCTA shapefile data - see `DATA_LICENSES.md` and `webapp/asset_manifest.v1.json`.

This is a proof of concept and is not intended for commercial use. Users should adhere to terms of service when using tools and resources from any imagery and data providers. 


## License

The YOLO-enabled release is a composite-license package. TowerScout-authored code may be Apache-2.0 where ownership and relicensing authority are confirmed, but the current YOLO-enabled package/image is distributed with AGPL-3.0 obligations because it includes Ultralytics YOLOv5 runtime source and YOLO-derived detector weights.

See `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, and `PROVIDER_TERMS.md`. The generated release control ZIP is authoritative for release-specific source, checksum, image digest, SBOM-reference, and manifest metadata. The running local app also exposes the source/license notice at `/license`.
